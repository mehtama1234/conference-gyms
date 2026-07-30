#!/usr/bin/env python3
"""Validate all tracked production-lane artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


LANES = [
    {
        "lane_id": "terminaltraj-production-lane",
        "name": "TerminalTraj",
        "validator": "scripts/validate_terminaltraj_lane.py",
        "status": "real_local_run_replay_passed_export_blocked",
        "runtime": "passed",
        "replay": "passed",
        "export": "blocked",
        "summary": "One released TerminalTraj task ran locally, passed its executable verifier, replayed, and emitted a normalized real trace.",
    },
    {
        "lane_id": "cybergym-production-lane",
        "name": "CyberGym",
        "validator": "scripts/validate_cybergym_lane.py",
        "status": "source_pinned_task_manifest_fixture_poc_solved_export_blocked",
        "runtime": "task_manifest_fixture_poc_solved",
        "replay": "task_manifest_fixture_poc_replay_passed",
        "export": "blocked",
        "summary": "CyberGym is source-pinned with a security task contract, arvo:10400 fixture PoC solution plus independent discovery replay, a model-agent command harness ready but blocked on a configured real agent, and a second arvo:1065 task materialized with generated submit.sh, vulnerable/fixed verifier execution, and PoC DB exit codes 0/0 for an empty runtime probe; export remains blocked.",
    },
    {
        "lane_id": "openapps-production-lane",
        "name": "OpenApps",
        "validator": "scripts/validate_openapps_lane.py",
        "status": "source_pinned_browser_runtime_passed_single_task_export_blocked",
        "runtime": "browser_runtime_passed_single_task",
        "replay": "reward_fixture_and_browser_replay_passed",
        "export": "blocked",
        "summary": "OpenApps is source-pinned with package/config smoke, 8 app configs, 28 parsed original tasks, saved-state reward replay, local Chromium library extraction, and one real Playwright/Chromium AddToDo browser GUI task passed with reward 1.0.",
    },
]


def run_validator(script: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode == 0, result.stdout.strip()


def main() -> int:
    results = []
    failed = False
    for lane in LANES:
        ok, output = run_validator(lane["validator"])
        failed = failed or not ok
        entry = dict(lane)
        entry["validator_passed"] = ok
        entry["validator_output"] = output
        results.append(entry)

    real_runtimes = {"passed", "browser_runtime_passed_single_task", "task_manifest_fixture_poc_solved"}
    report = {
        "report_id": "gym-production-readiness-summary-v0-1",
        "lane_count": len(results),
        "validated_lane_count": sum(1 for item in results if item["validator_passed"]),
        "real_local_run_lane_count": sum(1 for item in results if item["runtime"] in real_runtimes),
        "export_blocked_lane_count": sum(1 for item in results if item["export"] == "blocked"),
        "lanes": results,
        "next_meaty_goal": "Run the CyberGym model-agent harness with a real agent command on arvo:10400, capture the resulting normalized trajectory and verifier result, then broaden to more stable README-subset verifier pairs while keeping hosted/SFT/training export blocked.",
    }

    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
