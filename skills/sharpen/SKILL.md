---
name: sharpen
description: Sharpen a task before starting. Focus on outcome, anti-over-engineering, and right-sizing specifications.
---

# Sharpen

Before starting implementation, ask how a pragmatic expert would approach this task: their simplest raw sources, their direct methods, and an outside check that the result is right.

Identify what the user or evaluation is really after, and whether the task is over- or under-specified.

## The Anti-Over-Engineering Principle (`NO-OVER-ENGINEERING`)

In a time-boxed exam or production sprint:
1. **Loosen constraints that do not serve the goal** as readily as you add ones that do.
2. **Leave choices that belong to the user open** instead of prematurely deciding them.
3. **Fold in only what makes the work better, not bigger**:
   - ❌ Do NOT add distributed locks or complex mutexes to read-heavy endpoints.
   - ❌ Do NOT introduce background queue systems, message brokers, or heavy ORMs unless explicitly requested by `README.md`.
   - ❌ Do NOT build speculative microservice abstractions, nested generic wrappers, or unrequested configuration files.
4. **Always maintain one outside check that the result is right**:
   - Verify with a focused test or live smoke probe (`0.0.0.0:<PORT>`).
5. **Document rejected complexity**:
   - Explicitly record rejected over-engineering alternatives in `.cofa/trace.json` (`rejected_over_engineering[]`) and `.cofa/decisions.tsv`.
   - This directly defends the candidate's cognition score during post-exam review (`사후 Q&A`).
