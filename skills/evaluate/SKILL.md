---
name: evaluate
description: Fast System-1 calibrated evaluation of observable evidence (state) using 6.0 Luna (gpt-6-luna). Evaluates boolean predicates (noul), categorical classifications (choice), and ordered rubric scores (score) with mathematical confidence.
---

# `evaluate`: System-1 Calibrated Evaluation with 6.0 Luna

The `evaluate` tool provides ultra-fast, deterministic, calibrated probability judgments over observable evidence (`state`) using **`6.0 Luna` (`gpt-6-luna`)**. It powers sub-second checks for operating loops, test suites, and subagents without verbose conversational overhead.

---

## 1. Core Principles

1. **System-1 Judgment vs. System-2 Generation**:
   - `evaluate` is NOT a text generator. It takes an observed `state` and a set of typed `questions`, and returns calibrated probabilities, expected scores, and mathematical confidence values.
2. **Observable Evidence First**:
   - Pass raw observed facts (command stdout/stderr, code snippets, HTTP responses, file contents) into `state`.
   - Never pass pre-asserted conclusions (e.g. *"The test passed with no errors, is it working?"*).
3. **Dual-Mode Engine (`gpt-6-luna`)**:
   - **Mode 1 (Native System-1)**: Calls `POST {OPENAI_BASE_URL}/v1/decisions` when `OPENAI_API_KEY` is present.
   - **Mode 2 (Pure CLI Fallback)**: Automatically falls back to `codex exec -m gpt-6-luna --sandbox read-only --output-schema` if `/v1/decisions` returns an error, HTTP 404, or if running offline.

---

## 2. Question Types

### 1) `noul` (Boolean Probability)
Evaluates whether a proposition is TRUE based strictly on the observable evidence in `state`, returning a calibrated probability $P \in [0.0, 1.0]$.

**Input Question**:
```json
{
  "has_zero_stub_violations": {
    "type": "noul",
    "instructions": "Does the code contain any TODO, FIXME, pass, or stub placeholder implementations?"
  }
}
```

**Output**:
```json
{
  "has_zero_stub_violations": {
    "type": "noul",
    "noul": 0.05
  }
}
```
*(If `min_confidence` is provided and $|2P - 1.0| < \text{min\_confidence}$, `"uncertain": true` is added).*

---

### 2) `choice` (Categorical Classification)
Selects the best option from a dictionary or list of choices, returning per-option probabilities and overall confidence:
$$\text{confidence} = \max\left(0.0, \frac{N \cdot p_{\text{top}} - 1}{N - 1}\right)$$

**Input Question**:
```json
{
  "error_category": {
    "type": "choice",
    "instructions": "Classify the failure reported in the server error log.",
    "criteria": {
      "network": "Connection refused, DNS timeout, or socket hangup",
      "auth": "Unauthorized 401, Forbidden 403, or invalid token",
      "validation": "Unprocessable Entity 422, bad parameter, or schema mismatch",
      "internal": "Unhandled 500 error or stack trace dump"
    },
    "min_confidence": 0.60
  }
}
```

**Output**:
```json
{
  "error_category": {
    "type": "choice",
    "choice": "validation",
    "confidence": 0.88,
    "probabilities": {
      "validation": 0.91,
      "internal": 0.06,
      "auth": 0.02,
      "network": 0.01
    }
  }
}
```
*(If `confidence < min_confidence`, `choice` is set to `"__uncertain__"` and `"uncertain": true` is added).*

---

### 3) `score` (Ordered Rubric Levels)
Scores `state` against an ordered array of descriptive rubric levels ($0, 1, 2, \dots, N-1$). It computes the continuous expected score and Mean Absolute Deviation (MAD) confidence:
$$\text{score} = \sum_{i=0}^{N-1} i \cdot p_i, \quad m = \arg\max_i(p_i), \quad \text{MAD} = \frac{1}{N}\sum_{i=0}^{N-1} \left|i - \frac{N-1}{2}\right|, \quad \text{confidence} = \max\left(0.0, 1.0 - \frac{\sum_i p_i |i - m|}{\text{MAD}}\right)$$

**Input Question**:
```json
{
  "ui_responsiveness": {
    "type": "score",
    "instructions": "Rate the layout and responsive design of the component code.",
    "criteria": [
      "Hardcoded pixel widths, broken flex/grid, overlapping elements on mobile",
      "Responsive layout with minor padding/margin inconsistencies",
      "Clean fluid design, modern CSS grid/flex, fully accessible touch targets"
    ]
  }
}
```

**Output**:
```json
{
  "ui_responsiveness": {
    "type": "score",
    "score": 1.92,
    "confidence": 0.89,
    "legend": {
      "0": "Hardcoded pixel widths, broken flex/grid, overlapping elements on mobile",
      "1": "Responsive layout with minor padding/margin inconsistencies",
      "2": "Clean fluid design, modern CSS grid/flex, fully accessible touch targets"
    },
    "probabilities": {
      "0": 0.01,
      "1": 0.06,
      "2": 0.93
    }
  }
}
```

---

### 4) `items` (Batch Evaluation)
Pass up to 50 items in a single call. Each item is evaluated independently in the context of `state`:

```json
{
  "state": "Requirements: all database models must define created_at and updated_at timestamps.",
  "items": {
    "user_model": "class User(Base): id = Column(Integer, primary_key=True)",
    "order_model": "class Order(Base): id = Column(Integer); created_at = Column(DateTime); updated_at = Column(DateTime)"
  },
  "questions": {
    "has_required_timestamps": {
      "type": "noul",
      "instructions": "Does the model class define both created_at and updated_at?"
    }
  }
}
```

**Output**:
```json
{
  "results": {
    "user_model": {
      "has_required_timestamps": { "type": "noul", "noul": 0.02 }
    },
    "order_model": {
      "has_required_timestamps": { "type": "noul", "noul": 0.98 }
    }
  },
  "errors": {},
  "meta": { "item_count": 2 }
}
```

---

## 3. Standard 3-Zone Decision Thresholds

When evaluating automated gates and loop milestones, apply the standard 3-zone interpretation:

| Zone | `noul` Probability | 3-Level `score` (0..2) | Meaning & Action |
|---|---|---|---|
| **PASS** | $\ge 0.85$ | $\ge 1.70$ | Safe to proceed to next slice or phase without human intervention. |
| **SUSPICIOUS** | $0.50 .. 0.84$ | $1.00 .. 1.69$ | Borderline or ambiguous evidence. Requires investigation or System-2 review (`architect`). |
| **FAIL** | $< 0.50$ | $< 1.00$ | Definite violation or defect. Must be fixed before submission. |

---

## 4. How to Invoke

### Option A: Via MCP Tool (`evaluate`)
When registered as an MCP server, call the `evaluate` tool directly:
```json
{
  "name": "evaluate",
  "arguments": {
    "state": "<observed evidence text or JSON>",
    "questions": {
      "check_id": {
        "type": "noul",
        "instructions": "Is the condition satisfied?"
      }
    }
  }
}
```

### Option B: Via CLI Subcommand (`eval`)
Run evaluations directly from the shell:
```bash
# Inline JSON
python3 .cofa/luna_mcp.py eval --request '{"state": "...", "questions": {...}}'

# Or via JSON file
python3 .cofa/luna_mcp.py eval --request /tmp/eval_request.json
```

---

## 5. English Model-Facing Input Policy

Use English for every model-facing natural-language field: question `instructions`, `criteria` descriptions, and evidence/context text in `state` or `items`. English questions alone are insufficient when the state still contains non-English prose. Apply this to MCP calls and CLI requests.

Before calling `evaluate`:
1. **Translate Evidence Faithfully**: Retain original non-English evidence in the local workspace or document, and pass a faithful English translation in `state` or `items`.
2. **Preserve Modality & Uncertainty**: Preserve speaker attribution, negation, conditions, scope, quantities, chronology, and uncertainty. Do not resolve ambiguity or inject agent conclusions while translating.
3. **Preserve Literals & Identifiers**: Keep programmatic keys, IDs, file paths, URLs, code snippets, and exact-match literals unchanged.
4. **Verify Assembled Payload**: Ensure the assembled payload contains clear, calibrated English text to maximize scoring accuracy with `6.0 Luna`. User-facing conversations remain in the user's preferred language.

