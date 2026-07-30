# Conference World Anatomy Map

This map is the working extraction layer over the local ICML/ICLR world repos in
this folder. It answers a simple question for each world:

```text
What is the world made of, how does an agent act in it, how is success checked,
and what should AIDF copy or adapt?
```

This is intentionally implementation-facing. The companion inventory is
`CONFERENCE_WORLD_ANALYSIS.md`; this file goes one level deeper into mechanics.

## Anatomy Template

Each world should eventually be described with these fields:

```text
state model
action model
observation model
task source / generation
reset model
runtime dependencies
verifier / score model
trace format
human / expert evidence
difficulty / chaos
AIDF mapping
implementation gap
```

## Priority Worlds

### tau2-bench

Local repo: `tau2-bench`

World type: customer-service shared-state tool world.

Confirmed local evidence:

- `README.md` defines domains, policies, tools, tasks, text/voice modes, user
  simulator, and optional Gymnasium interface.
- `src/tau2` owns the main runtime code.
- `data/tau2` contains domain/task data.
- `tests/test_domains` and `tests/test_gym` show this is intended to be
  executable and testable.

Anatomy:

```text
state model:
  domain-owned customer-service state, such as airline, retail, telecom, mock,
  and banking knowledge records.

action model:
  agent uses domain tools; simulated user may also use user tools in dual-control
  settings.

observation model:
  conversational turns, tool outputs, user responses, and domain state feedback.

task source:
  domain task definitions plus policy documents and knowledge assets.

reset model:
  per-task/domain state reset implied by evaluation harness and task fixtures.

runtime:
  Python/uv package, optional voice and knowledge extras, optional gym extra.

verifier / score:
  task/domain graders evaluate whether the final shared state and conversation
  satisfy policy and goal constraints.

trace:
  trajectories are central; repo includes evaluation/traj language and leaderboard
  submission flow.

difficulty:
  shared control, user communication, policy following, knowledge retrieval,
  tool correctness, and updated grading versions.
```

AIDF mapping:

```text
EvaluationWorld:
  customer-service world with shared mutable state.

Company graph / connector simulators:
  maps closely to enterprise connector state plus user/stakeholder simulator.

Harness:
  agent/user/tool trajectory should normalize into AIDF world-player trace.

Verifier:
  state-change and policy-compliance verifiers.
```

AIDF gap:

```text
Need a tau-style dual-control enterprise world adapter:
  user simulator can mutate state
  agent tools mutate same state
  verifier checks both final state and policy/process trace
```

### BIRD-Interact

Local repo: `BIRD-Interact`

World type: interactive database/text-to-SQL world.

Confirmed local evidence:

- `README.md`, `mini_interact/README.md`, and `BIRD-Interact-ADK/README.md`
  describe the benchmark variants.
- `BIRD-Interact-ADK/docker-compose.yml` and `env/docker-compose.yml` show
  containerized database/runtime setup.
- `BIRD-Interact-ADK/db_environment`, `user_simulator`, `system_agent`, and
  `orchestrator` expose the core world components.
- `evaluation/src` and `evaluation/run` contain evaluation machinery.

Anatomy:

```text
state model:
  relational database plus knowledge/context needed to answer or modify data.

action model:
  SQL, CRUD-style database operations, exploration, clarification questions,
  and interaction with user simulator/system agent.

observation model:
  query results, execution errors, user-simulator responses, and environment
  feedback.

task source:
  database tasks, personalized/knowledge-based mini-interact tasks, examples.

reset model:
  Docker/database environment reset around task execution.

runtime:
  Docker Compose plus Python orchestrator/evaluation packages.

verifier / score:
  executable SQL/task checks, interaction outcome checks, and evaluation scripts.

trace:
  conversation/interaction traces across agent, user simulator, DB, and system.

difficulty:
  ambiguity, clarification, DB exploration, execution errors, CRUD state changes,
  and memory/interaction scaling.
```

AIDF mapping:

```text
Enterprise database world:
  warehouse/query connector simulator, stateful DB, user clarifications.

Source intake:
  schema/docs/task requirements become state variables, actions, constraints,
  verifier signals.

Verifier:
  SQL result checks, state-diff checks, query/tool trace checks.
```

AIDF gap:

```text
Need a first-class database-world package shape:
  schema snapshot
  seed data
  allowed SQL/CRUD tools
  clarification policy
  executable verifier
  reset snapshot
```

### SimuHome

Local repo: `SimuHome`

World type: temporal smart-home simulator.

Confirmed local evidence:

- `README.md` says the simulator is Matter-grounded, time accelerated, and
  supports scheduled workflows.
- `data/benchmark` contains benchmark JSON episodes.
- `src/simulator`, `src/agents`, `src/clients`, and `prompts` expose simulator,
  agent, API client, and task prompt pieces.
- `src/agents/tools.py` exposes device/environment tools for agents.

Anatomy:

```text
state model:
  smart-home devices plus environmental variables such as temperature and
  humidity evolving over simulated time.

action model:
  device API calls, add/remove devices, scheduling, tick/time controls, and
  finish answer.

observation model:
  tool responses, device/environment state, time progression, and task feedback.

task source:
  benchmark JSON episodes organized by question type, feasibility, and seed.

reset model:
  per-episode simulator initialization from benchmark seed/config.

runtime:
  uv/Python simulator server and CLI.

verifier / score:
  task feasibility and goal satisfaction over state/time.

trace:
  agent steps, tool calls, raw responses, and trajectory memory are represented
  in agent strategy code.

difficulty:
  time, asynchronous effects, scheduling, feasibility/infeasibility, and
  environment dynamics after actions.
```

AIDF mapping:

```text
Long-horizon EvaluationWorld:
  async waits, timers, scheduled actions, state variables changing after action.

Enterprise analogy:
  calendar deadlines, SLA timers, ticket aging, stakeholder response windows,
  queued workflow actions.
```

AIDF gap:

```text
Need stronger async/time semantics in AIDF worlds:
  virtual clock
  scheduled future action
  state transition after delay
  verifier over temporal state, not only final text
```

### RedTeamCUA

Local repo: `RedTeamCUA`

World type: adversarial hybrid web/OS computer-use sandbox.

Confirmed local evidence:

- `README.md` describes VM OS plus Docker web replicas and RTC-Bench.
- `goals/adv` and `goals/benign` contain paired adversarial/benign task JSON.
- `adv/` contains platform-specific adversarial injection assets.
- `desktop_env/evaluators`, `desktop_env/providers`, and `desktop_env/server`
  expose execution and evaluation surfaces.
- `evaluation_examples` contains task suites.

Anatomy:

```text
state model:
  OS desktop state plus web application state in Reddit, OwnCloud, RocketChat,
  or related replicated platforms.

action model:
  computer-use actions over browser/OS plus optional platform setup/injection
  scripts.

observation model:
  screenshots, accessibility trees, GUI state, web content, files, and task
  environment responses.

task source:
  benign task plus adversarial injection scenario, with CIA security objective.

reset model:
  VM/cloud/local sandbox plus web platform setup per scenario.

runtime:
  Python, VM/AWS or VMware setup, Docker web services, CUA agent wrappers.

verifier / score:
  evaluators check security violations and task outcomes.

trace:
  CUA action trajectories through desktop/web environment.

difficulty:
  indirect prompt injection, hybrid web/OS context, decoupled vs end-to-end
  navigation, confidentiality/integrity/availability violations.
```

AIDF mapping:

```text
Chaos / safety world:
  environment-originated adversarial content, policy gates, GUI action trace,
  sandboxed execution, security verifier.

Enterprise analogy:
  malicious email, poisoned ticket, adversarial document, unsafe instruction in
  Slack/Teams/SharePoint/CRM.
```

AIDF gap:

```text
Need explicit environment-originated instruction policy:
  source trust labels
  adversarial content locations
  allowed/forbidden action set
  safety verifier over trace and state mutation
```

### MEnvAgent

Local repo: `MEnvAgent`

World type: automated software environment construction and validation.

Confirmed local evidence:

- `README.md`, `menvagent/README.md`, and `curation/README.md` define the
  environment-construction system.
- `curation/swe_task_crawling` shows source/task acquisition.
- `menvagent` is the package that builds or repairs environments.

Anatomy:

```text
state model:
  source repository, dependency files, runtime environment, task metadata, and
  validation state.

action model:
  inspect project, infer dependencies, build Docker/runtime env, run tests,
  repair setup.

observation model:
  build logs, install errors, test results, dependency conflicts, validation
  output.

task source:
  software engineering tasks crawled/curated from repositories/issues.

reset model:
  container/environment rebuild and rerun.

runtime:
  Python plus Docker/environment tooling.

verifier / score:
  whether the generated environment can run the task/tests reliably.

trace:
  setup, repair, execution, and validation logs.

difficulty:
  polyglot dependencies, stale packages, missing setup docs, environment drift.
```

AIDF mapping:

```text
Source-to-world factory:
  source repo -> environment spec -> executable world -> validation receipt.

Software domain pack:
  dependency conventions, test commands, verifier obligations, repair policy.
```

AIDF gap:

```text
Need environment construction as a formal world-factory stage:
  source intake does not stop at task extraction
  it must produce runnable environment setup and verifier readiness
```

### CyberGym

Local repo: `CyberGym`

World type: real vulnerability/codebase world.

Confirmed local evidence:

- `README.md` describes vulnerability-analysis benchmark behavior.
- `src/cybergym` contains the package.
- `examples/agents` and `scripts/server_data` indicate agent examples and
  benchmark data/server support.
- `pyproject.toml` defines package runtime.

Anatomy:

```text
state model:
  vulnerable codebase, vulnerability description, pre/post patch versions,
  tests or proof-of-concept artifacts.

action model:
  inspect code, write exploit/PoC test, run code/tests.

observation model:
  source files, compiler/test output, sanitizer/runtime errors, verifier output.

task source:
  real vulnerabilities across projects.

reset model:
  repository checkout/environment reset around vulnerability instance.

runtime:
  Python package plus project-specific build/test environments.

verifier / score:
  executable PoC should reproduce vulnerability on pre-patch and not on
  post-patch.

trace:
  agent coding/test trajectory and generated PoC artifact.

difficulty:
  codebase exploration, vulnerability reasoning, exploit construction, build
  variability, security dual-use constraints.
```

AIDF mapping:

```text
Security source-to-world:
  advisory/source record + repo snapshot -> executable security task.

Verifier:
  pre/post condition checks are exactly the kind of hard verifier AIDF should
  preserve.
```

AIDF gap:

```text
Need pre/post-state verifier contracts:
  vulnerable-before / fixed-after
  exploit or regression artifact
  safety policy around generated exploit handling
```

### CVE-Factory

Local repo: `CVE-Factory`

World type: large-scale security world generator.

Confirmed local evidence:

- `README.md` and `docs` describe the pipeline.
- `cve_tasks` contains large task collections.
- `original_cves_md` stores source CVE material.
- `orchestrator`, `agents`, and `skills/cve-test-generator` expose generation
  and evaluation mechanics.
- `dev-env/docker-compose.yaml` and `dev-env/Dockerfile` show executable
  environment support.

Anatomy:

```text
state model:
  CVE source documents, repo/task environments, generated tests, task metadata,
  validation artifacts.

action model:
  generate task, build environment, run agent/test-generator, validate.

observation model:
  CVE text, repository/build output, generated tests, validation logs.

task source:
  sparse CVE metadata and original vulnerability descriptions.

reset model:
  Docker development environment and task-specific runnable artifacts.

runtime:
  orchestrator, agents, skills, Docker-in-Docker style dev environment.

verifier / score:
  correctness/fidelity of generated executable CVE tasks and tests.

trace:
  generation pipeline and agent/test-generator outputs.

difficulty:
  sparse source descriptions, environment setup, vulnerability fidelity, scale,
  and cheat/leak detection.
```

AIDF mapping:

```text
World generation:
  source intake -> building blocks -> runnable world package -> verifier.

Enterprise analogy:
  sparse SOP/ticket/policy source -> generated enterprise task with verifiable
  expected state.
```

AIDF gap:

```text
Need source-to-world generation provenance:
  source span
  extracted task
  generated environment
  verifier
  quality/cheat/fidelity checks
```

### Vision2Web

Local repo: `Vision2Web`

World type: hierarchical visual website development benchmark.

Confirmed local evidence:

- `README.md` defines Level 1 static webpage, Level 2 interactive frontend, and
  Level 3 full-stack website tasks.
- `vision2web/core/sandbox.py` manages Docker task isolation.
- `vision2web/evaluation/functional_tester.py` uses Claude Code plus
  `playwright-cli` for structured workflows.
- `vision2web/evaluation/prompts.py` defines visual and functional judge
  prompts and states that real user interactions should drive state changes.
- `vision2web/inference/adapters` includes agent framework adapters.

Anatomy:

```text
state model:
  generated web project files, running app state, browser state, screenshots,
  prototypes, workflow nodes.

action model:
  coding agent edits project; evaluation agent uses browser actions such as
  click, fill, select, keyboard, screenshot.

observation model:
  files, build output, browser DOM/accessibility snapshot, screenshots, URL and
  page state.

task source:
  visual prototypes plus textual requirements across web hierarchy levels.

reset model:
  Docker sandbox per generated project/task.

runtime:
  Python, Docker, Playwright CLI, optional agent CLIs.

verifier / score:
  visual score plus functional workflow score.

trace:
  agent logs, browser action workflow, screenshots, per-node results.

difficulty:
  long-horizon full-stack implementation, responsive design, visual fidelity,
  functional workflows, state continuity across browser steps.
```

AIDF mapping:

```text
Artifact world:
  generated app is the world artifact; browser verifier executes behavior.

Harness:
  compare candidate implementation through functional and visual scorecards.
```

AIDF gap:

```text
Need generated-artifact worlds:
  world can be a produced app/document/report, not only a preexisting simulator
  verifier must open/run/use the artifact
```

### MiniAppBench

Local repo: `MiniAppBench`

World type: interactive HTML application generation and agentic evaluation.

Confirmed local evidence:

- `README.md` defines MiniApps, MiniAppEval, Playwright dependency, and
  intention/static/dynamic scoring.
- `data/query_validation_100.json` contains validation tasks.
- `miniappbench/examples/mcp.json` and `miniappbench/aworld` indicate agent/tool
  evaluation infrastructure.

Anatomy:

```text
state model:
  generated source code plus live browser instance and interaction trajectory.

action model:
  model generates an HTML app; evaluator agent explores app via browser actions.

observation model:
  DOM state, console logs, source code, browser trajectory, visual/static
  evidence.

task source:
  real-world production-like mini-app requests across domains.

reset model:
  per app/browser instance evaluation.

runtime:
  Python, Playwright, browser automation, model/judge APIs.

verifier / score:
  intention alignment, static quality, and dynamic logic.

trace:
  exploratory browser trajectory and evidence collected by evaluator.

difficulty:
  open-ended outputs without one rigid oracle, interactive logic, robustness,
  scientific/tool/game app semantics.
```

AIDF mapping:

```text
Open-ended artifact evaluation:
  combine structured rubric with agentic exploration and dynamic evidence.

Enterprise analogy:
  generated workbook, dashboard, workflow, SOP, report, or mini tool must be
  opened and used, not just read as text.
```

AIDF gap:

```text
Need agentic verifier support:
  verifier can explore an artifact through tools and produce evidence-backed
  rubric scores
```

### Agent-Data-Protocol

Local repo: `Agent-Data-Protocol`

World type: trajectory interchange protocol and dataset adapters.

Confirmed local evidence:

- `README.md` describes a protocol-oriented repo.
- `schema` owns the common schema.
- `datasets/*/sample_raw.json`, `sample_std.json`, and `sample_atif.json` show
  raw-to-standard trajectory conversion.
- `agents/*` include adapters for multiple agent frameworks.

Anatomy:

```text
state model:
  not a world by itself; defines trajectory records across worlds.

action model:
  standardized action/observation/message/tool/event records.

observation model:
  normalized observations from heterogeneous agent datasets.

task source:
  many external agent trajectory datasets.

reset model:
  not applicable as runtime; applies to dataset conversion.

runtime:
  schema, converters, dataset adapters, tests.

verifier / score:
  schema validation and conversion fidelity.

trace:
  core asset; raw, standardized, and ATIF-style samples.

difficulty:
  cross-framework normalization without losing environment/action semantics.
```

AIDF mapping:

```text
Canonical trace bridge:
  useful target for AIDF world-player trace import/export.

Harness:
  normalize external gym traces into AIDF evidence and possibly ADP-compatible
  trajectories.
```

AIDF gap:

```text
Need explicit trace interop:
  AIDF trace -> ADP trajectory
  ADP trajectory -> AIDF reasoning_run / world_player_trace
```

## Additional Deep-Dive Worlds

### VERINA

Local repo: `VERINA`

Evidence: `README.md`, `datasets/verina/*/{task.json,description.txt,task.lean}`,
`scripts/benchmark.py`, `scripts/quality_assurance.py`.

Anatomy:

```text
state:
  programming task, signature, Lean ground truth, tests, rejected inputs, metadata

actions:
  generate code, generate specification, generate proof, or generate combinations

observations:
  task description, few-shot examples, Lean/test feedback, benchmark reports

verifier:
  Lean plus tests/rejected-input checks

runtime:
  uv, Lean/Lake, optional Docker/Postgres for Prefect orchestration

trace:
  generated artifacts, per-round eval reports, scores, pass-at-k summaries

difficulty:
  correctness must survive formal verification, not just natural-language judging
```

AIDF mapping:

```text
Verifier-first world:
  formal proof feedback should be a normal verifier signal beside tests, rubric
  scores, and human review.
```

AIDF gap:

```text
Need formal_verifier building block:
  language, verifier version, proof obligations, generated artifacts, error class,
  repair attempts
```

### AlgoVeri

Local repo: `AlgoVeri`

Evidence: `README.md`, `algoveri_data/README.md`, `src/eval/*`,
`src/verifiers/*`.

Anatomy:

```text
state:
  same classical algorithm represented in Dafny, Verus, and Lean

actions:
  produce implementation/proof in selected verifier language, then repair

observations:
  NL problem, formal spec, compiler/verifier errors, semantic feedback

verifier:
  Dafny, Verus, Lean

runtime:
  configured verifier images, Apptainer/Docker style isolation, model configs

trace:
  generated attempts, verifier outcomes, semantic checks, repair trajectory

difficulty:
  same concept changes difficulty when represented in different proof systems
```

AIDF mapping:

```text
Representation variants:
  one intended task can have multiple domain representations and verifier contracts.
```

AIDF gap:

```text
Need representation_variant metadata:
  same task, different formalism, different verifier, same intended contract
```

### Swing-Bench

Local repo: `Swing-Bench`

Evidence: `README.md`, `swingarena/{collect,prepare,inference,harness,statistics}`,
`swingarena/harness/readme.md`.

Anatomy:

```text
state:
  GitHub issue, repo checkout, CI workflow, golden patch/tests, retrieval index

actions:
  retrieve context, edit files, generate patch, generate tests, review, run CI

observations:
  issue text, repo files, search results, CI logs, reviewer output

verifier:
  Docker/act CI simulation plus rule-based patch/test validation

runtime:
  Docker, act, language build tools, Java/BM25 retrieval, model APIs/local models

trace:
  patch attempts, test attempts, CI outcomes, battle rounds, cost/token stats

difficulty:
  real repository context, long files, CI behavior, multi-turn patch/test/review
```

AIDF mapping:

```text
Software world as work system:
  repo + issue + CI + generated artifacts + reviewer loop.
```

AIDF gap:

```text
Need software_ci_world package:
  repo snapshot, issue, allowed tools, retrieval index, CI command, oracle,
  patch/test/review trace schema
```

### RealPDEBench

Local repo: `RealPDEBench`

Evidence: `README.md`, `realpdebench/{train.py,eval.py}`, `realpdebench/data/*`,
`realpdebench/utils/metrics.py`.

Anatomy:

```text
state:
  paired real and numerical physical trajectories across several PDE scenarios

actions:
  train/evaluate forecasting models, choose data type, tune config, run inference

observations:
  spatiotemporal fields, real measurements, simulations, parameter partitions

verifier:
  RMSE, MAE, relative L2, R2, force/kinetic/motion metrics

runtime:
  Python package, HF datasets/checkpoints, GPU-heavy training/eval configs

trace:
  configs, checkpoints, metrics, split choices, rollout behavior

difficulty:
  sim-to-real transfer, rollout horizon, distribution shift
```

AIDF mapping:

```text
Scientific source-to-world:
  raw measurement + simulation + split policy + physical metrics becomes a world.
```

AIDF gap:

```text
Need science world package:
  observation data, simulated data, physical parameters, rollout horizon,
  metric family
```

### PhyWorldBench

Local repo: `PhyWorldBench`

Evidence: `README.md`, `prompts-with-standard-and-index.json`,
`prompt_index_to_prompt.json`, `sample_video_frames.py`, `evaluate_videos.py`,
`analyze_results.py`.

Anatomy:

```text
state:
  physics prompt, generated video, sampled frames, required objects/events/standards

actions:
  generate video externally, sample frames, evaluate against standards

observations:
  prompt variants, frames, VLM judgments, standard-level yes/no results

verifier:
  VLM judge over object presence, event occurrence, and physics standards

runtime:
  video files, OpenCV frame sampling, Azure/OpenAI-compatible VLM

trace:
  per-video JSON and aggregate pass rates

difficulty:
  physical realism is temporal and visual; answer correctness is not one string
```

AIDF mapping:

```text
Multimodal rubric world:
  rubric items attach to frames/time windows/artifacts, not only final text.
```

AIDF gap:

```text
Need multimodal verifier signals:
  artifact locator, frame/time evidence, rubric item, judgment, confidence
```

### AstaBench

Local repo: `AstaBench`

Evidence: `README.md`, `astabench/config/v1.0.0.yml`, `astabench/tools/*`,
`astabench/evals/*`.

Anatomy:

```text
state:
  InspectAI TaskState with problem, target, metadata, provided tools, sandbox state

actions:
  literature search, code execution, report/table editing, answer submission

observations:
  tool list, search results, sandbox files, execution history, model usage logs

verifier:
  Inspect/Asta scorers, task-specific rubrics, exact answers, cost summaries

runtime:
  InspectAI, Docker sandboxes, Asta MCP tools, HF datasets, model APIs

trace:
  .eval logs, tool calls, metadata, usage costs, scoring outputs

difficulty:
  scientific work spans search, synthesis, code, data analysis, and discovery
```

AIDF mapping:

```text
Task-provided tools:
  tools are part of the world contract, not arbitrary agent conveniences.
```

AIDF gap:

```text
Need versioned tool constraints:
  task tools, solver tools, merge rules, usage cost, solve/score separation
```

### MedAgentGym

Local repo: `MedAgentGym`

Evidence: `README.md`, `ehr_gym/env/base.py`, `data/metadata.json`, `configs/*`.

Anatomy:

```text
state:
  Gymnasium EHR environment with chat messages, goal, history, task, elapsed time

actions:
  code/action strings that query/analyze medical data and answer tasks

observations:
  chat history, action outputs, execution records, debugger/context signals

verifier:
  task ground truth, score utilities, trajectory verifier for selecting rollouts

runtime:
  Docker isolation, protected EHR data, model configs, async rollout

trace:
  code, outputs, success flags, execution time, sampled trajectories

difficulty:
  restricted data, code-centric reasoning, domain safety, verifier-selected attempts
```

AIDF mapping:

```text
Protected-data world:
  controlled access to data plus auditable code trace.
```

AIDF gap:

```text
Need protected_data_world mode:
  data access policy, execution sandbox, trajectory verifier, safety constraints
```

### CausalGame

Local repo: `CausalGame`

Evidence: `README.md`, `experiments/*/{game.json,action_space.json}`,
`api/*`, `agent/*`.

Anatomy:

```text
state:
  hidden structural causal model, budget, drone designs, visible/censored history

actions:
  deploy experiments, query environment, inspect history, submit final design

observations:
  survival, hit count, visible environment variables, mission status

verifier:
  final 1,000-drone fleet run against scenario threshold

runtime:
  FastAPI backend, scenario JSON configs, tool-calling agent harness, Docker mode

trace:
  deployments, design choices, observations, queried variables, final survival

difficulty:
  hidden confounders, selection bias, noise, local optima, environment shift
```

AIDF mapping:

```text
Experiment-budget world:
  agent must learn by intervention, not only read supplied context.
```

AIDF gap:

```text
Need hidden_state and intervention schema:
  visible fields, hidden fields, intervention actions, observation policy,
  final deployment verifier
```

### MADQA

Local repo: `MADQA`

Evidence: `README.md`, `eval/README.md`, `baselines/*`.

Anatomy:

```text
state:
  question over PDF corpus, page evidence, answer aliases, gold citations

actions:
  retrieve pages/docs, inspect text/visual content, answer, cite evidence

observations:
  retrieved pages, OCR/text snippets, visual evidence, search history

verifier:
  ANLS*, semantic judge, document F1, page F1, effort/accuracy metrics

runtime:
  HF dataset, PDF tooling, BM25/MLLM/file-search/recursive baselines

trace:
  answer, citations, search history, iteration count

difficulty:
  cross-page and cross-document reasoning with strategic evidence navigation
```

AIDF mapping:

```text
Evidence-navigation world:
  final answer, supporting citations, and wasted effort are all scoreable.
```

AIDF gap:

```text
Need evidence metrics:
  citation precision/recall, effort-vs-accuracy, search-history schema
```

### CounselBench

Local repo: `CounselBench`

Evidence: `README.md`, `prompts/judge_prompts.py`, `llm_as_judges/*`,
`run_adversarial/*`.

Anatomy:

```text
state:
  counseling post, response, expert ratings, adversarial questions, failure labels

actions:
  generate response, judge response, classify critique/failure mode

observations:
  post, response, comments, rubric dimensions, annotated failure spans

verifier:
  professional ratings, LLM judge scores, reliability stats, adversarial labels

runtime:
  HF datasets, model APIs, judge scripts, human-evaluation processing

trace:
  generated responses, scores, critique classifications, toxic/incorrect spans

difficulty:
  open-ended quality, safety, empathy, medical-advice boundaries, expert disagreement
```

AIDF mapping:

```text
Rubric-mining world:
  expert comments become dimensions, failure modes, adversarial cases, calibration.
```

AIDF gap:

```text
Need rubric_mining pipeline:
  dimension extraction, failure taxonomy, inter-rater reliability, judge calibration
```

### WebDevJudge

Local repo: `WebDevJudge`

Evidence: `README.md`, `prompts/*`, `evaluator/*`, `envs/README.md`.

Anatomy:

```text
state:
  web task, generated implementation, screenshots, interactive env, rubric, labels

actions:
  judge static code, inspect screenshot, interact with website, apply rubric

observations:
  code, screenshots, task metadata, dynamic interaction results, generated rubrics

verifier:
  preference labels, Likert/rubric judging, dynamic GUI eval, unit feasibility label

runtime:
  Next.js workspaces, ChromeDriver, Xvfb, model APIs, data-prep scripts

trace:
  judge outputs, CSV predictions, dynamic logs, task metadata, rubrics

difficulty:
  UI quality is code + visual render + live behavior
```

AIDF mapping:

```text
Interactive artifact world:
  generated artifacts must be opened and used, not only read.
```

AIDF gap:

```text
Need web_ui verifier package:
  DOM/code checks, screenshots, browser actions, behavior evidence, rubric scores
```

### THOR

Local repo: `THOR`

Evidence: `README.md`, `TIRGen/*`, `inference/*`, `inference/math_verifier.py`.

Anatomy:

```text
state:
  math problem, reasoning trajectory, candidate tool calls, execution feedback

actions:
  reason, choose executable step, call code tool, repair failed tool call

observations:
  tool output, execution error, verifier check, trajectory correctness

verifier:
  math answer verifier plus code execution feedback

runtime:
  SandboxFusion, TIRGen, inference scripts, model training/inference stack

trace:
  tool-integrated reasoning paths, filtering decisions, repair attempts, final answer

difficulty:
  long reasoning has sparse final reward; tools create intermediate checkpoints
```

AIDF mapping:

```text
Tool-integrated reasoning:
  convert reasoning steps into executable checkpoints and repair loops.
```

AIDF gap:

```text
Need TIR trace type:
  reasoning step, proposed tool call, execution result, repair action,
  final-answer linkage
```

### World-In-World

Local repo: `World-In-World`

Evidence: `README.md`, `docs/01_setup_env.md`, `docs/03_run_commands.md`,
`downstream/simulator.py`, `downstream/evaluator.py`, `downstream/utils/*`.

Anatomy:

```text
state:
  embodied scene, current viewpoint/observation, world-model prediction, task goal

actions:
  text action, viewpoint action, low-level control, navigation/manipulation command

observations:
  rendered scene, generated future world, detection/segmentation outputs, task state

verifier:
  task-specific metrics for active recognition, embodied QA, image-goal navigation,
  and manipulation

runtime:
  Habitat-sim, scene datasets, VLM policy, world-model server, SAM/Grounding-SAM,
  manipulation backend

trace:
  closed-loop planning steps, proposed imagined worlds, executed actions, results

difficulty:
  model must help the agent act in a live loop, not merely generate plausible video
```

AIDF mapping:

```text
Closed-loop world-model evaluation:
  evaluate whether a generated/imagined world improves downstream action.
```

AIDF gap:

```text
Need imagined_state support:
  actual observation, predicted next state, chosen action, executed state,
  usefulness score
```

### MC-Search

Local repo: `MC-Search`

Evidence: `README.md`, `src/*/mc_search_agent.py`, `src/*/mc_search_evaluate.py`,
`src/llm_as_judge/judge.py`.

Anatomy:

```text
state:
  multimodal search task with local data, query, candidate evidence, answer target

actions:
  retrieve/search, inspect text/image evidence, answer, self-evaluate

observations:
  retrieved candidates, model-specific multimodal outputs, judge feedback

verifier:
  evaluation scripts plus LLM-as-judge path

runtime:
  model-specific agents for GPT, Gemini, Qwen-VL, InternVL

trace:
  search/evidence path, answer, judge result

difficulty:
  multiple model adapters need the same task contract and comparable evidence path
```

AIDF mapping:

```text
Adapter-neutral multimodal search:
  same world should run against many provider-specific agents.
```

AIDF gap:

```text
Need provider adapter contract:
  model capability, input modalities, evidence trace, judge result
```

### TerminalTraj

Local repo: `TerminalTraj`

Evidence: `README.md`.

Anatomy:

```text
state:
  terminal task trajectory dataset and model-training/evaluation assets

actions:
  shell commands, file operations, iterative terminal decisions

observations:
  command outputs, errors, filesystem/task state, prior steps

verifier:
  dataset/task-specific success labels or evaluation scripts

runtime:
  terminal environment plus trajectory/model tooling

trace:
  core asset: long terminal interaction traces

difficulty:
  long command sequences require memory, recovery, and grounded state tracking
```

AIDF mapping:

```text
Terminal work trajectories:
  useful for training/evaluating agents that act through shell and filesystem.
```

AIDF gap:

```text
Need terminal trace normalization:
  command, cwd, stdout/stderr, exit code, file diff, recovery marker
```

### daVinci-Dev

Local repo: `daVinci-Dev`

Evidence: `README.md`, `env_traj_utils/README.md`, `pipeline/README.md`,
`pipeline/text_from_huggingface.md`.

Anatomy:

```text
state:
  software-development trajectories from SWE-agent style environments

actions:
  search/replace edits, file inspection, reasoning summaries, commit-style actions

observations:
  repository context, issue/PR data, relevant files, trajectory messages

verifier:
  primarily dataset conversion/filtering; downstream training/eval consumes traces

runtime:
  HF data, Go/Rust tokenizer pipeline, XML/text renderers, token-length filters

trace:
  environment-native trajectories converted to trainable XML/text/parquet

difficulty:
  preserve environment semantics while compressing very long software trajectories
```

AIDF mapping:

```text
Trace-to-training supply chain:
  world traces become mid-training data only after faithful rendering/filtering.
```

AIDF gap:

```text
Need trace renderer:
  AIDF trace -> trainable transcript with provenance, action semantics,
  length accounting, and filter reasons
```

### AgentFlow

Local repo: `AgentFlow`

Evidence: `README.md`, `assets/doc/benchmark.md`, `assets/doc/logs.md`,
`agentflow/tracer/*`, `agentflow/reward.py`, `train/rollout.py`.

Anatomy:

```text
state:
  long-horizon reasoning task with planner/executor/verifier/generator memory

actions:
  plan, execute tools, verify, generate final answer, update memory

observations:
  tool outputs, verifier feedback, evolving memory, benchmark results

verifier:
  benchmark-specific scoring and reward functions

runtime:
  vLLM/model servers, task scripts, rollout service, Flow-GRPO training

trace:
  output_i.json with query, response, memory, tool calls, final scores

difficulty:
  sparse rewards across long reasoning flows; optimization happens in the flow
```

AIDF mapping:

```text
Harness-to-training loop:
  traces, verifier signals, and rewards feed optimization, not only reporting.
```

AIDF gap:

```text
Need trainable feedback export:
  trace + verifier signal + reward + memory state + tool usage
```

### OpenApps

Local repo: `OpenApps`

Evidence: `README.md`, `site/Intro to UI Agents.md`, `config/tasks/*`,
`tests/*`, `src/open_apps/*`.

Anatomy:

```text
state:
  configurable browser/app UI state, task goal, screenshots/accessibility text

actions:
  click, type, scroll, select, multi-step app interaction

observations:
  screenshots, accessibility tree/text, past actions, app state

verifier:
  task completion monitor and task-specific checks

runtime:
  Python environment, configurable apps, BrowserGym-style env args, agents

trace:
  screenshots, action list, observations, task outcome

difficulty:
  repeatable UI tasks with many generated goal variations and longer horizons
```

AIDF mapping:

```text
Synthetic app-world generator:
  configurable apps can create many controlled UI tasks from reusable state.
```

AIDF gap:

```text
Need app state generator:
  app seed state, task variation, observation mode, completion monitor
```

### ScaleCUA

Local repo: `ScaleCUA`

Evidence: `README.md`, `playground/README.md`, `evaluation/*/README.md`,
`playground/envs/base_env.py`.

Anatomy:

```text
state:
  computer-use environment across web, Ubuntu, Android, Windows, macOS

actions:
  UI grounding, planner actions, native agent actions, browser/OS/mobile controls

observations:
  screenshot, UI state, environment feedback, VNC/browser/mobile status

verifier:
  benchmark-specific evaluators for WebArenaLite, OSWorld, AndroidLab,
  AndroidWorld, WindowsAgentArena, MacOSArena

runtime:
  Playwright, Docker Ubuntu web env, Android tooling, OS-specific eval adapters

trace:
  agent run records, environment steps, results per benchmark

difficulty:
  unified computer-use across many substrate types and action spaces
```

AIDF mapping:

```text
Multi-substrate CUA world:
  one agent abstraction should run on web, desktop, and mobile with substrate
  adapters.
```

AIDF gap:

```text
Need environment substrate abstraction:
  web, desktop, mobile, browser-in-OS, action encoder, observation encoder,
  verifier adapter
```

### UI-Venus-VenusBench-Mobile

Local repo: `UI-Venus-VenusBench-Mobile`

Evidence: `README.md`, `task_instance_goal.json`, `android_world/registry.py`,
`android_world/policy/verification.py`, `android_world/env/*`.

Anatomy:

```text
state:
  Android emulator, installed apps, task goal, files/APKs, GUI state, memory

actions:
  tap, type, scroll, app navigation, coordinate actions, function-call actions

observations:
  screenshots, device state, app state, previous turns, external files

verifier:
  programmatic OS-state inspection or MLLM judgment depending on task

runtime:
  AndroidWorld, emulator, ADB, APK install scripts, config YAML, verifier model URL

trace:
  task run logs, action history, cost/time, diagnostic category results

difficulty:
  vague instructions, conflicts, multi-round memory, GUI state awareness,
  visual manipulation, popups/crashes/noise, stability variants
```

AIDF mapping:

```text
Mobile world with diagnostics:
  benchmark should score not only success, but which capability failed.
```

AIDF gap:

```text
Need capability diagnostic taxonomy:
  task category, perturbation mode, verifier type, cost, stability runs,
  failure capability label
```

## Next Deep-Dive Targets

These still need the same treatment next:

```text
None from the current priority local list. Remaining work is synthesis and
implementation mapping, not first-pass anatomy.
```

## Cross-Cutting AIDF Requirements Emerging So Far

### A. World State Must Be First-Class

The repos repeatedly encode mutable state: DB rows, smart-home devices, web app
state, OS/web platform state, code repos, Docker environments, and generated
artifacts.

AIDF should require every generated/evaluation world to declare:

```text
initial_state_ref
state_store_type
allowed_mutations
reset_snapshot_ref
state_diff_verifier_refs
```

### B. Actions Need Tool Semantics And Policy

Actions are not generic text. They are SQL, browser clicks, terminal commands,
device API calls, formal proof attempts, CI runs, document retrieval, or app
interactions.

AIDF should require:

```text
tool_surface_ref
action_schema_refs
permission_policy_refs
forbidden_action_refs
mutation_log_ref
```

### C. Verifiers Need Multiple Strength Levels

The repos mix hard executable checks and softer expert/rubric checks. AIDF
should preserve the distinction.

```text
deterministic verifier:
  tests, SQL result, state diff, CI, Lean/Dafny/Verus, sandbox flag

agentic verifier:
  browser exploration, document navigation, generated app inspection

expert/rubric verifier:
  human labels, clinical judgment, visual quality, synthesis quality
```

### D. Reset And Replay Are Not Optional

Every serious executable world has some reset or replay idea: Docker rebuild,
DB reset, episode seed, VM setup, browser sandbox, environment reconstruction,
or trace replay.

AIDF should require:

```text
reset_snapshot_ref
runtime_mode
replay_contract_ref
trace_contract_ref
execution_receipt_ref
```

### E. Source-To-World Must Retain Provenance

`CVE-Factory`, `MEnvAgent`, `CyberGym`, `Vision2Web`, and `MiniAppBench` show
that source material becomes tasks and runnable worlds. The transformation must
be reviewable.

AIDF should retain:

```text
source_packet_ref
extracted_building_block_refs
world_seed_ref
generated_task_refs
verifier_generation_refs
quality_gate_refs
```

### F. Difficulty Comes From Controlled Mess

The strongest worlds add ambiguity, async changes, adversarial content,
environment variation, hidden causal structure, build failures, stale context,
or user co-action.

AIDF should encode:

```text
chaos_facets
variation_family_refs
hidden_fact_refs
distractor_refs
pass_at_k_difficulty_receipts
expert_solvability_refs
```
