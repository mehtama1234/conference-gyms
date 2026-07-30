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
        "status": "source_pinned_import_smoke_passed_heavy_runtime_blocked",
        "runtime": "blocked_heavy_data",
        "replay": "not_attempted",
        "export": "blocked",
        "summary": "CyberGym is source-pinned with a security task contract and no-heavy import smoke; server/data runtime remains blocked.",
    },
    {
        "lane_id": "openapps-production-lane",
        "name": "OpenApps",
        "validator": "scripts/validate_openapps_lane.py",
        "status": "source_pinned_reward_fixture_passed_browser_runtime_blocked",
        "runtime": "state_reward_fixture_passed_browser_blocked",
        "replay": "not_attempted",
        "export": "blocked",
        "summary": "OpenApps is source-pinned with package/config smoke, 8 app configs, 28 parsed original tasks, and a non-browser saved-state reward fixture; browser/runtime execution remains blocked.",
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

    report = {
        "report_id": "gym-production-readiness-summary-v0-1",
        "lane_count": len(results),
        "validated_lane_count": sum(1 for item in results if item["validator_passed"]),
        "real_local_run_lane_count": sum(1 for item in results if item["runtime"] == "passed"),
        "export_blocked_lane_count": sum(1 for item in results if item["export"] == "blocked"),
        "lanes": results,
        "next_meaty_goal": "Promote OpenApps from source/config smoke to one deterministic local GUI task with app-state reset, dummy or fixture action, reward verifier receipt, cleanup, and normalized GUI trace; then revisit CyberGym heavy server runtime.",
    }

    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
