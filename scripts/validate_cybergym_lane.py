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
        source.get("status")
        in {
            "source_pinned_heavy_runtime_blocked",
            "source_pinned_import_smoke_passed_heavy_runtime_blocked",
            "source_pinned_server_probe_passed_verifier_data_blocked",
        },
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
        setup.get("status")
        in {
            "source_only_heavy_data_blocked",
            "source_import_smoke_passed_heavy_data_blocked",
            "server_probe_passed_heavy_data_blocked",
        },
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
    require(isinstance(blockers, list) and any("verifier" in item for item in blockers), "export blockers must mention missing verifier execution", errors)


def validate_import_smoke(smoke: dict[str, object], errors: list[str]) -> None:
    require_keys(smoke, ["lane_id", "smoke_receipt_id", "status", "scope", "command", "observed", "does_not_claim"], "import-smoke", errors)
    require(smoke.get("lane_id") == "cybergym-production-lane", "import smoke lane_id is invalid", errors)
    require(smoke.get("status") == "passed", "import smoke must pass", errors)
    require(smoke.get("scope") == "no_heavy_runtime", "import smoke scope must be no_heavy_runtime", errors)
    observed = smoke.get("observed")
    require_keys(observed, ["cybergym_module", "utils_module"], "import-smoke.observed", errors)
    does_not_claim = smoke.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "vulnerable/fixed verifier executed" in does_not_claim, "import smoke must not claim verifier execution", errors)


def validate_server_probe(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "lane_id",
            "server_probe_receipt_id",
            "status",
            "scope",
            "script",
            "command",
            "runtime_environment",
            "server_startup",
            "selected_submission_probe",
            "poc_database",
            "blocking_error",
            "cleanup",
            "does_not_claim",
        ],
        "server-probe",
        errors,
    )
    require(receipt.get("lane_id") == "cybergym-production-lane", "server probe lane_id is invalid", errors)
    require(receipt.get("status") == "server_probe_passed_verifier_blocked", "server probe status is invalid", errors)
    require(receipt.get("scope") == "submission_server_startup_and_valid_poc_route", "server probe scope is invalid", errors)
    require(receipt.get("script") == "scripts/probe_cybergym_server.py", "server probe script is invalid", errors)
    startup = receipt.get("server_startup")
    require_keys(startup, ["status", "health_probe", "health_status", "mask_map_loaded"], "server-probe.server_startup", errors)
    if isinstance(startup, dict):
        require(startup.get("status") == "passed", "server startup must pass", errors)
        require(startup.get("health_status") == 200, "server startup health status must be 200", errors)
    probe = receipt.get("selected_submission_probe")
    require_keys(
        probe,
        ["real_task_id", "agent_facing_task_id", "agent_id", "checksum_valid", "poc_bytes", "endpoint", "response_status", "response_error"],
        "server-probe.selected_submission_probe",
        errors,
    )
    if isinstance(probe, dict):
        require(probe.get("real_task_id") == "arvo:10400", "server probe real task id must be arvo:10400", errors)
        require(probe.get("agent_facing_task_id") == "7fa395d7dac0", "server probe masked task id is invalid", errors)
        require(probe.get("checksum_valid") is True, "server probe checksum must be valid", errors)
        require(probe.get("poc_bytes") == 4, "server probe PoC byte count should be 4", errors)
        require(probe.get("response_status") == 500, "server probe should block at missing verifier image", errors)
        require("No such image" in str(probe.get("response_error")), "server probe response must cite missing image", errors)
    db = receipt.get("poc_database")
    require_keys(db, ["status", "record_count", "record"], "server-probe.poc_database", errors)
    if isinstance(db, dict):
        require(db.get("status") == "written", "server probe DB status must be written", errors)
        require(db.get("record_count") == 1, "server probe DB should contain one record", errors)
        record = db.get("record")
        require_keys(record, ["agent_id", "task_id", "poc_hash", "poc_length", "vul_exit_code", "fix_exit_code"], "server-probe.poc_database.record", errors)
        if isinstance(record, dict):
            require(record.get("task_id") == "arvo:10400", "server probe DB task id should be unmasked", errors)
            require(record.get("poc_length") == 4, "server probe DB PoC length should be 4", errors)
            require(record.get("vul_exit_code") is None, "server probe must not claim vulnerable verifier exit code", errors)
            require(record.get("fix_exit_code") is None, "server probe must not claim fixed verifier exit code", errors)
    blocker = receipt.get("blocking_error")
    require_keys(blocker, ["stage", "error_type", "primary_error", "meaning"], "server-probe.blocking_error", errors)
    if isinstance(blocker, dict):
        require("n132/arvo:10400-vul" in str(blocker.get("primary_error")), "server probe blocker must cite missing arvo image", errors)
    does_not_claim = receipt.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "vulnerable verifier executed" in does_not_claim, "server probe must not claim vulnerable verifier execution", errors)


def main() -> int:
    errors: list[str] = []
    source = load_json(LANE / "source-pin.json")
    contract = load_json(LANE / "task-contract.json")
    setup = load_json(LANE / "setup-receipt.json")
    smoke = load_json(LANE / "import-smoke-receipt.json")
    server_probe = load_json(LANE / "server-probe-receipt.json")
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
    if isinstance(server_probe, dict):
        validate_server_probe(server_probe, errors)
    else:
        errors.append("server-probe-receipt.json must be an object")
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
