---
name: cofa-loop-graph
description: Complete 180-minute hackathon operating loop and Level-2 verification graph for Codex. Covers 2-step Cofa-Grill alignment, Tracer-Bullet vertical slicing with executor (5.6 Terra), System-1 fast verification with luna_checker (6.0 Luna), and final submission fidelity check with architect (6.1 Sol).
---

# `cofa-loop-graph`: 180-Minute Operating Loop & Verification Graph

This skill drives the complete 180-minute development lifecycle for the Cofa-Probe hackathon environment. It organizes the exam into 3 distinct phases with a task-type-agnostic architecture:

```
[T+00m..02m] Setup & Install (install.sh)
  │
  ▼
[T+02m..15m] Checkpoint 1: 2-Step Cofa-Grill (Archetype Detection, Repo Map & trace.json)
  │
  ▼
[T+15m..150m] Build Loop: Tracer-Bullet Vertical Slices (Main + executor + luna_checker)
  │
  ▼
[T+150m..175m] Checkpoint 2: Pre-Submission Verification & 사후 Q&A Defense (architect)
  │
  ▼
[T+175m..180m] Final Local Commit & Clean-Up (NEVER git push)
```

---

## 1. Multi-Model Architecture & Slot Hygiene

The operating loop coordinates 3 recommended models to optimize speed, accuracy, and token efficiency:

| Role | Agent / Invocation | Model | Reasoning Effort | sandbox_mode | Responsibility |
|---|---|---|---|---|---|
| **Orchestrator** | Main CLI Session | `6.1 Sol` (`gpt-6.1-sol`) | `high` | Default | Reads problem, executes Step 1A DM formulation, conducts Step 1B Frontier grill, and coordinates slice dispatch. |
| **Worker** | `executor` subagent | `5.6 Terra` (`gpt-5.6-terra`) | `medium` | `workspace-write` | Implements bounded Tracer-Bullet slices, API routes, data scripts, UI components, and tests. |
| **System-1 Evaluator** | `luna_checker` subagent / `cofa_verify.py` | `6.0 Luna` (`gpt-6-luna`) | `low` | `read-only` | Rapidly scores predicates, quantitative metrics, and qualitative rubrics in `.cofa/trace.json`. |
| **System-2 Auditor** | `architect` subagent | `6.1 Sol` (`gpt-6.1-sol`) | `medium` | `read-only` | Final pre-submission 2-axis review (Spec & Safe-But-Wrong output + Closed-set defect mechanisms). |

### Slot Hygiene & Context Isolation
- **Token Discipline**: Always launch `executor` with `fork_context: false` (or `fork_turns: "none"`) to avoid passing full conversation history. Pass a self-contained brief.
- **Slot Hygiene**: Always call `close_agent` after receiving the subagent's report to keep execution slots free and prevent dangling sessions.

---

## 2. Checkpoint 1 (`T+02m..15m`) — `2-Step Cofa-Grill` (Unified Planning Gate)

> 💡 **Instant Kickoff Trigger**: Typing `$cofa-start` with zero arguments immediately runs this entire sequence (CSV anomaly inspection, repo map, DM question formulation, and trace.json initialization).

Spend the first 15 minutes establishing exact requirements, uncovering data anomalies, preventing over-engineering, and locking `.cofa/trace.json` (`gate_frozen: true`).

### Step 1A (`T+02m..06m`): CSV Inspection, Archetype Detection, Fact Scan & DM Questions
Main session (`6.1 Sol`):
1. **Run CSV Data Anomaly Inspection**:
   ```bash
   python3 .cofa/cofa_verify.py --inspect-csv
   ```
   Immediately uncover row counts, column headers, missing cells, mixed-type values, negative numbers, key column duplicates, and malformed rows across all workspace CSVs.
2. **Detect Task Archetype**:
   - **Archetype A: Data / Pipeline / ML / CLI**: No web server (`"has_web_server": false`). Focus on data parsing, schemas, numeric precision, and safe-but-wrong output prevention.
   - **Archetype B: Backend API / Microservice**: Web server (`"has_web_server": true`). Focus on `0.0.0.0` host binding, HTTP status codes, edge validation, and latency.
   - **Archetype C: Full-Stack / Frontend Web App**: Web server (`"has_web_server": true`). Focus on `0.0.0.0` binding, UI 5-State Matrix (`default`, `loading`, `empty`, `filter-zero`, `inline-error`), `NO-PASSWORD-POPUP-TRAP` (suppress Chrome password popup via `autoComplete="new-password"` or `type="text"` with `WebkitTextSecurity:'disc'` to prevent proctoring fullscreen-exit penalties), 1-click role switcher buttons (e.g., `[관리자 계정 즉시 로그인]`, `[직원 계정 즉시 로그인]`), and tabular numeric presentation.
3. **Generate a 25-Line `.cofa/repo_map.md`**:
   Write a compact reference map to orient `fork_context: false` workers in 1 turn:
   - Primary entrypoint file paths.
   - Data files and schema shapes.
   - Fast reproduction and test commands (<2s).
   - Locked constraints and anti-over-engineering rules.
4. **Draft 3–4 Progressive DM Questions for `업무 담당자` (Scenario Agent)**:
   - ❌ **Prohibited**: Never ask `"지금 당장 해야 할 일을 하나, 둘, 셋, 넷으로 알려 주세요"`.
   - ✅ **Stage 1 (Scope & Boundary)**:
     `"제가 어떤 범위의 맥락이나 운영 기준을 여쭤보면 될까요?"`
   - ✅ **Stage 2 (CSV Anomalies & Granular Context)**:
     Ask specific questions directly based on `--inspect-csv` findings (e.g., how to handle discovered missing salary cells, negative quantities, duplicate user IDs, or malformed lines).
   - ✅ **Stage 3 (Priorities & Fallback Rules)**:
     Ask about ranking rules, error handling priorities (quarantine vs error vs default), or fallback behaviors.
5. Candidate pastes these questions into the Scenario Agent DM and receives answers.

### Step 1B (`T+06m..15m`): 1-Round Frontier `grill-me` + `sharpen` (Lock Scope & Contracts)
Main session (`6.1 Sol`):
1. **Five-Line Inverted Interview Restate**:
   Restate the target deliverable, evaluator, core success metric, anti-over-engineering boundary, and `{ root, first_nail }` load-bearing risk.
2. Present **one single Frontier Round** containing 2–4 high-leverage decision questions to lock:
   - **Stage 1 (Story & Business Rules)**: Core end-to-end flow and DM priorities.
   - **Stage 2 (UI 5-State & Information Diet)**: `default`, `loading`, `empty`, `filter-zero` (with reset button), `inline-error` (with recovery guidance, no `alert()`), One-Fact-One-Place (`IF-ZERO-DUPLICATION`), and `tabular-nums` for numbers.
   - **Stage 3 (4-Layer System & Frozen Table)**: Architecture boundaries and verification table lock (`gate_frozen: true`).
3. Candidate confirms (replies `"yes"`).
4. **Populate `.cofa/trace.json`**:
   - Set `"has_web_server": false` for Archetype A, or `true` for Archetype B/C.
   - Set `"gate_frozen": true` to activate Perspective 1 (`gate_lock`: No Skip-with-Reason Escape).
   - `binary_checks[]`: List functional requirements (`BC-01..N`) with expected `code_refs`, `test_cmd`, and `live_probe`.
   - `quantitative_metrics[]`: Performance and accuracy thresholds (`QM-01..N`).
   - `qualitative_rubrics[]`: Quality criteria (`QR-01..N`) scored on [0.0, 2.0].
   - `rejected_over_engineering[]`: Explicitly recorded anti-over-engineering decisions.
5. Log baseline decision:
   ```bash
   bash .cofa/log_decision.sh "T+15m" "Lock MVP Scope & trace.json" "Locked core flow; rejected over-engineering; froze verification table" "trace.json initialized" "PASS"
   ```

---

## 3. Build Loop (`T+15m..150m`) — Tracer-Bullet Vertical Slices & 4-Layer Architecture

Never build horizontal layers in isolation. Build vertical, testable slices adhering to the **4-Layer Web Architecture** and verified by the **4-Perspective Graph**:

### The 4-Layer Web Architecture (`[BC-C1]`)
1. **`data/parser`**: Header-name mapping (never numeric indices) + row-level error quarantine (`validRows` / `invalidRows`) + Safe-But-Wrong avoidance (no silent 0/empty suppression).
2. **`domain/model`**: Pure business logic, filtering, sorting, and aggregations (used as derived state via `useMemo`/computed, never duplicated into mutable `useState`).
3. **`api/server`**: `0.0.0.0` routes returning structured data alongside anomaly metadata.
4. **`ui/components`**: 4-Partition UI state (`Raw Data`, `View Control`, `Async Feedback`, `Derived State`) + UI 5-State Matrix (`default`, `loading`, `empty`, `filter-zero`, `inline-error`) + `NO-PASSWORD-POPUP-TRAP` (suppress Chrome password popup via `autoComplete="new-password"` or `type="text"` with `WebkitTextSecurity:'disc'` to prevent exam fullscreen exit) + 1-Click Role Switcher buttons (`[관리자 즉시 로그인]`, `[직원 즉시 로그인]`).

### Vertical Slicing Workflow
For each vertical slice (e.g., Slice 1: End-to-End Core Flow, Slice 2: Edge-Case Handling, Slice 3: Fallbacks):

1. **Delegate to `executor` (`5.6 Terra`)**:
   - Spawn `executor` with `fork_context: false` and a self-contained brief:
     ```
     Implement BC-01 and BC-02:
     - Consult .cofa/repo_map.md for entrypoints and schemas.
     - Enforce ZERO-STUB & NO-TEST-CHEATING (no .skip/.only stubs).
     - Wire every new module into live entrypoint (CODE-WIRING-B1).
     - Conditional rules: if web server, bind to 0.0.0.0; if data pipeline, prevent safe-but-wrong outputs.
     - Follow 3-hypothesis debugging if tests fail; stop on 3 identical failures.
     - Run test command and return fresh output.
     ```
2. **Inspect Changed Files & Verification Output**:
   - Apply `verification-before-completion`: inspect `git diff` and examine fresh test output.
3. **Run Level-2 Verification & 4-Perspective Graph Audit**:
   - Web server tasks:
     ```bash
     python3 .cofa/with_server.py --server "npm run dev" --port 3000 -- python3 .cofa/cofa_verify.py --run-tests --live
     ```
   - Non-web tasks (Data/CLI/ML):
     ```bash
     python3 .cofa/cofa_verify.py --run-tests
     ```
   - Automatically validates all 4 Graph Perspectives:
     - **P1 `gate_lock`**: Frozen checks intact, zero skipped items.
     - **P2 `structure_wiring`**: Entrypoint reachability, zero unimported modules (`CODE-WIRING-B1`).
     - **P3 `ontology_contract`**: Header-name mapping in parsers, zero `window.alert()` in UI.
     - **P4 `traceability_dag`**: Complete DAG edges (`source+desc` ➔ `code_refs` ➔ `test/probe` ➔ `decision`).
4. **Fast System-1 Check with `luna_checker` (`6.0 Luna`)**:
   - Verify affected `binary_checks` and `qualitative_rubrics`.
   - Ensure corrupt inputs do not silently mask errors (Safe-But-Wrong check).
   - Capture `luna_checker`'s judgment rationale (`judgment_reason_kr`) into `.cofa/trace.json` (`qa_briefing.review_agent_records`).
5. **Log Decision in `.cofa/decisions.tsv` & Update `qa_briefing`**:
   - Log design decision:
     ```bash
     bash .cofa/log_decision.sh "<phase>" "<decision>" "<why_and_rejected_alt>" "<evidence>" "<result>"
     ```
   - Progressively update `.cofa/trace.json` (`qa_briefing`):
     - `ui_state_strategy`: Document frontend component state partitioning (data source, view filter/sort, async feedback, derived states) and design rationales.
     - `data_error_handling`: Document CSV/data parsers, handled anomalies (missing values, format errors, type mismatch, outliers, duplicates), and Safe-But-Wrong avoidance logic.
6. **Slot Clean-Up**:
   - Call `close_agent` on the completed `executor` or `luna_checker` instance.

---

## 4. Checkpoint 2 (`T+150m..175m`) — Pre-Submission & `사후 Q&A` Defense

> 💡 **Instant Defense Trigger**: Typing `$qa-briefing` with zero arguments immediately runs this inspection, executes `--cheatsheet`, and outputs the complete 4-part Korean briefing.

At 25 minutes before submission, transition from active feature coding to verification, documentation fidelity, and defense preparation.

1. **Dispatch `architect` (`6.1 Sol`)**:
   - Run `architect` in read-only mode for the 2-Axis Audit:
     - Axis 1: Spec compliance, safe-but-wrong prevention, and 1:1 code-to-document fidelity.
     - Axis 2: Closed-set defect mechanisms (`condition`, `state`, `dataFlow`, `asyncControl`, `cleanup`, `concurrency`, `recovery`, `crash`, `dataFormat`, `testGap`).
   - `architect` generates `review_summary_kr` covering audit findings with rationales, UI component state architecture, and Data/CSV error handling.
   - Record architect's findings into `.cofa/trace.json` (`qa_briefing`).
2. **Verify Submission Document Fidelity (`[BASE-3] CODE-DOC-FIDELITY`)**:
   - Ensure the submission document (e.g., `REPORT.md` or `README.md`) contains:
     - `선택한 판단과 근거` (Key architectural choices and rationale)
     - `검증 결과` (Actual test pass rates, live latency metrics, and probe outcomes)
     - `남은 한계` (Honest trade-offs and remaining limitations)
3. **Run Full Level-2 Verification & Defense Briefing**:
   ```bash
   python3 .cofa/cofa_verify.py --run-tests --luna --cheatsheet
   ```
   *(Add `--live` if `has_web_server: true` and server is running).*
4. **Deliver Korean 4-Part Post-Submission Written Q&A Final Briefing**:
   - When Checkpoint 2 completes (or upon running `$qa-briefing`), the orchestrator MUST print the comprehensive Korean 4-Part Briefing (`[사후 서술형 Q&A 대비 최종 브리핑]`) directly in chat:
     1. **UI 컴포넌트 상태 설계 전략 요약 (`ui_state_strategy`)**:
        - Component list, 4-tier state partitioning (원본 데이터 상태, 뷰 제어 상태, 비동기 피드백 상태, 파생 상태), and design rationales (Single Source of Truth, preventing state drift).
     2. **데이터(CSV/입력) 오류 및 예외 핸들링 방법 요약 (`data_error_handling`)**:
        - File & function citations, anomaly handling (결측치, 형식 오류, 타입 불일치, 이상치, 중복), Safe-But-Wrong avoidance rationale, and UI inline error feedback.
     3. **검수 에이전트(luna_checker & architect) 기록 및 판정 이유 요약 (`review_agent_records`)**:
        - Summary of all checks, verdicts, and explicit reasons WHY each review agent judged items that way (`judgment_reason_kr` / `why_judged_this_way`).
     4. **핵심 아키텍처 결정, 업무 담당자 우선순위 및 과설계 배제/한계점 요약**:
        - Architectural decisions and trade-offs, Scenario Agent DM confirmed rules, anti-over-engineering justifications, and honest remaining limitations.

---

## 5. Final Wrap-Up (`T+175m..180m`) — Local Git Commit Only

In the final 5 minutes:

1. **Check Git Status**:
   ```bash
   git status
   ```
2. **Commit Changes Locally**:
   ```bash
   git add -A && git commit -m "Complete implementation with dynamic BC/QM/QR verification"
   ```
3. ⚠️ **NEVER RUN `git push`**:
   The exam container environment strictly prohibits `git push`. Pushing to remote repositories violates exam policy and may trigger network boundary warnings.
