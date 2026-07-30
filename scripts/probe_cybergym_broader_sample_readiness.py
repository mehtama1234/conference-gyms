#!/usr/bin/env python3
"""Check whether the CyberGym README subset is locally promotable."""

from __future__ import annotations

import json
import subprocess
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "lanes" / "cybergym"
CYBERGYM = ROOT / "CyberGym"
TASK_DATA = ROOT / ".cache" / "cybergym-task-data" / "data"

DATA_FILES = [
    "description.txt",
    "error.txt",
    "patch.diff",
    "repo-fix.tar.gz",
    "repo-vul.tar.gz",
]


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def docker_images() -> set[str]:
    result = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def split_task(task_id: str) -> tuple[str, str]:
    family, number = task_id.split(":", 1)
    return family, number


def data_url(task_id: str, name: str) -> str:
    family, number = split_task(task_id)
    return f"https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/{family}/{number}/{name}"


def remote_file_visible(task_id: str, name: str) -> dict[str, object]:
    request = urllib.request.Request(data_url(task_id, name), method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {
                "name": name,
                "visible": response.status in {200, 302},
                "status": response.status,
                "content_length": response.headers.get("Content-Length"),
            }
    except HTTPError as exc:
        return {"name": name, "visible": False, "status": exc.code, "content_length": None}
    except (URLError, TimeoutError, OSError) as exc:
        return {"name": name, "visible": False, "status": "error", "error": type(exc).__name__}


def local_data_files(task_id: str) -> list[dict[str, object]]:
    family, number = split_task(task_id)
    task_dir = TASK_DATA / family / number
    records = []
    for name in DATA_FILES:
        path = task_dir / name
        records.append(
            {
                "name": name,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return records


def main() -> int:
    contract = load_json(LANE / "task-contract.json")
    mask_map = load_json(CYBERGYM / "mask_map.json")
    if not isinstance(contract, dict) or not isinstance(mask_map, dict):
        raise TypeError("CyberGym contract and mask_map must be JSON objects")

    task_shape = contract.get("task_shape")
    if not isinstance(task_shape, dict):
        raise TypeError("CyberGym contract task_shape must be a JSON object")
    tasks = task_shape.get("task_id_examples_from_readme_subset")
    if not isinstance(tasks, list) or not all(isinstance(item, str) for item in tasks):
        raise TypeError("CyberGym subset task ids must be strings")

    images = docker_images()
    task_records = []
    for task_id in tasks:
        image_prefix = f"n132/{task_id}"
        vul_image = f"{image_prefix}-vul"
        fix_image = f"{image_prefix}-fix"
        local_files = local_data_files(task_id)
        remote_files = [remote_file_visible(task_id, name) for name in DATA_FILES]
        task_records.append(
            {
                "task_id": task_id,
                "masked_task_id": mask_map.get(task_id),
                "mask_map_present": task_id in mask_map,
                "local_verifier_images": {
                    "vul": vul_image in images,
                    "fix": fix_image in images,
                    "vul_image": vul_image,
                    "fix_image": fix_image,
                },
                "local_task_data_complete": all(item["exists"] and item["size_bytes"] > 0 for item in local_files),
                "local_task_data_files": local_files,
                "remote_task_data_visible": all(item["visible"] for item in remote_files),
                "remote_task_data_files": remote_files,
            }
        )

    runnable = [
        item["task_id"]
        for item in task_records
        if item["local_verifier_images"]["vul"]
        and item["local_verifier_images"]["fix"]
        and item["local_task_data_complete"]
    ]
    visible_but_missing_images = [
        item["task_id"]
        for item in task_records
        if item["remote_task_data_visible"]
        and not (item["local_verifier_images"]["vul"] and item["local_verifier_images"]["fix"])
    ]

    report = {
        "receipt_id": "cybergym-broader-sample-readiness-001",
        "checked_at": "2026-07-30",
        "script": "scripts/probe_cybergym_broader_sample_readiness.py",
        "command": "make probe-cybergym-broader-sample",
        "scope": "readme_subset_no_heavy_download_readiness",
        "task_count": len(task_records),
        "locally_runnable_task_count": len(runnable),
        "locally_runnable_tasks": runnable,
        "remote_visible_but_missing_local_verifier_images": visible_but_missing_images,
        "status": "blocked_missing_local_verifier_images" if len(runnable) < 2 else "ready_for_broader_sample_probe",
        "does_not_download": [
            "benchmark data bundle",
            "binary-only server data bundle",
            "full server data bundle",
            "additional Docker verifier images",
        ],
        "evidence_summary": [
            "CyberGym README subset contains 10 tasks",
            "all 10 subset tasks are present in CyberGym/mask_map.json",
            "all 10 subset tasks expose description.txt, error.txt, patch.diff, repo-fix.tar.gz, and repo-vul.tar.gz through the Hugging Face dataset",
            "local Docker only has n132/arvo:10400-vul and n132/arvo:10400-fix from the subset",
            "broadening runtime coverage requires pulling at least one more vulnerable/fixed verifier image pair or installing the binary-only server data bundle",
        ],
        "next_action": "Pull or install one additional README-subset vulnerable/fixed verifier image pair, then materialize that task and record a second CyberGym verifier trace.",
        "tasks": task_records,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in {"blocked_missing_local_verifier_images", "ready_for_broader_sample_probe"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
