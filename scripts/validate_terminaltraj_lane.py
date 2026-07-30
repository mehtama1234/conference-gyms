#!/usr/bin/env python3
"""Validate the TerminalTraj production-lane contract artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "lanes" / "terminaltraj"


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


def validate_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(
        trace,
        [
            "schema_version",
            "trace_id",
            "lane_id",
            "source",
            "runtime_status",
            "task",
            "reset",
            "observations",
            "actions",
            "verifier",
            "final_state",
            "cleanup",
            "quality",
            "export_decision",
        ],
        "trace",
        errors,
    )
    require(trace.get("schema_version") == "terminal-sandbox-trace/v0.1", "unexpected trace schema_version", errors)
    require(trace.get("lane_id") == "terminaltraj-production-lane", "unexpected trace lane_id", errors)

    source = trace.get("source")
    require_keys(source, ["local_repo", "upstream_remote", "commit", "license"], "trace.source", errors)
    if isinstance(source, dict):
        commit = source.get("commit")
        require(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "source.commit must be a 40-character lowercase SHA", errors)

    runtime = trace.get("runtime_status")
    require_keys(runtime, ["mode", "is_real_runtime", "blockers"], "trace.runtime_status", errors)
    if isinstance(runtime, dict):
        require(runtime.get("mode") in {"fixture_contract", "real_local_run", "hosted_run"}, "runtime_status.mode is invalid", errors)
        if runtime.get("mode") == "fixture_contract":
            require(runtime.get("is_real_runtime") is False, "fixture trace must set is_real_runtime=false", errors)
            require(bool(runtime.get("blockers")), "fixture trace must keep explicit blockers", errors)
        if runtime.get("mode") == "real_local_run":
            require(runtime.get("is_real_runtime") is True, "real trace must set is_real_runtime=true", errors)

    observations = trace.get("observations")
    require(isinstance(observations, list) and len(observations) >= 1, "trace must contain at least one observation", errors)
    if isinstance(observations, list):
        for index, observation in enumerate(observations):
            require_keys(observation, ["step", "kind", "content", "evidence"], f"observations[{index}]", errors)

    actions = trace.get("actions")
    require(isinstance(actions, list), "trace.actions must be a list", errors)
    if isinstance(actions, list):
        for index, action in enumerate(actions):
            require_keys(action, ["step", "action_type", "raw", "expected_effect", "status"], f"actions[{index}]", errors)

    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "kind", "passed", "evidence"], "trace.verifier", errors)
    if isinstance(verifier, dict):
        if runtime if isinstance(runtime, dict) else None:
            if runtime.get("mode") == "fixture_contract":
                require(verifier.get("status") == "not_run", "fixture verifier status must be not_run", errors)
                require(verifier.get("passed") is False, "fixture verifier must not claim pass", errors)

    quality = trace.get("quality")
    require_keys(quality, ["evidence_completeness", "replay_confidence", "failure_category", "notes"], "trace.quality", errors)
    if isinstance(quality, dict):
        require(quality.get("evidence_completeness") in {"contract_only", "partial", "complete"}, "invalid quality.evidence_completeness", errors)
        require(quality.get("replay_confidence") in {"none", "low", "medium", "high"}, "invalid quality.replay_confidence", errors)

    export = trace.get("export_decision")
    require_keys(export, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], "trace.export_decision", errors)
    if isinstance(export, dict):
        require(export.get("hosted_conversion") == "blocked", "hosted conversion must stay blocked for this lane", errors)
        require(export.get("sft_export") == "blocked", "SFT export must stay blocked for this lane", errors)
        require(export.get("training_export") == "blocked", "training export must stay blocked for this lane", errors)


def validate_task_manifest(task_manifest: dict[str, object], errors: list[str]) -> None:
    require_keys(
        task_manifest,
        [
            "lane_id",
            "task_manifest_id",
            "status",
            "source_dataset",
            "task",
            "runtime",
            "file_hashes",
            "verifier_expectations",
            "license_status",
            "execution_status",
            "export_decision",
        ],
        "task-manifest",
        errors,
    )
    require(task_manifest.get("lane_id") == "terminaltraj-production-lane", "task manifest lane_id is invalid", errors)
    require(
        task_manifest.get("status") in {"selected_not_run", "selected_real_local_run_passed_export_blocked"},
        "task manifest status is invalid",
        errors,
    )
    task = task_manifest.get("task")
    require_keys(task, ["task_id", "difficulty", "category", "parser_name", "summary"], "task-manifest.task", errors)
    if isinstance(task, dict):
        require(task.get("task_id") == "task_5279", "task manifest must identify selected task_5279", errors)
        require(task.get("parser_name") == "pytest", "task_5279 parser must be pytest", errors)
    runtime = task_manifest.get("runtime")
    require_keys(runtime, ["dockerfile_base_image", "base_image_local_status", "compose_service", "test_entrypoint", "verifier"], "task-manifest.runtime", errors)
    if isinstance(runtime, dict):
        require(runtime.get("base_image_local_status") in {"missing", "present"}, "base image status is invalid", errors)
    license_status = task_manifest.get("license_status")
    require_keys(license_status, ["repo_level_license", "source_license_row_found", "decision"], "task-manifest.license_status", errors)
    if isinstance(license_status, dict):
        require(license_status.get("source_license_row_found") is False, "selected task license row must not be marked found without evidence", errors)
        require(
            license_status.get("decision") in {"unresolved_for_selected_task", "resolved_for_local_validation_only"},
            "selected task license decision is invalid",
            errors,
        )
        if license_status.get("decision") == "resolved_for_local_validation_only":
            require(license_status.get("source_license_resolved_from_upstream") is True, "resolved license must cite upstream resolution", errors)
            require(license_status.get("upstream_license") == "MIT", "task_5279 upstream license must be MIT", errors)
    execution_status = task_manifest.get("execution_status")
    require_keys(execution_status, ["reset", "agent_actions", "verifier", "cleanup"], "task-manifest.execution_status", errors)
    if isinstance(execution_status, dict):
        allowed_execution_states = {"not_run", "passed"}
        for key, value in execution_status.items():
            require(value in allowed_execution_states, f"task execution_status.{key} has invalid state", errors)
        if task_manifest.get("status") == "selected_real_local_run_passed_export_blocked":
            for key, value in execution_status.items():
                require(value == "passed", f"task execution_status.{key} must be passed after real local run", errors)


def validate_setup_receipt(setup_receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        setup_receipt,
        [
            "lane_id",
            "setup_receipt_id",
            "status",
            "checked_at",
            "host_capabilities",
            "downloaded_inputs",
            "selected_task",
            "base_image",
            "blockers",
        ],
        "setup-receipt",
        errors,
    )
    require(setup_receipt.get("lane_id") == "terminaltraj-production-lane", "setup receipt lane_id is invalid", errors)
    require(setup_receipt.get("status") in {"partial_blocked", "passed"}, "setup receipt status is invalid", errors)
    base_image = setup_receipt.get("base_image")
    require_keys(base_image, ["image", "local_status", "pull_attempted"], "setup-receipt.base_image", errors)
    if isinstance(base_image, dict):
        require(base_image.get("local_status") in {"missing", "present"}, "setup receipt base image status is invalid", errors)
        if setup_receipt.get("status") == "passed":
            require(base_image.get("local_status") == "present", "passed setup receipt must have present base image", errors)
            require(base_image.get("pull_attempted") is True, "passed setup receipt must record pull attempt", errors)


def validate_cross_artifacts(
    source_pin: dict[str, object],
    task_manifest: dict[str, object],
    setup_receipt: dict[str, object],
    trace: dict[str, object],
    export_decision: dict[str, object],
    errors: list[str],
) -> None:
    require(source_pin.get("lane_id") == trace.get("lane_id"), "source pin lane_id does not match trace", errors)
    require(task_manifest.get("lane_id") == trace.get("lane_id"), "task manifest lane_id does not match trace", errors)
    require(setup_receipt.get("lane_id") == trace.get("lane_id"), "setup receipt lane_id does not match trace", errors)
    source = trace.get("source")
    if isinstance(source, dict):
        require(source_pin.get("commit") == source.get("commit"), "source pin commit does not match trace source commit", errors)
        require(source_pin.get("upstream_remote") == source.get("upstream_remote"), "source pin remote does not match trace source remote", errors)
    task = task_manifest.get("task")
    trace_task = trace.get("task")
    if isinstance(task, dict) and isinstance(trace_task, dict):
        require(task.get("task_id") == trace_task.get("task_id"), "task manifest task_id does not match trace task_id", errors)
    require(export_decision.get("lane_id") == trace.get("lane_id"), "export decision lane_id does not match trace", errors)
    require(export_decision.get("training_export") == "blocked", "export decision must block training export", errors)
    require(export_decision.get("sft_export") == "blocked", "export decision must block SFT export", errors)


def validate_receipts(
    reset_receipt: dict[str, object],
    verifier_receipt: dict[str, object],
    cleanup_receipt: dict[str, object],
    replay_receipt: dict[str, object],
    license_receipt: dict[str, object],
    privacy_receipt: dict[str, object],
    split_receipt: dict[str, object],
    errors: list[str],
) -> None:
    require(reset_receipt.get("status") == "passed", "reset receipt must be passed", errors)
    require(verifier_receipt.get("status") == "passed", "verifier receipt must be passed", errors)
    result = verifier_receipt.get("result")
    require_keys(result, ["exit_code", "collected", "passed", "failed"], "verifier-receipt.result", errors)
    if isinstance(result, dict):
        require(result.get("exit_code") == 0, "verifier exit_code must be 0", errors)
        require(result.get("collected") == 4, "verifier must collect 4 tests for task_5279", errors)
        require(result.get("passed") == 4, "verifier must pass 4 tests for task_5279", errors)
        require(result.get("failed") == 0, "verifier must fail 0 tests for task_5279", errors)
    require(cleanup_receipt.get("status") == "passed", "cleanup receipt must be passed", errors)
    require(replay_receipt.get("status") == "passed", "replay receipt must be passed", errors)
    replay_result = replay_receipt.get("verifier_result")
    require_keys(replay_result, ["exit_code", "collected", "passed", "failed", "summary"], "replay-receipt.verifier_result", errors)
    if isinstance(replay_result, dict):
        require(replay_result.get("exit_code") == 0, "replay verifier exit_code must be 0", errors)
        require(replay_result.get("collected") == 4, "replay verifier must collect 4 tests", errors)
        require(replay_result.get("passed") == 4, "replay verifier must pass 4 tests", errors)
        require(replay_result.get("failed") == 0, "replay verifier must fail 0 tests", errors)
    replay_export = replay_receipt.get("export_decision")
    require_keys(replay_export, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], "replay-receipt.export_decision", errors)
    if isinstance(replay_export, dict):
        require(replay_export.get("hosted_conversion") == "blocked", "replay hosted conversion must remain blocked", errors)
        require(replay_export.get("sft_export") == "blocked", "replay SFT export must remain blocked", errors)
        require(replay_export.get("training_export") == "blocked", "replay training export must remain blocked", errors)

    require(license_receipt.get("status") == "resolved_for_local_validation_only", "license receipt must be local-validation only", errors)
    license_decision = license_receipt.get("decision")
    require_keys(license_decision, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], "license-receipt.decision", errors)
    if isinstance(license_decision, dict):
        require(license_decision.get("local_contract_validation") == "allowed", "license receipt must allow local validation", errors)
        require(license_decision.get("hosted_conversion") == "blocked", "license receipt must block hosted conversion", errors)
        require(license_decision.get("sft_export") == "blocked", "license receipt must block SFT export", errors)
        require(license_decision.get("training_export") == "blocked", "license receipt must block training export", errors)
    evidence = license_receipt.get("evidence")
    require(isinstance(evidence, list) and len(evidence) >= 2, "license receipt must include repository and license API evidence", errors)
    if isinstance(evidence, list):
        license_ids = {entry.get("license_spdx_id") for entry in evidence if isinstance(entry, dict)}
        require("MIT" in license_ids, "license evidence must include MIT SPDX id", errors)

    for name, receipt in [("privacy", privacy_receipt), ("split", split_receipt)]:
        require(receipt.get("status") == "local_validation_allowed_export_blocked", f"{name} receipt must allow local validation only", errors)
        decision = receipt.get("decision")
        require_keys(decision, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], f"{name}-receipt.decision", errors)
        if isinstance(decision, dict):
            require(decision.get("local_contract_validation") == "allowed", f"{name} receipt must allow local validation", errors)
            require(decision.get("hosted_conversion") == "blocked", f"{name} receipt must block hosted conversion", errors)
            require(decision.get("sft_export") == "blocked", f"{name} receipt must block SFT export", errors)
            require(decision.get("training_export") == "blocked", f"{name} receipt must block training export", errors)


def main() -> int:
    errors: list[str] = []
    source_pin = load_json(LANE / "source-pin.json")
    task_manifest = load_json(LANE / "task-manifest.json")
    setup_receipt = load_json(LANE / "setup-receipt.json")
    fixture_trace = load_json(LANE / "trace.fixture.json")
    real_trace = load_json(LANE / "trace.real.json")
    reset_receipt = load_json(LANE / "reset-receipt.json")
    verifier_receipt = load_json(LANE / "verifier-receipt.json")
    cleanup_receipt = load_json(LANE / "cleanup-receipt.json")
    replay_receipt = load_json(LANE / "replay-receipt.json")
    license_receipt = load_json(LANE / "license-resolution-receipt.json")
    privacy_receipt = load_json(LANE / "privacy-review-receipt.json")
    split_receipt = load_json(LANE / "split-integrity-receipt.json")
    export_decision = load_json(LANE / "export-decision.json")
    load_json(LANE / "trace.schema.json")

    require(isinstance(source_pin, dict), "source-pin.json must be an object", errors)
    require(isinstance(task_manifest, dict), "task-manifest.json must be an object", errors)
    require(isinstance(setup_receipt, dict), "setup-receipt.json must be an object", errors)
    require(isinstance(fixture_trace, dict), "trace.fixture.json must be an object", errors)
    require(isinstance(real_trace, dict), "trace.real.json must be an object", errors)
    require(isinstance(reset_receipt, dict), "reset-receipt.json must be an object", errors)
    require(isinstance(verifier_receipt, dict), "verifier-receipt.json must be an object", errors)
    require(isinstance(cleanup_receipt, dict), "cleanup-receipt.json must be an object", errors)
    require(isinstance(replay_receipt, dict), "replay-receipt.json must be an object", errors)
    require(isinstance(license_receipt, dict), "license-resolution-receipt.json must be an object", errors)
    require(isinstance(privacy_receipt, dict), "privacy-review-receipt.json must be an object", errors)
    require(isinstance(split_receipt, dict), "split-integrity-receipt.json must be an object", errors)
    require(isinstance(export_decision, dict), "export-decision.json must be an object", errors)

    if isinstance(task_manifest, dict):
        validate_task_manifest(task_manifest, errors)
    if isinstance(setup_receipt, dict):
        validate_setup_receipt(setup_receipt, errors)
    if isinstance(fixture_trace, dict):
        validate_trace(fixture_trace, errors)
    if isinstance(real_trace, dict):
        validate_trace(real_trace, errors)
    if (
        isinstance(reset_receipt, dict)
        and isinstance(verifier_receipt, dict)
        and isinstance(cleanup_receipt, dict)
        and isinstance(replay_receipt, dict)
        and isinstance(license_receipt, dict)
        and isinstance(privacy_receipt, dict)
        and isinstance(split_receipt, dict)
    ):
        validate_receipts(
            reset_receipt,
            verifier_receipt,
            cleanup_receipt,
            replay_receipt,
            license_receipt,
            privacy_receipt,
            split_receipt,
            errors,
        )
    if (
        isinstance(source_pin, dict)
        and isinstance(task_manifest, dict)
        and isinstance(setup_receipt, dict)
        and isinstance(fixture_trace, dict)
        and isinstance(real_trace, dict)
        and isinstance(export_decision, dict)
    ):
        validate_cross_artifacts(source_pin, task_manifest, setup_receipt, fixture_trace, export_decision, errors)
        validate_cross_artifacts(source_pin, task_manifest, setup_receipt, real_trace, export_decision, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("TerminalTraj lane artifacts validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
