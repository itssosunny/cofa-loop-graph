---
name: cofa-start
description: Zero-argument T+01m exam kickoff skill. Immediately runs --inspect-csv, analyzes README.md to generate .cofa/repo_map.md, drafts 3-4 Korean DM questions for 업무 담당자, initializes .cofa/trace.json, and presents the 1-round Frontier grill.
---

# `cofa-start`: Zero-Argument Exam Kickoff

This skill is designed as an **instant, zero-argument trigger** for `T+01m` of the Cofa-Probe hackathon exam.

---

## Immediate Execution Rule (Zero Arguments Required)

When the user types `$cofa-start` (even with no arguments or additional text), **DO NOT prompt for instructions or ask what to do**. Immediately execute the following 4-step sequence:

### Step 1. Run CSV Data Anomaly Inspection
Execute:
```bash
python3 .cofa/cofa_verify.py --inspect-csv
```
Inspect all CSV files in the workspace for:
- Row counts and column headers (including whitespace or case anomalies).
- Missing, empty, or null values per column.
- Mixed-type or numeric anomalies (e.g. non-numeric strings in numeric columns, negative numbers in price/count fields).
- Duplicate identifiers in key/ID columns.
- Malformed rows where column count != header count.

### Step 2. Generate the 25-Line `.cofa/repo_map.md`
Read `README.md` and inspect workspace structure to write a compact `.cofa/repo_map.md` (<= 25 lines) to orient workers:
- Primary entrypoint file paths.
- Data files and schema shapes.
- Fast reproduction and test commands (<2s).
- Locked constraints and anti-over-engineering rules.

### Step 3. Draft 3–4 Progressive Korean DM Questions for `업무 담당자`
Formulate 3–4 progressive DM questions combining `README.md` requirements with the actual CSV anomalies discovered in Step 1:
- **Stage 1 (Scope & Boundary)**:
  `"제가 어떤 범위의 맥락이나 운영 기준을 여쭤보면 될까요?"`
- **Stage 2 (CSV Anomalies & Domain Context)**:
  Directly reference discovered anomalies (e.g., `"salary 컬럼의 결측치 처리 정책(기본값/행 제외/오류)과 user_id 중복 시 최신 행 유지 여부를 확인 부탁드립니다."`).
- **Stage 3 (Priorities & Fallback Rules)**:
  Ask about sorting/ranking edge cases, rate limits, or error fallback policies.
Print these questions formatted with a clear copy-paste block so the candidate can paste them directly into the Scenario Agent DM window.

### Step 4. Initialize `.cofa/trace.json` & Present 1-Round Frontier Grill
1. Copy `.cofa/trace.template.json` to `.cofa/trace.json` if not already present.
2. Ensure `"gate_frozen": true` is set (Perspective 1 Gate Lock).
3. Populate initial `binary_checks[]`, `quantitative_metrics[]`, and `qualitative_rubrics[]` based on `README.md` and DM requirements. Ensure `binary_checks[]` covers the **3-Tier Test Pyramid**:
   - `BC-01` (`rule_kind: "invariant"`, `test_tier: "unit"`): Data parser anomaly quarantine & pure domain calculations.
   - `BC-02` (`rule_kind: "constraint"`, `test_tier: "integration"`): API input validation, role guard checks, and CSV-to-API flow.
   - `BC-03` (`rule_kind: "requirement"`, `test_tier: "e2e"`): Rendered DOM 5-State flow, 1-Click Role Switcher execution, and live browser tests via bundled headless `playwright` MCP.
   Every test suite referenced in `test_refs` MUST be annotated with the literal tag `@trace BC-XX`.
4. Present the **Five-Line Inverted Restate** and **1-Round Frontier `grill-me`** in Korean to lock scope with the candidate:
   - Target Deliverable & Archetype (Data/API/Web).
   - Core Success Metric.
   - Anti-Over-Engineering Boundary (`sharpen`).
   - Load-Bearing Risk (`{ root, first_nail }`).
   - 2–3 high-leverage decision questions (Tracer-bullet flow, rejected abstractions, verification checks).
5. Log the baseline decision:
   ```bash
   bash .cofa/log_decision.sh "T+15m" "Kickoff Scope Lock" "Locked MVP scope & frozen verification table" "trace.json initialized" "PASS"
   ```
