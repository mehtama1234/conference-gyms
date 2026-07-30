#!/usr/bin/env python3
"""Attempt one OpenApps browser task through the MCP/Playwright session."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".cache" / "openapps-browser-venv"
PYTHON = VENV / "bin" / "python"
OPENAPPS_SRC = ROOT / "OpenApps" / "src"
TMP = ROOT / ".cache" / "tmp"
BROWSERS = ROOT / ".cache" / "ms-playwright"

RUNTIME_PACKAGES = [
    "browsergym-core==0.14.3",
    "playwright==1.44.0",
    "python-fasthtml",
    "hydra-core",
    "deepdiff",
    "omegaconf",
    "uvicorn",
    "requests",
    "pytest",
    "pillow",
    "fastapi",
    "feedgen",
    "jinja2",
    "python-multipart",
    "thefuzz",
]


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TMPDIR"] = str(TMP)
    env["PYTHONPATH"] = str(OPENAPPS_SRC)
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSERS)
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
            raise RuntimeError("python3.12 is required for OpenApps browser replay")
        venv.EnvBuilder(with_pip=True).create(VENV)
        run([str(PYTHON), "-m", "pip", "install", "--upgrade", "pip"])

    probe = run(
        [
            str(PYTHON),
            "-c",
            "import browsergym.core, playwright, fasthtml, hydra, deepdiff, fastlite",
        ],
        check=False,
    )
    if probe.returncode != 0:
        run([str(PYTHON), "-m", "pip", "install", *RUNTIME_PACKAGES])

    browser_probe = run(
        [
            str(PYTHON),
            "-c",
            "from pathlib import Path; import os; "
            "root=Path(os.environ['PLAYWRIGHT_BROWSERS_PATH']); "
            "raise SystemExit(0 if list(root.glob('chromium-*')) else 1)",
        ],
        check=False,
    )
    if browser_probe.returncode != 0:
        run([str(PYTHON), "-m", "playwright", "install", "chromium"], check=False)


def main() -> int:
    ensure_venv()
    code = r"""
import asyncio
import builtins
import json
from fasthtml.common import Link
from fastlite import database

# OpenApps commit 015715a expects older fasthtml.common exports. Keep the
# compatibility shim local to the replay instead of editing the upstream clone.
builtins.picolink = Link(
    rel="stylesheet",
    href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
)
builtins.database = database

from open_apps.mcp.session import Session
from open_apps.tasks.tasks import AddToDoTask


async def run_task():
    session = Session("todo")
    report = {
        "task_name": "add_call_mom_to_my_todo",
        "runtime_shims": ["builtins.picolink", "builtins.database"],
    }
    try:
        await session.start()
        reset_obs = await session.reset()
        initial = session.get_state()
        task = AddToDoTask(
            goal="Add 'Call Mom' to my todo list.",
            todo_name="Call Mom",
            is_done=False,
        )
        session.set_task(task)
        await session.page.wait_for_selector("#new-title", timeout=5000)
        box = await session.page.locator("#new-title").bounding_box()
        cx = int(box["x"] + box["width"] / 2)
        cy = int(box["y"] + box["height"] / 2)
        obs1 = await session.act(f"mouse_click({cx}, {cy})")
        obs2 = await session.act("keyboard_type('Call Mom')")
        obs3 = await session.act("keyboard_press('Enter')")
        final = session.get_state()
        report.update(
            {
                "status": "passed" if obs3.reward == 1.0 else "failed",
                "task_id": task.task_id,
                "base_url": session.appserver.base_url,
                "registered_apps": session.appserver.registered_apps(),
                "initial_url": reset_obs.url,
                "final_url": obs3.url,
                "actions": [obs1.action_desc, obs2.action_desc, obs3.action_desc],
                "errors": [obs1.error, obs2.error, obs3.error],
                "initial_todo_count": len(initial["todo"]),
                "final_todo_count": len(final["todo"]),
                "final_contains_call_mom": any(
                    item.get("title") == "Call Mom" for item in final["todo"]
                ),
                "reward": obs3.reward,
                "done": obs3.done,
                "screenshot_bytes": len(obs3.screenshot_png),
            }
        )
    except Exception as exc:
        report.update(
            {
                "status": "blocked_or_error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
    finally:
        await session.close()
    return report


print(json.dumps(asyncio.run(run_task()), indent=2))
"""
    result = run([str(PYTHON), "-c", code], check=False)
    print(result.stdout.rstrip())
    try:
        report = json.loads(result.stdout[result.stdout.index("{") :])
    except Exception:
        return 1
    return 0 if report.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
