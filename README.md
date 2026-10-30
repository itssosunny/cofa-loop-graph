# `cofa-loop-graph`

A clean-room, zero-dependency operating loop and Level-2 verification graph plugin for the 180-minute Cofa-Probe hackathon workspace with Codex.

It provides autonomous scope alignment (`2-Step Cofa-Grill`), a **task-type-agnostic architecture** (Universal Core + Conditional Data/Pipeline Rules + Conditional Web/Server Rules), vertical slicing with specialized subagents (`6.1 Sol`, `5.6 Terra`, `6.0 Luna`), and dynamic verification backed by `.cofa/cofa_verify.py`, `.cofa/with_server.py`, `.cofa/log_decision.sh`, and `.cofa/trace.json`.

Complies with the official OpenAI Codex Plugin specification, Agent Plugins 1.0 specification, and `@skill-creator` validation standards.

---

## Quick Start (Two Installation Methods)

### Method A: Automated All-in-One Install (Recommended for Exam Workspace)
Registers subagents into `~/.codex/agents/`, enables `multi_agent = true` in `~/.codex/config.toml`, copies all 6 skills to global/local paths, registers the plugin via `codex plugin`, and initializes `.cofa/` verifier scripts:

```bash
git clone https://github.com/itssosunny/cofa-loop-graph.git /tmp/cofa-plugin && bash /tmp/cofa-plugin/install.sh .
```

*Optional Model ID Overrides (e.g., during trial verification):*
```bash
SOL_MODEL_ID="gpt-6.1-sol" TERRA_MODEL_ID="gpt-5.6-terra" LUNA_MODEL_ID="gpt-6-luna" bash /tmp/cofa-plugin/install.sh .
```

### Method B: Official Codex Plugin CLI Install
Add this repository as a local or Git marketplace and install the plugin:

```bash
# From local directory:
codex plugin marketplace add /path/to/cofa-loop-graph
codex plugin add cofa-loop-graph@cofa

# Or from public GitHub repo:
codex plugin marketplace add itssosunny/cofa-loop-graph --ref main
codex plugin add cofa-loop-graph@cofa
```

---

## Task-Type-Agnostic Architecture

The loop detects and supports three task archetypes seamlessly:

1. **Archetype A: Data / Pipeline / ML / Quantitative CLI**:
   - Web server disabled (`"has_web_server": false`). Localhost bind checks skipped.
   - Enforces **Safe-But-Wrong Output Prevention**: prevents corrupt/missing inputs from silently returning `0`/`NaN`/`[]`.
   - Maps fields strictly by header name, never hardcoded column indices. No premature float rounding.
2. **Archetype B: Backend API / Microservice**:
   - Web server enabled (`"has_web_server": true`). Enforces `0.0.0.0` host binding.
   - Automated server management via `.cofa/with_server.py` with guaranteed process group cleanup (no zombie servers).
   - Validates HTTP response status codes, latency thresholds, and input validation.
3. **Archetype C: Full-Stack / Frontend Web App**:
   - Web server enabled (`"has_web_server": true`).
   - Requires explicit `loading`, `empty`, `inline-error` (no `window.alert()`), and `focus/hover` states.
   - Requires `tabular-nums` for numeric stability, `single-flight` double-submit prevention, and race condition guards.

---

## File Structure

```text
cofa-loop-graph/
├── plugin.json                              # Agent Plugins 1.0 manifest ($schema, interface, extensions, mcpServers)
├── .codex-plugin/
│   └── plugin.json                          # Canonical Codex plugin manifest
├── .mcp.json                                # Declares "evaluate" MCP server (.cofa/luna_mcp.py mcp)
├── .agents/
│   └── plugins/
│       └── marketplace.json                 # Marketplace catalog ("cofa" namespace)
├── agents/                                  # Codex Subagent Definitions (registered in config.toml)
│   ├── executor.toml                        # 5.6 Terra worker (workspace-write, 3-hypothesis debugging, safe-but-wrong prevention)
│   ├── luna_checker.toml                    # 6.0 Luna evaluator (read-only, evidence-before-score, safe-but-wrong checks)
│   └── architect.toml                       # 6.1 Sol auditor (read-only, 2-axis review: Spec/Fidelity + Closed-set defect mechanisms)
├── skills/                                  # 6 Portable Workflow Skills (with agents/openai.yaml)
│   ├── cofa-loop-graph/
│   │   ├── SKILL.md                         # 180m operating loop (Archetype detection, Checkpoint 1, Slicing, Checkpoint 2)
│   │   └── agents/openai.yaml               # Codex skill presentation metadata
│   ├── grill-me/
│   │   ├── SKILL.md                         # 5-line inverted restate + {root, first_nail} + 1-Round Frontier grill
│   │   └── agents/openai.yaml
│   ├── to-questionnaire/
│   │   ├── SKILL.md                         # 3-Stage progressive DM questions for 업무 담당자
│   │   └── agents/openai.yaml
│   ├── sharpen/
│   │   ├── SKILL.md                         # Anti-over-engineering rules (NO-OVER-ENGINEERING)
│   │   └── agents/openai.yaml
│   ├── verification-before-completion/
│   │   ├── SKILL.md                         # Iron Law: fresh evidence before claims (no git push)
│   │   └── agents/openai.yaml
│   └── evaluate/
│       ├── SKILL.md                         # System-1 calibrated evaluation with 6.0 Luna (noul/choice/score/items)
│       └── agents/openai.yaml
├── .cofa/
│   ├── cofa_verify.py                       # Level-2 verifier (BASE guards, test-cheating detection, BC, QM, QR, cheatsheet)
│   ├── luna_mcp.py                          # Dual-mode evaluate MCP server & CLI runner (Mode 1 /v1/decisions, Mode 2 codex exec)
│   ├── with_server.py                       # Process group server wrapper with guaranteed TCP wait and SIGKILL cleanup
│   ├── log_decision.sh                      # UTC ISO-8601 decision logger for .cofa/decisions.tsv
│   └── trace.template.json                  # Template schema for .cofa/trace.json
├── install.sh                               # Automated installer with subagents, 6 skills, and [mcp_servers.evaluate] wiring
└── README.md
```

---

## What Is Included

### 1. Three Specialized Codex Subagents (`agents/*.toml`)
Installed into `~/.codex/agents/` and registered under `[agents.<name>]` in `~/.codex/config.toml`:

| Subagent | Default Model | Mode | Purpose |
|---|---|---|---|
| **`executor`** | `gpt-5.6-terra` | `workspace-write` | Fast implementation worker with 3-hypothesis debugging, 3-strike circuit breaker, and safe-but-wrong checks. |
| **`luna_checker`** | `gpt-6-luna` | `read-only` | System-1 fast evaluator citing `evidence_quote` and `limitation_or_gap` before assigning score. |
| **`architect`** | `gpt-6.1-sol` | `read-only` | System-2 independent auditor checking 2 axes: (1) Spec, Safe-But-Wrong & Fidelity, (2) Closed-Set Defect Mechanisms. |

### 2. Six Workflow Skills (`skills/*`)
Each skill includes a validated `SKILL.md` and `agents/openai.yaml`:

1. **`cofa-loop-graph`**: Integrated 180-minute operating loop connecting Checkpoint 1, vertical slice execution, and Checkpoint 2.
2. **`grill-me`**: 5-line inverted restate + `{ root, first_nail }` check + 1-round fast Frontier interview.
3. **`to-questionnaire`**: Formulates progressive, high-context questions for the Scenario Agent (`업무 담당자`) DM (never asks `"1, 2, 3, 4로 할 일 알려주세요"`).
4. **`sharpen`**: Anti-over-engineering rulebook (`NO-OVER-ENGINEERING`) ensuring minimal necessary abstractions and outcome-driven delivery.
5. **`verification-before-completion`**: Strict verification gate requiring fresh command execution output before making completion claims or committing.
6. **`evaluate`**: System-1 calibrated evaluation of observable evidence (`state`) using `6.0 Luna` (`gpt-6-luna`), supporting `noul`, `choice`, `score`, and `items`.

### 3. Dual-Mode `evaluate` MCP Server & CLI Runner (`.cofa/luna_mcp.py`)
100% Python 3 Standard Library MCP server and standalone evaluation tool powered by `6.0 Luna` (`gpt-6-luna`):
- **Dual-Mode Engine**:
  - **Mode 1 (Native System-1)**: Calls `POST {OPENAI_BASE_URL}/v1/decisions` when `OPENAI_API_KEY` is available.
  - **Mode 2 (CLI Fallback)**: Automatically falls through on error or offline to `codex exec -m gpt-6-luna --sandbox read-only --output-schema`.
- **Mathematical Calibrated Metrics**:
  - `choice` confidence: $\max\left(0.0, \frac{N \cdot p_{\text{top}} - 1}{N - 1}\right)$
  - `score` continuous value & MAD confidence: $\text{score} = \sum i \cdot p_i$, $\text{confidence} = \max\left(0.0, 1.0 - \frac{\text{spread}}{\text{MAD}}\right)$
  - `min_confidence` uncertainty thresholding
- **Stdio MCP Protocol**: Fully compatible with Codex MCP tools (`initialize`, `ping`, `tools/list`, `tools/call`).
- **CLI Runner**: `python3 .cofa/luna_mcp.py eval --request '{"state": "...", "questions": {...}}'`.

### 4. Level-2 Dynamic Verifier & Tool Suite (`.cofa/*`)
100% Python 3 Standard Library + Bash scripts. Requires zero external pip packages or API keys:
- **`[BASE-1] ZERO-STUB & NO-TEST-CHEATING`**: Fails on no-op handlers (`onClick={() => {}}`), `TODO`/`FIXME`, `[DEBUG-*]` leftovers, or test-cheating markers (`.skip`, `.only`, `.todo`, `@pytest.mark.skip`).
- **`[BASE-2] HOST-BIND-0000`**: Conditional on `has_web_server: true`. Ensures web servers bind to `0.0.0.0:<PORT>`.
- **`[BASE-3] CODE-DOC-FIDELITY`**: Ensures cited submission documents exist and are non-empty.
- **Dynamic Binary Checks (`binary_checks[]`)**: Validates code traceability, detects test-masking anti-patterns (`| tail`, `|| true`), and fires live HTTP probes (`--live`).
- **Dynamic Quantitative Metrics (`quantitative_metrics[]`)**: Measures latency and numeric thresholds against target values.
- **Dynamic Qualitative Rubrics (`qualitative_rubrics[]`)**: Invokes `6.0 Luna` with anti-injection guards and evidence-first scoring.
- **Pre-Submission Cheatsheet (`--cheatsheet`)**: Outputs a 1-page summary of decisions, rationales, logged `.cofa/decisions.tsv` entries, and limitations for `사후 Q&A`.
- **`with_server.py`**: Runs tests against background servers with guaranteed TCP polling and process group SIGTERM/SIGKILL termination.
- **`log_decision.sh`**: Records single-line sanitized decision records into `.cofa/decisions.tsv`.
- **`luna_mcp.py`**: Evaluates `noul`, `choice`, `score`, and `items` over observable state.

---

## 180-Minute Execution Protocol

```
[T+00m..02m] Plugin Installation (Method A or B)
     │
[T+02m..15m] Checkpoint 1: 2-Step Cofa-Grill
     │       • Step 1A: Archetype detection (Data/API/Web) + 25-line .cofa/repo_map.md + DM questions
     │       • Step 1B: 1-Round Frontier grill (restate + root/first_nail) to lock MVP flow & trace.json
     │       • Log baseline: bash .cofa/log_decision.sh "T+15m" "Lock MVP" "..." "..." "PASS"
     │
[T+15m..150m] Build Loop: Tracer-Bullet Vertical Slices
     │       • Delegate slices to executor (5.6 Terra) with fork_context: false
     │       • Server tasks: python3 .cofa/with_server.py --server "..." --port ... -- python3 .cofa/cofa_verify.py --run-tests --live
     │       • Data tasks: python3 .cofa/cofa_verify.py --run-tests
     │       • Check: luna_checker (6.0 Luna)
     │       • Log decisions to .cofa/decisions.tsv
     │       • Slot cleanup: close_agent on completed instances
     │
[T+150m..175m] Checkpoint 2: Pre-Submission Verification & Defense
     │       • python3 .cofa/cofa_verify.py --run-tests --luna --cheatsheet
     │       • Run architect (6.1 Sol) for 2-axis review (Spec/Fidelity + Closed-set defect mechanisms)
     │       • Review cheatsheet & .cofa/decisions.tsv for 사후 Q&A
     │
[T+175m..180m] Final Local Commit
             • git add -A && git commit -m "..."
             • NEVER git push (strictly prohibited in exam)
```

---

## Important Exam Rules

1. **Local Git Only**: Do **NOT** run `git push`. Remote pushes are strictly prohibited in the exam environment.
2. **Standard Models Only**: Use only the 3 officially recommended models (`6.1 Sol`, `5.6 Terra`, `6.0 Luna`).
3. **No External APIs or Keys**: All evaluations run either locally via Python standard library or via pre-authenticated `codex exec` calls to `6.0 Luna`.
