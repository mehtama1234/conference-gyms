# Production Readiness Status

## Current State

The production proof now has three lanes.

| Lane | Current proof | Runtime status | Export status |
| --- | --- | --- | --- |
| `TerminalTraj` | One released task, `task_5279`, ran locally, passed the released pytest verifier, replayed through a tracked wrapper, and produced `trace.real.json`. | Passed for one task. | Hosted conversion, SFT export, and training export blocked. |
| `CyberGym` | Repo pinned, security task contract normalized, and no-heavy import smoke passed. | Heavy runtime blocked until data/server receipts exist. | Hosted conversion, SFT export, and training export blocked. |
| `OpenApps` | Repo pinned, package root import passed, 8 app configs discovered, 28 original tasks parsed, `AddToDoTask` saved-state reward fixture passed, and reward fixture replay passed. | Browser runtime blocked until full dependencies, BrowserGym, and Playwright/Chromium are installed. | Hosted conversion, SFT export, and training export blocked. |

Run the aggregate gate:

```bash
python3 scripts/validate_production_lanes.py
```

Expected result:

- all lane validators pass
- one lane has a real local run
- all lanes keep export blocked

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

OpenApps proves the third family contract:

- browser/GUI app world
- transparent Python app state
- ground-truth reward model
- app config discovery
- task YAML parsing
- saved-state reward fixture
- saved-state reward replay
- dependency/browser blockers

## What Is Not Proven Yet

The repo does not yet prove:

- CyberGym server startup
- CyberGym selected task generation
- CyberGym PoC submission
- CyberGym vulnerable/fixed verifier execution
- OpenApps BrowserGym startup
- OpenApps dummy-agent or fixture task execution
- OpenApps reward verifier execution
- hosted conversion approval
- SFT or training export approval
- a public remote push for this gym analysis repo

## Next Meaty Goal

Promote OpenApps from source/config smoke to one real local GUI task first,
because it is lower infrastructure than CyberGym:

1. install OpenApps dependencies in an isolated environment
2. install Playwright Chromium
3. select one low-risk task, such as `add_call_mom_to_my_todo`
4. reset the app state
5. run a deterministic fixture or dummy agent action
6. record the app state before and after
7. run the ground-truth reward/verifier
8. emit a normalized GUI trace
9. keep export blocked unless license/privacy/split receipts explicitly clear it

After that, promote CyberGym from contract-only to one real local security task
if storage and runtime are acceptable:

1. install CyberGym server dependencies into an isolated venv
2. download only the documented subset or binary-only server data
3. start the local PoC submission server
4. generate one subset task, such as `arvo:10400`
5. submit a trivial PoC to prove server wiring
6. record vulnerable/fixed verifier output
7. emit `trace.real.json` for CyberGym
8. keep export blocked unless contamination, split, privacy, and security review
   receipts explicitly clear it
