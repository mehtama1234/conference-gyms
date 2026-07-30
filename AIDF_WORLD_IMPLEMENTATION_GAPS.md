# AIDF World Implementation Gaps From Conference Worlds

This file converts the local conference-world review into implementation work for
AIDF. The source analysis is in `CONFERENCE_WORLD_ANALYSIS.md` and
`WORLD_ANATOMY_MAP.md`.

## 1. World Package Contract

AIDF should treat every benchmark world as a package with explicit runtime
semantics, not as a prompt bundle.

Required fields:

```text
world_id
domain
runtime substrate
initial state
observable state
hidden state, if any
allowed actions
tool contracts
reset protocol
task source
scenario generator
verifier stack
trace schema
cost policy
licensing/access constraints
```

Why:

`tau2-bench`, `BIRD-Interact`, `CausalGame`, `OpenApps`,
`UI-Venus-VenusBench-Mobile`, and `ScaleCUA` all define worlds through state,
actions, reset, tools, and verifiers.

## 2. Verifier Stack

AIDF needs multiple verifier strengths in one contract.

Verifier types:

```text
exact_oracle
unit_test_or_ci
formal_verifier
simulator_metric
state_inspection
browser_or_gui_evidence
multimodal_judge
expert_rubric
llm_judge_with_calibration
human_review
```

Why:

`VERINA` and `AlgoVeri` need formal proof verification. `Swing-Bench` needs CI.
`RealPDEBench` needs numerical metrics. `WebDevJudge`, `PhyWorldBench`, and
`CounselBench` need rubric/judge calibration. `MADQA` needs answer and citation
metrics.

## 3. Trace And Evidence Schema

AIDF traces should carry evidence, not just messages.

Required trace events:

```text
observation
reasoning step
tool/action proposal
tool/action execution
state delta
artifact creation
verifier signal
repair attempt
human/judge feedback
cost usage
final submission
```

Evidence attachments:

```text
file path
line range
database row/query
screenshot
video frame/time window
browser action
terminal command output
formal verifier error
CI log
citation document/page
human comment
rubric item
```

Why:

`MADQA`, `WebDevJudge`, `PhyWorldBench`, `TerminalTraj`, `daVinci-Dev`, and
`Agent-Data-Protocol` all show that the trace becomes the reusable asset for
grading, replay, training, and debugging.

## 4. Source-To-World Builder

AIDF should support a repeatable path from source documents or systems into world
packages.

Pipeline:

```text
source intake
domain object extraction
state variable extraction
action/tool extraction
constraint extraction
failure-mode extraction
success criterion extraction
hidden-fact/distractor extraction
verifier signal extraction
rubric extraction
scenario template generation
world package assembly
package validation
```

Why:

`Agent-Data-Protocol`, `daVinci-Dev`, `Swing-Bench`, `CounselBench`,
`WebDevJudge`, and `PhyWorldBench` all have data/sourcing pipelines that turn raw
material into benchmarkable tasks.

## 5. Runtime Substrate Adapters

AIDF needs a substrate abstraction for where the world runs.

Substrates:

```text
pure data task
terminal/filesystem
repository plus CI
database service
browser/web app
desktop OS
Android/mobile emulator
robotics/embodied simulator
scientific simulator
formal proof environment
protected enterprise data environment
```

Why:

`ScaleCUA`, `UI-Venus-VenusBench-Mobile`, `World-In-World`, `MedAgentGym`,
`RealPDEBench`, `VERINA`, `AlgoVeri`, and `Swing-Bench` all require different
execution substrates but the harness should see the same world-player interface.

## 6. Difficulty And Variation Controls

AIDF should generate harder worlds by controlling state, dependency, noise, hidden
facts, and perturbations.

Variation knobs:

```text
longer dependency graph
more hidden state
more distractors
noisy observations
async waits
stakeholder interruptions
environment shift
task ambiguity
GUI popups/crashes
limited action budget
limited observation budget
larger artifact set
cross-document/cross-system dependencies
```

Why:

`CausalGame`, `SimuHome`, `MADQA`, `UI-Venus-VenusBench-Mobile`,
`RedTeamCUA`, and `BIRD-Interact` show that long horizon is about dependencies
and uncertainty, not longer wording.

## 7. Human And Expert Feedback Loop

AIDF should make human feedback a first-class input to rubric creation and judge
calibration.

Required support:

```text
expert comment ingestion
rubric dimension mining
failure taxonomy mining
inter-rater reliability
judge-vs-human calibration
adversarial case generation
review queue
appeal/override trail
```

Why:

`CounselBench`, `WebDevJudge`, `MADQA`, and AstaBench-style scorer workflows show
that open-ended work needs calibrated expert feedback, not only golden answers.

## 8. Harness-To-Training Export

AIDF should export traces and verifier signals into trainable data.

Exports:

```text
raw trace
normalized trace
agent-data-protocol compatible trace
trainable transcript
reward-labeled trajectory
repair dataset
rubric-labeled examples
hard-negative/adversarial examples
```

Why:

`AgentFlow`, `THOR`, `MedAgentGym`, `TerminalTraj`, `daVinci-Dev`, and
`Agent-Data-Protocol` show that benchmark worlds are also data factories for
training, repair, and policy improvement.

## Recommended Implementation Order

1. Define the canonical `WorldPackage` schema.
2. Define `WorldTrace` plus evidence attachments.
3. Add runtime substrate adapters for terminal, web/browser, repo+CI, formal
   verifier, and external gym wrappers.
4. Add verifier stack contracts.
5. Add source-to-world extraction outputs.
6. Add variation/difficulty controls.
7. Add rubric mining and human calibration records.
8. Add trace export for training and external protocols.

