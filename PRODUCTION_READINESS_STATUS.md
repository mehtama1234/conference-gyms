# Production Readiness Status

## Current State

The production proof now has three lanes.

| Lane | Current proof | Runtime status | Export status |
| --- | --- | --- | --- |
| `TerminalTraj` | One released task, `task_5279`, ran locally, passed the released pytest verifier, replayed through a tracked wrapper, and produced `trace.real.json`. | Passed for one task. | Hosted conversion, SFT export, and training export blocked. |
| `CyberGym` | Repo pinned, security task contract normalized, one `arvo:10400` task was materialized from Hugging Face files, generated `README.md`/`submit.sh`, fixture MNG PoC was submitted through generated `submit.sh`, vulnerable build produced ASAN evidence in `mng_get_long`, fixed build exited 0, and PoC DB stored exit codes 1/0. | Passed for one fixture PoC solution; no model-agent exploit discovery claim. | Hosted conversion, SFT export, and training export blocked. |
| `OpenApps` | Repo pinned, package root import passed, 8 app configs discovered, 28 original tasks parsed, `AddToDoTask` saved-state reward fixture passed, reward fixture replay passed, no-sudo Chromium library extraction passed, and one real Playwright/Chromium browser GUI task added `Call Mom` with reward 1.0. | Passed for one selected GUI task with local compatibility shims. | Hosted conversion, SFT export, and training export blocked. |

Run the aggregate gate:

```bash
python3 scripts/validate_production_lanes.py
```

Expected result:

- all lane validators pass
- three lanes have real local runs
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
- submission server startup
- selected `arvo:10400` task data materialization
- generated task README and submit script
- masked task checksum validation
- PoC upload and database write
- vulnerable/fixed Docker verifier execution
- normalized real security verifier trace
- fixture PoC solution with vulnerable/fixed exit codes 1/0
- README-subset broader-sample readiness scan
- explicit blocker that only `arvo:10400` has local verifier images

OpenApps proves the third family contract:

- browser/GUI app world
- transparent Python app state
- ground-truth reward model
- app config discovery
- task YAML parsing
- saved-state reward fixture
- saved-state reward replay
- MCP/Playwright browser runtime for one selected task
- no-sudo local Chromium library extraction
- deterministic GUI action trace
- ground-truth browser reward verifier
- normalized real browser GUI trace

## What Is Not Proven Yet

The repo does not yet prove:

- CyberGym model-agent exploit discovery or independent exploit-discovery trajectory
- CyberGym coverage beyond the single `arvo:10400` fixture solution
- OpenApps full 28-task browser coverage
- OpenApps dummy-agent or model-agent task execution
- upstream dependency policy that removes local OpenApps/FastHTML compatibility shims
- hosted conversion approval
- SFT or training export approval

## Next Meaty Goal

OpenApps has now reached the first real local GUI task proof. The next choice is
to harden OpenApps or move to CyberGym:

1. for OpenApps, remove or upstream the FastHTML compatibility shims
2. sample more than one selected GUI task
3. add cleanup/replay receipts for the broader GUI sample
4. decide whether deterministic fixtures or dummy/model agents are the production proof
5. keep export blocked unless license/privacy/split receipts explicitly clear it

Promote CyberGym from fixture-only solution to agent-performance evidence:

1. use the generated `arvo:10400` task files
2. run a model agent or independent exploit-discovery process against those files
3. submit exactly one final PoC through generated `submit.sh`
4. record solved or benchmark-meaningful vulnerable/fixed verifier output with discovery trace
5. pull or install at least one more README-subset vulnerable/fixed verifier pair
6. keep export blocked unless contamination, split, privacy, and security review
   receipts explicitly clear it
