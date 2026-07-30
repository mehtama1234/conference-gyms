# Production Readiness Status

## Current State

The production proof now has two lanes.

| Lane | Current proof | Runtime status | Export status |
| --- | --- | --- | --- |
| `TerminalTraj` | One released task, `task_5279`, ran locally, passed the released pytest verifier, replayed through a tracked wrapper, and produced `trace.real.json`. | Passed for one task. | Hosted conversion, SFT export, and training export blocked. |
| `CyberGym` | Repo pinned, security task contract normalized, and no-heavy import smoke passed. | Heavy runtime blocked until data/server receipts exist. | Hosted conversion, SFT export, and training export blocked. |

Run the aggregate gate:

```bash
python3 scripts/validate_production_lanes.py
```

Expected result:

- both lane validators pass
- one lane has a real local run
- both lanes keep export blocked

## What Is Actually Proven

TerminalTraj proves the full local mechanics:

- source pin
- selected released task
- Docker setup
- reset
- initial observation
- action sequence
- executable verifier result
- cleanup
- replay
- normalized trace
- export gates

CyberGym proves the second family contract:

- source pin
- security task shape
- vulnerable/fixed verifier model
- PoC submission fields
- anti-leakage and network policy requirements
- no-heavy package import
- honest data/server blockers

## What Is Not Proven Yet

The repo does not yet prove:

- CyberGym server startup
- CyberGym selected task generation
- CyberGym PoC submission
- CyberGym vulnerable/fixed verifier execution
- hosted conversion approval
- SFT or training export approval
- a public remote push for this gym analysis repo

## Next Meaty Goal

Promote CyberGym from contract-only to one real local security task if storage
and runtime are acceptable:

1. install CyberGym server dependencies into an isolated venv
2. download only the documented subset or binary-only server data
3. start the local PoC submission server
4. generate one subset task, such as `arvo:10400`
5. submit a trivial PoC to prove server wiring
6. record vulnerable/fixed verifier output
7. emit `trace.real.json` for CyberGym
8. keep export blocked unless contamination, split, privacy, and security review
   receipts explicitly clear it

If CyberGym data remains too heavy, the fallback is a third low-infrastructure
real-run lane from another terminal/code benchmark, using the TerminalTraj
evidence contract.
