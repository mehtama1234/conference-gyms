# Agent Gym Repos

This folder contains public benchmark, environment, and trajectory repos related
to the ICML/ICLR themes on executable benchmark replay and guided trajectories.

See `CONFERENCE_WORLD_ANALYSIS.md` for the expanded ICML/ICLR world inventory,
including the additional repos added after the first pass and the AIDF mapping
template.

Analysis artifacts:

- `CONFERENCE_WORLD_ANALYSIS.md`: inventory, taxonomy, and cross-repo patterns.
- `WORLD_ANATOMY_MAP.md`: repo-by-repo state/action/verifier/runtime anatomy.
- `AIDF_WORLD_IMPLEMENTATION_GAPS.md`: platform capabilities AIDF should build
  from these worlds.
- `WORLD_PACKAGE_INVENTORY.yaml`: structured first-pass map from local worlds to
  AIDF world-package fields and adapter priorities.
- `conference-world-adapter-readiness.json`: generated AIDF readiness rollup
  with world-package projection status, runtime adapter families, and
  contract-smoke coverage.
- `agent-data-protocol-approval-overrides.template.json`: generated ADP
  approval override template with one editable entry per dataset approval
  receipt.

Current adapter coverage from the generated readiness rollup:

- 33 local world-package projections.
- 0 projection errors.
- 8 runtime adapter families.
- 8 runtime family contract smokes.
- No missing runtime family contract-smoke ids.
- 17 source-specific package projections and 16 inventory projections.
- 1 first heavy-run receipt candidate: `Agent-Data-Protocol`.
- 1 policy/export decision receipt: `Agent-Data-Protocol`.
- 1 dataset review matrix: `Agent-Data-Protocol`.
- 1 dataset approval receipt-template set: `Agent-Data-Protocol`.
- 1 generated ADP approval override template with 280 editable receipt entries.
- `OpenApps` source-specific projection is ready and its no-heavy-run adapter
  smoke and evidence/gate receipts are complete; heavy-run blockers remain.
- `Agent-Data-Protocol` source-specific projection is ready and its no-heavy-run
  adapter smoke and evidence/gate receipts are complete; full dataset
  conversion, split integrity, and training-export blockers remain. It is now
  also the selected first heavy-run lane, with local fixture/schema validation
  passing 289 checks in a temporary `litellm` execution environment. Its
  policy/export decision receipt allows local fixture evidence only for adapter
  contract validation. Its dataset review matrix records per-dataset license,
  privacy, split, hosted conversion, and training-export status; those gates
  remain blocked until dataset-level approval receipts are completed. Its
  approval receipt-template set now creates the concrete blocked receipts that
  must be filled in for each dataset.
  The CLI can validate edited override files in strict mode so unsupported
  approvals without evidence do not silently open export gates.
- `MC-Search` is now the first second source-specific bridge in the
  trajectory/data family; its projection, no-heavy-run adapter smoke, and
  evidence/gate receipts are complete; Hugging Face dataset download, KB
  embedding build, model/API credentials, agent run, evaluator run, judge
  calibration, and training-export blockers remain.
- `ScaleCUA` is now the first second source-specific bridge outside the
  trajectory/data family; its cross-platform CUA projection, no-heavy-run
  adapter smoke, and evidence/gate receipts are complete; model serving,
  browser/VM/Android platform setup, WebArenaLiteV2 launcher assets, evaluator
  execution, privacy review, and training-export blockers remain.
- `CyberGym`, `BIRD-Interact`, `VERINA`, and `RealPDEBench` were added as the
  parallel second-bridge batch across terminal/sandbox, external user/database
  loop, formal proof, and scientific simulator families; each has no-heavy-run
  smoke and evidence/gate receipts, while runtime data, service/toolchain,
  verifier execution, replay, privacy/license, and export blockers remain.
- `TerminalTraj` source-specific projection is ready and its no-heavy-run
  adapter smoke and evidence/gate receipts are complete; Docker/materialization,
  validator, sandbox isolation, and training-export blockers remain.
- `Gaia2-ARE` source-specific projection is ready and its no-heavy-run adapter
  smoke and evidence/gate receipts are complete; scenario materialization,
  model credentials, runtime lifecycle, replay, and training-export blockers
  remain.
- `Swing-Bench` source-specific projection is ready and its no-heavy-run
  adapter smoke and evidence/gate receipts are complete; target repo checkout,
  dependency install, CI execution, generated-code review, and training-export
  blockers remain.
- `AlgoVeri` source-specific projection is ready and its no-heavy-run adapter
  smoke and evidence/gate receipts are complete; formal toolchain install,
  theorem split, verifier execution, timeout/replay, and training-export
  blockers remain.
- `SimuHome` source-specific projection is ready and its no-heavy-run adapter
  smoke and evidence/gate receipts are complete; simulator startup, dependency
  setup, seed/replay, metric execution, cleanup, license, and training-export
  blockers remain.
- `UI-Venus-VenusBench-Mobile` source-specific projection is ready and its
  no-heavy-run adapter smoke and evidence/gate receipts are complete; emulator
  startup, Android SDK/AVD setup, APK install, screenshot/accessibility capture,
  gesture execution, completion verification, cleanup, privacy review, and
  training-export blockers remain.

The first source-specific adapter targets are listed in
`CONFERENCE_WORLD_ANALYSIS.md`: `OpenApps`, `Agent-Data-Protocol`,
`MC-Search`, `ScaleCUA`, `CyberGym`, `BIRD-Interact`, `VERINA`,
`RealPDEBench`, `TerminalTraj`, `Gaia2-ARE`, `Swing-Bench`, `AlgoVeri`,
`SimuHome`, and `UI-Venus-VenusBench-Mobile`.

## External Benchmark / Environment Replay

| Folder | Source | What It Is | Useful For AIDF |
|---|---|---|---|
| `CyberGym` | `sunblaze-ucb/cybergym` | Real vulnerability-analysis benchmark with executable PoC verification. | Security world replay, pre/post patch verifiers, sandboxed code evidence. |
| `Gaia2-ARE` | `facebookresearch/meta-agents-research-environments` | Dynamic asynchronous agent environments and Gaia2 scenarios. | Long-horizon async worlds, action-level verifiers, environment event loops. |
| `OpenApps` | `facebookresearch/OpenApps` | Configurable UI apps for evaluating computer-use agents across variations. | UI world variants, robustness across layout/content changes. |
| `BIRD-Interact` | `bird-bench/BIRD-Interact` | Dynamic interactive text-to-SQL with user simulator, CRUD, and executable tests. | Enterprise database-agent worlds, clarification loops, stateful task checks. |
| `MedAgentGym` | `wshi83/MedAgentGym` | Biomedical coding-agent environment with sandbox tasks and feedback. | Domain-specific scientific/healthcare coding worlds and trajectory sampling. |
| `AstaBench` | `allenai/asta-bench` | Scientific research-agent benchmark with tools, costs, and standardized scoring. | Research-agent eval adapters, tool/cost normalization, scientific workflows. |
| `SandboxEscapeBench` | `UKGovernmentBEIS/sandbox_escape_bench` | Inspect AI eval for container breakout capability. | Chaos/security hardening worlds and infrastructure-risk evaluation. |
| `CVE-Factory` | `livecvebench/CVE-Factory` | Multi-agent pipeline that turns CVEs into executable security tasks. | Source-to-world generation for security, large-scale executable task synthesis. |
| `MEnvAgent` | `ernie-research/MEnvAgent` | Automated Docker environment construction for polyglot SWE tasks. | Environment construction, reuse, repair, and verifiable software worlds. |

## Guided Trajectories / Agent Data

| Folder | Source | What It Is | Useful For AIDF |
|---|---|---|---|
| `MC-Search` | `YennNing/MC-Search` | Multimodal agentic search benchmark with verified stepwise chains. | Guided retrieval trajectories, process rubrics, hop-wise evidence. |
| `Agent-Data-Protocol` | `neulab/agent-data-protocol` | Common protocol for agent trajectories, actions, observations, and SFT conversion. | Canonical trajectory interchange schema and adapter target. |
| `daVinci-Dev` | `GAIR-NLP/daVinci-Dev` | Agent-native mid-training data/pipeline for software engineering. | Contextually/environmentally native trajectories and tool/test evidence. |
| `ScaleCUA` | `OpenGVLab/ScaleCUA` | Cross-platform computer-use agent data, models, evaluation, and playground. | Human-agent GUI data pipeline, cross-platform action spaces. |
| `AgentFlow` | `lupantech/AgentFlow` | Planner/executor/verifier/generator agent loop with Flow-GRPO training. | Multi-module agent loop, trajectory-level reward propagation. |
| `TerminalTraj` | `multimodal-art-projection/TerminalTraj` | Dockerized terminal-agent trajectory generation. | Verified terminal trajectories and executable validation patterns. |

## Practical Reading Order

1. `Agent-Data-Protocol`: understand the common trajectory representation.
2. `Gaia2-ARE`: understand dynamic environment execution and action-level verification.
3. `MEnvAgent`: understand automated environment construction and reuse.
4. `CyberGym` and `BIRD-Interact`: understand executable verifier design in concrete domains.
5. `MC-Search`, `daVinci-Dev`, and `TerminalTraj`: understand guided/process trajectory data.
6. `OpenApps` and `ScaleCUA`: understand GUI/computer-use variants.
7. `AstaBench`, `MedAgentGym`, `SandboxEscapeBench`, and `CVE-Factory`: understand domain-specific, safety, and large-scale world generation patterns.

## First AIDF Adapter Candidates

Continue with dataset-level `Agent-Data-Protocol` approvals or promote the next
remaining inventory world into source-specific runtime wiring.

All current runtime family primitives now have a first concrete bridge:

- browser GUI
- trajectory/data
- terminal/sandbox
- external environment loop
- repository/CI
- formal proof
- scientific/device simulator
- mobile GUI/emulator

`Agent-Data-Protocol` is already the first source-specific trajectory/data
bridge, so it now acts as the common trace/evidence export layer for later
adapters. `TerminalTraj` is already the first source-specific terminal/sandbox
bridge, so it now acts as the command/file/validator evidence pattern for later
terminal and security worlds. `Gaia2-ARE` is already the first source-specific
external-loop bridge, so it now acts as the reset/step/event/validation evidence
pattern for later dynamic environments. `Swing-Bench` is already the first
source-specific repository/CI bridge, so it now acts as the checkout, patch,
test/CI, review, and generated-code gate pattern for later software-development
worlds. `AlgoVeri` is already the first source-specific formal-proof bridge, so it now
acts as the theorem/spec, proof edit, formal verifier diagnostic, timeout,
replay, and export-gate pattern for later proof worlds. `SimuHome` is already
the first source-specific scientific-simulator bridge, so it now acts as the
simulator reset, seed/replay, state/action, metric, cleanup, and export-gate
pattern for later scientific and device-state worlds. `UI-Venus-VenusBench-Mobile`
is already the first source-specific mobile GUI bridge, so it now acts as the
emulator, APK install, screenshot/accessibility, gesture, completion, cleanup,
privacy, and export-gate pattern for later mobile and cross-platform computer-use
worlds. `ScaleCUA` is already the second source-specific browser/GUI-family
bridge and the first cross-platform CUA bridge, so it now acts as the platform
config, model endpoint, screenshot/action trace, WebArenaLiteV2/AndroidWorld
evaluator, privacy, and export-gate pattern for later computer-use worlds.

The next decision is which remaining inventory world should receive the next
source-specific bridge, such as `MedAgentGym`, `CVE-Factory`, `AstaBench`,
`CausalGame`, `World-In-World`, `RedTeamCUA`, or `Vision2Web`.
