#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual-Mode evaluate MCP Server and CLI runner for 6.0 Luna (gpt-6-luna).
100% Python 3 Standard Library.

Modes:
  Mode 1 (Native System-1 via OpenAI /v1/decisions):
    Calls POST {OPENAI_BASE_URL}/v1/decisions when OPENAI_API_KEY is available.
    Circuit breaker falls through to Mode 2 on any non-200, 404, or network failure.
  Mode 2 (Pure CLI Fallback via codex exec):
    Executes 'codex exec -m gpt-6-luna' with a strict JSON schema for calibrated probabilities.

Supported Question Types:
  - 'noul' / 'predicate': Boolean probability P in [0.0, 1.0]
  - 'choice': Categorical classification with per-option probabilities and confidence
  - 'score': Ordered rubric levels 0..N-1 with continuous expected score and MAD confidence
  - 'items': Optional batch evaluation across multiple items
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple, Union

_DECISIONS_ENDPOINT_AVAILABLE = True


# ============================================================================
# Mathematical Metrics for Calibrated Probabilities
# ============================================================================

def compute_noul_metrics(prob: float, min_confidence: Optional[float] = None) -> Dict[str, Any]:
    """Computes calibrated probability and uncertainty for a boolean predicate ('noul')."""
    p = max(0.0, min(1.0, float(prob)))
    res: Dict[str, Any] = {
        "type": "noul",
        "noul": round(p, 4)
    }
    if min_confidence is not None:
        # Distance from 0.5 scaled to [0, 1]
        binary_conf = abs(2.0 * p - 1.0)
        if binary_conf < float(min_confidence):
            res["uncertain"] = True
    return res


def compute_choice_metrics(raw_probs: Dict[str, float], min_confidence: Optional[float] = None) -> Dict[str, Any]:
    """
    Computes choice result, per-option probabilities, and confidence over N options:
      confidence = max(0.0, (N * p_top - 1.0) / (N - 1.0))
    """
    N = len(raw_probs)
    if N == 0:
        return {
            "type": "choice",
            "choice": "__uncertain__",
            "confidence": 0.0,
            "probabilities": {},
            "uncertain": True
        }

    total = sum(raw_probs.values())
    if total > 0.0:
        probs = {str(k): float(v) / total for k, v in raw_probs.items()}
    else:
        probs = {str(k): 1.0 / float(N) for k in raw_probs.keys()}

    top_choice = max(probs.keys(), key=lambda k: probs[k])
    p_top = probs[top_choice]

    if N > 1:
        conf = max(0.0, (float(N) * p_top - 1.0) / (float(N) - 1.0))
    else:
        conf = 1.0

    res: Dict[str, Any] = {
        "type": "choice",
        "choice": top_choice,
        "confidence": round(conf, 4),
        "probabilities": {k: round(v, 4) for k, v in probs.items()}
    }

    if min_confidence is not None and conf < float(min_confidence):
        res["choice"] = "__uncertain__"
        res["uncertain"] = True

    return res


def compute_score_metrics(
    raw_probs: List[float],
    criteria: Optional[List[Any]] = None,
    min_confidence: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes continuous expected score, MAD-based confidence, and per-level probabilities:
      score = sum(i * p_i)
      m = argmax(p_i)
      MAD = (1 / N) * sum(|i - (N - 1) / 2|)
      spread = sum(p_i * |i - m|)
      confidence = max(0.0, 1.0 - (spread / MAD))
    """
    N = len(raw_probs)
    if N == 0:
        return {
            "type": "score",
            "score": 0.0,
            "confidence": 0.0,
            "legend": {},
            "probabilities": {},
            "uncertain": True
        }

    total = sum(raw_probs)
    if total > 0.0:
        probs = [float(p) / total for p in raw_probs]
    else:
        probs = [1.0 / float(N)] * N

    score_val = sum(i * probs[i] for i in range(N))
    m = max(range(N), key=lambda i: probs[i])

    mad = sum(abs(i - (float(N) - 1.0) / 2.0) for i in range(N)) / float(N) if N > 0 else 1.0
    spread = sum(probs[i] * abs(i - m) for i in range(N))
    if mad > 0.0:
        conf = max(0.0, 1.0 - (spread / mad))
    else:
        conf = 1.0

    if criteria and isinstance(criteria, list) and len(criteria) == N:
        legend = {str(i): str(criteria[i]) for i in range(N)}
    else:
        legend = {str(i): f"Level {i}" for i in range(N)}

    res: Dict[str, Any] = {
        "type": "score",
        "score": round(score_val, 4),
        "confidence": round(conf, 4),
        "legend": legend,
        "probabilities": {str(i): round(probs[i], 4) for i in range(N)}
    }

    if min_confidence is not None and conf < float(min_confidence):
        res["uncertain"] = True

    return res


# ============================================================================
# Dual-Mode Evaluation Handlers
# ============================================================================

def _normalize_instructions(instr: Any) -> str:
    if isinstance(instr, (dict, list)):
        return json.dumps(instr, ensure_ascii=False)
    return str(instr if instr is not None else "")


def _extract_choice_options(qdef: Dict[str, Any]) -> List[Tuple[str, str]]:
    criteria = qdef.get("criteria")
    choices = qdef.get("choices")
    opts: List[Tuple[str, str]] = []

    if isinstance(criteria, dict):
        for k, v in criteria.items():
            opts.append((str(k), str(v if v is not None else k)))
    elif isinstance(criteria, list):
        for c in criteria:
            if isinstance(c, dict):
                v = str(c.get("value", c.get("name", "")))
                d = str(c.get("description", v))
                opts.append((v, d))
            else:
                opts.append((str(c), str(c)))
    elif isinstance(choices, list):
        for c in choices:
            if isinstance(c, dict):
                v = str(c.get("value", c.get("name", "")))
                d = str(c.get("description", v))
                opts.append((v, d))
            else:
                opts.append((str(c), str(c)))
    return opts


def _extract_score_levels(qdef: Dict[str, Any]) -> List[str]:
    criteria = qdef.get("criteria")
    levels = qdef.get("levels")
    out: List[str] = []

    source = criteria if isinstance(criteria, list) else (levels if isinstance(levels, list) else [])
    for i, item in enumerate(source):
        if isinstance(item, dict):
            desc = str(item.get("description", item.get("label", f"L{i}")))
        else:
            desc = str(item)
        out.append(desc)
    if not out:
        out = ["Level 0", "Level 1", "Level 2"]
    return out


def _evaluate_mode1_decisions(
    state: Any,
    questions: Dict[str, Any],
    model_id: str,
    api_key: str
) -> Dict[str, Any]:
    """Mode 1: Native System-1 via OpenAI /v1/decisions endpoint."""
    state_str = json.dumps(state, ensure_ascii=False, indent=2) if isinstance(state, (dict, list)) else str(state)

    wire_questions: List[Dict[str, Any]] = []
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        instr_str = _normalize_instructions(qdef.get("instructions"))

        if qtype in ("noul", "predicate"):
            wire_questions.append({
                "type": "predicate",
                "name": qid,
                "instructions": instr_str
            })
        elif qtype == "choice":
            opts = _extract_choice_options(qdef)
            wire_questions.append({
                "type": "choice",
                "name": qid,
                "instructions": instr_str,
                "choices": [{"value": val, "description": desc} for val, desc in opts]
            })
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            wire_questions.append({
                "type": "score",
                "name": qid,
                "instructions": instr_str,
                "levels": [{"label": f"L{i}", "description": desc} for i, desc in enumerate(levels)]
            })

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    url = f"{base_url}/decisions"

    req_payload = json.dumps({
        "model": model_id,
        "input": state_str,
        "questions": wire_questions
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=req_payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        resp_bytes = response.read()
        resp_data = json.loads(resp_bytes.decode("utf-8"))

    raw_answers = (
        resp_data.get("answers")
        or resp_data.get("decisions")
        or resp_data.get("results")
        or resp_data.get("questions")
        or []
    )
    ans_map: Dict[str, Any] = {}
    if isinstance(raw_answers, list):
        for a in raw_answers:
            name = a.get("name") or a.get("question_id") or a.get("id")
            if name:
                ans_map[str(name)] = a
    elif isinstance(raw_answers, dict):
        ans_map = {str(k): v for k, v in raw_answers.items()}

    formatted: Dict[str, Any] = {}
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        ans = ans_map.get(qid, {})
        min_conf = qdef.get("min_confidence")

        if qtype in ("noul", "predicate"):
            prob = float(ans.get("probability", ans.get("score", ans.get("value", 0.5))))
            formatted[qid] = compute_noul_metrics(prob, min_conf)
        elif qtype == "choice":
            raw_p = ans.get("probabilities", [])
            prob_map: Dict[str, float] = {}
            if isinstance(raw_p, list):
                for item in raw_p:
                    prob_map[str(item.get("value", ""))] = float(item.get("probability", 0.0))
            elif isinstance(raw_p, dict):
                prob_map = {str(k): float(v) for k, v in raw_p.items()}
            formatted[qid] = compute_choice_metrics(prob_map, min_conf)
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            raw_p = ans.get("probabilities", [])
            probs_list = [0.0] * len(levels)
            if isinstance(raw_p, list):
                for seq_idx, p in enumerate(raw_p):
                    if isinstance(p, dict):
                        val = p.get("value")
                        if val is not None and str(val).isdigit():
                            idx = int(val)
                            if 0 <= idx < len(levels):
                                probs_list[idx] = float(p.get("probability", 0.0))
                        elif seq_idx < len(levels):
                            probs_list[seq_idx] = float(p.get("probability", 0.0))
                    elif isinstance(p, (int, float)):
                        if seq_idx < len(levels):
                            probs_list[seq_idx] = float(p)
            elif isinstance(raw_p, dict):
                for i in range(len(levels)):
                    probs_list[i] = float(raw_p.get(str(i), 0.0))
            formatted[qid] = compute_score_metrics(probs_list, levels, min_conf)

    return formatted


def _mock_generate_output(questions: Dict[str, Any]) -> Dict[str, Any]:
    """Generates synthetic calibrated probabilities when COFA_EVAL_MOCK=1."""
    out: Dict[str, Any] = {}
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        if qtype in ("noul", "predicate"):
            out[qid] = {"probability": 0.95}
        elif qtype == "choice":
            opts = _extract_choice_options(qdef)
            keys = [val for val, _ in opts]
            if keys:
                p_map = {k: 0.1 for k in keys}
                p_map[keys[0]] = 0.8
                out[qid] = {"probabilities": p_map}
            else:
                out[qid] = {"probabilities": {}}
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            N = len(levels)
            probs = [0.1] * N
            if N > 0:
                probs[-1] = 0.8
                total = sum(probs)
                probs = [p / total for p in probs]
            out[qid] = {"probabilities": probs}
    return out


def _evaluate_mode2_codex(
    state: Any,
    questions: Dict[str, Any],
    model_id: str
) -> Dict[str, Any]:
    """Mode 2: Pure CLI Fallback via codex exec -m gpt-6-luna."""
    state_str = json.dumps(state, ensure_ascii=False, indent=2) if isinstance(state, (dict, list)) else str(state)

    schema_props: Dict[str, Any] = {}
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        if qtype in ("noul", "predicate"):
            schema_props[qid] = {
                "type": "object",
                "properties": {
                    "probability": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "required": ["probability"]
            }
        elif qtype == "choice":
            opts = _extract_choice_options(qdef)
            opt_keys = [val for val, _ in opts]
            schema_props[qid] = {
                "type": "object",
                "properties": {
                    "probabilities": {
                        "type": "object",
                        "properties": {k: {"type": "number", "minimum": 0.0, "maximum": 1.0} for k in opt_keys},
                        "required": opt_keys
                    }
                },
                "required": ["probabilities"]
            }
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            N = len(levels)
            schema_props[qid] = {
                "type": "object",
                "properties": {
                    "probabilities": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "minItems": N,
                        "maxItems": N
                    }
                },
                "required": ["probabilities"]
            }

    output_schema = {
        "type": "object",
        "properties": schema_props,
        "required": list(schema_props.keys())
    }

    prompt_lines = [
        "You are an expert System-1 calibrated evaluator.",
        "Evaluate the following questions strictly based on the observable facts in State.",
        "Do not assume or infer details not directly supported by State.",
        "",
        "=== State ===",
        state_str,
        "",
        "=== Questions ==="
    ]
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        instr = _normalize_instructions(qdef.get("instructions"))
        prompt_lines.append(f"Question ID: {qid}")
        prompt_lines.append(f"Type: {qtype}")
        prompt_lines.append(f"Instructions: {instr}")
        if qtype == "choice":
            opts = _extract_choice_options(qdef)
            prompt_lines.append(f"Choices: {json.dumps(dict(opts), ensure_ascii=False)}")
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            prompt_lines.append(f"Levels: {json.dumps(levels, ensure_ascii=False)}")
        prompt_lines.append("")
    prompt_lines.append("Return the calibrated probabilities matching the output schema.")
    prompt = "\n".join(prompt_lines)

    if os.environ.get("COFA_EVAL_MOCK") == "1":
        raw_data = _mock_generate_output(questions)
        formatted: Dict[str, Any] = {}
        for qid, qdef in questions.items():
            qtype = qdef.get("type", "noul")
            q_out = raw_data.get(qid, {})
            min_conf = qdef.get("min_confidence")
            if qtype in ("noul", "predicate"):
                p = float(q_out.get("probability", 0.5))
                formatted[qid] = compute_noul_metrics(p, min_conf)
            elif qtype == "choice":
                p_dict = q_out.get("probabilities", {})
                formatted[qid] = compute_choice_metrics(p_dict, min_conf)
            elif qtype == "score":
                levels = _extract_score_levels(qdef)
                p_list = q_out.get("probabilities", [])
                formatted[qid] = compute_score_metrics(p_list, levels, min_conf)
        return formatted

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as sf:
        json.dump(output_schema, sf, ensure_ascii=False)
        schema_path = sf.name
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as of:
        out_path = of.name

    raw_data: Dict[str, Any] = {}
    try:
        cmd = [
            "codex", "exec",
            "--skip-git-repo-check",
            "--color", "never",
            "--sandbox", "read-only",
            "-c", 'model_reasoning_effort="low"',
            "-m", model_id,
            "--output-schema", schema_path,
            "-o", out_path,
            prompt
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
        if proc.returncode != 0:
            raise RuntimeError(f"codex exec exited with status {proc.returncode}: {proc.stderr.strip()}")
        with open(out_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        raise RuntimeError("codex command not found in PATH")
    except Exception as exc:
        raise RuntimeError(f"codex exec error: {exc}")
    finally:
        if os.path.exists(schema_path):
            try:
                os.remove(schema_path)
            except OSError:
                pass
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass

    formatted: Dict[str, Any] = {}
    for qid, qdef in questions.items():
        qtype = qdef.get("type", "noul")
        q_out = raw_data.get(qid, {})
        min_conf = qdef.get("min_confidence")

        if qtype in ("noul", "predicate"):
            p = float(q_out.get("probability", 0.5))
            formatted[qid] = compute_noul_metrics(p, min_conf)
        elif qtype == "choice":
            p_dict = q_out.get("probabilities", {})
            formatted[qid] = compute_choice_metrics(p_dict, min_conf)
        elif qtype == "score":
            levels = _extract_score_levels(qdef)
            p_list = q_out.get("probabilities", [])
            formatted[qid] = compute_score_metrics(p_list, levels, min_conf)

    return formatted


def evaluate_single(state: Any, questions: Dict[str, Any], model_id: str) -> Dict[str, Any]:
    """Executes single evaluation round with circuit breaker fallback."""
    global _DECISIONS_ENDPOINT_AVAILABLE
    openai_key = os.environ.get("OPENAI_API_KEY")

    if openai_key and _DECISIONS_ENDPOINT_AVAILABLE:
        try:
            return _evaluate_mode1_decisions(state, questions, model_id, openai_key)
        except Exception as exc:
            _DECISIONS_ENDPOINT_AVAILABLE = False
            sys.stderr.write(f"[luna_mcp] Decisions API unavailable ({exc}), falling back to codex exec Mode 2.\n")
            sys.stderr.flush()
            return _evaluate_mode2_codex(state, questions, model_id)
    else:
        return _evaluate_mode2_codex(state, questions, model_id)


def evaluate_tool_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Top-level handler for tool 'evaluate', supporting state, questions, and items."""
    questions = arguments.get("questions")
    if not questions or not isinstance(questions, dict):
        raise ValueError("Missing or invalid 'questions' map in evaluate request.")

    state = arguments.get("state")
    items = arguments.get("items")
    if state is None and items is None:
        raise ValueError("Either 'state' or 'items' must be provided in evaluate request.")
    if state is None:
        state = ""

    model_arg = arguments.get("model")
    model_id = os.environ.get("LUNA_MODEL_ID", "gpt-6-luna")
    if model_arg:
        if model_arg in ("jev", "jev-latest", "jev-preview"):
            model_id = "gpt-6-luna"
        else:
            model_id = str(model_arg)

    if items is not None:
        normalized_items: Dict[str, Any] = {}
        if isinstance(items, list):
            for idx, item in enumerate(items):
                if isinstance(item, dict):
                    item_id = str(item.get("id", idx))
                    item_state = item.get("state", item)
                    normalized_items[item_id] = item_state
                else:
                    normalized_items[str(idx)] = item
        elif isinstance(items, dict):
            normalized_items = items
        else:
            raise ValueError("'items' must be a dictionary or a list of item objects.")

        batch_results: Dict[str, Any] = {}
        for item_id, item_state in normalized_items.items():
            context_state = {"item": item_state, "context": state} if state else {"item": item_state}
            batch_results[item_id] = evaluate_single(context_state, questions, model_id)
        return {
            "results": batch_results,
            "errors": {},
            "meta": {"item_count": len(batch_results)}
        }
    else:
        # Single evaluation: return results directly at top-level ({qid: answer_obj, ...})
        return evaluate_single(state, questions, model_id)


# ============================================================================
# MCP Stdio Server Protocol
# ============================================================================

def get_tool_definition() -> Dict[str, Any]:
    return {
        "name": "evaluate",
        "description": "System-1 fast calibrated evaluation of observable evidence (state) using 6.0 Luna (gpt-6-luna). Evaluates boolean predicates (noul), categorical classifications (choice), and ordered rubric scores (score) with mathematical confidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "description": "Content to judge: plain text, code snippet, log output, or structured JSON object/array. Optional with items, where it is sent to every item as context."
                },
                "questions": {
                    "type": "object",
                    "description": "Map of question_id -> question definition with type ('noul', 'choice', 'score'), instructions, criteria, and optional min_confidence.",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "noul (boolean predicate probability in [0, 1]), choice (categorical classification), or score (continuous position on ordered criteria levels)"
                            },
                            "instructions": {
                                "description": "The judgment to make: string, or object/array for definitions and examples."
                            },
                            "criteria": {
                                "description": "Optional for noul; map of option to description for choice; ordered array of level descriptions for score."
                            },
                            "min_confidence": {
                                "type": ["null", "number"],
                                "description": "Abstain threshold in [0, 1]. Below this threshold, choice becomes '__uncertain__' and uncertain=True is added."
                            }
                        },
                        "required": ["type", "instructions"]
                    }
                },
                "items": {
                    "description": "Optional map or array of items to evaluate independently in batch.",
                    "anyOf": [
                        {"type": "object"},
                        {"type": "array", "items": {"type": "object"}}
                    ]
                },
                "model": {
                    "type": "string",
                    "description": "Optional model override (defaults to gpt-6-luna)."
                },
                "include_item_usage": {
                    "type": "boolean",
                    "description": "Optional boolean to include item usage metadata."
                }
            },
            "required": ["questions"]
        }
    }


def run_mcp_server() -> None:
    """Runs a standard MCP JSON-RPC 2.0 stdio server with dual newline / Content-Length framing."""
    stdin_stream = sys.stdin
    stdout_stream = sys.stdout

    while True:
        line = stdin_stream.readline()
        if not line:
            break

        stripped = line.strip()
        if not stripped:
            continue

        uses_content_length = False
        body_str = ""

        if stripped.lower().startswith("content-length:"):
            uses_content_length = True
            try:
                length = int(stripped.split(":", 1)[1].strip())
            except ValueError:
                continue

            # Read headers until empty line
            while True:
                h_line = stdin_stream.readline()
                if not h_line or h_line.strip() == "":
                    break

            body_str = stdin_stream.read(length)
        elif stripped.startswith("{") or stripped.startswith("["):
            body_str = stripped
        else:
            continue

        try:
            req = json.loads(body_str)
        except json.JSONDecodeError:
            continue

        if not isinstance(req, dict):
            continue

        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        response: Optional[Dict[str, Any]] = None

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "cofa-evaluate",
                        "version": "0.1.0"
                    }
                }
            }
        elif method in ("notifications/initialized", "initialized"):
            response = None
        elif method == "ping":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [get_tool_definition()]
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name == "evaluate":
                try:
                    eval_out = evaluate_tool_handler(tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(eval_out, ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as err:
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Evaluation error: {err}"
                        }
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        else:
            if msg_id is not None:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }

        if response is not None:
            resp_body = json.dumps(response, ensure_ascii=False)
            if uses_content_length:
                payload = f"Content-Length: {len(resp_body.encode('utf-8'))}\r\n\r\n{resp_body}"
                stdout_stream.write(payload)
            else:
                stdout_stream.write(resp_body + "\n")
            stdout_stream.flush()


# ============================================================================
# CLI Runner Entrypoint
# ============================================================================

def run_eval_cli(request_arg: str) -> int:
    """CLI test and evaluation runner that parses JSON input and prints result."""
    text = request_arg.strip()
    if text.startswith("{") or text.startswith("["):
        data = json.loads(text)
    else:
        with open(text, "r", encoding="utf-8") as f:
            data = json.load(f)

    if not isinstance(data, dict):
        sys.stderr.write("Error: request JSON must be a dictionary object.\n")
        return 1

    result = evaluate_tool_handler(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Dual-Mode evaluate MCP Server and CLI runner for 6.0 Luna")
    subparsers = parser.add_subparsers(dest="subcommand")

    # MCP stdio subcommand
    subparsers.add_parser("mcp", help="Run MCP JSON-RPC 2.0 stdio server")

    # eval subcommand
    eval_parser = subparsers.add_parser("eval", help="Evaluate request from inline JSON or file path")
    eval_parser.add_argument("--request", required=True, help="Inline JSON string or path to request JSON file")

    # If no subcommand provided, default to mcp
    if len(sys.argv) == 1:
        run_mcp_server()
        return 0

    args = parser.parse_args()
    if args.subcommand == "eval":
        return run_eval_cli(args.request)
    else:
        run_mcp_server()
        return 0


if __name__ == "__main__":
    sys.exit(main())
