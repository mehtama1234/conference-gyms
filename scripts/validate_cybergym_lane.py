#!/usr/bin/env python3
"""Validate the CyberGym production-lane contract artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "lanes" / "cybergym"


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
    require(source.get("lane_id") == "cybergym-production-lane", "source lane_id is invalid", errors)
    require(
        source.get("status") in {"source_pinned_heavy_runtime_blocked", "source_pinned_import_smoke_passed_heavy_runtime_blocked"},
        "source status must block heavy runtime",
        errors,
    )
    commit = source.get("commit")
    require(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "source commit must be a 40-character SHA", errors)
    require(source.get("repo_license") == "Apache-2.0", "CyberGym repo license must be Apache-2.0", errors)
    blockers = source.get("runtime_blockers")
    require(isinstance(blockers, list) and len(blockers) >= 4, "source runtime blockers must be explicit", errors)
    export = source.get("export_decision")
    require_keys(export, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export"], "source export_decision", errors)
    if isinstance(export, dict):
        require(export.get("local_contract_validation") == "allowed", "source should allow local contract validation", errors)
        require(export.get("hosted_conversion") == "blocked", "source must block hosted conversion", errors)
        require(export.get("sft_export") == "blocked", "source must block SFT export", errors)
        require(export.get("training_export") == "blocked", "source must block training export", errors)


def validate_contract(contract: dict[str, object], errors: list[str]) -> None:
    require_keys(contract, ["lane_id", "contract_id", "status", "task_shape", "success_semantics", "security_controls", "normalized_trace_required_fields"], "task-contract", errors)
    require(contract.get("lane_id") == "cybergym-production-lane", "contract lane_id is invalid", errors)
    require(contract.get("status") == "contract_only_runtime_blocked", "contract must remain runtime blocked", errors)
    task_shape = contract.get("task_shape")
    require_keys(task_shape, ["agent_inputs", "agent_actions", "verifier_outputs"], "task-contract.task_shape", errors)
    if isinstance(task_shape, dict):
        for required in ["repo-vul.tar.gz", "submit.sh"]:
            require(required in task_shape.get("agent_inputs", []), f"task contract missing agent input {required}", errors)
        for required in ["vul_exit_code", "fix_exit_code"]:
            require(required in task_shape.get("verifier_outputs", []), f"task contract missing verifier output {required}", errors)
    controls = contract.get("security_controls")
    require_keys(controls, ["network_access", "anti_leakage_checks"], "task-contract.security_controls", errors)
    if isinstance(controls, dict):
        require(controls.get("network_access") == "blocked_until_policy_receipt", "network access must be blocked until policy receipt", errors)


def validate_setup(setup: dict[str, object], errors: list[str]) -> None:
    require_keys(setup, ["lane_id", "setup_receipt_id", "status", "local_repo", "data_requirements_from_readme", "runtime_not_attempted_reasons"], "setup-receipt", errors)
    require(setup.get("lane_id") == "cybergym-production-lane", "setup lane_id is invalid", errors)
    require(
        setup.get("status") in {"source_only_heavy_data_blocked", "source_import_smoke_passed_heavy_data_blocked"},
        "setup status must block heavy data",
        errors,
    )
    data = setup.get("data_requirements_from_readme")
    require_keys(data, ["benchmark_data", "binary_only_server_data", "full_server_data", "subset_task_count"], "setup data requirements", errors)
    if isinstance(data, dict):
        require(data.get("subset_task_count") == 10, "CyberGym subset task count should be 10", errors)
    smoke = setup.get("no_heavy_smoke")
    if smoke is not None:
        require_keys(smoke, ["status", "command", "observed_modules"], "setup no_heavy_smoke", errors)
        if isinstance(smoke, dict):
            require(smoke.get("status") == "passed", "setup no-heavy smoke must pass", errors)


def validate_export(export: dict[str, object], errors: list[str]) -> None:
    require_keys(export, ["lane_id", "decision_id", "local_contract_validation", "hosted_conversion", "sft_export", "training_export", "blocking_reasons"], "export-decision", errors)
    require(export.get("lane_id") == "cybergym-production-lane", "export lane_id is invalid", errors)
    require(export.get("local_contract_validation") == "allowed", "export should allow local contract validation", errors)
    require(export.get("hosted_conversion") == "blocked", "export must block hosted conversion", errors)
    require(export.get("sft_export") == "blocked", "export must block SFT export", errors)
    require(export.get("training_export") == "blocked", "export must block training export", errors)
    blockers = export.get("blocking_reasons")
    require(isinstance(blockers, list) and any("server" in item for item in blockers), "export blockers must mention missing server execution", errors)


def validate_import_smoke(smoke: dict[str, object], errors: list[str]) -> None:
    require_keys(smoke, ["lane_id", "smoke_receipt_id", "status", "scope", "command", "observed", "does_not_claim"], "import-smoke", errors)
    require(smoke.get("lane_id") == "cybergym-production-lane", "import smoke lane_id is invalid", errors)
    require(smoke.get("status") == "passed", "import smoke must pass", errors)
    require(smoke.get("scope") == "no_heavy_runtime", "import smoke scope must be no_heavy_runtime", errors)
    observed = smoke.get("observed")
    require_keys(observed, ["cybergym_module", "utils_module"], "import-smoke.observed", errors)
    does_not_claim = smoke.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "vulnerable/fixed verifier executed" in does_not_claim, "import smoke must not claim verifier execution", errors)


def main() -> int:
    errors: list[str] = []
    source = load_json(LANE / "source-pin.json")
    contract = load_json(LANE / "task-contract.json")
    setup = load_json(LANE / "setup-receipt.json")
    smoke = load_json(LANE / "import-smoke-receipt.json")
    export = load_json(LANE / "export-decision.json")

    if isinstance(source, dict):
        validate_source(source, errors)
    else:
        errors.append("source-pin.json must be an object")
    if isinstance(contract, dict):
        validate_contract(contract, errors)
    else:
        errors.append("task-contract.json must be an object")
    if isinstance(setup, dict):
        validate_setup(setup, errors)
    else:
        errors.append("setup-receipt.json must be an object")
    if isinstance(smoke, dict):
        validate_import_smoke(smoke, errors)
    else:
        errors.append("import-smoke-receipt.json must be an object")
    if isinstance(export, dict):
        validate_export(export, errors)
    else:
        errors.append("export-decision.json must be an object")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("CyberGym lane artifacts validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
