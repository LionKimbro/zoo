"""One-time migration from legacy PROJ.txt to the new Zoo format.

This script is intentionally conservative:
  - it reads the old registry at the legacy OneDrive-era location,
  - it writes per-project JSON files plus index.json into the Machine-Root Zoo,
  - it emits a remainder file mapping each new GUID to the old ID and legacy dir,
  - it refuses to run if the target Zoo store already appears populated.

It is designed to be run once.
"""

from __future__ import annotations

import json
from pathlib import Path
import uuid

import machineroot


LEGACY_ROOT = Path(r"F:\bigfiles\onedrive2022\OneDrive\origins\2021\data\lists\PROJ")
LEGACY_REGISTRY_PATH = LEGACY_ROOT / "PROJ.txt"
REMAINDER_FILENAME = "legacy-remainder.json"

# Fixed namespace so the migration is deterministic if it ever needs to be rerun.
MIGRATION_NAMESPACE = uuid.UUID("9d42cb13-bd92-4918-9195-0f467ab0f4e3")
TRANSFERRED_LEGACY_KEYS = {"ID", "TAG", "TITLE", "CREATED", "HOOK", "DESCRIPTION", "TAGS"}


def main():
    zoo_root = Path(machineroot.get("db-root-2026")) / "zoo"
    projects_root = zoo_root / "projects"
    index_path = zoo_root / "index.json"
    remainder_path = zoo_root / REMAINDER_FILENAME

    legacy_rows = read_json(LEGACY_REGISTRY_PATH)
    ensure_can_run(projects_root, index_path, remainder_path)

    projects_root.mkdir(parents=True, exist_ok=True)

    index_rows = []
    remainder_rows = []

    for legacy_row in legacy_rows:
        project = convert_legacy_project(legacy_row)
        project_id = project["id"]
        write_json(projects_root / f"{project_id}.json", project)

        index_rows.append(make_index_row(project))
        remainder_rows.append(make_remainder_row(project_id, legacy_row))

    write_json(index_path, index_rows)
    write_json(
        remainder_path,
        {
            "document": {
                "document-id": "zoo.legacy-remainder.v1",
                "title": "Zoo Legacy Migration Remainder",
                "purpose": "Associate each migrated Zoo project GUID with its prior legacy project id and legacy data directory."
            },
            "source": {
                "legacy-registry": str(LEGACY_REGISTRY_PATH),
                "legacy-project-root": str(LEGACY_ROOT)
            },
            "associations": remainder_rows
        },
    )

    print(f"Migrated {len(index_rows)} projects.")
    print(f"Wrote index: {index_path}")
    print(f"Wrote remainder: {remainder_path}")


def ensure_can_run(projects_root: Path, index_path: Path, remainder_path: Path):
    if not LEGACY_REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Legacy registry not found: {LEGACY_REGISTRY_PATH}")

    if index_path.exists():
        raise RuntimeError(f"Refusing to run: target index already exists: {index_path}")

    if remainder_path.exists():
        raise RuntimeError(f"Refusing to run: remainder file already exists: {remainder_path}")

    if projects_root.exists():
        existing = list(projects_root.glob("*.json"))
        if existing:
            raise RuntimeError(
                f"Refusing to run: target projects dir already contains project files: {projects_root}"
            )


def convert_legacy_project(legacy_row: dict) -> dict:
    legacy_id = str(legacy_row["ID"])
    project_id = str(uuid.uuid5(MIGRATION_NAMESPACE, legacy_id))

    project = {
        "id": project_id,
        "description": None
    }

    copy_string(legacy_row, "TAG", project, "tag")
    copy_string(legacy_row, "TITLE", project, "title")
    copy_string(legacy_row, "CREATED", project, "created")
    copy_string(legacy_row, "HOOK", project, "hook")
    copy_string(legacy_row, "DESCRIPTION", project, "description")

    tags = legacy_row.get("TAGS")
    if tags:
        project["tags"] = list(tags)

    return project


def make_index_row(project: dict) -> dict:
    row = {"id": project["id"]}
    for key in ["title", "tag", "tags", "created", "hook"]:
        if key in project:
            row[key] = project[key]
    return row


def make_remainder_row(project_id: str, legacy_row: dict) -> dict:
    legacy_id = str(legacy_row["ID"])
    row = {
        "id": project_id,
        "legacy-id": legacy_id,
        "remainder": {}
    }
    for key, value in legacy_row.items():
        if key not in TRANSFERRED_LEGACY_KEYS:
            row["remainder"][key] = value
    return row


def copy_string(src: dict, src_key: str, dst: dict, dst_key: str):
    value = src.get(src_key)
    if isinstance(value, str) and value:
        dst[dst_key] = value


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    tmp_path.replace(path)


if __name__ == "__main__":
    main()

