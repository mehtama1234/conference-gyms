#!/usr/bin/env python3
"""Replay the selected TerminalTraj task_5279 lane.

This script is intentionally narrow. It is the production-lane replay wrapper
for one released task, not a generic TerminalTraj runner.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "lanes" / "terminaltraj"
CACHE = ROOT / ".cache" / "terminaltraj"
TMPDIR = ROOT / ".cache" / "tmp"
ARCHIVE = CACHE / "5k_instances.tar.gz"
TASK_DIR = CACHE / "extract-one" / "5k_instances" / "task_5279"
DATASET_URL = "https://huggingface.co/datasets/m-a-p/TerminalTraj-5k-instances/resolve/main/5k_instances.tar.gz"
BASE_IMAGE = "yizhilll/tb_container-392402c50123e9f1ba672a157adc3750:tmux_asciinema_v2"
IMAGE_NAME = "terminaltraj-task-5279-client"
CONTAINER_NAME = "terminaltraj-task-5279-client"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env["TMPDIR"] = str(TMPDIR)
    if env:
        merged_env.update(env)
    print("+", " ".join(cmd))
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else str(ROOT),
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )


def compose_env() -> dict[str, str]:
    logs = TASK_DIR / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return {
        "T_BENCH_TASK_DOCKER_CLIENT_IMAGE_NAME": IMAGE_NAME,
        "T_BENCH_TASK_DOCKER_CLIENT_CONTAINER_NAME": CONTAINER_NAME,
        "T_BENCH_TEST_DIR": "/tests",
        "T_BENCH_TASK_LOGS_PATH": str(logs),
        "T_BENCH_CONTAINER_LOGS_PATH": "/logs",
    }


def ensure_inputs() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    TMPDIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        print(f"Downloading {DATASET_URL}")
        urllib.request.urlretrieve(DATASET_URL, ARCHIVE)
    if not (TASK_DIR / "task.yaml").exists():
        TASK_DIR.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            archive.extractall(CACHE / "extract-one", members=[m for m in archive.getmembers() if m.name.startswith("5k_instances/task_5279/")])


def cleanup() -> None:
    if TASK_DIR.exists():
        try:
            run(["docker", "compose", "down"], cwd=TASK_DIR, env=compose_env())
        except subprocess.CalledProcessError as exc:
            print(exc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep-container", action="store_true", help="Leave the task container running for inspection.")
    args = parser.parse_args()

    ensure_inputs()
    run(["docker", "pull", BASE_IMAGE])
    run(["docker", "compose", "build"], cwd=TASK_DIR, env=compose_env())
    run(["docker", "compose", "up", "-d"], cwd=TASK_DIR, env=compose_env())

    try:
        initial = run(
            [
                "docker",
                "exec",
                CONTAINER_NAME,
                "sh",
                "-lc",
                "test -f /app/tubesync/local_settings.py && grep -n \"addons_config\\|custom_tubesync\" /app/tubesync/local_settings.py",
            ]
        )
        print(initial.stdout)

        action_script = """cp /app/tubesync/local_settings.py /app/tubesync/local_settings_backup.py
python3 - <<'PY'
from pathlib import Path
p = Path('/app/tubesync/local_settings.py')
s = p.read_text()
old = "Path('/config/addons_config/tubesync')"
new = "Path('/config/custom_tubesync_data')"
if old not in s:
    raise SystemExit('old path missing')
p.write_text(s.replace(old, new))
PY
mkdir -p /config/custom_tubesync_data
printf 'TubeSync configuration successfully redirected' > /config/custom_tubesync_data/config_test.txt
python3 -m py_compile /app/tubesync/local_settings.py /app/tubesync/local_settings_backup.py
"""
        run(["docker", "exec", CONTAINER_NAME, "sh", "-lc", action_script])

        run(["docker", "exec", CONTAINER_NAME, "sh", "-lc", "mkdir -p /tests"])
        run(["docker", "cp", str(TASK_DIR / "tests" / "test_outputs.py"), f"{CONTAINER_NAME}:/tests/test_outputs.py"])
        run(["docker", "cp", str(TASK_DIR / "run-tests.sh"), f"{CONTAINER_NAME}:/tests/run-tests.sh"])
        verifier = run(
            [
                "docker",
                "exec",
                "-e",
                "TEST_DIR=/tests",
                CONTAINER_NAME,
                "sh",
                "-lc",
                "chmod +x /tests/run-tests.sh && /tests/run-tests.sh",
            ]
        )
        print(verifier.stdout)
        if "4 passed" not in verifier.stdout:
            raise RuntimeError("Verifier output did not contain expected '4 passed' marker")
    finally:
        if not args.keep_container:
            cleanup()

    if not args.keep_container:
        leftover = shutil.which("docker")
        if leftover:
            ps = run(["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}} {{.Status}}"])
            if ps.stdout.strip():
                raise RuntimeError(f"Container still running after cleanup: {ps.stdout.strip()}")

    print("TerminalTraj task_5279 replay passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
