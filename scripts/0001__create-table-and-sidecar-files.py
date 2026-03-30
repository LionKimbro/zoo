"""Create local-folders-table.json and sidecar-project-links.json.

This script reads legacy-remainder.json from the Zoo data root and derives:
  - local-folders-table.json: machine-local folder GUID -> absolute path
  - sidecar-project-links.json: project GUID -> folder GUID links

The generated folder GUIDs are deterministic and are based on legacy LOC values.
"""

from __future__ import annotations

import json
from pathlib import Path
import uuid

import machineroot


REMAINDER_FILENAME = "legacy-remainder.json"
LOCAL_FOLDERS_TABLE_FILENAME = "local-folders-table.json"
SIDECAR_PROJECT_LINKS_FILENAME = "sidecar-project-links.json"

LEGACY_FOLDER_NAMESPACE = uuid.UUID("4d9f0f3c-9d68-4f43-a4f1-0a6cbb6dbd1e")
FOLDER_LABEL = "Projlist legacy folder"


def main():
    zoo_root = Path(machineroot.get("db-root-2026")) / "zoo"
    remainder_path = zoo_root / REMAINDER_FILENAME
    local_folders_table_path = zoo_root / LOCAL_FOLDERS_TABLE_FILENAME
    sidecar_project_links_path = zoo_root / SIDECAR_PROJECT_LINKS_FILENAME

    ensure_can_run(remainder_path, local_folders_table_path, sidecar_project_links_path)
    remainder_doc = read_json(remainder_path)

    legacy_root = Path(remainder_doc["source"]["legacy-project-root"])
    associations = remainder_doc.get("associations", [])

    local_folders_table = {}
    sidecar_links = []

    for association in associations:
        folder_guid, folder_path = convert_association(legacy_root, association)
        if folder_guid is None:
            continue

        sidecar_links.append(
            {
                "from": association["id"],
                "to": folder_guid,
                "kind": "folder",
                "label": FOLDER_LABEL,
                "source": REMAINDER_FILENAME
            }
        )

        if folder_path.exists() and folder_path.is_dir():
            local_folders_table[folder_guid] = str(folder_path)

    write_json(local_folders_table_path, local_folders_table)
    write_json(sidecar_project_links_path, sidecar_links)

    print(f"Wrote local folders table: {local_folders_table_path}")
    print(f"  Entries: {len(local_folders_table)}")
    print(f"Wrote sidecar links: {sidecar_project_links_path}")
    print(f"  Links: {len(sidecar_links)}")


def ensure_can_run(remainder_path: Path, local_folders_table_path: Path, sidecar_project_links_path: Path):
    if not remainder_path.exists():
        raise FileNotFoundError(f"Legacy remainder not found: {remainder_path}")

    if local_folders_table_path.exists():
        raise RuntimeError(f"Refusing to run: target already exists: {local_folders_table_path}")

    if sidecar_project_links_path.exists():
        raise RuntimeError(f"Refusing to run: target already exists: {sidecar_project_links_path}")


def convert_association(legacy_root: Path, association: dict):
    remainder = association.get("remainder")
    if not isinstance(remainder, dict):
        return None, None

    loc = remainder.get("LOC")
    if not isinstance(loc, str) or not loc:
        return None, None

    folder_guid = make_folder_guid(loc)
    folder_path = legacy_root / loc
    return folder_guid, folder_path


def make_folder_guid(loc: str) -> str:
    return str(uuid.uuid5(LEGACY_FOLDER_NAMESPACE, f"legacy-folder:{loc}"))


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
