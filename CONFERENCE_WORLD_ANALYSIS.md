# ICML/ICLR Conference World Analysis

This folder is the local working area for conference-linked agent worlds,
benchmarks, simulators, trajectory datasets, verifier suites, and world-building
systems.

The purpose is not only to run these repos. The purpose is to reverse-engineer
how strong benchmarks become executable worlds, then map those patterns back to
AIDF source intake, domain packs, world factory, harness, verifiers, traces, and
failure learning.

## Current AIDF Adapter Coverage

The machine-readable readiness report is
`conference-world-adapter-readiness.json`. The current report has 66 adapter
artifacts, 33 local world package projections, zero projection errors, and complete runtime-family
contract-smoke coverage: 8 adapter families, 8 family contract smokes, and no
missing family ids. Seventeen worlds now have source-specific package projections;
the remaining 16 are valid inventory projections that still need source-specific
runtime wiring. OpenApps, Agent-Data-Protocol, TerminalTraj, Gaia2-ARE,
Swing-Bench, AlgoVeri, SimuHome, UI-Venus-VenusBench-Mobile, MC-Search, and
ScaleCUA, plus the parallel second-bridge batch `CyberGym`, `BIRD-Interact`,
`VERINA`, and `RealPDEBench`, now have no-heavy-run adapter smoke traces and
evidence/gate receipts.
Agent-Data-Protocol
also has the first heavy-run receipt candidate for local fixture data-pipeline
execution, with local fixture/schema validation passing 289 checks in a temporary
`litellm` execution environment, plus a policy/export decision receipt that
allows local fixture evidence only for adapter contract validation. Hosted
dataset conversion, downstream reuse, and SFT training export remain blocked
until dataset-level license, privacy, split-integrity, and export approvals
exist. ADP also has a dataset review matrix that repeats those blocked decisions
per dataset instead of treating one sample lane as enough, plus concrete blocked
approval receipt templates for license, privacy, split integrity, hosted
conversion, and training export. The generated
`agent-data-protocol-approval-overrides.template.json` file is the editable
operator input for turning reviewed receipts into CLI overrides. Their
remaining milestones are clearing explicit heavy-run blockers before claiming
browser benchmark execution, full dataset conversion, terminal Docker execution,
dynamic environment execution, repository checkout, dependency install, CI
execution, formal toolchain install, theorem split, verifier execution,
simulator startup, metric execution, mobile emulator execution, APK install,
screenshot/accessibility capture, gesture execution, validator normalization,
split-integrity, sandbox, replay, generated-code review, cleanup, model serving,
cross-platform CUA platform setup, WebArenaLiteV2 launcher assets, privacy
review, or training-export readiness.

In plain terms, AIDF now has a named adapter contract for every kind of runtime
shape present in the local conference worlds. These contracts do not claim that
the heavy benchmark runs have been executed. They define what AIDF must capture
when those runs are wired: reset, observation, action, verifier signal, trace,
training export gates, required evidence, and known blockers.

| Priority | Adapter family | Worlds | What it means |
| --- | --- | --- | --- |
| 1 | `browser-gui-world-adapter` | `MiniAppBench`, `OpenApps`, `RedTeamCUA`, `ScaleCUA`, `Vision2Web`, `WebDevJudge` | Browser or web-app tasks need page/app reset, screenshot/DOM observation, GUI actions, browser/verifier evidence, and trace export. |
| 2 | `trajectory-data-world-adapter` | `CounselBench`, `DeepSynth`, `MADQA`, `daVinci-Dev`; first target `Agent-Data-Protocol` and second bridge `MC-Search` are source-specific | Data and trace repos need import/export, schema validation, labels/rubrics, split controls, and training-export gates. |
| 3 | `terminal-sandbox-world-adapter` | `CVE-Factory`, `CyberGym`, `MedAgentGym`; first target `TerminalTraj` is source-specific | Terminal and sandbox worlds need isolated filesystem/container reset, command traces, file diffs, validator logs, and sandbox receipts. |
| 4 | `external-gym-loop-adapter` | `AgentFlow`, `PhyWorldBench`, `SandboxEscapeBench`, `THOR`; first target `Gaia2-ARE` is source-specific | External environments already have their own loop; AIDF needs to bridge reset/step/observe/action/verify into common traces. |
| 5 | `repository-ci-world-adapter` | First target `Swing-Bench` is source-specific | Code-repo worlds need pinned checkout, patch replay, tests/CI, review artifacts, diff evidence, and executable verifier receipts. |
| 6 | `formal-proof-world-adapter` | `VERINA`; first target `AlgoVeri` is source-specific | Proof worlds need theorem/proof-state reset, tactic or proof-edit actions, prover diagnostics, timeout policy, and formal verifier receipts. |
| 7 | `scientific-simulator-world-adapter` | `CausalGame`, `RealPDEBench`, `World-In-World`; first target `SimuHome` is source-specific | Science worlds need simulator reset, state/action schemas, seed/replay evidence, metrics, constraints, calibration, and claim boundaries. |
| 8 | `mobile-gui-world-adapter` | `UI-Venus-VenusBench-Mobile` | Mobile GUI worlds need emulator snapshots, app install state, screenshots/accessibility, gestures, completion checks, and cleanup receipts. |

The next engineering move is to replace inventory-only projections inside each
family with source-specific runtime adapters, starting from the highest-reuse
families.

### Source-Specific Adapter Migration Roadmap

The readiness report also chooses one first local world per adapter family. That
choice is not a statement that the other worlds matter less. It is the smallest
representative target for turning each family contract into concrete code.

| Priority | Adapter family | First source-specific target | Status | Why this target comes first |
| --- | --- | --- | --- | --- |
| 1 | `browser-gui-world-adapter` | `OpenApps` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; heavy-run blockers remain. | Configurable UI reset and browser action traces without needing mobile or VM control first. |
| 2 | `trajectory-data-world-adapter` | `Agent-Data-Protocol` | Source-specific projection, no-heavy-run adapter smoke, evidence/gate receipts, and first heavy-run receipt candidate complete; local fixture/schema validation passes, while full hosted conversion, split, privacy, license, and export blockers remain. | Baseline trajectory interchange format used by other trace and training-export adapters. |
| 2b | `trajectory-data-world-adapter` | `MC-Search` | Second source-specific bridge complete; Hugging Face dataset download, KB embedding build, model/API credentials, agent run, evaluator run, judge calibration, and export blockers remain. | Multimodal search trajectories test whether the trajectory/data family supports retrieval evidence and structured subquestion chains beyond ADP schema conversion. |
| 2c | `browser-gui-world-adapter` | `ScaleCUA` | Second browser/GUI-family bridge and first non-trajectory second bridge complete; model serving, browser/VM/Android platform setup, WebArenaLiteV2 launcher assets, evaluator execution, privacy review, and export blockers remain. | Cross-platform CUA tests whether the browser/GUI family can represent screenshot/action traces, platform setup, model endpoint receipts, and evaluator outputs beyond browser-only OpenApps tasks. |
| 2d | `terminal-sandbox-world-adapter` | `CyberGym` | Parallel second-bridge batch complete; dataset/server data, PoC server, Docker/binary runner, firewall, verifier execution, and export blockers remain. | Real security tasks test whether terminal/sandbox contracts handle generated PoCs, pre/post patch verifier logs, and network/firewall receipts. |
| 2e | `external-gym-loop-adapter` | `BIRD-Interact` | Parallel second-bridge batch complete; PostgreSQL services, ground-truth/testcase access, LLM provider config, evaluation execution, and export blockers remain. | Interactive database/user-simulator tasks test user turns, DB state, SQL actions, and executable test-case verifier receipts. |
| 2f | `formal-proof-world-adapter` | `VERINA` | Parallel second-bridge batch complete; Lean toolchain, Prefect runtime, model provider, benchmark execution, proof replay, and export blockers remain. | Lean verifiable-code tasks test code/spec/proof artifact chains beyond AlgoVeri's cross-tool format. |
| 2g | `scientific-simulator-world-adapter` | `RealPDEBench` | Parallel second-bridge batch complete; HF datasets, checkpoints, environment setup, inference/evaluation, metric reports, and export blockers remain. | Paired real/sim PDE forecasting tests scientific metrics, dataset/checkpoint receipts, and sim-to-real boundary evidence. |
| 3 | `terminal-sandbox-world-adapter` | `TerminalTraj` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; Docker/runtime blockers remain. | Terminal trajectory normalization before higher-risk security benchmark execution. |
| 4 | `external-gym-loop-adapter` | `Gaia2-ARE` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; runtime lifecycle/replay blockers remain. | Clear external reset/step/observe/action environment-loop target. |
| 5 | `repository-ci-world-adapter` | `Swing-Bench` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; repo checkout, dependency, CI, generated-code, and export blockers remain. | Local repository/CI world for checkout, patch, test, and review evidence. |
| 6 | `formal-proof-world-adapter` | `AlgoVeri` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; formal toolchain, theorem split, verifier execution, timeout/replay, and export blockers remain. | Proof contracts across multiple formal toolchains. |
| 7 | `scientific-simulator-world-adapter` | `SimuHome` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; simulator startup, dependency, seed/replay, metric, cleanup, license, and export blockers remain. | Explicit simulator/device state model for reset, action, metrics, and replay. |
| 8 | `mobile-gui-world-adapter` | `UI-Venus-VenusBench-Mobile` | Source-specific projection, no-heavy-run adapter smoke, and evidence/gate receipts complete; emulator startup, Android SDK/AVD setup, APK install, screenshot/accessibility capture, gesture execution, completion verification, cleanup, privacy, and export blockers remain. | Local mobile GUI world for emulator state, gestures, screenshots, and completion checks. |

Each family follows the same four implementation milestones:

1. Replace the inventory projection for the first target with a source-specific
   runtime projection.
2. Run one no-heavy-run adapter smoke for that target.
3. Prove evidence capture and training/export gate receipts before any heavy
   benchmark run.
4. Clear the explicit heavy-run blockers before claiming benchmark execution
   readiness.

## Current Local Repos

### Executable Agent Worlds

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `CyberGym` | ICLR 2026 | Real vulnerability/codebase world | Source description plus codebase becomes executable PoC task; verifier runs pre/post patch. |
| `Gaia2-ARE` | ICLR 2026 | Dynamic async agent environments | Independent environment events, temporal constraints, action-level verifiers. |
| `BIRD-Interact` | ICLR 2026 | Interactive database world | User simulator, DB exploration, SQL/CRUD actions, executable checks. |
| `MedAgentGym` | ICLR 2026 | Biomedical coding/data-science world | Domain-specific sandbox tasks, feedback, ground truth, trajectory generation. |
| `AstaBench` | ICLR 2026 | Scientific research-agent suite | Tool/cost normalization, scientific workflows, standardized scoring. |
| `SandboxEscapeBench` | ICML 2026 | Container security CTF world | Nested sandbox, shell agent, flag/verifier, infra-risk evaluation. |
| `CVE-Factory` | ICML 2026 | Security world generator | CVE metadata becomes runnable vulnerability environments and training tasks. |
| `MEnvAgent` | ICML 2026 | Software environment construction | Automated Docker environment setup, repair, validation, reuse. |
| `SimuHome` | ICLR 2026 | Smart-home simulator | Matter-style device APIs, time acceleration, environmental variables, scheduled actions. |
| `RedTeamCUA` | ICLR 2026 | Hybrid web/OS adversarial CUA sandbox | VM plus Docker web apps, indirect prompt injection, CIA-style security goals. |
| `CausalGame` | ICML 2026 | Interactive scientific discovery game | Agent designs experiments under confounding, censoring, noisy measurements. |
| `tau2-bench` | ICML 2026 | Shared user-agent tool world | User and agent both affect state; policy, tools, tasks, user simulator. |
| `World-In-World` | ICLR 2026 | Closed-loop embodied world-model benchmark | Action API, planning, generated future observations, task success as world-model metric. |

### Software, Code, And Verification Worlds

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `VERINA` | ICLR 2026 | Lean verifiable-code benchmark | Code/spec/proof chain; modular scoring of intermediate artifacts. |
| `AlgoVeri` | ICML 2026 | Cross-tool verified-code benchmark | Same algorithm contracts across Dafny, Verus, and Lean reveal environment effects. |
| `Swing-Bench` | ICLR 2026 | CI-driven GitHub issue arena | Submitter/reviewer agents, retrieval over codebase, CI as executable verifier. |
| `Vision2Web` | ICML 2026 | Visual website development benchmark | Hierarchical web tasks, Playwright/GUI verification, visual and functional scoring. |
| `MiniAppBench` | ICML 2026 | Interactive HTML app benchmark | Browser automation explores generated apps and scores intention/static/dynamic behavior. |
| `WebDevJudge` | ICLR 2026 | Web-development judge benchmark | Static and interactive judge evaluation with human preference labels and rubrics. |
| `EditBench` | ICLR 2026 | Mentioned, not cloned yet | Real instructed code edits with cursor/highlight context. |
| `DRPBench` | ICML 2026 | Mentioned, not cloned yet | Concurrent-code data-race prediction and fine-grained diagnostic labels. |

### GUI, Mobile, And Computer-Use Worlds

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `OpenApps` | ICLR 2026 | Configurable UI app benchmark | Environment variation as robustness metric. |
| `ScaleCUA` | ICLR 2026 | Cross-platform CUA data/eval | Human-agent GUI data pipeline and cross-platform action spaces. |
| `UI-Venus-VenusBench-Mobile` | ICML 2026 | Mobile GUI benchmark | User-intent task design, environment variation, capability diagnostics. |
| `RedTeamCUA` | ICLR 2026 | Hybrid web/OS adversarial GUI sandbox | Security under GUI/web environment-originated instructions. |

### Science, Physical, And Multimodal Worlds

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `RealPDEBench` | ICLR 2026 | Paired real/sim physical-system benchmark | Real measurements plus simulations, sim-to-real transfer, scientific metrics. |
| `PhyWorldBench` | ICLR 2026 | Text-to-video physical realism benchmark | Physical-principle taxonomy, human plus model-based evaluation. |
| `AstaBench` | ICLR 2026 | Scientific research-agent benchmark | Research task suite, tools, cost controls, agent comparison. |
| `MedAgentGym` | ICLR 2026 | Biomedical coding world | Executable biomedical reasoning tasks and training trajectories. |
| `CausalGame` | ICML 2026 | Causal discovery world | Active experiments under hidden bias and noisy observation. |

### Trajectory And Process Data

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `Agent-Data-Protocol` | ICLR 2026 | Agent trajectory interchange | Common action/observation/trajectory protocol. |
| `MC-Search` | ICLR 2026 | Multimodal search trajectories | Verified subquestion chains, evidence attribution, process supervision. |
| `TerminalTraj` | ICML 2026 | Dockerized terminal trajectories | Large verified terminal trajectories with executable validation. |
| `daVinci-Dev` | ICML 2026 | Software-agent mid-training data | Tool/test/context trajectories for code agents. |
| `AgentFlow` | ICLR 2026 | Planner/executor/verifier loop | Process reward propagation and modular agent optimization. |
| `THOR` | ICLR 2026 | Tool-integrated math/code reasoning | Step-level tool feedback plus trajectory-level RL. |
| `DeepSynth` | ICLR 2026 | Deep information synthesis benchmark | Multi-source long-horizon synthesis tasks with structured scoring. |
| `MADQA` | ICML 2026 | Document-agent QA benchmark | Accuracy-effort tradeoff, PDF navigation, strategic vs brute-force search. |

### Rubric, Judge, And Expert Feedback Benchmarks

| Repo | Conference signal | World type | What matters for AIDF |
| --- | --- | --- | --- |
| `CounselBench` | ICLR 2026 | Expert mental-health evaluation | Human expert rubrics, adversarial questions, LLM-judge failure analysis. |
| `WebDevJudge` | ICLR 2026 | Judge reliability benchmark | Human labels, structured rubrics, static and interactive evaluation. |
| `MiniAppBench` | ICML 2026 | Agentic app evaluator | Exploratory testing and multidimensional scoring without one rigid oracle. |
| `PhyWorldBench` | ICLR 2026 | Physical realism rubric | Physics category taxonomy and model/human scoring. |
| `DeepSynth` | ICLR 2026 | Synthesis scoring | Long-horizon information gathering and structured answer evaluation. |

## Other Mentioned Worlds Not Yet Local

These were mentioned in the ICML/ICLR analysis, but are not currently cloned as
local repos in this folder.

| Name | Likely role | Status |
| --- | --- | --- |
| `EditBench` | Real-world instructed code editing | Paper/notes identified; local repo not added. |
| `DRPBench` | Concurrent-code comprehension/data-race benchmark | Paper/notes identified; local repo not added. |
| `FlashWorld` | Fast 3D scene generation | More generative model than agent runtime. |
| `ImageDoctor` | Grounded image-quality diagnosis | Rubric/judge pattern more than executable agent world. |
| `FRABench` / `UFEval` | Fine-grained evaluation generalization | Rubric/eval-family pattern. |
| `VenusBench-Mobile` | Cloned through `UI-Venus-VenusBench-Mobile` branch | Local. |
| `SAW-Bench`, `dWorldEval`, `EcoVLA`, `BehaviorVLA`, `VectorWorld`, `PanoWorld-X` | Embodied/robotics/world-model evaluation | Mentioned in notes; not all have verified local repos yet. |

## What To Extract From Every World

Use this template for each deeper analysis.

```text
repo
conference / paper
domain
world type
state model
action model
observation model
task source
task generation method
reset model
runtime dependencies
verifier model
reward / score model
trace format
human / expert evidence
failure taxonomy
environment variation / chaos
security / safety boundaries
cost / latency tracking
data licensing / access
what runs locally
what is blocked
AIDF equivalent package
AIDF gap
```

## Cross-Repo World Design Patterns

### 1. Worlds Are State Machines, Not Prompts

The strongest repos define mutable state, action surfaces, observations, reset,
and verifiers. Examples: `SimuHome`, `BIRD-Interact`, `tau2-bench`,
`RedTeamCUA`, `CyberGym`, `SandboxEscapeBench`.

AIDF mapping:

```text
EvaluationWorld / WorkWorldInstance
ToolSurface
StateStore
ResetSnapshot
VerifierSet
TraceContract
```

### 2. Verifiers Are Executable Where Possible

Security, code, database, formal-methods, and web tasks lean heavily on
executable checks: tests, CI, SQL execution, Lean/Dafny/Verus, browser
automation, sandbox flags, pre/post patch reproduction.

AIDF mapping:

```text
aidf-verifiers
aidf-agent-evaluation-core score receipts
harness scorecard
state diff checks
artifact checks
policy checks
```

### 3. Human Judgment Is Still Needed For Open-Ended Work

`CounselBench`, `WebDevJudge`, `MiniAppBench`, `PhyWorldBench`, `DeepSynth`, and
`MADQA` show that open-ended domains need rubrics, human labels, expert
annotations, or judge calibration. The key is not replacing verifiers with
judges; it is combining deterministic checks with structured expert judgment.

AIDF mapping:

```text
rubric dimensions
expert traces
human review gates
reviewer calibration
judge evidence packets
```

### 4. World Difficulty Comes From Controlled Variation

Several worlds vary UI layout, mobile state, tool behavior, hidden causal
structure, device timing, adversarial injections, or data consistency.

AIDF mapping:

```text
chaos facets
coverage matrix
negative profiles
variation families
Pass@K difficulty gates
```

### 5. Trajectories Are Training And Debugging Assets

`Agent-Data-Protocol`, `TerminalTraj`, `MC-Search`, `daVinci-Dev`, `THOR`, and
`AgentFlow` show that the path matters: action, observation, intermediate
evidence, tool feedback, corrections, and final result.

AIDF mapping:

```text
reasoning run artifact
world player trace
harness experiment ledger
expert trace contracts
failure attribution
training bridge receipts
```

### 6. Source-To-World Generation Is A First-Class Capability

`CVE-Factory`, `MEnvAgent`, `TerminalTraj`, `MiniAppBench`, and `Vision2Web`
show different ways to transform source material into runnable work:
CVE metadata to security tasks, repos to Docker environments, terminal tasks to
validated trajectories, user requests to interactive apps, prototypes to web
tasks.

AIDF mapping:

```text
source intake
building blocks
domain representation
world factory
enterprise package
AgentWorks / Docker World export
```

## AIDF Implementation Implications

The existing AIDF codebase already has many matching pieces:

- `packages/aidf-world-factory`: work-world generation, AgentWorks adapters,
  source-to-world building blocks, domain projection, runtime matrix receipts.
- `packages/aidf-enterprise`: company graph, connector datasets, evidence
  assembly, task coverage, failure attribution.
- `packages/aidf-deployable-project`: source-to-world summary and enterprise
  eval bridge.
- `packages/aidf-agent-evaluation-core`: scorecards, source-to-world eval chain,
  external gym adapter work.
- `packages/aidf-harness`: experiment plans, ledgers, run/evidence closure.
- `packages/aidf-verifiers`: deterministic and rubric verifier surfaces.
- `library/domain-packs`: mini-world examples with tasks, policies, chaos,
  evidence requirements, HIL gates, and verifiers.

The next practical step is not to design one more abstract world model. It is to
analyze these repos one by one and produce adapter/readiness specs.

## Recommended Deep-Dive Order

1. `Agent-Data-Protocol`: trajectory schema target.
2. `tau2-bench`: enterprise shared-state/user-agent world.
3. `BIRD-Interact`: database-agent world with clarification and CRUD.
4. `SimuHome`: time and async state world.
5. `RedTeamCUA`: adversarial GUI/web/OS world.
6. `MEnvAgent`: Docker environment construction.
7. `CyberGym` and `CVE-Factory`: security source-to-world generation.
8. `Vision2Web` and `MiniAppBench`: generated artifact plus browser verifier.
9. `AstaBench`, `MedAgentGym`, `CausalGame`, `RealPDEBench`: scientific worlds.
10. `CounselBench`, `WebDevJudge`, `PhyWorldBench`, `DeepSynth`, `MADQA`:
    rubric, judge, and expert feedback mining.

For each, produce:

```text
world anatomy
run/readiness status
adapter target
AIDF concept mapping
implementation gap
```
