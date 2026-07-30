# TerminalTraj Production Lane

## Current Status

Status: source pinned, runtime blocked.

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

The local repo does not contain the released Docker task instances. The README
points to the Hugging Face instance release, but those files have not been
downloaded or materialized here.

Because of that, this lane cannot honestly claim:

- task reset
- Docker runtime setup
- validator execution
- replay
- normalized real trace
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
