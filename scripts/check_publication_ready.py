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

    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    upstream_name = upstream.stdout.strip() if upstream.returncode == 0 else None
    sync_state = "unknown"
    if upstream_name:
        counts = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream_name}"])
        if counts.returncode == 0:
            ahead, behind = [int(part) for part in counts.stdout.split()]
            if ahead == 0 and behind == 0:
                sync_state = "synced"
            elif ahead > 0:
                sync_state = "ahead"
            elif behind > 0:
                sync_state = "behind"
    else:
        errors.append("main does not track an upstream branch")

    if sync_state == "ahead":
        next_action = "git push"
    elif remote_exists and not errors and sync_state == "synced":
        next_action = "No publication action required."
    else:
        next_action = status["next_required_action"]

    publication_status = "blocked"
    if not errors and remote_exists and sync_state == "synced":
        publication_status = "published_synced"
    elif not errors and remote_exists:
        publication_status = "ready_to_push"

    report = {
        "publication_status": publication_status,
        "validation_passed": validation.returncode == 0,
        "worktree_clean": not git_status.stdout.strip(),
        "origin": origin,
        "remote_exists": remote_exists,
        "upstream": upstream_name,
        "sync_state": sync_state,
        "errors": errors,
        "next_action": next_action,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors or not remote_exists else 0


if __name__ == "__main__":
    raise SystemExit(main())
