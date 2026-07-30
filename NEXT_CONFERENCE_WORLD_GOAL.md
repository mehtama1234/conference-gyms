# Next Conference World Goal

## Current State

The current readiness report has:

- 66 adapter artifacts.
- 33 local world-package projections.
- 8 runtime adapter families.
- Complete family contract-smoke coverage.
- 17 source-specific package projections.
- 14 source-specific no-heavy-run adapter smokes: `OpenApps`,
  `Agent-Data-Protocol`, `TerminalTraj`, `Gaia2-ARE`, `Swing-Bench`,
  `AlgoVeri`, `SimuHome`, `UI-Venus-VenusBench-Mobile`, `MC-Search`,
  `ScaleCUA`, `CyberGym`, `BIRD-Interact`, `VERINA`, `RealPDEBench`.
- 14 evidence/gate receipts for the same source-specific bridges.
- 1 first heavy-run receipt candidate for `Agent-Data-Protocol`.
- 1 policy/export decision receipt for `Agent-Data-Protocol`.
- 1 dataset review matrix for `Agent-Data-Protocol`.
- 1 dataset approval receipt-template set for `Agent-Data-Protocol`.
- 1 generated ADP approval override template with 280 editable receipt entries.
- 16 inventory projections that still need source-specific runtime wiring.
- 0 projection errors.

Every runtime adapter family now has a first concrete source-specific bridge:

- `OpenApps`: browser GUI.
- `Agent-Data-Protocol`: trajectory/data.
- `MC-Search`: second trajectory/data bridge.
- `ScaleCUA`: second browser/GUI bridge and first cross-platform CUA bridge.
- `CyberGym`: second terminal/sandbox bridge.
- `BIRD-Interact`: second external environment/user-database loop bridge.
- `VERINA`: second formal-proof bridge.
- `RealPDEBench`: second scientific simulator bridge.
- `TerminalTraj`: terminal/sandbox.
- `Gaia2-ARE`: external environment loop.
- `Swing-Bench`: repository/CI.
- `AlgoVeri`: formal proof.
- `SimuHome`: scientific/device simulator.
- `UI-Venus-VenusBench-Mobile`: mobile GUI/emulator.

`Agent-Data-Protocol` is now the selected first heavy-run lane. The receipt is
partially cleared: local fixture/schema validation passed with 289 checks in the
temporary `litellm` execution environment. The policy/export decision receipt
allows local fixture evidence for adapter contract validation only. It is still
blocked for hosted dataset conversion, downstream reuse, SFT export, and broader
training export until license/privacy/split/training-export approvals exist.
The dataset review matrix now repeats that status per ADP dataset, so the next
approval work has explicit rows to clear instead of one global statement. The
approval receipt-template set now creates the blocked receipts that each row
must complete, and the generated override template is the file reviewers can
edit and feed back into the CLI.

## Next Goal

The next concrete goal is:

> Clear dataset-level `Agent-Data-Protocol` approvals or pick the next remaining
> inventory world to move into source-specific runtime wiring.

In simple words, the first phase proved that AIDF knows how to describe each
kind of world. The next phase should make one low-infrastructure lane actually
pass end to end, while showing that more adapter families can handle more than
their first example. The trajectory/data family has now done that with
`MC-Search`. The browser/GUI family has also done that with `ScaleCUA`.
Terminal/sandbox, external loop, formal proof, and scientific simulator families
now also have parallel second bridges with `CyberGym`, `BIRD-Interact`,
`VERINA`, and `RealPDEBench`.

## What To Do Next

### 1. Clear Dataset-Level ADP Approvals

Current observed status:

- local ADP validation passed: 289 checks, 0 failures
- `litellm` is available in the temp execution venv used for the receipt
- training export remains blocked until license, privacy, split-integrity, and
  export approvals are recorded
- local fixture evidence is allowed only for adapter contract validation
- dataset review rows exist for ADP local fixtures
- blocked approval receipt templates exist for each ADP dataset
- a generated override template exists at
  `agent-data-protocol-approval-overrides.template.json`

The next output should be real dataset-level approval decisions if this data
will be used beyond local validation.

### 2. Choose The Next Inventory World To Promote

Pick a remaining inventory world where source-specific wiring will teach us
something new.

Good candidates:

- `MedAgentGym` or `CVE-Factory` for additional terminal/sandbox and security
  world coverage.
- `CausalGame` or `World-In-World` for richer scientific/interactive
  simulator coverage.
- `RedTeamCUA`, `Vision2Web`, or `MiniAppBench` for more GUI/browser variants.
- `AstaBench` for scientific research-agent tools, cost, and scoring.

### 3. Keep Heavy Claims Blocked Until Receipts Exist

For any real run, require:

- source/license/privacy review
- runtime setup receipt
- reset receipt
- initial observation
- action trace
- verifier result
- final state or failure receipt
- cleanup receipt
- replay/determinism evidence where applicable
- training-export decision

## Recommended First Move

Continue with `Agent-Data-Protocol` if the next move is approvals: dataset
license review, privacy review, split manifest, hosted conversion receipt, and
training-export approval.

In parallel or immediately after, either clear those ADP approvals or promote
the next remaining inventory world. The best pragmatic options are `MedAgentGym`,
`CVE-Factory`, `AstaBench`, `CausalGame`, `World-In-World`, `RedTeamCUA`,
`Vision2Web`, or `MiniAppBench`.
