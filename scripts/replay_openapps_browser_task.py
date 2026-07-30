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
LOCAL_DEBS = ROOT / ".cache" / "local-debs"
LOCAL_LIBS = ROOT / ".cache" / "local-browser-libs"

RUNTIME_PACKAGES = [
    "browsergym-core==0.14.3",
    "playwright==1.44.0",
    "python-fasthtml==0.12.14",
    "starlette==0.46.2",
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
    lib_path = local_lib_path()
    if lib_path is not None:
        env["LD_LIBRARY_PATH"] = f"{lib_path}:{env.get('LD_LIBRARY_PATH', '')}"
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def local_lib_path() -> Path | None:
    lib = LOCAL_LIBS / "lib"
    return lib if lib.exists() else None


def ensure_local_browser_libs() -> None:
    """Extract Chromium's missing shared libraries into ignored .cache."""
    lib = LOCAL_LIBS / "lib"
    required = [lib / "libnss3.so", lib / "libnspr4.so", lib / "libasound.so.2"]
    if all(path.exists() for path in required):
        return

    LOCAL_DEBS.mkdir(parents=True, exist_ok=True)
    packages = ["libnss3", "libnspr4", "libasound2t64"]
    download = subprocess.run(
        ["apt-get", "download", *packages],
        cwd=LOCAL_DEBS,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if download.returncode != 0:
        raise RuntimeError(f"apt-get download failed:\n{download.stdout}")

    extract = LOCAL_LIBS / "extract"
    extract.mkdir(parents=True, exist_ok=True)
    lib.mkdir(parents=True, exist_ok=True)
    for deb in LOCAL_DEBS.glob("*.deb"):
        subprocess.run(["dpkg-deb", "-x", str(deb), str(extract)], check=True)
    for shared in extract.glob("usr/lib/x86_64-linux-gnu/*.so*"):
        target = lib / shared.name
        if not target.exists():
            target.write_bytes(shared.read_bytes())
    alsa = lib / "libasound.so.2"
    if not alsa.exists() and (lib / "libasound.so.2.0.0").exists():
        alsa.symlink_to("libasound.so.2.0.0")


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

    ensure_local_browser_libs()
    probe = run(
        [
            str(PYTHON),
            "-c",
            "import importlib.metadata as md; "
            "import browsergym.core, playwright, fasthtml, hydra, deepdiff, fastlite, starlette; "
            "raise SystemExit(0 if md.version('python-fasthtml') == '0.12.14' "
            "and md.version('starlette') == '0.46.2' else 1)",
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
import typing

builtins.Any = typing.Any
import fastcore.xml as fastcore_xml

_original_to_xml = fastcore_xml.to_xml


def _to_xml_bool_compat(*elms, **kwargs):
    def clean(elm):
        if isinstance(elm, bool):
            return ""
        if isinstance(elm, tuple):
            return tuple(clean(item) for item in elm)
        if isinstance(elm, list):
            return [clean(item) for item in elm]
        return elm

    return _original_to_xml(*(clean(elm) for elm in elms), **kwargs)


fastcore_xml.to_xml = _to_xml_bool_compat
import fasthtml.core as fasthtml_core

fasthtml_core.to_xml = _to_xml_bool_compat
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
        "runtime_shims": [
            "builtins.Any",
            "fastcore.xml.to_xml bool-child compatibility",
            "builtins.picolink",
            "builtins.database",
        ],
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


report = asyncio.run(run_task())
print("OPENAPPS_BROWSER_REPLAY_REPORT_START")
print(json.dumps(report, indent=2))
print("OPENAPPS_BROWSER_REPLAY_REPORT_END")
"""
    result = run([str(PYTHON), "-c", code], check=False)
    print(result.stdout.rstrip())
    try:
        body = result.stdout.split("OPENAPPS_BROWSER_REPLAY_REPORT_START", 1)[1]
        body = body.split("OPENAPPS_BROWSER_REPLAY_REPORT_END", 1)[0]
        report = json.loads(body)
    except Exception:
        return 1
    return 0 if report.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
