#!/usr/bin/env python3
"""Audit repeatability of small arvo:1065 verifier probes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "cybergym-arvo1065-stability"

INPUTS = {
    "empty": b"",
    "hello_text": b"hello\n",
    "one_null": b"\x00",
    "jpeg_empty": b"\xff\xd8\xff\xd9",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def docker_exit(image: str, poc_path: Path) -> int | str:
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "-v",
            f"{poc_path}:/tmp/poc:ro",
            image,
            "/bin/bash",
            "-lc",
            "timeout -s SIGKILL 10 /bin/arvo >/tmp/out 2>&1",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode == 125:
        return f"docker_error:{result.stdout[-500:]}"
    return result.returncode


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    rounds = 5
    inputs = []
    any_variation = False
    any_fixed_failure = False
    for name, payload in INPUTS.items():
        path = CACHE / f"{name}.poc"
        path.write_bytes(payload)
        vul_codes = [docker_exit("n132/arvo:1065-vul", path) for _ in range(rounds)]
        fix_codes = [docker_exit("n132/arvo:1065-fix", path) for _ in range(rounds)]
        vul_unique = sorted({str(code) for code in vul_codes})
        fix_unique = sorted({str(code) for code in fix_codes})
        any_variation = any_variation or len(vul_unique) > 1 or len(fix_unique) > 1
        any_fixed_failure = any_fixed_failure or any(str(code) != "0" for code in fix_unique)
        inputs.append(
            {
                "name": name,
                "size_bytes": len(payload),
                "sha256": sha256(payload),
                "vul_exit_codes": vul_codes,
                "fix_exit_codes": fix_codes,
                "vul_unique_exit_codes": vul_unique,
                "fix_unique_exit_codes": fix_unique,
            }
        )

    report = {
        "receipt_id": "cybergym-arvo-1065-stability-audit-001",
        "checked_at": "2026-07-30",
        "script": "scripts/audit_cybergym_arvo1065_stability.py",
        "command": "make audit-cybergym-arvo1065-stability",
        "task_id": "arvo:1065",
        "scope": "direct_docker_repeatability_for_small_non_exploit_inputs",
        "rounds_per_input_per_build": rounds,
        "status": "unstable_non_exploit_probe_behavior" if any_variation or any_fixed_failure else "stable_non_exploit_probe_behavior",
        "classification": {
            "tiny_input_exit_code_variation_observed": any_variation,
            "fixed_build_failure_observed": any_fixed_failure,
            "promote_as_exploit_evidence": False,
        },
        "inputs": inputs,
        "interpretation": "Small task-facing inputs can produce varying sanitizer exits on arvo:1065, including fixed-build failures. Treat arvo:1065 as a second task materialization/runtime proof until a stronger PoC has stable vulnerable-only behavior.",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
