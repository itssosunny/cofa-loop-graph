---
name: verification-before-completion
description: Iron law of verification before claiming completion or committing. Requires fresh command execution output before declaring status.
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

Violating the letter of this rule is violating the spirit of this rule.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not executed the verification command or probe in the current turn and inspected its real output, you cannot claim it passes.

## The Gate Function

BEFORE claiming any task is complete, passing, or ready for commit:

1. **IDENTIFY**: What command or live endpoint probe proves this claim?
2. **RUN**: Execute the FULL command or probe against the actual running code/server.
3. **READ**: Inspect exit code, stdout, stderr, HTTP status code, and response body.
4. **VERIFY**: Does the output genuinely confirm the claim?
   - If NO: State the actual failing output and exact error.
   - If YES: State the claim accompanied by the actual output.
5. **ONLY THEN**: Make the status claim or commit locally.

Skip any step = unverified assertion.

## Red Flags — STOP

- Using speculative language: "should work now", "probably passes", "seems complete".
- Expressing satisfaction before running verification ("Done!", "Looks great!", "Fixed!").
- Trusting subagent success reports without inspecting `git diff` or running test/probe commands yourself.
- Staging or committing code without fresh test output.
- Running `git push` (STRICTLY PROHIBITED in the exam environment: local commits only!).

## Verification Rules by Artifact Type

| Target | Required Evidence | Insufficient Evidence |
|---|---|---|
| **Unit / Integration Tests** | Test command exits `0` with 0 failures | Previous test run, "linter passes" |
| **Web Endpoints** | Live HTTP probe to `0.0.0.0:<PORT>` returns expected status code and body | Server process started, code looks right |
| **UI Components** | Render verification, no-op handler check passes | HTML template exists |
| **Submission Documentation** | `cofa_verify.py` passes `[BASE-3] CODE-DOC-FIDELITY` | Markdown file written without checking code |

## Exam Git Rule: Local Commit Only

In the hackathon exam environment:
- ✅ Allowed: `git status`, `git diff`, `git add -A && git commit -m "..."`
- ❌ **STRICTLY PROHIBITED**: `git push` (violates exam network boundaries and repository management rules).
