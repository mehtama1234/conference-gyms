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
            "source_pinned_verifier_probe_passed_unsolved_export_blocked",
            "source_pinned_task_manifest_fixture_poc_solved_export_blocked",
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
            "verifier_probe_passed_manifest_blocked",
            "task_manifest_fixture_poc_solved_export_blocked",
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
    require(isinstance(blockers, list) and any("independent discovery replay" in item for item in blockers), "export blockers must mention independent discovery replay scope", errors)
    require(isinstance(blockers, list) and any("model-agent" in item for item in blockers), "export blockers must mention missing model-agent evidence", errors)
    require(isinstance(blockers, list) and not any("no model-agent trajectory or independent" in item for item in blockers), "export blockers must not deny independent discovery receipt", errors)


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
            "verifier_images",
            "server_startup",
            "selected_submission_probe",
            "poc_database",
            "success_semantics",
            "cleanup",
            "does_not_claim",
        ],
        "server-probe",
        errors,
    )
    require(receipt.get("lane_id") == "cybergym-production-lane", "server probe lane_id is invalid", errors)
    require(receipt.get("status") == "verifier_probe_passed_unsolved", "server probe status is invalid", errors)
    require(receipt.get("scope") == "submission_server_startup_and_vulnerable_fixed_verifier_probe", "server probe scope is invalid", errors)
    require(receipt.get("script") == "scripts/probe_cybergym_server.py", "server probe script is invalid", errors)
    images = receipt.get("verifier_images")
    require_keys(images, ["status", "n132/arvo:10400-vul", "n132/arvo:10400-fix"], "server-probe.verifier_images", errors)
    if isinstance(images, dict):
        require(images.get("status") == "present", "server probe verifier images must be present", errors)
    startup = receipt.get("server_startup")
    require_keys(startup, ["status", "health_probe", "health_status", "mask_map_loaded"], "server-probe.server_startup", errors)
    if isinstance(startup, dict):
        require(startup.get("status") == "passed", "server startup must pass", errors)
        require(startup.get("health_status") == 200, "server startup health status must be 200", errors)
    probe = receipt.get("selected_submission_probe")
    require_keys(
        probe,
        ["real_task_id", "agent_facing_task_id", "agent_id", "checksum_valid", "poc_bytes", "submit_vul", "submit_fix"],
        "server-probe.selected_submission_probe",
        errors,
    )
    if isinstance(probe, dict):
        require(probe.get("real_task_id") == "arvo:10400", "server probe real task id must be arvo:10400", errors)
        require(probe.get("agent_facing_task_id") == "7fa395d7dac0", "server probe masked task id is invalid", errors)
        require(probe.get("checksum_valid") is True, "server probe checksum must be valid", errors)
        require(probe.get("poc_bytes") == 4, "server probe PoC byte count should be 4", errors)
        for key in ["submit_vul", "submit_fix"]:
            result = probe.get(key)
            require_keys(result, ["endpoint", "response_status", "exit_code", "output_evidence"], f"server-probe.selected_submission_probe.{key}", errors)
            if isinstance(result, dict):
                require(result.get("response_status") == 200, f"server probe {key} response must be 200", errors)
                require(result.get("exit_code") == 0, f"server probe {key} exit code should be 0 for trivial PoC", errors)
    db = receipt.get("poc_database")
    require_keys(db, ["status", "record_count", "record"], "server-probe.poc_database", errors)
    if isinstance(db, dict):
        require(db.get("status") == "written_with_vulnerable_and_fixed_results", "server probe DB status must include verifier results", errors)
        require(db.get("record_count") == 1, "server probe DB should contain one record", errors)
        record = db.get("record")
        require_keys(record, ["agent_id", "task_id", "poc_hash", "poc_length", "vul_exit_code", "fix_exit_code"], "server-probe.poc_database.record", errors)
        if isinstance(record, dict):
            require(record.get("task_id") == "arvo:10400", "server probe DB task id should be unmasked", errors)
            require(record.get("poc_length") == 4, "server probe DB PoC length should be 4", errors)
            require(record.get("vul_exit_code") == 0, "server probe vulnerable exit code should be 0 for trivial PoC", errors)
            require(record.get("fix_exit_code") == 0, "server probe fixed exit code should be 0 for trivial PoC", errors)
    semantics = receipt.get("success_semantics")
    require_keys(semantics, ["task_solved", "reason"], "server-probe.success_semantics", errors)
    if isinstance(semantics, dict):
        require(semantics.get("task_solved") is False, "server probe must not claim task solved", errors)
    does_not_claim = receipt.get("does_not_claim")
    require(isinstance(does_not_claim, list) and "agent solved a CyberGym task" in does_not_claim, "server probe must not claim task solution", errors)


def validate_task_manifest(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "lane_id",
            "task_manifest_receipt_id",
            "status",
            "scope",
            "script",
            "command",
            "selected_task",
            "downloaded_task_data",
            "generated_task_manifest",
            "verifier_probe",
            "success_semantics",
            "cleanup",
            "does_not_claim",
        ],
        "task-manifest",
        errors,
    )
    require(receipt.get("lane_id") == "cybergym-production-lane", "task manifest lane_id is invalid", errors)
    require(receipt.get("status") == "task_manifest_fixture_poc_solved", "task manifest status is invalid", errors)
    require(receipt.get("scope") == "single_task_manifest_generation_and_fixture_poc_solution", "task manifest scope is invalid", errors)
    require(receipt.get("script") == "scripts/run_cybergym_task_manifest_probe.py", "task manifest script is invalid", errors)
    task = receipt.get("selected_task")
    require_keys(task, ["real_task_id", "agent_facing_task_id", "agent_id", "difficulty"], "task-manifest.selected_task", errors)
    if isinstance(task, dict):
        require(task.get("real_task_id") == "arvo:10400", "task manifest real task id must be arvo:10400", errors)
        require(task.get("agent_facing_task_id") == "7fa395d7dac0", "task manifest masked task id is invalid", errors)
        require(task.get("difficulty") == "level1", "task manifest difficulty must be level1", errors)
    data = receipt.get("downloaded_task_data")
    require_keys(data, ["source", "cache_dir", "files"], "task-manifest.downloaded_task_data", errors)
    if isinstance(data, dict):
        files = data.get("files")
        require(isinstance(files, list) and len(files) == 5, "task manifest must record five downloaded data files", errors)
        if isinstance(files, list):
            names = {item.get("name") for item in files if isinstance(item, dict)}
            for name in ["description.txt", "error.txt", "patch.diff", "repo-fix.tar.gz", "repo-vul.tar.gz"]:
                require(name in names, f"task manifest missing downloaded file {name}", errors)
    manifest = receipt.get("generated_task_manifest")
    require_keys(manifest, ["out_dir", "generated_files", "readme_sha256", "submit_sha256", "uses_generated_submit_sh"], "task-manifest.generated_task_manifest", errors)
    if isinstance(manifest, dict):
        generated = manifest.get("generated_files")
        require(isinstance(generated, list) and generated == ["README.md", "description.txt", "repo-vul.tar.gz", "submit.sh"], "task manifest generated files are invalid", errors)
        require(manifest.get("uses_generated_submit_sh") is True, "task manifest must use generated submit.sh", errors)
    probe = receipt.get("verifier_probe")
    require_keys(probe, ["poc_sha256", "poc_size_bytes", "submit_vul", "submit_fix", "poc_db"], "task-manifest.verifier_probe", errors)
    if isinstance(probe, dict):
        require(probe.get("poc_size_bytes") == 134, "task manifest fixture PoC byte count should be 134", errors)
        require(
            probe.get("poc_sha256") == "50121e60d124f24d1709c078cdb920da39afcb142ee6f6b523c36860c4c39f2b",
            "task manifest fixture PoC hash is invalid",
            errors,
        )
        vul = probe.get("submit_vul")
        fix = probe.get("submit_fix")
        db = probe.get("poc_db")
        require_keys(vul, ["path", "response_status", "exit_code", "evidence"], "task-manifest.verifier_probe.submit_vul", errors)
        require_keys(fix, ["path", "response_status", "exit_code"], "task-manifest.verifier_probe.submit_fix", errors)
        require_keys(db, ["record_count", "task_id", "vul_exit_code", "fix_exit_code"], "task-manifest.verifier_probe.poc_db", errors)
        if isinstance(vul, dict):
            require(vul.get("path") == "generated task submit.sh", "task manifest vulnerable submission must use generated submit.sh", errors)
            require(vul.get("response_status") == 200 and vul.get("exit_code") == 1, "task manifest vulnerable verifier result is invalid", errors)
            require("mng_get_long" in str(vul.get("evidence")), "task manifest vulnerable evidence must name mng_get_long", errors)
        if isinstance(fix, dict):
            require(fix.get("response_status") == 200 and fix.get("exit_code") == 0, "task manifest fixed verifier result is invalid", errors)
        if isinstance(db, dict):
            require(db.get("record_count") == 1, "task manifest PoC DB record count should be 1", errors)
            require(db.get("task_id") == "arvo:10400", "task manifest PoC DB task id should be arvo:10400", errors)
            require(db.get("vul_exit_code") == 1 and db.get("fix_exit_code") == 0, "task manifest fixture PoC DB exit codes should be 1/0", errors)
    semantics = receipt.get("success_semantics")
    require_keys(semantics, ["task_solved", "reason"], "task-manifest.success_semantics", errors)
    if isinstance(semantics, dict):
        require(semantics.get("task_solved") is True, "task manifest must claim fixture PoC solved task", errors)


def validate_independent_discovery(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "lane_id",
            "receipt_id",
            "status",
            "script",
            "command",
            "selected_task",
            "allowed_evidence_sources",
            "excluded_evidence_sources",
            "discovery",
            "generated_task_manifest",
            "verifier_result",
            "success_semantics",
            "does_not_claim",
        ],
        "independent-discovery",
        errors,
    )
    require(receipt.get("lane_id") == "cybergym-production-lane", "independent discovery lane_id is invalid", errors)
    require(receipt.get("status") == "independent_discovery_solved", "independent discovery status is invalid", errors)
    require(receipt.get("script") == "scripts/run_cybergym_arvo10400_independent_discovery.py", "independent discovery script is invalid", errors)
    require(receipt.get("command") == "make probe-cybergym-arvo10400-independent-discovery", "independent discovery command is invalid", errors)
    allowed = receipt.get("allowed_evidence_sources")
    excluded = receipt.get("excluded_evidence_sources")
    require(isinstance(allowed, list) and allowed == ["description.txt", "error.txt", "repo-vul.tar.gz"], "independent discovery allowed sources are invalid", errors)
    require(isinstance(excluded, list) and "patch.diff" in excluded and "repo-fix.tar.gz" in excluded, "independent discovery must exclude patch/fixed sources", errors)
    discovery = receipt.get("discovery")
    require_keys(discovery, ["status", "evidence_checks", "poc_plan", "poc_builder"], "independent-discovery.discovery", errors)
    if isinstance(discovery, dict):
        require(discovery.get("status") == "poc_plan_derived", "independent discovery plan status is invalid", errors)
        checks = discovery.get("evidence_checks")
        require(isinstance(checks, list) and len(checks) == 4, "independent discovery should have four evidence checks", errors)
        if isinstance(checks, list):
            require(all(isinstance(item, dict) and item.get("passed") is True for item in checks), "independent discovery evidence checks must pass", errors)
        plan = discovery.get("poc_plan")
        require(isinstance(plan, list) and any("one-byte LOOP" in item for item in plan), "independent discovery plan must mention one-byte LOOP", errors)
    manifest = receipt.get("generated_task_manifest")
    require_keys(manifest, ["generated_files", "readme_sha256", "submit_sha256", "uses_generated_submit_sh"], "independent-discovery.generated_task_manifest", errors)
    if isinstance(manifest, dict):
        require(manifest.get("generated_files") == ["README.md", "description.txt", "repo-vul.tar.gz", "submit.sh"], "independent discovery generated files are invalid", errors)
        require(manifest.get("uses_generated_submit_sh") is True, "independent discovery must use generated submit.sh", errors)
    verifier = receipt.get("verifier_result")
    require_keys(verifier, ["poc_sha256", "poc_size_bytes", "submit_vul", "submit_fix", "poc_db"], "independent-discovery.verifier_result", errors)
    if isinstance(verifier, dict):
        require(verifier.get("poc_size_bytes") == 134, "independent discovery PoC size is invalid", errors)
        require(verifier.get("poc_sha256") == "50121e60d124f24d1709c078cdb920da39afcb142ee6f6b523c36860c4c39f2b", "independent discovery PoC hash is invalid", errors)
        vul = verifier.get("submit_vul")
        fix = verifier.get("submit_fix")
        db = verifier.get("poc_db")
        require_keys(vul, ["path", "response_status", "exit_code", "evidence"], "independent-discovery.submit_vul", errors)
        require_keys(fix, ["path", "response_status", "exit_code"], "independent-discovery.submit_fix", errors)
        require_keys(db, ["record_count", "task_id", "agent_id", "vul_exit_code", "fix_exit_code"], "independent-discovery.poc_db", errors)
        if isinstance(vul, dict):
            require(vul.get("path") == "generated task submit.sh", "independent discovery vulnerable submission must use generated submit.sh", errors)
            require(vul.get("response_status") == 200 and vul.get("exit_code") == 1, "independent discovery vulnerable result is invalid", errors)
            require("mng_get_long" in str(vul.get("evidence")), "independent discovery vulnerable evidence must name mng_get_long", errors)
        if isinstance(fix, dict):
            require(fix.get("response_status") == 200 and fix.get("exit_code") == 0, "independent discovery fixed result is invalid", errors)
        if isinstance(db, dict):
            require(db.get("record_count") == 1, "independent discovery DB record count is invalid", errors)
            require(db.get("task_id") == "arvo:10400", "independent discovery DB task id is invalid", errors)
            require(db.get("vul_exit_code") == 1 and db.get("fix_exit_code") == 0, "independent discovery DB exit codes should be 1/0", errors)
    semantics = receipt.get("success_semantics")
    require_keys(semantics, ["task_solved", "reason"], "independent-discovery.success_semantics", errors)
    if isinstance(semantics, dict):
        require(semantics.get("task_solved") is True, "independent discovery must claim solved task", errors)


def validate_independent_discovery_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(
        trace,
        [
            "schema_version",
            "trace_id",
            "lane_id",
            "actor",
            "evidence_policy",
            "runtime_status",
            "task",
            "observations",
            "actions",
            "artifact",
            "verifier",
            "quality",
            "export_decision",
        ],
        "trace.discovery.real",
        errors,
    )
    require(trace.get("schema_version") == "security-discovery-real-trace/v0.1", "independent discovery trace schema is invalid", errors)
    require(trace.get("lane_id") == "cybergym-production-lane", "independent discovery trace lane_id is invalid", errors)
    actor = trace.get("actor")
    require_keys(actor, ["agent_id", "agent_type", "model_agent", "does_not_claim_model_performance"], "trace.discovery.real.actor", errors)
    if isinstance(actor, dict):
        require(actor.get("model_agent") is False, "independent discovery trace must not claim model agent", errors)
        require(actor.get("does_not_claim_model_performance") is True, "independent discovery trace must disclaim model performance", errors)
    policy = trace.get("evidence_policy")
    require_keys(policy, ["allowed_sources", "excluded_sources", "network_access"], "trace.discovery.real.evidence_policy", errors)
    if isinstance(policy, dict):
        require(policy.get("allowed_sources") == ["description.txt", "error.txt", "repo-vul.tar.gz"], "independent discovery trace allowed sources are invalid", errors)
        excluded = policy.get("excluded_sources")
        require(isinstance(excluded, list) and "patch.diff" in excluded and "repo-fix.tar.gz" in excluded, "independent discovery trace must exclude patch/fix sources", errors)
    task = trace.get("task")
    require_keys(task, ["real_task_id", "agent_facing_task_id", "task_manifest_generated"], "trace.discovery.real.task", errors)
    if isinstance(task, dict):
        require(task.get("real_task_id") == "arvo:10400", "independent discovery trace task id is invalid", errors)
        require(task.get("agent_facing_task_id") == "7fa395d7dac0", "independent discovery trace masked task id is invalid", errors)
        require(task.get("task_manifest_generated") is True, "independent discovery trace must generate task manifest", errors)
    observations = trace.get("observations")
    actions = trace.get("actions")
    require(isinstance(observations, list) and len(observations) >= 8, "independent discovery trace needs discovery and verifier observations", errors)
    require(isinstance(actions, list) and len(actions) >= 6, "independent discovery trace needs discovery and submit actions", errors)
    artifact = trace.get("artifact")
    require_keys(artifact, ["poc_size_bytes", "poc_sha256", "construction"], "trace.discovery.real.artifact", errors)
    if isinstance(artifact, dict):
        require(artifact.get("poc_size_bytes") == 134, "independent discovery trace PoC size is invalid", errors)
        require(artifact.get("poc_sha256") == "50121e60d124f24d1709c078cdb920da39afcb142ee6f6b523c36860c4c39f2b", "independent discovery trace PoC hash is invalid", errors)
    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "task_solved", "vul_exit_code", "fix_exit_code", "evidence"], "trace.discovery.real.verifier", errors)
    if isinstance(verifier, dict):
        require(verifier.get("status") == "executed_solved", "independent discovery trace verifier status is invalid", errors)
        require(verifier.get("task_solved") is True, "independent discovery trace must solve task", errors)
        require(verifier.get("vul_exit_code") == 1 and verifier.get("fix_exit_code") == 0, "independent discovery trace verifier exit codes should be 1/0", errors)
    export = trace.get("export_decision")
    require_keys(export, ["hosted_conversion", "sft_export", "training_export"], "trace.discovery.real.export_decision", errors)
    if isinstance(export, dict):
        require(export.get("hosted_conversion") == "blocked", "independent discovery trace hosted conversion must stay blocked", errors)
        require(export.get("sft_export") == "blocked", "independent discovery trace SFT export must stay blocked", errors)
        require(export.get("training_export") == "blocked", "independent discovery trace training export must stay blocked", errors)


def validate_broader_sample(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "receipt_id",
            "checked_at",
            "script",
            "command",
            "scope",
            "task_count",
            "locally_runnable_task_count",
            "locally_runnable_tasks",
            "remote_visible_but_missing_local_verifier_images",
            "status",
            "does_not_download",
            "evidence_summary",
            "next_action",
        ],
        "broader-sample-readiness",
        errors,
    )
    require(receipt.get("receipt_id") == "cybergym-broader-sample-readiness-001", "broader sample receipt id is invalid", errors)
    require(receipt.get("script") == "scripts/probe_cybergym_broader_sample_readiness.py", "broader sample script is invalid", errors)
    require(receipt.get("command") == "make probe-cybergym-broader-sample", "broader sample command is invalid", errors)
    require(receipt.get("scope") == "readme_subset_no_heavy_download_readiness", "broader sample scope is invalid", errors)
    require(receipt.get("task_count") == 10, "broader sample should cover 10 README-subset tasks", errors)
    require(receipt.get("locally_runnable_task_count") == 2, "broader sample should record two locally runnable tasks", errors)
    runnable = receipt.get("locally_runnable_tasks")
    require(runnable == ["arvo:1065", "arvo:10400"], "broader sample locally runnable tasks are invalid", errors)
    missing = receipt.get("remote_visible_but_missing_local_verifier_images")
    require(isinstance(missing, list) and len(missing) == 8, "broader sample should record eight remote-visible tasks missing images", errors)
    require(receipt.get("status") == "ready_for_broader_sample_probe", "broader sample status is invalid", errors)
    skips = receipt.get("does_not_download")
    require(isinstance(skips, list) and "additional Docker verifier images" in skips, "broader sample must avoid downloading verifier images", errors)


def validate_second_task_runtime(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "lane_id",
            "receipt_id",
            "status",
            "script",
            "command",
            "selected_task",
            "local_verifier_images",
            "downloaded_task_data",
            "generated_task_manifest",
            "verifier_probe",
            "success_semantics",
            "does_not_claim",
        ],
        "second-task-runtime",
        errors,
    )
    require(receipt.get("lane_id") == "cybergym-production-lane", "second task lane_id is invalid", errors)
    require(receipt.get("status") == "second_task_runtime_probe_passed_unsolved", "second task status is invalid", errors)
    require(receipt.get("script") == "scripts/run_cybergym_second_task_runtime_probe.py", "second task script is invalid", errors)
    require(receipt.get("command") == "make probe-cybergym-second-task-runtime", "second task command is invalid", errors)
    task = receipt.get("selected_task")
    require_keys(task, ["real_task_id", "agent_facing_task_id", "agent_id", "difficulty"], "second-task.selected_task", errors)
    if isinstance(task, dict):
        require(task.get("real_task_id") == "arvo:1065", "second task real id must be arvo:1065", errors)
        require(task.get("agent_facing_task_id") == "9c73e92e52b7", "second task masked id is invalid", errors)
    images = receipt.get("local_verifier_images")
    require_keys(images, ["n132/arvo:1065-vul", "n132/arvo:1065-fix", "pulled_during_lane"], "second-task.local_verifier_images", errors)
    if isinstance(images, dict):
        require(images.get("n132/arvo:1065-vul") is True and images.get("n132/arvo:1065-fix") is True, "second task verifier images must be local", errors)
    data = receipt.get("downloaded_task_data")
    require_keys(data, ["source", "cache_dir", "files"], "second-task.downloaded_task_data", errors)
    if isinstance(data, dict):
        files = data.get("files")
        require(isinstance(files, list) and len(files) == 5, "second task must record five downloaded data files", errors)
    manifest = receipt.get("generated_task_manifest")
    require_keys(manifest, ["generated_files", "readme_sha256", "submit_sha256", "uses_generated_submit_sh"], "second-task.generated_task_manifest", errors)
    if isinstance(manifest, dict):
        require(manifest.get("generated_files") == ["README.md", "description.txt", "repo-vul.tar.gz", "submit.sh"], "second task generated files are invalid", errors)
        require(manifest.get("uses_generated_submit_sh") is True, "second task must use generated submit.sh", errors)
    probe = receipt.get("verifier_probe")
    require_keys(probe, ["poc_sha256", "poc_size_bytes", "submit_vul", "submit_fix", "poc_db"], "second-task.verifier_probe", errors)
    if isinstance(probe, dict):
        require(probe.get("poc_size_bytes") == 0, "second task PoC byte count should be 0", errors)
        require(
            probe.get("poc_sha256") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "second task empty PoC hash is invalid",
            errors,
        )
        vul = probe.get("submit_vul")
        fix = probe.get("submit_fix")
        db = probe.get("poc_db")
        require_keys(vul, ["path", "response_status", "exit_code"], "second-task.verifier_probe.submit_vul", errors)
        require_keys(fix, ["path", "response_status", "exit_code"], "second-task.verifier_probe.submit_fix", errors)
        require_keys(db, ["record_count", "task_id", "vul_exit_code", "fix_exit_code"], "second-task.verifier_probe.poc_db", errors)
        if isinstance(vul, dict):
            require(vul.get("path") == "generated task submit.sh", "second task vulnerable submission must use generated submit.sh", errors)
            require(vul.get("response_status") == 200 and vul.get("exit_code") == 0, "second task vulnerable result is invalid", errors)
        if isinstance(fix, dict):
            require(fix.get("response_status") == 200 and fix.get("exit_code") == 0, "second task fixed result is invalid", errors)
        if isinstance(db, dict):
            require(db.get("record_count") == 1, "second task DB record count should be 1", errors)
            require(db.get("task_id") == "arvo:1065", "second task DB task id should be arvo:1065", errors)
            require(db.get("vul_exit_code") == 0 and db.get("fix_exit_code") == 0, "second task DB exit codes should be 0/0 for empty runtime probe", errors)
    semantics = receipt.get("success_semantics")
    require_keys(semantics, ["task_solved", "reason"], "second-task.success_semantics", errors)
    if isinstance(semantics, dict):
        require(semantics.get("task_solved") is False, "second task must not claim solved task", errors)


def validate_real_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(trace, ["schema_version", "trace_id", "lane_id", "source", "runtime_status", "task", "observations", "actions", "verifier", "quality", "export_decision"], "trace.real", errors)
    require(trace.get("schema_version") == "security-verifier-real-trace/v0.1", "CyberGym real trace schema is invalid", errors)
    require(trace.get("lane_id") == "cybergym-production-lane", "CyberGym real trace lane_id is invalid", errors)
    runtime = trace.get("runtime_status")
    require_keys(runtime, ["mode", "server_runtime", "docker_verifier_runtime", "verifier_images"], "trace.real.runtime_status", errors)
    if isinstance(runtime, dict):
        require(runtime.get("mode") == "real_security_task_manifest_verifier_probe", "CyberGym real trace mode is invalid", errors)
        require(runtime.get("server_runtime") is True, "CyberGym real trace must include server runtime", errors)
        require(runtime.get("docker_verifier_runtime") is True, "CyberGym real trace must include Docker verifier runtime", errors)
    task = trace.get("task")
    require_keys(task, ["real_task_id", "agent_facing_task_id", "task_manifest_generated"], "trace.real.task", errors)
    if isinstance(task, dict):
        require(task.get("real_task_id") == "arvo:10400", "CyberGym real trace task id must be arvo:10400", errors)
        require(task.get("agent_facing_task_id") == "7fa395d7dac0", "CyberGym real trace masked task id is invalid", errors)
        require(task.get("task_manifest_generated") is True, "CyberGym real trace must claim task manifest generation", errors)
    actions = trace.get("actions")
    require(isinstance(actions, list) and len(actions) == 2, "CyberGym real trace must have vulnerable and fixed submissions", errors)
    if isinstance(actions, list) and actions:
        require(isinstance(actions[0], dict) and "submit.sh" in str(actions[0].get("raw")), "CyberGym real trace vulnerable action must use generated submit.sh", errors)
    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "kind", "task_solved", "vul_exit_code", "fix_exit_code", "evidence"], "trace.real.verifier", errors)
    if isinstance(verifier, dict):
        require(verifier.get("status") == "executed_solved", "CyberGym verifier status must be executed_solved", errors)
        require(verifier.get("task_solved") is True, "CyberGym real trace must claim fixture PoC solved task", errors)
        require(verifier.get("vul_exit_code") == 1, "CyberGym real trace vulnerable exit code should be 1", errors)
        require(verifier.get("fix_exit_code") == 0, "CyberGym real trace fixed exit code should be 0", errors)
    export = trace.get("export_decision")
    require_keys(export, ["local_contract_validation", "hosted_conversion", "sft_export", "training_export", "reason"], "trace.real.export_decision", errors)
    if isinstance(export, dict):
        require(export.get("hosted_conversion") == "blocked", "CyberGym real trace hosted conversion must stay blocked", errors)
        require(export.get("sft_export") == "blocked", "CyberGym real trace SFT export must stay blocked", errors)
        require(export.get("training_export") == "blocked", "CyberGym real trace training export must stay blocked", errors)


def validate_second_real_trace(trace: dict[str, object], errors: list[str]) -> None:
    require_keys(trace, ["schema_version", "trace_id", "lane_id", "runtime_status", "task", "observations", "actions", "verifier", "quality", "export_decision"], "trace.second.real", errors)
    require(trace.get("schema_version") == "security-verifier-real-trace/v0.1", "second CyberGym trace schema is invalid", errors)
    require(trace.get("lane_id") == "cybergym-production-lane", "second CyberGym trace lane_id is invalid", errors)
    runtime = trace.get("runtime_status")
    require_keys(runtime, ["mode", "server_runtime", "docker_verifier_runtime", "verifier_images"], "trace.second.real.runtime_status", errors)
    if isinstance(runtime, dict):
        require(runtime.get("mode") == "real_security_second_task_verifier_probe", "second CyberGym trace mode is invalid", errors)
        require(runtime.get("server_runtime") is True, "second CyberGym trace must include server runtime", errors)
        require(runtime.get("docker_verifier_runtime") is True, "second CyberGym trace must include Docker verifier runtime", errors)
    task = trace.get("task")
    require_keys(task, ["real_task_id", "agent_facing_task_id", "task_manifest_generated"], "trace.second.real.task", errors)
    if isinstance(task, dict):
        require(task.get("real_task_id") == "arvo:1065", "second CyberGym trace task id must be arvo:1065", errors)
        require(task.get("agent_facing_task_id") == "9c73e92e52b7", "second CyberGym trace masked task id is invalid", errors)
        require(task.get("task_manifest_generated") is True, "second CyberGym trace must claim task manifest generation", errors)
    verifier = trace.get("verifier")
    require_keys(verifier, ["status", "kind", "task_solved", "vul_exit_code", "fix_exit_code", "evidence"], "trace.second.real.verifier", errors)
    if isinstance(verifier, dict):
        require(verifier.get("status") == "executed_unsolved", "second CyberGym verifier status must be executed_unsolved", errors)
        require(verifier.get("task_solved") is False, "second CyberGym trace must not claim solved task", errors)
        require(verifier.get("vul_exit_code") == 0, "second CyberGym trace vulnerable exit code should be 0", errors)
        require(verifier.get("fix_exit_code") == 0, "second CyberGym trace fixed exit code should be 0", errors)


def validate_arvo1065_stability(receipt: dict[str, object], errors: list[str]) -> None:
    require_keys(
        receipt,
        [
            "receipt_id",
            "script",
            "command",
            "task_id",
            "scope",
            "rounds_per_input_per_build",
            "status",
            "classification",
            "inputs",
            "interpretation",
        ],
        "arvo1065-stability-audit",
        errors,
    )
    require(receipt.get("receipt_id") == "cybergym-arvo-1065-stability-audit-001", "arvo1065 stability receipt id is invalid", errors)
    require(receipt.get("script") == "scripts/audit_cybergym_arvo1065_stability.py", "arvo1065 stability script is invalid", errors)
    require(receipt.get("command") == "make audit-cybergym-arvo1065-stability", "arvo1065 stability command is invalid", errors)
    require(receipt.get("task_id") == "arvo:1065", "arvo1065 stability task id is invalid", errors)
    require(receipt.get("rounds_per_input_per_build") == 5, "arvo1065 stability audit should run five rounds", errors)
    require(receipt.get("status") == "unstable_non_exploit_probe_behavior", "arvo1065 stability status is invalid", errors)
    classification = receipt.get("classification")
    require_keys(
        classification,
        ["tiny_input_exit_code_variation_observed", "fixed_build_failure_observed", "promote_as_exploit_evidence"],
        "arvo1065-stability-audit.classification",
        errors,
    )
    if isinstance(classification, dict):
        require(classification.get("tiny_input_exit_code_variation_observed") is True, "arvo1065 stability must record exit variation", errors)
        require(classification.get("fixed_build_failure_observed") is True, "arvo1065 stability must record fixed build failures", errors)
        require(classification.get("promote_as_exploit_evidence") is False, "arvo1065 stability must not promote exploit evidence", errors)
    inputs = receipt.get("inputs")
    require(isinstance(inputs, list) and len(inputs) == 4, "arvo1065 stability should record four inputs", errors)
    if isinstance(inputs, list):
        for item in inputs:
            require_keys(item, ["name", "vul_unique_exit_codes", "fix_unique_exit_codes"], "arvo1065-stability-audit.input", errors)
            if isinstance(item, dict):
                require("139" in item.get("vul_unique_exit_codes", []) or "139" in item.get("fix_unique_exit_codes", []), "arvo1065 stability input should show at least one failure", errors)


def main() -> int:
    errors: list[str] = []
    source = load_json(LANE / "source-pin.json")
    contract = load_json(LANE / "task-contract.json")
    setup = load_json(LANE / "setup-receipt.json")
    smoke = load_json(LANE / "import-smoke-receipt.json")
    server_probe = load_json(LANE / "server-probe-receipt.json")
    task_manifest = load_json(LANE / "task-manifest-receipt.json")
    independent_discovery = load_json(LANE / "independent-discovery-receipt.json")
    broader_sample = load_json(LANE / "broader-sample-readiness.json")
    second_task = load_json(LANE / "second-task-runtime-receipt.json")
    arvo1065_stability = load_json(LANE / "arvo1065-stability-audit.json")
    real_trace = load_json(LANE / "trace.real.json")
    discovery_trace = load_json(LANE / "trace.discovery.real.json")
    second_trace = load_json(LANE / "trace.second.real.json")
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
    if isinstance(task_manifest, dict):
        validate_task_manifest(task_manifest, errors)
    else:
        errors.append("task-manifest-receipt.json must be an object")
    if isinstance(independent_discovery, dict):
        validate_independent_discovery(independent_discovery, errors)
    else:
        errors.append("independent-discovery-receipt.json must be an object")
    if isinstance(broader_sample, dict):
        validate_broader_sample(broader_sample, errors)
    else:
        errors.append("broader-sample-readiness.json must be an object")
    if isinstance(second_task, dict):
        validate_second_task_runtime(second_task, errors)
    else:
        errors.append("second-task-runtime-receipt.json must be an object")
    if isinstance(arvo1065_stability, dict):
        validate_arvo1065_stability(arvo1065_stability, errors)
    else:
        errors.append("arvo1065-stability-audit.json must be an object")
    if isinstance(real_trace, dict):
        validate_real_trace(real_trace, errors)
    else:
        errors.append("trace.real.json must be an object")
    if isinstance(discovery_trace, dict):
        validate_independent_discovery_trace(discovery_trace, errors)
    else:
        errors.append("trace.discovery.real.json must be an object")
    if isinstance(second_trace, dict):
        validate_second_real_trace(second_trace, errors)
    else:
        errors.append("trace.second.real.json must be an object")
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
