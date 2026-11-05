# `cofa-loop-graph`

A clean-room, zero-dependency operating loop and Level-2 verification graph plugin for the 180-minute Cofa-Probe hackathon workspace with Codex.

It provides autonomous scope alignment (`2-Step Cofa-Grill`), a **task-type-agnostic architecture** (Universal Core + Conditional Data/Pipeline Rules + Conditional Web/Server Rules), vertical slicing with specialized subagents (`6.1 Sol`, `5.6 Terra`, `6.0 Luna`), and dynamic verification backed by `.cofa/cofa_verify.py`, `.cofa/with_server.py`, `.cofa/log_decision.sh`, and `.cofa/trace.json`.

Complies with the official OpenAI Codex Plugin specification, Agent Plugins 1.0 specification, and `@skill-creator` validation standards.

---

## Quick Start (Two Installation Methods)

### Method A: Automated All-in-One Install (Recommended for Exam Workspace)
Registers subagents into `~/.codex/agents/`, enables `multi_agent = true` in `~/.codex/config.toml`, copies all 8 skills to global/local paths, registers the plugin via `codex plugin`, and initializes `.cofa/` verifier scripts:

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
3. **Archetype C: Full-Stack / Frontend Web App (4-Layer Web Architecture `[BC-C1]`)**:
   - Web server enabled (`"has_web_server": true`).
   - Strict 4-Layer Separation:
     - `data/parser`: Header-name mapping (never numeric indices) + row error quarantine + zero Safe-But-Wrong masking.
     - `domain/model`: Pure business logic, filtering, aggregations (derived state; never duplicated in mutable state).
     - `api/server`: `0.0.0.0` routes returning structured data + anomaly metadata.
     - `ui/components`: 4-Partition state (`Raw Data`, `View Control`, `Async Feedback`, `Derived State`) + UI 5-State Matrix (`default`, `loading`, `empty`, `filter-zero` with reset, `inline-error` with recovery guidance) + `NO-PASSWORD-POPUP-TRAP` (suppress Chrome password manager popup via `autoComplete="new-password"` or `type="text"` with `WebkitTextSecurity:'disc'` to prevent proctoring fullscreen exit) + 1-Click Role Switcher buttons (`[관리자 즉시 로그인]`, `[직원 즉시 로그인]`).
   - Requires `tabular-nums` for numeric stability, `single-flight` double-submit prevention, and race condition guards.

---

## 3-Tier Test Pyramid & Bidirectional Traceability (`@trace`)

Every functional check (`BC-*`) and quantitative metric (`QM-*`) is bound to test code via explicit bidirectional traceability:
- **Tier 1 (`unit`)**: Fast unit tests for `data/parser` header mapping & row quarantine invariants (`BC-*`), data row conservation (`QM-01`), and `domain/model` pure business logic.
- **Tier 2 (`integration`)**: Integration tests for `api/server` request validation, role guard checks, and domain score/count aggregation metrics (`QM-02`).
- **Tier 3 (`e2e`)**: End-to-end DOM rendering and interaction tests via `.cofa/with_server.py` and the bundled headless `playwright` MCP server. Verifies 5-state transitions, 1-Click Role Switcher execution, and 0 console errors.
- **Bidirectional `@trace` Tagging**: Every test function or file MUST contain the literal check ID (e.g., `# @trace BC-01`, `// @trace BC-02`, `# @trace QM-01`).
- **60-Second Cofa Browser Batched Smoke (H-Tier)**: Prior to final submission, click through the Cofa left-sidebar Browser preview tab:
  1. 기본 렌더링 및 CSV 로드 확인 (헤더/데이터 정상 표시 여부)
  2. 1-Click 역할 전환 버튼 클릭 동작 확인 (관리자/직원 권한 즉시 전환)
  3. 필터 0건 / 인라인 에러 등 5-State 전환 확인 (빈 검색결과 초기화 버튼 동작)
  4. 브라우저 런타임/콘솔 에러 0건 확인 (DevTools 콘솔 Uncaught Exception 부재)

---

## 4-Perspective Graph Verification

Built directly into `.cofa/cofa_verify.py`, the verifier enforces four architectural perspectives:
- **Perspective 1 (`gate_lock`)**: Frozen verification table lock (`gate_frozen: true`). Enforces 3-Tier Test Pyramid coverage (`unit`, `integration`, and `e2e` when web server is active) (`P1-TEST-TIER-GAP`, `P1-TEST-TIER-INVALID`). Prevents removing frozen `BC-*` checks or skipping them via `SKIP`/`N/A` (No Skip-with-Reason Escape).
- **Perspective 2 (`structure_wiring`)**: Live entrypoint reachability (`CODE-WIRING-B1`). Ensures every non-entrypoint module or parser referenced in trace table or `qa_briefing` is imported and wired into the application flow (zero orphaned modules).
- **Perspective 3 (`ontology_contract`)**: Enforces header-name mapping contracts on CSV parsers, forbids `window.alert()` in UI components, and enforces Chrome password manager popup suppression (`NO-PASSWORD-POPUP-TRAP`) to prevent proctoring fullscreen-exit penalties.
- **Perspective 4 (`traceability_dag`)**: Verifies complete DAG edges from requirements/constraints/invariants/quantitative metrics (`rule_kind` + `source` + `description`) to code (`code_refs`) to test files (`test_refs` containing literal `@trace BC-XX` / `@trace QM-XX`) to architecture decisions (`decision_and_rationale`). Flag missing test files (`P4-MISSING-TEST-FILE`) or untagged test files (`P4-TEST-TRACE-TAG`).

---

## File Structure

```text
cofa-loop-graph/
├── AGENTS.md                                # Workspace & agent operating instructions
├── plugin.json                              # Agent Plugins 1.0 manifest ($schema, interface, extensions, mcpServers)
├── .codex-plugin/
│   └── plugin.json                          # Canonical Codex plugin manifest
├── .mcp.json                                # Declares "evaluate" (Luna) and "playwright" (--headless) MCP servers
├── .agents/
│   └── plugins/
│       └── marketplace.json                 # Marketplace catalog ("cofa" namespace)
├── agents/                                  # Codex Subagent Definitions (registered in config.toml)
│   ├── executor.toml                        # 5.6 Terra worker (workspace-write, 3-hypothesis debugging, safe-but-wrong prevention)
│   ├── luna_checker.toml                    # 6.0 Luna evaluator (read-only, evidence-before-score, safe-but-wrong checks)
│   └── architect.toml                       # 6.1 Sol auditor (read-only, 2-axis review: Spec/Fidelity + Closed-set defect mechanisms)
├── skills/                                  # 8 Portable Workflow Skills (with agents/openai.yaml)
│   ├── cofa-start/
│   │   ├── SKILL.md                         # Zero-argument T+01m exam kickoff ($cofa-start)
│   │   └── agents/openai.yaml
│   ├── cofa-loop-graph/
│   │   ├── SKILL.md                         # 180m operating loop (Archetype detection, Checkpoint 1, Slicing, Checkpoint 2)
│   │   └── agents/openai.yaml               # Codex skill presentation metadata
│   ├── qa-briefing/
│   │   ├── SKILL.md                         # Zero-argument T+160m Korean 4-Part Q&A Final Briefing ($qa-briefing)
│   │   └── agents/openai.yaml
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
├── install.sh                               # Automated installer with subagents, 8 skills, and [mcp_servers.evaluate] wiring
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

### 2. Eight Workflow Skills (`skills/*`)
Each skill includes a validated `SKILL.md` and `agents/openai.yaml`:

1. **`$cofa-start`**: **Zero-argument T+01m exam kickoff trigger**. Immediately runs `--inspect-csv`, generates `.cofa/repo_map.md`, drafts Korean DM questions for `업무 담당자`, initializes `.cofa/trace.json`, and outputs the 1-round Frontier grill.
2. **`$qa-briefing`**: **Zero-argument T+160m exam defense trigger**. Immediately inspects workspace code, updates `.cofa/trace.json`, runs `--cheatsheet`, and outputs the complete 4-part Korean briefing (`[사후 서술형 Q&A 대비 최종 브리핑]`).
3. **`cofa-loop-graph`**: Integrated 180-minute operating loop connecting Checkpoint 1, vertical slice execution, and Checkpoint 2.
4. **`grill-me`**: 5-line inverted restate + `{ root, first_nail }` check + 1-round fast Frontier interview.
5. **`to-questionnaire`**: Formulates progressive, high-context questions for the Scenario Agent (`업무 담당자`) DM (never asks `"1, 2, 3, 4로 할 일 알려주세요"`).
6. **`sharpen`**: Anti-over-engineering rulebook (`NO-OVER-ENGINEERING`) ensuring minimal necessary abstractions and outcome-driven delivery.
7. **`verification-before-completion`**: Strict verification gate requiring fresh command execution output before making completion claims or committing.
8. **`evaluate`**: System-1 calibrated evaluation of observable evidence (`state`) using `6.0 Luna` (`gpt-6-luna`), supporting `noul`, `choice`, `score`, and `items`.

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
- **CSV Data Anomaly Scanner (`--inspect-csv`)**: Scans all workspace CSV files for row/column counts, missing cells, mixed numeric types, negative numbers, key column duplicates, and malformed rows; generates Scenario Agent DM questions.
- **4-Perspective Graph Verification**: Deterministic checks enforcing P1 Frozen Table Lock (`gate_frozen: true`), P2 Live Entrypoint Wiring (`CODE-WIRING-B1`), P3 Data/UI Ontology Contracts, and P4 Traceability DAG completeness.
- **Dynamic Binary Checks (`binary_checks[]`)**: Validates code traceability, detects test-masking anti-patterns (`| tail`, `|| true`), and fires live HTTP probes (`--live`).
- **Dynamic Quantitative Metrics (`quantitative_metrics[]`)**: Measures latency and numeric thresholds against target values.
- **Dynamic Qualitative Rubrics (`qualitative_rubrics[]`)**: Invokes `6.0 Luna` with anti-injection guards and evidence-first scoring.
- **Pre-Submission Cheatsheet (`--cheatsheet`)**: Outputs the 4-part Korean briefing (`[사후 서술형 Q&A 대비 최종 브리핑]`) covering UI component states, data/CSV error handling (including discovered anomalies), review agent records with rationales, and logged decisions.
- **`with_server.py`**: Runs tests against background servers with guaranteed TCP polling and process group SIGTERM/SIGKILL termination.
- **`log_decision.sh`**: Records single-line sanitized decision records into `.cofa/decisions.tsv`.
- **`luna_mcp.py`**: Evaluates `noul`, `choice`, `score`, and `items` over observable state.

---

## 180-Minute Execution Protocol

```
[T+00m..02m] Plugin Installation (Method A or B)
     │
[T+02m..15m] Checkpoint 1: $cofa-start (Zero-Argument Instant Kickoff)
     │       • python3 .cofa/cofa_verify.py --inspect-csv (headers, nulls, types, duplicates)
     │       • 25-line .cofa/repo_map.md + Scenario Agent DM questions
     │       • 1-Round Frontier grill to lock MVP flow & trace.json (gate_frozen: true)
     │
[T+15m..150m] Build Loop: Tracer-Bullet Vertical Slices & 4-Layer Separation
     │       • Delegate slices to executor (5.6 Terra) with fork_context: false
     │       • Enforce CODE-WIRING-B1 (every module wired into entrypoint)
     │       • Verify: python3 .cofa/cofa_verify.py --run-tests --live (all 4 Graph Perspectives)
     │       • System-1 Check: luna_checker (6.0 Luna)
     │       • Slot cleanup: close_agent on completed instances
     │
[T+150m..175m] Checkpoint 2: $qa-briefing (Zero-Argument Defense Briefing)
     │       • python3 .cofa/cofa_verify.py --run-tests --luna --cheatsheet
     │       • System-2 Audit: architect (6.1 Sol) 2-axis review
     │       • Complete 4-Part Korean Post-Submission Q&A Briefing printed directly in chat
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
