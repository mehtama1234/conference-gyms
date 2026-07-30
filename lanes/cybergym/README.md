# CyberGym Production Lane

## Current Status

Status: source pinned, no-heavy import smoke passed, selected task manifest
generated, and vulnerable/fixed verifier execution passed for a fixture MNG PoC
solution. A second README-subset task, `arvo:1065`, is also materialized and
verifier-runnable locally with an empty runtime probe.

CyberGym is the second production lane after TerminalTraj. It represents the
security/code family: an agent receives a vulnerable codebase, proposes a proof
of concept, submits it to a server, and the verifier compares behavior against
vulnerable and fixed builds.

Unlike the TerminalTraj starter task, this lane should not be treated as
model-agent performance evidence yet. The repo is available locally, the single
`arvo:10400` data files were materialized from Hugging Face, CyberGym generated
the task README and `submit.sh`, the generated `submit.sh` reached the
vulnerable verifier, the fixed verifier also executed, and the PoC database
stored vulnerable/fixed exit codes 1/0 for a fixture MNG PoC. The selected
`arvo:1065` verifier images are also local and its generated task has a
second-task runtime trace with vulnerable/fixed exit codes 0/0 for an empty
probe. Broader benchmark/server data remains heavyweight:

- benchmark data: about 240GB
- binary-only server data: about 130GB
- full server data: about 10TB

The correct production stance is therefore: pin the repo, define the evidence
contract, record verifier execution honestly, separate fixture success from
model-agent discovery, and block export until security, privacy, license, and
split decisions are recorded.

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
  task files, generated `submit.sh` use, and fixture PoC verifier result.
- `independent-discovery-receipt.json`: task-facing independent discovery replay
  for `arvo:10400`, derived from description, error trace, and vulnerable
  source inspection, with vulnerable/fixed verifier result 1/0.
- `broader-sample-readiness.json`: README-subset readiness scan showing that
  all 10 sample task files are remotely visible and `arvo:10400` plus
  `arvo:1065` have local vulnerable/fixed verifier images.
- `second-task-runtime-receipt.json`: generated `arvo:1065` task manifest,
  generated `submit.sh` use, vulnerable/fixed verifier execution, and PoC DB
  write for an empty runtime probe.
- `arvo1065-stability-audit.json`: repeated direct-Docker audit showing tiny
  non-exploit inputs can vary on `arvo:1065`, including fixed-build failures, so
  the second task is not promoted as exploit evidence.
- `trace.real.json`: normalized real security task-manifest verifier trace for
  the fixture `arvo:10400` PoC.
- `trace.discovery.real.json`: normalized independent discovery trajectory for
  `arvo:10400`, including evidence policy, discovery observations/actions, PoC
  artifact hash, verifier result, quality, and export gate.
- `trace.second.real.json`: normalized second-task runtime trace for
  `arvo:1065`.
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
make probe-cybergym-arvo10400-independent-discovery
make probe-cybergym-broader-sample
make probe-cybergym-second-task-runtime
```

Expected output:

```text
CyberGym lane artifacts validate
```
