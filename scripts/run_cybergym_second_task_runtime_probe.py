#!/usr/bin/env python3
"""Materialize a second CyberGym task and run its vulnerable/fixed verifiers."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import run_cybergym_task_manifest_probe as base


ROOT = Path(__file__).resolve().parents[1]
CYBERGYM = ROOT / "CyberGym"
TASK_DATA = ROOT / ".cache" / "cybergym-task-data"
RUN_ROOT = ROOT / ".cache" / "cybergym-second-task-runtime-probe"

TASK_ID = "arvo:1065"
MASKED_TASK_ID = "9c73e92e52b7"
AGENT_ID = "cybergym-second-task-runtime-probe-agent"
DATA_FILES = [
    "description.txt",
    "error.txt",
    "patch.diff",
    "repo-fix.tar.gz",
    "repo-vul.tar.gz",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_task(task_id: str) -> tuple[str, str]:
    return tuple(task_id.split(":", 1))  # type: ignore[return-value]


def download_task_data() -> list[dict[str, object]]:
    family, number = split_task(TASK_ID)
    task_dir = TASK_DATA / "data" / family / number
    task_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name in DATA_FILES:
        path = task_dir / name
        if not path.exists() or path.stat().st_size == 0:
            url = f"https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/{family}/{number}/{name}"
            with urllib.request.urlopen(url, timeout=300) as response, path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        records.append(
            {
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def docker_image_present(image: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def generate_task(base_url: str, out_dir: Path) -> dict[str, object]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = base.run(
        [
            str(base.PYTHON),
            "-m",
            "cybergym.task.gen_task",
            "--task-id",
            TASK_ID,
            "--agent-id",
            AGENT_ID,
            "--out-dir",
            str(out_dir),
            "--data-dir",
            str(TASK_DATA / "data"),
            "--server",
            base_url,
            "--mask-map",
            str(CYBERGYM / "mask_map.json"),
            "--difficulty",
            "level1",
        ],
        check=False,
    )
    generated_files = sorted(str(path.relative_to(out_dir)) for path in out_dir.rglob("*") if path.is_file())
    return {
        "exit_code": result.returncode,
        "output_tail": result.stdout[-2000:],
        "out_dir": str(out_dir.relative_to(ROOT)),
        "generated_files": generated_files,
        "readme_sha256": sha256(out_dir / "README.md") if (out_dir / "README.md").exists() else None,
        "submit_sha256": sha256(out_dir / "submit.sh") if (out_dir / "submit.sh").exists() else None,
    }


def submit_vul(out_dir: Path) -> dict[str, object]:
    poc_path = out_dir / "poc-empty.bin"
    poc_path.write_bytes(b"")
    result = base.run(["bash", str(out_dir / "submit.sh"), str(poc_path)], check=False)
    return {
        "command": "bash submit.sh poc-empty.bin",
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-3000:],
        "poc_path": str(poc_path.relative_to(ROOT)),
        "poc_size_bytes": poc_path.stat().st_size,
        "poc_sha256": sha256(poc_path),
    }


def submit_fix(base_url: str, poc_path: Path) -> dict[str, object]:
    code = r"""
import hashlib
import json
from pathlib import Path

import requests

base_url = __BASE_URL__
poc_path = Path(__POC_PATH__)
task_id = __MASKED_TASK_ID__
agent_id = __AGENT_ID__
checksum = hashlib.sha256(f"{task_id}{agent_id}CyberGym".encode()).hexdigest()
payload = {
    "task_id": task_id,
    "agent_id": agent_id,
    "checksum": checksum,
    "require_flag": False,
}
response = requests.post(
    f"{base_url}/submit-fix",
    data={"metadata": json.dumps(payload)},
    files={"file": ("poc-empty.bin", poc_path.read_bytes(), "application/octet-stream")},
    headers={"X-API-Key": "cybergym-030a0cd7-5908-4862-8ab9-91f2bfc7b56d"},
    timeout=30,
)
print(json.dumps({"response_status": response.status_code, "response_text": response.text[:2000]}, indent=2))
"""
    code = (
        code.replace("__BASE_URL__", repr(base_url))
        .replace("__POC_PATH__", repr(str(poc_path)))
        .replace("__MASKED_TASK_ID__", repr(MASKED_TASK_ID))
        .replace("__AGENT_ID__", repr(AGENT_ID))
    )
    result = base.run([str(base.PYTHON), "-c", code], check=False)
    if result.returncode != 0:
        return {"response_status": "client_error", "response_text": result.stdout[-2000:]}
    return json.loads(result.stdout)


def main() -> int:
    base.ensure_venv()
    data_records = download_task_data()
    if RUN_ROOT.exists():
        shutil.rmtree(RUN_ROOT)
    run_dir = RUN_ROOT / "run"
    log_dir = run_dir / "logs"
    db_path = run_dir / "poc.db"
    out_dir = run_dir / "task"
    log_dir.mkdir(parents=True, exist_ok=True)
    port = base.open_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(CYBERGYM / "src")
    env["TMPDIR"] = str(base.TMP)
    proc = subprocess.Popen(
        [
            str(base.PYTHON),
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
        "task_id": TASK_ID,
        "agent_facing_task_id": MASKED_TASK_ID,
        "agent_id": AGENT_ID,
        "data_files": data_records,
        "runtime": {
            "python": "python3.12",
            "venv": ".cache/cybergym-server-venv",
            "run_dir": ".cache/cybergym-second-task-runtime-probe/run",
            "verifier_images": {
                "n132/arvo:1065-vul": docker_image_present("n132/arvo:1065-vul"),
                "n132/arvo:1065-fix": docker_image_present("n132/arvo:1065-fix"),
            },
        },
    }
    try:
        base.wait_for_server(base_url, proc)
        report["server_ready"] = True
        report["task_generation"] = generate_task(base_url, out_dir)
        if report["task_generation"]["exit_code"] == 0:
            report["submit_vul_via_task_manifest"] = submit_vul(out_dir)
            report["submit_fix_private"] = submit_fix(base_url, out_dir / "poc-empty.bin")
            report["poc_db"] = base.read_poc_db(db_path)
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

    db = report.get("poc_db")
    if isinstance(db, dict):
        records = db.get("records")
        record = records[0] if isinstance(records, list) and records else {}
        if isinstance(record, dict) and record.get("vul_exit_code") is not None and record.get("fix_exit_code") is not None:
            task_solved = record.get("vul_exit_code") != 0 and record.get("fix_exit_code") == 0
            report["status"] = "second_task_runtime_probe_passed_solved" if task_solved else "second_task_runtime_probe_passed_unsolved"
            report["success_semantics"] = {
                "task_solved": task_solved,
                "note": "This proves a second CyberGym README-subset task can be materialized and verified locally. The submitted PoC is an empty runtime probe and is not exploit-discovery evidence.",
            }

    print("CYBERGYM_SECOND_TASK_RUNTIME_PROBE_REPORT_START")
    print(json.dumps(report, indent=2))
    print("CYBERGYM_SECOND_TASK_RUNTIME_PROBE_REPORT_END")
    return 0 if report.get("status") in {"second_task_runtime_probe_passed_unsolved", "second_task_runtime_probe_passed_solved"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
