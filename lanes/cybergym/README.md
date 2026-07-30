# CyberGym Production Lane

## Current Status

Status: source pinned, no-heavy import smoke passed, runtime contract
documented, heavy run blocked.

CyberGym is the second production lane after TerminalTraj. It represents the
security/code family: an agent receives a vulnerable codebase, proposes a proof
of concept, submits it to a server, and the verifier compares behavior against
vulnerable and fixed builds.

Unlike the TerminalTraj starter task, this lane should not be treated as a small
local run yet. The repo is available locally, but benchmark data and server
runtime data are heavyweight:

- benchmark data: about 240GB
- binary-only server data: about 130GB
- full server data: about 10TB

The correct production stance is therefore: pin the repo, define the evidence
contract, block runtime claims until data/server receipts exist, and block export
until security, privacy, license, and split decisions are recorded.

## What This Lane Normalizes

CyberGym adds fields that TerminalTraj does not cover:

- vulnerable repository artifact
- proof-of-concept file
- submission server URL and PoC database
- vulnerable-build result
- fixed-build result
- network/firewall policy
- any-of vs final-submission metric
- anti-leakage checks for patch history, known PoCs, and internet shortcuts

## Contract Artifacts

- `source-pin.json`: upstream repo, commit, license, and conference signal.
- `task-contract.json`: normalized security task shape.
- `setup-receipt.json`: local repo/install/data/server status and blockers.
- `import-smoke-receipt.json`: no-heavy package import smoke for `cybergym`
  and `cybergym.utils`.
- `export-decision.json`: explicit block on hosted conversion, SFT export, and
  training export.
- `../../scripts/validate_cybergym_lane.py`: local validator for the lane
  artifacts.

Run:

```bash
python3 scripts/validate_cybergym_lane.py
```

Expected output:

```text
CyberGym lane artifacts validate
```
