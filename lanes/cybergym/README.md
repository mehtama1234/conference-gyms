# CyberGym Production Lane

## Current Status

Status: source pinned, no-heavy import smoke passed, selected task manifest
generated, and vulnerable/fixed verifier execution passed for a trivial
unsolved PoC.

CyberGym is the second production lane after TerminalTraj. It represents the
security/code family: an agent receives a vulnerable codebase, proposes a proof
of concept, submits it to a server, and the verifier compares behavior against
vulnerable and fixed builds.

Unlike the TerminalTraj starter task, this lane should not be treated as a solved
task run yet. The repo is available locally, the single `arvo:10400` data files
were materialized from Hugging Face, CyberGym generated the task README and
`submit.sh`, the generated `submit.sh` reached the vulnerable verifier, the
fixed verifier also executed, and the PoC database stored exit codes. The
selected `arvo:10400` verifier images are local, but broader benchmark/server
data remains heavyweight:

- benchmark data: about 240GB
- binary-only server data: about 130GB
- full server data: about 10TB

The correct production stance is therefore: pin the repo, define the evidence
contract, record verifier execution honestly, avoid claiming task success for a
trivial PoC, and block export until security, privacy, license, and split
decisions are recorded.

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
- `server-probe-receipt.json`: local FastAPI submission server startup,
  masked task submission, vulnerable/fixed verifier execution, and PoC DB write.
- `task-manifest-receipt.json`: single-task data materialization, generated
  task files, generated `submit.sh` use, and unsolved verifier result.
- `trace.real.json`: normalized real security task-manifest verifier trace for
  the trivial `arvo:10400` PoC.
- `export-decision.json`: explicit block on hosted conversion, SFT export, and
  training export.
- `../../scripts/validate_cybergym_lane.py`: local validator for the lane
  artifacts.

Run:

```bash
python3 scripts/validate_cybergym_lane.py
```

The probes are local-only because they install server dependencies into an
ignored venv and write ignored task/data/PoC cache files:

```bash
make probe-cybergym-server
make probe-cybergym-task-manifest
```

Expected output:

```text
CyberGym lane artifacts validate
```
