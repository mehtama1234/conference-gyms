# OpenApps Production Lane

## Current Status

Status: source pinned, source/config smoke passed, state reward fixture passed,
and one real Playwright/Chromium browser GUI task passed. Export remains
blocked.

OpenApps is the third production lane. It represents browser/GUI worlds with
transparent Python app state and ground-truth rewards. It is lower
infrastructure than CyberGym because the README says it runs on a single CPU
without Docker or OS emulators, but broader agent/browser runs still require
Python dependencies, BrowserGym, Playwright/Chromium, and optional model keys.

## Current Proof

The lane currently proves:

- repo source pin
- package root import
- app config discovery
- task YAML parsing
- local task inventory count
- non-browser task reward check for `AddToDoTask`
- local no-sudo Chromium library extraction
- real MCP/Playwright browser execution for `AddToDoTask`
- deterministic browser actions: click, type `Call Mom`, press Enter
- final todo count moved from 15 to 16
- ground-truth browser reward was 1.0
- normalized real browser GUI trace
- export blocked by CC BY-NC 4.0 and missing privacy/split/export receipts

It does not yet claim:

- all 28 OpenApps tasks pass
- a model-agent task execution receipt
- runtime shims are acceptable production dependency policy
- hosted conversion, SFT export, or training export approval

## Contract Artifacts

- `source-pin.json`: upstream repo, commit, license, and blockers.
- `task-contract.json`: GUI/browser task shape and reward model.
- `source-smoke-receipt.json`: package root import and config/task parsing.
- `reward-fixture-receipt.json`: repo task class and saved-state reward check.
- `replay-receipt.json`: repeatable local replay of the saved-state reward
  fixture.
- `browser-runtime-attempt-receipt.json`: repeatable local browser GUI run for
  the selected AddToDo task.
- `trace.fixture.json`: normalized non-browser state/reward fixture trace.
- `trace.real.json`: normalized real browser GUI trace for the selected task.
- `export-decision.json`: explicit hosted/SFT/training export block.
- `../../scripts/validate_openapps_lane.py`: local validator.

Run:

```bash
python3 scripts/validate_openapps_lane.py
```

The browser replay is local-only because it may install packages and Chromium
into ignored `.cache/` paths and uses local compatibility shims:

```bash
make replay-openapps-browser
```

Expected output:

```text
OpenApps lane artifacts validate
```
