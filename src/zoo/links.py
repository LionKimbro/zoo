"""links.py  -- sidecar project/resource links and local folder resolution"""

import os

from . import paths


PROJECT_LINKS = "PROJECT_LINKS"
LOCAL_FOLDERS = "LOCAL_FOLDERS"


g = {
    PROJECT_LINKS: [],
    LOCAL_FOLDERS: {}
}


def load():
    project_links = paths.read_sidecar_project_links()
    local_folders = paths.read_local_folders_table()

    g[PROJECT_LINKS] = project_links if isinstance(project_links, list) else []
    g[LOCAL_FOLDERS] = local_folders if isinstance(local_folders, dict) else {}


def links_from(project_id, kind=None):
    found = []
    for link in g[PROJECT_LINKS]:
        if not isinstance(link, dict):
            continue
        if str(link.get("from")) != str(project_id):
            continue
        if kind is not None and link.get("kind") != kind:
            continue
        found.append(link)
    return found


def first_folder_link(project_id):
    found = links_from(project_id, kind="folder")
    if found:
        return found[0]
    return None


def local_folder_path(folder_id):
    path = g[LOCAL_FOLDERS].get(str(folder_id))
    if not path:
        return None
    if not os.path.isdir(path):
        return None
    return path


def folder_link_status(project_id):
    link = first_folder_link(project_id)
    if link is None:
        return {
            "linked": False,
            "available": False,
            "message": "No linked folder.",
            "path": None,
            "link": None
        }

    folder_id = link.get("to")
    path = local_folder_path(folder_id)
    label = link.get("label") or "Linked folder"
    if path is None:
        return {
            "linked": True,
            "available": False,
            "message": f"{label} not available on this machine.",
            "path": None,
            "link": link
        }

    return {
        "linked": True,
        "available": True,
        "message": f"{label} available locally.",
        "path": path,
        "link": link
    }


def open_folder_for_project(project_id):
    status = folder_link_status(project_id)
    path = status["path"]
    if path is None:
        return False
    paths.windows_open_folder_path(path)
    return True
