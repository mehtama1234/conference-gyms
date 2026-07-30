#!/usr/bin/env python3
"""Validate the OpenApps production-lane contract artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "lanes" / "openapps"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_keys(obj: object, keys: list[str], where: str, errors: list[str]) -> None:
    require(isinstance(obj, dict), f"{where} must be an object", errors)
    if not isinstance(obj, dict):
        return
    missing = [key for key in keys if key not in obj]
    require(not missing, f"{where} missing keys: {', '.join(missing)}", errors)


def validate_source(source: dict[str, object], errors: list[str]) -> None:
    require_keys(source, ["lane_id", "status", "upstream_remote", "commit", "repo_license", "runtime_blockers", "export_decision"], "source-pin", errors)
    require(source.get("lane_id") == "openapps-production-lane", "source lane_id is invalid", errors)
    require(
        source.get("status") in {
            "source_pinned_source_smoke_passed_runtime_blocked",
            "source_pinned_reward_fixture_passed_browser_runtime_blocked",
            "source_pinned_reward_fixture_passed_browser_attempt_blocked",
            "source_pinned_browser_runtime_passed_single_task_export_blocked",
        },
        "source status is invalid",
        errors,
    )
    commit = source.get("commit")
    require(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "source commit must be a 40-character SHA", errors)
    require(source.get("repo_license") == "CC-BY-NC-4.0", "OpenApps license must be CC-BY-NC-4.0", errors)
    blockers = source.get("runtime_blockers")
    require(isinstance(blockers, list) and any("Playwright" in item or "browser" in item for item in blockers), "source blockers must mention Playwright/browser runtime", errors)
    require(isinstance(blockers, list) and any("FastHTML" in item for item in blockers), "source blockers must mention OpenApps/FastHTML runtime compatibility", errors)


def validate_contract(contract: dict[str, object], errors: list[str]) -> None:
    require_keys(contract, ["lane_id", "contract_id", "status", "world_family", "task_shape", "success_semantics", "normalized_trace_required_fields"], "task-contract", errors)
    require(contract.get("lane_id") == "openapps-production-lane", "contract lane_id is invalid", errors)
    require(
        contract.get("status")
        in {
            "contract_only_runtime_blocked",
            "reward_fixture_passed_browser_runtime_blocked",
            "reward_fixture_and_single_browser_task_passed_export_blocked",
        },
        "contract status is invalid",
        errors,
    )
    require(contract.get("world_family") == "browser_gui", "OpenApps must be browser_gui family", errors)
    shape = contract.get("task_shape")
    require_keys(shape, ["apps_observed", "original_task_count", "agent_inputs", "agent_actions", "verifier_outputs"], "task-contract.task_shape", errors)
    if isinstance(shape, dict):
        require(shape.get("original_task_count") == 28, "OpenApps original task count should be 28", errors)
        apps = shape.get("apps_observed")
        require(isinstance(apps, list) and len(apps) == 8 and "todo" in apps and "calendar" in apps, "OpenApps app list is invalid", errors)
        outputs = shape.get("verifier_outputs")
        require(isinstance(outputs, list) and "task reward" in outputs and "state diff" in outputs, "OpenApps verifier outputs must include reward and state diff", errors)


def validate_smoke(smoke: dict[str, object], errors: list[str]) -> None:
    require_keys(smoke, ["lane_id", "smoke_receipt_id", "status", "scope", "observed", "known_runtime_blockers", "does_not_claim"], "source-smoke", errors)
    require(smoke.get("lane_id") == "openapps-production-lane", "smoke lane_id is invalid", errors)
    require(smoke.get("status") == "passed", "smoke must pass", errors)
    require(smoke.get("scope") == "source_config_only", "smoke scope must be source_config_only", errors)
    observed = smoke.get("observed")
    require_keys(observed, ["open_apps_module", "app_count", "apps", "original_task_count", "first_task_keys"], "source-smoke.observed", errors)
    if isinstance(observed, dict):
        require(observed.get("app_count") == 8, "smoke app_count should be 8", errors)
        require(observed.get("original_task_count") == 28, "smoke original_task_count should be 28", errors)
    blockers = smoke.get("known_runtime_blockers")
    require(isinstance(blockers, list) and any("hydra" in item for item in blockers), "smoke blockers must mention hydra", errors)
    does_not_claim = smoke.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "reward verifier execution" in does_not_claim, "smoke must not claim reward verifier execution", errors)


def validate_reward_receipt(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(receipt, ["lane_id", "reward_receipt_id", "status", "scope", "task", "environment", "inputs", "result", "does_not_claim"], "reward-fixture", errors)
    require(receipt.get("lane_id") == "openapps-production-lane", "reward receipt lane_id is invalid", errors)
    require(receipt.get("status") == "passed", "reward fixture must pass", errors)
    require(receipt.get("scope") == "non_browser_saved_state_reward", "reward fixture scope is invalid", errors)
    task = receipt.get("task")
    require_keys(task, ["task_name", "task_class", "task_id", "goal", "todo_name", "is_done"], "reward-fixture.task", errors)
    if isinstance(task, dict):
        require(task.get("task_name") == "add_call_mom_to_my_todo", "reward fixture task name is invalid", errors)
        require(task.get("task_class") == "open_apps.tasks.tasks.AddToDoTask", "reward fixture task class is invalid", errors)
    inputs = receipt.get("inputs")
    require_keys(inputs, ["initial_state", "current_state", "initial_todo_count", "current_todo_count"], "reward-fixture.inputs", errors)
    if isinstance(inputs, dict):
        require(inputs.get("initial_todo_count") == 15, "reward fixture initial todo count should be 15", errors)
        require(inputs.get("current_todo_count") == 16, "reward fixture current todo count should be 16", errors)
    result = receipt.get("result")
    require_keys(result, ["check_if_task_is_complete", "verifier", "state_comparison"], "reward-fixture.result", errors)
    if isinstance(result, dict):
        require(result.get("check_if_task_is_complete") is True, "OpenApps reward fixture must pass", errors)
    does_not_claim = receipt.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "browser launched" in does_not_claim, "reward fixture must not claim browser launch", errors)


def validate_replay_receipt(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(receipt, ["lane_id", "replay_receipt_id", "status", "scope", "script", "command", "result", "does_not_claim"], "replay-receipt", errors)
    require(receipt.get("lane_id") == "openapps-production-lane", "replay receipt lane_id is invalid", errors)
    require(receipt.get("status") == "passed", "OpenApps replay receipt must pass", errors)
    require(receipt.get("scope") == "non_browser_saved_state_reward", "OpenApps replay scope is invalid", errors)
    result = receipt.get("result")
    require_keys(result, ["task_id", "initial_todo_count", "current_todo_count", "state_comparison", "complete"], "replay-receipt.result", errors)
    if isinstance(result, dict):
        require(result.get("initial_todo_count") == 15, "OpenApps replay initial count should be 15", errors)
        require(result.get("current_todo_count") == 16, "OpenApps replay current count should be 16", errors)
        require(result.get("complete") is True, "OpenApps replay must complete", errors)
    does_not_claim = receipt.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "browser launched" in does_not_claim, "OpenApps replay must not claim browser launch", errors)


def validate_browser_attempt(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "lane_id",
            "attempt_receipt_id",
            "status",
            "scope",
            "script",
            "command",
            "selected_task",
            "runtime_environment",
            "observed_progress",
            "result",
            "residual_warnings",
            "does_not_claim",
            "next_action",
        ],
        "browser-runtime-attempt",
        errors,
    )
    require(receipt.get("lane_id") == "openapps-production-lane", "browser attempt lane_id is invalid", errors)
    require(receipt.get("status") == "passed_browser_gui_runtime", "browser attempt must pass the selected browser GUI task", errors)
    require(receipt.get("scope") == "browser_gui_runtime_single_task", "browser attempt scope is invalid", errors)
    require(receipt.get("script") == "scripts/replay_openapps_browser_task.py", "browser attempt script is invalid", errors)
    task = receipt.get("selected_task")
    require_keys(task, ["task_name", "task_class", "goal", "expected_action_path"], "browser-runtime-attempt.selected_task", errors)
    if isinstance(task, dict):
        require(task.get("task_name") == "add_call_mom_to_my_todo", "browser attempt task name is invalid", errors)
        require(task.get("task_class") == "open_apps.tasks.tasks.AddToDoTask", "browser attempt task class is invalid", errors)
    runtime = receipt.get("runtime_environment")
    require_keys(runtime, ["python", "venv", "pythonpath", "playwright_browsers_path", "local_browser_libraries", "minimal_dependency_strategy"], "browser-runtime-attempt.runtime_environment", errors)
    if isinstance(runtime, dict):
        require(runtime.get("python") == "python3.12", "browser attempt must use Python 3.12", errors)
        require(runtime.get("venv") == ".cache/openapps-browser-venv", "browser attempt venv is invalid", errors)
    progress = receipt.get("observed_progress")
    require(isinstance(progress, list) and any("Chromium" in item for item in progress), "browser attempt must record Chromium download/setup progress", errors)
    require(isinstance(progress, list) and any("standalone Playwright Chromium" in item for item in progress), "browser attempt must record standalone Chromium launch smoke", errors)
    result = receipt.get("result")
    require_keys(
        result,
        ["status", "task_id", "actions", "errors", "initial_todo_count", "final_todo_count", "final_contains_call_mom", "reward", "done", "screenshot_bytes"],
        "browser-runtime-attempt.result",
        errors,
    )
    if isinstance(result, dict):
        require(result.get("status") == "passed", "browser attempt result must pass", errors)
        require(result.get("initial_todo_count") == 15, "browser attempt initial count should be 15", errors)
        require(result.get("final_todo_count") == 16, "browser attempt final count should be 16", errors)
        require(result.get("final_contains_call_mom") is True, "browser attempt must contain Call Mom", errors)
        require(result.get("reward") == 1.0, "browser attempt reward must be 1.0", errors)
        require(result.get("done") is True, "browser attempt must be done", errors)
        require(isinstance(result.get("actions"), list) and len(result["actions"]) >= 3, "browser attempt must record at least 3 actions", errors)
        require(isinstance(result.get("screenshot_bytes"), int) and result["screenshot_bytes"] > 0, "browser attempt must record a non-empty screenshot", errors)
    does_not_claim = receipt.get("does_not_claim")
    require(isinstance(does_not_claim, list) and any("all OpenApps tasks pass" in item for item in does_not_claim), "browser attempt must not claim full benchmark pass", errors)


def validate_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(trace, ["schema_version", "trace_id", "lane_id", "source", "runtime_status", "task", "observations", "actions", "verifier", "quality", "export_decision"], "trace.fixture", errors)
    require(trace.get("schema_version") == "browser-gui-state-trace/v0.1", "OpenApps trace schema is invalid", errors)
    require(trace.get("lane_id") == "openapps-production-lane", "OpenApps trace lane_id is invalid", errors)
    runtime = trace.get("runtime_status")
    require_keys(runtime, ["mode", "is_browser_runtime", "blockers"], "trace.runtime_status", errors)
    if isinstance(runtime, dict):
        require(runtime.get("mode") == "state_reward_fixture", "OpenApps trace mode must be state_reward_fixture", errors)
        require(runtime.get("is_browser_runtime") is False, "OpenApps fixture must not claim browser runtime", errors)
    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "kind", "passed", "evidence"], "trace.verifier", errors)
    if isinstance(verifier, dict):
        require(verifier.get("status") == "passed", "OpenApps trace verifier must pass", errors)
        require(verifier.get("passed") is True, "OpenApps trace verifier must be true", errors)


def validate_real_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(trace, ["schema_version", "trace_id", "lane_id", "source", "runtime_status", "task", "observations", "actions", "verifier", "quality", "export_decision"], "trace.real", errors)
    require(trace.get("schema_version") == "browser-gui-real-trace/v0.1", "OpenApps real trace schema is invalid", errors)
    require(trace.get("lane_id") == "openapps-production-lane", "OpenApps real trace lane_id is invalid", errors)
    runtime = trace.get("runtime_status")
    require_keys(runtime, ["mode", "is_browser_runtime", "browser", "local_runtime_notes"], "trace.real.runtime_status", errors)
    if isinstance(runtime, dict):
        require(runtime.get("mode") == "real_browser_gui_runtime", "OpenApps real trace mode must be real_browser_gui_runtime", errors)
        require(runtime.get("is_browser_runtime") is True, "OpenApps real trace must claim browser runtime", errors)
        notes = runtime.get("local_runtime_notes")
        require(isinstance(notes, list) and any("compatibility shims" in item for item in notes), "OpenApps real trace must record compatibility shims", errors)
    observations = trace.get("observations")
    require(isinstance(observations, list) and len(observations) >= 2, "OpenApps real trace must have initial and final observations", errors)
    if isinstance(observations, list) and len(observations) >= 2:
        require(isinstance(observations[0], dict) and observations[0].get("todo_count") == 15, "OpenApps real trace initial todo count should be 15", errors)
        require(isinstance(observations[-1], dict) and observations[-1].get("todo_count") == 16, "OpenApps real trace final todo count should be 16", errors)
        require(isinstance(observations[-1], dict) and observations[-1].get("contains_call_mom") is True, "OpenApps real trace must contain Call Mom", errors)
    actions = trace.get("actions")
    require(isinstance(actions, list) and len(actions) >= 3, "OpenApps real trace must record at least 3 actions", errors)
    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "kind", "passed", "reward", "evidence"], "trace.real.verifier", errors)
    if isinstance(verifier, dict):
        require(verifier.get("status") == "passed", "OpenApps real trace verifier must pass", errors)
        require(verifier.get("passed") is True, "OpenApps real trace verifier must be true", errors)
        require(verifier.get("reward") == 1.0, "OpenApps real trace reward must be 1.0", errors)
    export = trace.get("export_decision")
    require_keys(export, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], "trace.real.export_decision", errors)
    if isinstance(export, dict):
        require(export.get("hosted_conversion") == "blocked", "OpenApps real trace hosted conversion must stay blocked", errors)
        require(export.get("sft_export") == "blocked", "OpenApps real trace SFT export must stay blocked", errors)
        require(export.get("training_export") == "blocked", "OpenApps real trace training export must stay blocked", errors)


def validate_export(export: dict[str, object], errors: list[str]) -> None:
    require_keys(export, ["lane_id", "decision_id", "local_contract_validation", "hosted_conversion", "sft_export", "training_export", "blocking_reasons"], "export-decision", errors)
    require(export.get("lane_id") == "openapps-production-lane", "export lane_id is invalid", errors)
    require(export.get("local_contract_validation") == "allowed", "export should allow local contract validation", errors)
    require(export.get("hosted_conversion") == "blocked", "hosted conversion must be blocked", errors)
    require(export.get("sft_export") == "blocked", "SFT export must be blocked", errors)
    require(export.get("training_export") == "blocked", "training export must be blocked", errors)
    blockers = export.get("blocking_reasons")
    require(isinstance(blockers, list) and any("CC-BY-NC" in item for item in blockers), "export blockers must cite CC-BY-NC license", errors)
    require(isinstance(blockers, list) and any("one deterministic selected task" in item for item in blockers), "export blockers must cite single-task scope", errors)


def main() -> int:
    errors: list[str] = []
    artifacts = {
        "source": load_json(LANE / "source-pin.json"),
        "contract": load_json(LANE / "task-contract.json"),
        "smoke": load_json(LANE / "source-smoke-receipt.json"),
        "reward": load_json(LANE / "reward-fixture-receipt.json"),
        "replay": load_json(LANE / "replay-receipt.json"),
        "browser_attempt": load_json(LANE / "browser-runtime-attempt-receipt.json"),
        "trace": load_json(LANE / "trace.fixture.json"),
        "real_trace": load_json(LANE / "trace.real.json"),
        "export": load_json(LANE / "export-decision.json"),
    }
    if isinstance(artifacts["source"], dict):
        validate_source(artifacts["source"], errors)
    else:
        errors.append("source-pin.json must be an object")
    if isinstance(artifacts["contract"], dict):
        validate_contract(artifacts["contract"], errors)
    else:
        errors.append("task-contract.json must be an object")
    if isinstance(artifacts["smoke"], dict):
        validate_smoke(artifacts["smoke"], errors)
    else:
        errors.append("source-smoke-receipt.json must be an object")
    if isinstance(artifacts["reward"], dict):
        validate_reward_receipt(artifacts["reward"], errors)
    else:
        errors.append("reward-fixture-receipt.json must be an object")
    if isinstance(artifacts["replay"], dict):
        validate_replay_receipt(artifacts["replay"], errors)
    else:
        errors.append("replay-receipt.json must be an object")
    if isinstance(artifacts["browser_attempt"], dict):
        validate_browser_attempt(artifacts["browser_attempt"], errors)
    else:
        errors.append("browser-runtime-attempt-receipt.json must be an object")
    if isinstance(artifacts["trace"], dict):
        validate_trace(artifacts["trace"], errors)
    else:
        errors.append("trace.fixture.json must be an object")
    if isinstance(artifacts["real_trace"], dict):
        validate_real_trace(artifacts["real_trace"], errors)
    else:
        errors.append("trace.real.json must be an object")
    if isinstance(artifacts["export"], dict):
        validate_export(artifacts["export"], errors)
    else:
        errors.append("export-decision.json must be an object")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OpenApps lane artifacts validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
