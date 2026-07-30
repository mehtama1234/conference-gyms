#!/usr/bin/env python3
"""Probe CyberGym's local submission server without downloading server images."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import venv
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
CYBERGYM = ROOT / "CyberGym"
VENV = ROOT / ".cache" / "cybergym-server-venv"
PYTHON = VENV / "bin" / "python"
RUN_ROOT = ROOT / ".cache" / "cybergym-server-probe"
TMP = ROOT / ".cache" / "tmp"

PACKAGES = [
    "-e",
    "CyberGym[server]",
    "requests>=2.32.0",
]


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TMPDIR"] = str(TMP)
    env["PYTHONPATH"] = str(CYBERGYM / "src")
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def ensure_venv() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    if not PYTHON.exists():
        VENV.parent.mkdir(parents=True, exist_ok=True)
        python312 = subprocess.run(
            ["python3.12", "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if python312.returncode != 0:
            raise RuntimeError("python3.12 is required for CyberGym server probe")
        venv.EnvBuilder(with_pip=True).create(VENV)
        run([str(PYTHON), "-m", "pip", "install", "--upgrade", "pip"])

    probe = run(
        [
            str(PYTHON),
            "-c",
            "import cybergym, fastapi, uvicorn, sqlalchemy, requests",
        ],
        check=False,
    )
    if probe.returncode != 0:
        run([str(PYTHON), "-m", "pip", "install", *PACKAGES])


def open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(base_url: str, proc: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 20
    last_error = ""
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"CyberGym server exited early with code {proc.returncode}")
        try:
            with urlopen(f"{base_url}/openapi.json", timeout=1) as response:
                if response.status == 200:
                    return
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
        time.sleep(0.25)
    raise RuntimeError(f"CyberGym server did not become ready: {last_error}")


def submit_probe(base_url: str, run_dir: Path) -> dict[str, object]:
    code = r"""
import hashlib
import json
from pathlib import Path

import requests

base_url = __BASE_URL__
run_dir = Path(__RUN_DIR__)
real_task_id = "arvo:10400"
task_id = "7fa395d7dac0"
agent_id = "cybergym-local-server-probe-agent"
checksum = hashlib.sha256(f"{task_id}{agent_id}CyberGym".encode()).hexdigest()
payload = {
    "task_id": task_id,
    "agent_id": agent_id,
    "checksum": checksum,
    "require_flag": False,
}
poc = b"\x00\x01\x02\x03"
response = requests.post(
    f"{base_url}/submit-vul",
    data={"metadata": json.dumps(payload)},
    files={"file": ("poc", poc, "application/octet-stream")},
    timeout=30,
)
fix_response = requests.post(
    f"{base_url}/submit-fix",
    data={"metadata": json.dumps(payload)},
    files={"file": ("poc", poc, "application/octet-stream")},
    headers={"X-API-Key": "cybergym-030a0cd7-5908-4862-8ab9-91f2bfc7b56d"},
    timeout=30,
)
result = {
    "request": {
        "task_id": task_id,
        "real_task_id_expected_after_unmasking": real_task_id,
        "agent_id": agent_id,
        "checksum_valid": True,
        "poc_bytes": len(poc),
    },
    "submit_vul": {
        "response_status": response.status_code,
        "response_text": response.text[:2000],
    },
    "submit_fix": {
        "response_status": fix_response.status_code,
        "response_text": fix_response.text[:2000],
    },
}
print(json.dumps(result, indent=2))
"""
    code = code.replace("__BASE_URL__", repr(base_url)).replace("__RUN_DIR__", repr(str(run_dir)))
    result = run([str(PYTHON), "-c", code], check=False)
    if result.returncode != 0:
        return {
            "request": {
                "task_id": "7fa395d7dac0",
                "real_task_id_expected_after_unmasking": "arvo:10400",
                "agent_id": "cybergym-local-server-probe-agent",
                "checksum_valid": True,
                "poc_bytes": 4,
            },
            "submit_vul": {
                "response_status": "client_error",
                "response_text": result.stdout[-2000:],
            },
            "submit_fix": {
                "response_status": "not_attempted",
                "response_text": "",
            },
        }
    return json.loads(result.stdout)


def read_poc_db(db_path: Path) -> dict[str, object]:
    if not db_path.exists():
        return {"exists": False, "record_count": 0, "records": []}
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "select agent_id, task_id, poc_id, poc_hash, poc_length, vul_exit_code, fix_exit_code from poc_records"
        ).fetchall()
    return {
        "exists": True,
        "record_count": len(rows),
        "records": [
            {
                "agent_id": row[0],
                "task_id": row[1],
                "poc_id": row[2],
                "poc_hash": row[3],
                "poc_length": row[4],
                "vul_exit_code": row[5],
                "fix_exit_code": row[6],
            }
            for row in rows
        ],
    }


def docker_status() -> dict[str, object]:
    docker = shutil.which("docker")
    if docker is None:
        return {"docker_cli": "missing", "docker_info_exit_code": None, "docker_info_tail": ""}
    result = subprocess.run(
        [docker, "info", "--format", "{{json .ServerVersion}}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "docker_cli": docker,
        "docker_info_exit_code": result.returncode,
        "docker_info_tail": result.stdout[-500:],
    }


def verifier_image_status() -> dict[str, object]:
    result = subprocess.run(
        [
            "docker",
            "images",
            "--format",
            "{{.Repository}}:{{.Tag}} {{.Size}}",
            "n132/arvo",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    lines = [line for line in result.stdout.splitlines() if line.startswith("n132/arvo:10400-")]
    return {
        "command_exit_code": result.returncode,
        "required_images": {
            "n132/arvo:10400-vul": any(line.startswith("n132/arvo:10400-vul ") for line in lines),
            "n132/arvo:10400-fix": any(line.startswith("n132/arvo:10400-fix ") for line in lines),
        },
        "observed": lines,
    }


def main() -> int:
    ensure_venv()
    if RUN_ROOT.exists():
        shutil.rmtree(RUN_ROOT)
    run_dir = RUN_ROOT / "run"
    log_dir = run_dir / "logs"
    db_path = run_dir / "poc.db"
    log_dir.mkdir(parents=True, exist_ok=True)
    port = open_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(CYBERGYM / "src")
    env["TMPDIR"] = str(TMP)
    proc = subprocess.Popen(
        [
            str(PYTHON),
            "-m",
            "cybergym.server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--mask_map_path",
            str(CYBERGYM / "mask_map.json"),
            "--log_dir",
            str(log_dir),
            "--db_path",
            str(db_path),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    report: dict[str, object] = {
        "status": "started",
        "base_url": base_url,
        "runtime": {
            "python": "python3.12",
            "venv": ".cache/cybergym-server-venv",
            "log_dir": ".cache/cybergym-server-probe/run/logs",
            "db_path": ".cache/cybergym-server-probe/run/poc.db",
        },
        "docker_status": docker_status(),
        "verifier_image_status": verifier_image_status(),
    }
    try:
        wait_for_server(base_url, proc)
        report["server_ready"] = True
        report["submission_probe"] = submit_probe(base_url, run_dir)
        report["poc_db"] = read_poc_db(db_path)
    except Exception as exc:
        report["status"] = "blocked_or_error"
        report["error_type"] = type(exc).__name__
        report["error"] = str(exc)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        report["server_exit_code_after_terminate"] = proc.returncode
        if proc.stdout is not None:
            report["server_output_tail"] = proc.stdout.read()[-3000:]

    submit = report.get("submission_probe")
    db = report.get("poc_db")
    if isinstance(submit, dict) and isinstance(db, dict):
        records = db.get("records")
        record = records[0] if isinstance(records, list) and records else {}
        vul_exit_code = record.get("vul_exit_code") if isinstance(record, dict) else None
        fix_exit_code = record.get("fix_exit_code") if isinstance(record, dict) else None
        if vul_exit_code is not None and fix_exit_code is not None:
            report["status"] = "verifier_probe_passed"
            report["verifier_status"] = "vulnerable_and_fixed_executed"
            report["success_semantics"] = {
                "task_solved": vul_exit_code != 0 and fix_exit_code == 0,
                "note": "This probe uses a trivial 4-byte PoC to prove verifier execution, not to solve the task.",
            }
        else:
            report["status"] = "server_probe_passed_verifier_blocked"
            report["verifier_status"] = "blocked_missing_docker_image_or_server_data"

    print("CYBERGYM_SERVER_PROBE_REPORT_START")
    print(json.dumps(report, indent=2))
    print("CYBERGYM_SERVER_PROBE_REPORT_END")
    return 0 if report.get("status") in {"server_probe_passed_verifier_blocked", "verifier_probe_passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
