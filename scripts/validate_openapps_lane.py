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
    require(source.get("status") == "source_pinned_source_smoke_passed_runtime_blocked", "source status is invalid", errors)
    commit = source.get("commit")
    require(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "source commit must be a 40-character SHA", errors)
    require(source.get("repo_license") == "CC-BY-NC-4.0", "OpenApps license must be CC-BY-NC-4.0", errors)
    blockers = source.get("runtime_blockers")
    require(isinstance(blockers, list) and any("hydra" in item for item in blockers), "source blockers must mention missing hydra dependency", errors)


def validate_contract(contract: dict[str, object], errors: list[str]) -> None:
    require_keys(contract, ["lane_id", "contract_id", "status", "world_family", "task_shape", "success_semantics", "normalized_trace_required_fields"], "task-contract", errors)
    require(contract.get("lane_id") == "openapps-production-lane", "contract lane_id is invalid", errors)
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


def validate_export(export: dict[str, object], errors: list[str]) -> None:
    require_keys(export, ["lane_id", "decision_id", "local_contract_validation", "hosted_conversion", "sft_export", "training_export", "blocking_reasons"], "export-decision", errors)
    require(export.get("lane_id") == "openapps-production-lane", "export lane_id is invalid", errors)
    require(export.get("local_contract_validation") == "allowed", "export should allow local contract validation", errors)
    require(export.get("hosted_conversion") == "blocked", "hosted conversion must be blocked", errors)
    require(export.get("sft_export") == "blocked", "SFT export must be blocked", errors)
    require(export.get("training_export") == "blocked", "training export must be blocked", errors)
    blockers = export.get("blocking_reasons")
    require(isinstance(blockers, list) and any("CC-BY-NC" in item for item in blockers), "export blockers must cite CC-BY-NC license", errors)


def main() -> int:
    errors: list[str] = []
    artifacts = {
        "source": load_json(LANE / "source-pin.json"),
        "contract": load_json(LANE / "task-contract.json"),
        "smoke": load_json(LANE / "source-smoke-receipt.json"),
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
