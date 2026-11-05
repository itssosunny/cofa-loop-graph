# Agent Entrypoint: Cofa Loop Graph

This file contains repository instructions and operating standards for the `cofa-loop-graph` plugin repository and hackathon workspace.

## 1. Core Operating Loop (180-Minute Hackathon Architecture)

The workspace follows a 3-stage operating loop optimized for time-boxed exam execution:
1. **`T+01m` Exam Kickoff (`$cofa-start`)**:
   - Zero-argument kickoff skill.
   - Runs `python3 .cofa/cofa_verify.py --inspect-csv` to scan all workspace CSVs for anomalies, corrupt types, negative outliers, and duplicates.
   - Generates compact 25-line `.cofa/repo_map.md` to orient workers in 1 turn.
   - Drafts progressive Korean DM questions for `업무 담당자` combining `README.md` and discovered CSV anomalies.
   - Initializes `.cofa/trace.json` (`gate_frozen: true`) and presents 1-round Frontier Grill to lock scope.
2. **`T+15m..150m` Build Loop (`$cofa-loop-graph`)**:
   - Tracer-bullet vertical slices adhering to 4-Layer Web Architecture (`data/parser`, `domain/model`, `api/server`, `ui/components`).
   - Delegates bounded slices to `executor` (`5.6 Terra`).
   - Runs fast (<2s) System-1 evaluation via `luna_checker` (`6.0 Luna`) and Level-2 Graph Verification (`.cofa/cofa_verify.py`).
3. **`T+150m..180m` Final Defense & Briefing (`$qa-briefing`)**:
   - Dispatches read-only `architect` (`6.1 Sol`) for 2-Axis Audit and code-to-document fidelity.
   - Executes `python3 .cofa/cofa_verify.py --cheatsheet` to output the definitive Korean 4-Part Post-Submission Written Q&A Defense Briefing.

---

## 2. The 3-Tier Test Pyramid & Bidirectional Traceability (`@trace`)

Every functional requirement, constraint, invariant, and quantitative metric is bound to test code via explicit bidirectional traceability:
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

## 3. Bundled MCP Servers

1. **`evaluate` (`.cofa/luna_mcp.py`)**:
   - Fast System-1 structured evaluator powered by `6.0 Luna` (`gpt-6-luna`).
   - Provides `noul`, `choice`, `score`, and `items` evaluation modes.
2. **`playwright` (`@playwright/mcp@latest --headless`)**:
   - Bundled in `.mcp.json` and registered in `~/.codex/config.toml` by `install.sh`.
   - Runs in `--headless` mode to verify rendered DOM accessibility tree, interaction states, and console logs inside the Cofa container without popping up windows that steal fullscreen proctoring focus.

---

## 4. 4-Perspective Graph Verification (`.cofa/cofa_verify.py`)

- **Perspective 1 (`gate_lock`)**: Frozen verification table lock (`gate_frozen: true`). Enforces 3-Tier Test Pyramid coverage (`unit`, `integration`, and `e2e` when web server is active).
- **Perspective 2 (`structure_wiring`)**: Enforces `CODE-WIRING-B1`: every non-entrypoint module, parser, or component referenced in trace table or `qa_briefing` must be imported and reachable.
- **Perspective 3 (`ontology_contract`)**: Enforces header-name mapping in parsers, forbids `window.alert()` in UI, and enforces Chrome password manager popup suppression (`NO-PASSWORD-POPUP-TRAP`).
- **Perspective 4 (`traceability_dag`)**: Verifies complete DAG edges from requirements/constraints/invariants/quantitative metrics (`rule_kind` + `source` + `description`) to code (`code_refs`) to test files (`test_refs` containing literal `@trace BC-XX` / `@trace QM-XX`).
