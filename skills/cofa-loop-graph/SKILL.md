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

## 2. Checkpoint 1 (`T+02m..15m`) — `2-Step Cofa-Grill`

Spend the first 15 minutes establishing exact requirements, preventing over-engineering, and populating `.cofa/trace.json`.

### Step 1A (`T+02m..06m`): Archetype Detection, Fact Scan & DM Questions
Main session (`6.1 Sol`):
1. **Detect Task Archetype**:
   - **Archetype A: Data / Pipeline / ML / CLI**: No web server (`"has_web_server": false`). Focus on data parsing, schemas, numeric precision, and safe-but-wrong output prevention.
   - **Archetype B: Backend API / Microservice**: Web server (`"has_web_server": true`). Focus on `0.0.0.0` host binding, HTTP status codes, edge validation, and latency.
   - **Archetype C: Full-Stack / Frontend Web App**: Web server (`"has_web_server": true`). Focus on `0.0.0.0` binding, UI states (`loading`, `empty`, `inline-error`), `single-flight`, and `tabular-nums`.
2. **Generate a 25-Line `.cofa/repo_map.md`**:
   Write a compact reference map to orient `fork_context: false` workers in 1 turn:
   - Primary entrypoint file paths.
   - Data files and schema shapes.
   - Fast reproduction and test commands (<2s).
   - Locked constraints and anti-over-engineering rules.
3. **Draft 3–4 Progressive DM Questions for `업무 담당자` (Scenario Agent)**:
   - ❌ **Prohibited**: Never ask `"지금 당장 해야 할 일을 하나, 둘, 셋, 넷으로 알려 주세요"`.
   - ✅ **Stage 1 (Scope & Boundary)**:
     `"제가 어떤 범위의 맥락이나 운영 기준을 여쭤보면 될까요?"`
   - ✅ **Stage 2 (Granular Domain Context)**:
     Ask specific, fine-grained questions about edge cases, data anomalies, or user flows.
   - ✅ **Stage 3 (Priorities & Fallback Rules)**:
     Ask about ranking rules, error handling priorities, or fallback behaviors.
4. Candidate pastes these questions into the Scenario Agent DM and receives answers.

### Step 1B (`T+06m..15m`): 1-Round Frontier `grill-me` + `sharpen`
Main session (`6.1 Sol`):
1. **Five-Line Inverted Interview Restate**:
   Restate the target deliverable, evaluator, core success metric, anti-over-engineering boundary, and `{ root, first_nail }` load-bearing risk.
2. Present **one single Frontier Round** containing 2–4 high-leverage decision questions:
   ```markdown
   ❓ **Q1** - **Tracer-Bullet End-to-End Flow**:
   Should our 60-minute MVP focus on <specific core user flow from input/UI to final state>?
   ➡️ Recommended: Yes. Delivering a complete end-to-end slice early guarantees working software.

   ---

   ❓ **Q2** - **Anti-Over-Engineering (`sharpen`)**:
   Should we reject <unnecessary write locks / background queue / distributed cache>?
   ➡️ Recommended: Yes. Workload is read-heavy; in-memory caching satisfies all latency targets without distributed complexity.
   ```
3. Candidate confirms (replies `"yes"`).
4. **Populate `.cofa/trace.json`**:
   - Set `"has_web_server": false` for Archetype A, or `true` for Archetype B/C.
   - `binary_checks[]`: List functional requirements (`BC-01..N`) with expected `code_refs`, `test_cmd`, and `live_probe`.
   - `quantitative_metrics[]`: Performance and accuracy thresholds (`QM-01..N`).
   - `qualitative_rubrics[]`: Quality criteria (`QR-01..N`) scored on [0.0, 2.0].
   - `rejected_over_engineering[]`: Explicitly recorded anti-over-engineering decisions.
5. Log baseline decision:
   ```bash
   bash .cofa/log_decision.sh "T+15m" "Lock MVP Scope & trace.json" "Locked core flow; rejected over-engineering" "trace.json initialized" "PASS"
   ```

---

## 3. Build Loop (`T+15m..150m`) — Tracer-Bullet Vertical Slices

Never build horizontal layers in isolation. Build vertical, testable slices.

### Vertical Slicing Workflow
For each vertical slice (e.g., Slice 1: End-to-End Core Flow, Slice 2: Edge-Case Handling, Slice 3: Fallbacks):

1. **Delegate to `executor` (`5.6 Terra`)**:
   - Spawn `executor` with `fork_context: false` and a self-contained brief:
     ```
     Implement BC-01 and BC-02:
     - Consult .cofa/repo_map.md for entrypoints and schemas.
     - Enforce ZERO-STUB & NO-TEST-CHEATING (no .skip/.only stubs).
     - Conditional rules: if web server, bind to 0.0.0.0; if data pipeline, prevent safe-but-wrong outputs.
     - Follow 3-hypothesis debugging if tests fail; stop on 3 identical failures.
     - Run test command and return fresh output.
     ```
2. **Inspect Changed Files & Verification Output**:
   - Apply `verification-before-completion`: inspect `git diff` and examine fresh test output.
3. **Run Level-2 Verification**:
   - If task has a web server, test with guaranteed process cleanup:
     ```bash
     python3 .cofa/with_server.py --server "npm run dev" --port 3000 -- python3 .cofa/cofa_verify.py --run-tests --live
     ```
   - For non-web tasks (Data/CLI/ML):
     ```bash
     python3 .cofa/cofa_verify.py --run-tests
     ```
4. **Fast System-1 Check with `luna_checker` (`6.0 Luna`)**:
   - Verify affected `binary_checks` and `qualitative_rubrics`.
   - Ensure corrupt inputs do not silently mask errors (Safe-But-Wrong check).
5. **Log Decision in `.cofa/decisions.tsv`**:
   ```bash
   bash .cofa/log_decision.sh "<phase>" "<decision>" "<why_and_rejected_alt>" "<evidence>" "<result>"
   ```
6. **Slot Clean-Up**:
   - Call `close_agent` on the completed `executor` or `luna_checker` instance.

---

## 4. Checkpoint 2 (`T+150m..175m`) — Pre-Submission & `사후 Q&A` Defense

At 25 minutes before submission, transition from active feature coding to verification, documentation fidelity, and defense preparation.

1. **Run Full Level-2 Verification**:
   ```bash
   python3 .cofa/cofa_verify.py --run-tests --luna --cheatsheet
   ```
   *(Add `--live` if `has_web_server: true` and server is running).*
2. **Verify Submission Document Fidelity (`[BASE-3] CODE-DOC-FIDELITY`)**:
   - Ensure the submission document (e.g., `REPORT.md` or `README.md`) contains:
     - `선택한 판단과 근거` (Key architectural choices and rationale)
     - `검증 결과` (Actual test pass rates, live latency metrics, and probe outcomes)
     - `남은 한계` (Honest trade-offs and remaining limitations)
3. **Dispatch `architect` (`6.1 Sol`)**:
   - Run `architect` in read-only mode for the 2-Axis Audit:
     - Axis 1: Spec compliance, safe-but-wrong prevention, and 1:1 code-to-document fidelity.
     - Axis 2: Closed-set defect mechanisms (`condition`, `state`, `dataFlow`, `asyncControl`, `cleanup`, `concurrency`, `recovery`, `crash`, `dataFormat`, `testGap`).
4. **Study the Cheatsheet**:
   - Review the printed output of `python3 .cofa/cofa_verify.py --cheatsheet` (including logged decisions from `.cofa/decisions.tsv`) to prepare for the no-AI written Q&A (`사후 Q&A`).

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
