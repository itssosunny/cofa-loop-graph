---
name: grill-me
description: Fast Frontier-style interview to stress-test decisions and lock scope. In time-boxed hackathon settings, defaults to a single fast Frontier round.
---

# Grill-Me

Interview the candidate or user to reach a shared understanding before building. Map decisions as a **design tree**: every foundational decision branches into the technical and operational choices that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and provide your recommended answer.

## 1. Five-Line Inverted Interview Restate

Before presenting the Frontier round, restate the task context in exactly 5 lines to demonstrate alignment without stalling:

1. **Target Deliverable & Archetype**: e.g., Archetype A (Data/CLI) / Archetype B (API) / Archetype C (Web App).
2. **Primary Evaluator & Consumer**: What harness, grader, or persona executes the outcome.
3. **Core Success Metric**: The single load-bearing functional flow or metric required.
4. **Anti-Over-Engineering Boundary**: What speculative architectures are explicitly rejected (`sharpen`).
5. **Load-Bearing Risk (`{ root, first_nail }`)**:
   - `root`: The single hidden failure mode or bottleneck (e.g., corrupt input handling, latency cap).
   - `first_nail`: The smallest vertical tracer-bullet step that proves or breaks the root in the first slice.

## 2. One-Round Frontier Format

Format the Frontier round like so:

```
❓ **Q1** - **<question title>**: <question body, concise context and alternatives>

➡️ <your recommended answer with anti-over-engineering rationale>

---

❓ **Q2** - **<question title>**: <question body, concise context and alternatives>

➡️ <your recommended answer with anti-over-engineering rationale>
```

Word each question so answering `"yes"` accepts your recommended answer.

## 3. Time-Boxed Hackathon Rule (1-Round Frontier Default)

In a time-boxed exam or hackathon (e.g., 180 minutes), running open-ended multi-round interviews is an anti-pattern that drains critical implementation time.
- **Default to 1 single fast Frontier round (`T+06m..15m`)** with 2–4 targeted questions covering:
  1. The Tracer-Bullet End-to-End MVP flow.
  2. Anti-over-engineering boundary (`sharpen`).
  3. Dynamic verification checks to populate in `.cofa/trace.json`.
- When the candidate answers or confirms `"yes"`, immediately lock the decisions, populate `.cofa/trace.json`, and transition to the build loop. Do not stall with redundant interview rounds once the core scope is settled.

## 4. Autonomous Fact Scan

Finding _facts_ is your job, never the user's. Before asking questions, inspect the environment (`README.md`, existing workspace code, package configuration, sample data). Never ask the user for information you can discover directly from the workspace. Only present questions where user judgment or trade-off decisions are required.
