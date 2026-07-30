# OpenApps Production Lane

## Current Status

Status: source pinned, source/config smoke passed, state reward fixture passed,
browser runtime blocked.

OpenApps is the third production lane. It represents browser/GUI worlds with
transparent Python app state and ground-truth rewards. It is lower
infrastructure than CyberGym because the README says it runs on a single CPU
without Docker or OS emulators, but a real agent/browser run still requires
Python dependencies, BrowserGym, Playwright/Chromium, and optional model keys.

## Current Proof

The lane currently proves:

- repo source pin
- package root import
- app config discovery
- task YAML parsing
- local task inventory count
- non-browser task reward check for `AddToDoTask`
- export blocked by CC BY-NC 4.0 and missing runtime/export receipts

It does not yet claim:

- full dependency installation
- BrowserGym environment startup
- Playwright/Chromium browser run
- dummy-agent task execution
- browser reward verifier result
- normalized real browser GUI trace

## Contract Artifacts

- `source-pin.json`: upstream repo, commit, license, and blockers.
- `task-contract.json`: GUI/browser task shape and reward model.
- `source-smoke-receipt.json`: package root import and config/task parsing.
- `reward-fixture-receipt.json`: repo task class and saved-state reward check.
- `replay-receipt.json`: repeatable local replay of the saved-state reward
  fixture.
- `trace.fixture.json`: normalized non-browser state/reward fixture trace.
- `export-decision.json`: explicit hosted/SFT/training export block.
- `../../scripts/validate_openapps_lane.py`: local validator.

Run:

```bash
python3 scripts/validate_openapps_lane.py
```

Expected output:

```text
OpenApps lane artifacts validate
```
