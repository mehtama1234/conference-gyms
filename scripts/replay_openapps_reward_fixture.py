#!/usr/bin/env python3
"""Replay the OpenApps saved-state reward fixture."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".cache" / "openapps-reward-venv"
PYTHON = VENV / "bin" / "python"
OPENAPPS_SRC = ROOT / "OpenApps" / "src"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TMPDIR"] = str(ROOT / ".cache" / "tmp")
    env["PYTHONPATH"] = str(OPENAPPS_SRC)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        **kwargs,
    )


def ensure_venv() -> None:
    (ROOT / ".cache" / "tmp").mkdir(parents=True, exist_ok=True)
    if not PYTHON.exists():
        VENV.parent.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True).create(VENV)
        run([str(PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
    probe = subprocess.run(
        [str(PYTHON), "-c", "import deepdiff, omegaconf, hydra"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if probe.returncode != 0:
        run([str(PYTHON), "-m", "pip", "install", "deepdiff", "omegaconf", "hydra-core"])


def main() -> int:
    ensure_venv()
    code = r"""
import json
from pathlib import Path
from open_apps.tasks.tasks import AddToDoTask, AppStateComparison

root = Path('.')
initial = json.loads((root / 'OpenApps/tests/states/initial_state.json').read_text())
current = json.loads((root / 'OpenApps/tests/states/call_mom_todo_state.json').read_text())
task = AddToDoTask(goal='Add a to-do item to call mom', todo_name='Call Mom', is_done=False)
complete = task.check_if_task_is_complete(initial, current)
report = {
    'task_id': task.task_id,
    'initial_todo_count': len(initial['todo']),
    'current_todo_count': len(current['todo']),
    'state_comparison': AppStateComparison.__name__,
    'complete': complete,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if complete else 1)
"""
    result = run([str(PYTHON), "-c", code])
    print(result.stdout.rstrip())
    print("OpenApps reward fixture replay passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
