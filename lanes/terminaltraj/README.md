# TerminalTraj Production Lane

## Current Status

Status: source pinned, one released task selected, real local verifier passed,
export blocked.

This lane is the first production-readiness proof target for terminal/sandbox
gyms. The local checkout is enough to identify the paper, source repo, license,
dataset pointers, and released source-license metadata. It is not yet enough to
run a task because the released Docker task instances are not present locally.

## Source Pin

| Field | Value |
| --- | --- |
| Local folder | `TerminalTraj` |
| Upstream remote | `https://github.com/multimodal-art-projection/TerminalTraj.git` |
| Commit | `01305cbf0425b08b41cf8cfc3e30abb0f4953c27` |
| Branch state | `main...origin/main`, clean |
| Repo license | Apache-2.0 |
| Paper | `TerminalTraj: Large-Scale Terminal Agentic Trajectory Generation from Dockerized Environments` |
| Venue signal | ICML 2026 Spotlight |
| Dataset pointer | `m-a-p/TerminalTraj` |
| Instance pointer | `m-a-p/TerminalTraj-5k-instances` |
| Local source-license metadata | `TerminalTraj/source/repo&license.jsonl`, 2,481 rows |

## Why This Lane Comes First

TerminalTraj is the cleanest first production lane because the world shape is
simple but real. A task begins from a Dockerized repository environment. The
agent acts through terminal commands. The observable state is command output,
filesystem changes, exit status, and validator output. The verifier is
executable validation code rather than a loose natural-language judgment.

That gives us the minimum serious gym contract:

- reset a task into a known filesystem/container state
- capture the initial observation
- record terminal actions and command outputs
- run the task validator
- capture final files and verifier logs
- emit a normalized trace
- block export until license, privacy, split, and reuse receipts are cleared

## Current Blocker

The released instance archive has been downloaded into ignored local cache and
one task, `task_5279`, has been run locally. Docker is installed, the task base
image was pulled, the task image was built with `TMPDIR` redirected away from
the full `/tmp`, the container was reset, task actions were applied, and the
released pytest verifier passed all four checks. Export remains blocked because
the task-specific source-license row has not been resolved from
`repo&license.jsonl`.

Because of that, this lane can now claim local runtime validation for one task,
but still cannot honestly claim:

- training/export readiness

## Next Action

Create a minimal fixture or download one small released task instance, then
produce these artifacts:

1. `setup-receipt.json`
2. `task-manifest.json`
3. `reset-receipt.json`
4. `trace.normalized.json`
5. `verifier-receipt.json`
6. `cleanup-receipt.json`
7. `export-decision.json`

The first acceptable pass may be fixture-only, but it must say so explicitly and
must keep training/export blocked.

## Contract Artifacts

The lane now includes a fixture-level contract test:

- `source-pin.json`: upstream repo, commit, license, dataset pointers, and
  runtime blockers.
- `task-manifest.json`: selected released task, file hashes, task prompt
  summary, verifier shape, and unresolved license/runtime blockers.
- `setup-receipt.json`: local setup evidence for archive download, extraction,
  Docker availability, base image pull, and task image build.
- `reset-receipt.json`: real container reset and initial state evidence.
- `verifier-receipt.json`: released pytest verifier result, 4 passed.
- `cleanup-receipt.json`: container and network cleanup evidence.
- `trace.schema.json`: normalized terminal/sandbox trace shape.
- `trace.fixture.json`: non-runtime fixture trace that exercises the shape
  without claiming benchmark execution.
- `trace.real.json`: normalized real local trace for `task_5279`.
- `export-decision.json`: explicit block on hosted conversion, SFT export, and
  training export.
- `../../scripts/validate_terminaltraj_lane.py`: local validator for the lane
  artifacts.

Run:

```bash
python3 scripts/validate_terminaltraj_lane.py
```

Expected output:

```text
TerminalTraj lane artifacts validate
```
