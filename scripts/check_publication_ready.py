#!/usr/bin/env python3
"""Check whether the gym analysis repo is ready to publish."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "PUBLICATION_STATUS.json"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    errors: list[str] = []

    validation = run(["make", "validate"])
    if validation.returncode != 0:
        errors.append("make validate failed")

    git_status = run(["git", "status", "--short"])
    if git_status.stdout.strip():
        errors.append("tracked worktree is not clean")

    remote = run(["git", "remote", "get-url", "origin"])
    if remote.returncode != 0:
        errors.append("origin remote is not configured")
        origin = None
    else:
        origin = remote.stdout.strip()
        if origin != status["configured_origin"]:
            errors.append(f"origin remote mismatch: {origin}")

    remote_exists = False
    if origin:
        ls_remote = run(["git", "ls-remote", origin, "HEAD"])
        remote_exists = ls_remote.returncode == 0

    report = {
        "publication_status": "ready_to_push" if not errors and remote_exists else "blocked",
        "validation_passed": validation.returncode == 0,
        "worktree_clean": not git_status.stdout.strip(),
        "origin": origin,
        "remote_exists": remote_exists,
        "errors": errors,
        "next_action": "git push -u origin main" if remote_exists and not errors else status["next_required_action"],
    }
    print(json.dumps(report, indent=2))
    return 1 if errors or not remote_exists else 0


if __name__ == "__main__":
    raise SystemExit(main())
