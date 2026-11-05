---
name: qa-briefing
description: Generate comprehensive Korean 4-part post-submission written Q&A final briefing (UI state architecture, data/CSV error handling, review agent records & rationales, and architecture decisions) for exam defense.
---

# `qa-briefing`: Post-Submission Written Q&A Final Briefing

This skill inspects the completed workspace, `.cofa/trace.json`, and review agent records to produce the definitive **Korean 4-Part Post-Submission Written Q&A Final Briefing (`[사후 서술형 Q&A 대비 최종 브리핑]`)**.

In the hackathon evaluation, candidates face a no-AI written Q&A exam (`사후 서술형 Q&A`) immediately after code submission. This skill equips the candidate with an airtight conceptual defense of:
1. How UI component states were partitioned and why.
2. How data anomalies and CSV parsing errors were handled without Safe-But-Wrong masking.
3. Every judgment made by review agents (`luna_checker` & `architect`) and the exact reasons **why they judged each item that way**.
4. Core architectural choices, Scenario Agent (`업무 담당자`) confirmed priorities, anti-over-engineering rationales, and honest trade-offs.

---

## 1. When to Invoke

- **Automatically**: At Checkpoint 2 (`T+150m..175m`) of `$cofa-loop-graph`.
- **Manually**: Anytime in the final 30 minutes before submission by calling `$qa-briefing` or running:
  ```bash
  python3 .cofa/cofa_verify.py --cheatsheet
  ```

---

## 2. 4-Part Briefing Structure

When invoked, the skill reads `.cofa/trace.json` (specifically `qa_briefing`), scans code files, and outputs the briefing in clear Korean:

### Part 1: UI 컴포넌트 상태 설계 전략 요약 (`ui_state_strategy`)
- **주요 컴포넌트 및 파일**: Identifies key frontend components (e.g. `App.tsx`, `FilterBar.tsx`, `DataTable.tsx`, `FormModal.tsx`).
- **상태 구조 및 분리 기준 (4분할 원칙)**:
  1. **데이터 원본 상태 (Raw Data State)**: Single Source of Truth fetched from API or local storage, kept immutable or centrally managed.
  2. **뷰 제어 상태 (View Control State)**: User interactions (search keyword, filter category, sorting field/order, pagination) kept separate so raw data is never mutated.
  3. **비동기 피드백 상태 (Async Feedback State)**: Explicit `isLoading`, `isEmpty`, inline error messages (`errorMsg`), and submission locks (`isSubmitting`) to prevent duplicate requests and provide clear feedback instead of intrusive `alert()`.
  4. **파생 상태 (Derived State)**: Computed on-the-fly (e.g. `useMemo` or render-time calculations) from raw data and filter states, completely eliminating state synchronization bugs.
- **설계 근거 및 장점**: Explains why this state architecture minimizes bugs and improves responsiveness.

### Part 2: 데이터(CSV/입력) 오류 및 예외 핸들링 방법 요약 (`data_error_handling`)
- **처리 대상 파일 및 함수**: Identifies data loaders, parsers, and validation functions.
- **처리한 데이터 결함 및 이상치 유형**:
  - 결측치 및 빈 문자열 (`null`, `undefined`, `""`)
  - 형식 및 인코딩 오류 (잘못된 구분자, 누락된 따옴표, 줄바꿈 파손)
  - 타입 불일치 (숫자 필드에 문자열 유입, 잘못된 날짜 형식)
  - 도메인 이상치 (음수 금액, 비정상적 범위, 중복 식별자)
- **예외 처리 방식 및 근거**:
  - **헤더명 기반 동적 매핑**: Column index 대신 header name 기반 매핑으로 열 순서 변경에 견고함.
  - **행 단위 격리 (Row Quarantine / Fallback)**: 오류가 있는 행만 격리하거나 기본값으로 폴백하여 전체 애플리케이션 충돌 방지.
  - **Safe-But-Wrong 은폐 방지**: 오류를 무조건 0이나 빈 값으로 조용히 덮지 않고, 화면이나 로그에 유효하지 않은 데이터임을 명시.
  - **인라인 UI 안내**: 사용자 입력 오류 시 문제 필드 하단에 구체적인 오류 원인 표시.

### Part 3: 검수 에이전트(luna_checker & architect) 기록 및 판정 이유 요약 (`review_agent_records`)
- **전수 판정 요약**: All evaluations performed by `luna_checker` (System-1) and `architect` (System-2).
- **왜 그렇게 판단했는지 전수 근거 (`why_judged_this_way`)**:
  - 무엇을 확인했고 어떤 코드/데이터/동작 근거로 PASS, WATCH, BLOCK, 또는 해당 점수를 매겼는지 구체적 사유 명시.
- **코드 수정 및 합리적 수용 내역**:
  - 검수 지적 사항을 코드에서 어떻게 수정했는지, 혹은 왜 합리적 트레이드오프로 수용했는지 요약.

### Part 4: 핵심 아키텍처 결정, 업무 담당자 우선순위 및 과설계 배제/한계점 요약
- **핵심 아키텍처 결정 및 선택 근거**: Key design decisions recorded in `.cofa/decisions.tsv`.
- **`업무 담당자` DM 확인 요구사항**: Priorities, edge-case rules, and fallback policies confirmed during Step 1A.
- **과설계 배제 근거 (`rejected_over_engineering`)**: Unneeded distributed complexity or heavy patterns rejected to defend cognitive score.
- **솔직한 남은 한계점 (`known_limitations`)**: Transparent trade-offs acknowledged for the submission document.

---

## 3. Execution Procedure

1. **Verify or Populate `.cofa/trace.json`**:
   Ensure `.cofa/trace.json` has the `"qa_briefing"` section filled with details from the current implementation. If fields contain placeholder text, auto-extract details from source code:
   - Search for UI components in `*.tsx`, `*.jsx`, `*.vue`, `*.svelte`.
   - Search for data processing logic in `*.py`, `*.ts`, `*.js`.
   - Gather evaluation logs from `luna_checker` and `architect`.
2. **Execute Cheatsheet Command**:
   ```bash
   python3 .cofa/cofa_verify.py --cheatsheet
   ```
3. **Present the Full Briefing to the Candidate**:
   Directly print the 4-part Korean briefing in chat with structured bullet points so the candidate can read and memorize it before the written exam.
