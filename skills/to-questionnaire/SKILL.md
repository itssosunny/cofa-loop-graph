---
name: to-questionnaire
description: Turn missing context or ambiguous requirements into progressive, structured questions for a stakeholder or Scenario Agent (업무 담당자).
---

# To-Questionnaire

Turn ambiguous requirements or missing business context into a structured **questionnaire** or direct message sequence. The target may be an asynchronous human stakeholder or an in-exam Scenario Agent (`업무 담당자`).

The recipient holds domain context and operational priorities that the initial specification lacks; your questions pull it out systematically.

## Progressive Questioning Discipline for Scenario Agent (`업무 담당자`)

When interacting with a domain stakeholder or Scenario Agent in a time-boxed exam:

1. **Avoid Lazy Meta-Questions**:
   - ❌ **Never ask**: `"지금 당장 해야 할 일을 하나, 둘, 셋, 넷으로 알려 주세요"` (blocked by scenario evaluation rubrics).
   - ❌ **Never ask**: broad, passive questions that ask the stakeholder to design the software for you.

2. **Follow the 3-Stage Progressive Questioning Pattern**:
   - **Stage 1 (Scope & Operational Boundary)**:
     - Check the boundary of responsibilities and key deliverables:
       e.g., *"제가 어떤 범위의 맥락이나 운영 기준을 여쭤보면 될까요?"* or *"이번 과제에서 데이터 가공과 프론트엔드 연동 중 우선 집중해야 하는 핵심 사용자 흐름이 무엇인가요?"*
   - **Stage 2 (Granular & Concrete Domain Context)**:
     - Inquire about specific, detailed business rules, data schemas, or edge cases that appear minor but affect design:
       e.g., *"음수 수량이나 결측치 입력이 들어왔을 때 HTTP 400 에러로 즉시 거부해야 하나요, 아니면 0으로 클램핑해야 하나요?"*
   - **Stage 3 (Priorities, Validation & Fallback Rules)**:
     - Inquire about trade-offs, ranking criteria, or error recovery behavior:
       e.g., *"추천 결과가 부족할 경우 인기도 기반 폴백을 적용해야 하나요, 아니면 빈 상태 UI를 노출해야 하나요?"*

## Structure for Human Stakeholders

When drafting an async questionnaire document for a human collaborator:

```markdown
# <Questionnaire Title>

**Purpose:** Clarify key business rules and edge cases required for implementation.
**Target:** <Recipient Role> (e.g., 업무 담당자)

## 1. Scope & Core Flow
### <Question on core workflow and boundaries>
_Why this matters: determines whether we implement feature X or defer to v2._

## 2. Granular Edge Cases & Validation
### <Question on boundary values, errors, or data anomalies>
_Why this matters: fixes validation logic in API endpoints._

## 3. Operational Criteria & Fallbacks
### <Question on performance, caching, or fallback handling>
_Why this matters: shapes backend state management and response formatting._
```
