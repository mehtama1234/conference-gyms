# Source Repos

This repo tracks the analysis and production-readiness layer for the local
conference gym inventory. The benchmark repositories themselves are cloned next
to these files for inspection and smoke testing, but they are intentionally not
committed here.

The local source repos currently present are:

| Local folder | Role in the gym inventory |
| --- | --- |
| `Agent-Data-Protocol` | Common trajectory/action/observation interchange and export target. |
| `AgentFlow` | Planner, executor, verifier, and generator agent loop. |
| `AlgoVeri` | Cross-tool formal verification benchmark. |
| `AstaBench` | Scientific research-agent benchmark. |
| `BIRD-Interact` | Interactive database and user-simulator benchmark. |
| `BrowserGym` | Browser-agent environment framework. |
| `CVE-Factory` | CVE-to-executable-security-task generation. |
| `CausalGame` | Interactive causal discovery world. |
| `CounselBench` | Expert-rubric mental-health evaluation benchmark. |
| `CyberGym` | Executable vulnerability-analysis benchmark. |
| `DeepSynth` | Long-horizon information synthesis benchmark. |
| `Gaia2-ARE` | Dynamic asynchronous agent environments. |
| `MADQA` | Document-agent question-answering benchmark. |
| `MC-Search` | Multimodal agentic search trajectories. |
| `MEnvAgent` | Automated software environment construction. |
| `MedAgentGym` | Biomedical coding and data-science agent environment. |
| `MiniAppBench` | Interactive generated-app evaluation benchmark. |
| `OpenApps` | Configurable UI apps for computer-use agents. |
| `PhyWorldBench` | Physical realism evaluation for generated video. |
| `RealPDEBench` | Real/sim paired PDE forecasting benchmark. |
| `RedTeamCUA` | Adversarial computer-use agent sandbox. |
| `SandboxEscapeBench` | Container breakout and sandbox security benchmark. |
| `ScaleCUA` | Cross-platform computer-use agent data and evaluation. |
| `SimuHome` | Smart-home simulator and device-state world. |
| `Swing-Bench` | CI-driven software-engineering issue arena. |
| `THOR` | Tool-integrated math/code reasoning trajectories. |
| `TerminalTraj` | Dockerized terminal-agent trajectory generation. |
| `UI-Venus-VenusBench-Mobile` | Mobile GUI benchmark. |
| `VERINA` | Lean verifiable-code benchmark. |
| `Vision2Web` | Visual website development benchmark. |
| `WebDevJudge` | Web-development judge benchmark. |
| `World-In-World` | Closed-loop embodied world-model benchmark. |
| `daVinci-Dev` | Software-agent mid-training data pipeline. |
| `tau2-bench` | Shared user-agent tool world with policy and state. |

To reproduce an analysis run, restore or reclone those upstream repos into the
same local folder names, then use the tracked readiness files:

- `README.md`
- `CONFERENCE_WORLD_ANALYSIS.md`
- `WORLD_ANATOMY_MAP.md`
- `AIDF_WORLD_IMPLEMENTATION_GAPS.md`
- `WORLD_PACKAGE_INVENTORY.yaml`
- `conference-world-adapter-readiness.json`
- `agent-data-protocol-approval-overrides.template.json`

The repo boundary is deliberate: this project owns the normalized inventory,
adapter readiness claims, approval gates, and next-step plans. The upstream
benchmark repos own their implementations.
