# Production Readiness Goal

## Meaty End-To-End Goal

Make one conference gym lane real end to end:

> Run one local benchmark task from source repo to normalized AIDF trace, with
> reset evidence, initial observation, action trace, verifier result, final
> state, cleanup receipt, replay notes, and explicit export approval gates.

This is useful because the current inventory already describes many worlds. The
missing production proof is whether one world can actually move through the full
pipeline without hand-waving:

1. source repo is pinned and understood
2. runtime setup is reproducible
3. a task can be reset
4. an agent or fixture can act
5. the environment records observations and actions
6. the verifier decides pass/fail
7. the result is converted into the common trace format
8. quality and failure categories are assigned from evidence
9. training/export stays blocked unless license, privacy, split, and reuse
   receipts exist

## Recommended First Lane

Use `TerminalTraj` or `CyberGym` before browser/mobile/full external-service
lanes.

`TerminalTraj` is the lower-risk first production lane because terminal tasks
have a compact state surface: filesystem, commands, stdout/stderr, exit status,
file diffs, validator output, and cleanup. That is enough to prove the core
shape of a gym without needing browser state, mobile emulators, third-party
model endpoints, or human review.

`CyberGym` is the higher-value follow-up because security gyms add the thing we
ultimately care about: executable vulnerability verification. A successful
security lane proves that the pipeline can represent setup, exploit attempt,
patch state, verifier logs, network/sandbox boundaries, and safety gates.

## Definition Of Done For One Lane

A lane is production-ready only when the repo contains evidence for all of
these:

| Requirement | Evidence artifact |
| --- | --- |
| Source pin | upstream remote, commit SHA, local path, license note |
| Runtime setup | install command, environment variables, container or venv receipt |
| Task manifest | task id, prompt/source, initial files/state, expected verifier |
| Reset receipt | proof the task starts from a known state |
| Observation record | initial observation and every later observation |
| Action record | typed actions, raw commands/tool calls, timestamps, errors |
| Verifier result | deterministic pass/fail output or bounded judge output |
| Final state | final files/state plus verifier-facing artifacts |
| Cleanup receipt | processes, containers, temp files, credentials, network state |
| Normalized trace | AIDF/ADP-compatible JSON record for the run |
| Quality assessment | failure category, evidence completeness, replay confidence |
| Export decision | allowed/blocked for local validation, hosted conversion, SFT, training |

## Current Proof

The first concrete work item is now complete for `TerminalTraj`: one released
task ran locally, passed its executable verifier, replayed, produced a
normalized trace, and kept export blocked.

`CyberGym` is the second lane: source pin, task contract, and no-heavy import
smoke are complete; heavyweight data/server runtime remains blocked.

`OpenApps` is the third lane: source pin, package root import, app config
discovery, task YAML parsing, saved-state reward replay, no-sudo Chromium
library extraction, and a tracked MCP/Playwright browser attempt are complete.
The remaining blocker is OpenApps/FastHTML/Starlette runtime compatibility
before the todo page renders `#new-title`.

## Next Concrete Work Item

Promote OpenApps first, then CyberGym:

1. For OpenApps, resolve the FastHTML/Starlette compatibility issue so the
   todo page renders `#new-title`.
2. Rerun `make replay-openapps-browser`.
3. Reset app state and apply the deterministic AddToDo browser action path.
4. Record reward/verifier output.
5. Emit a normalized OpenApps GUI trace.
6. Keep export blocked unless privacy, split, license, and contamination
   receipts explicitly clear it.
7. Then return to CyberGym and attempt one local security task if storage allows.

## What This Does Not Claim

This does not claim that every local gym is production-ready. It does not claim
training data can be exported. It does not claim hosted conversion is approved.
It proves one lane deeply enough that the remaining worlds can be promoted with
the same evidence contract instead of new one-off formats.
