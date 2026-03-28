"""paths.py  -- path resolution, and basic file access"""

from symbols import *

import json
import os
import subprocess

import machineroot


def db_root():
    return machineroot.get("db-root-2026")


def zoo_root():
    return os.path.join(db_root(), "zoo")


def projects_root():
    return os.path.join(zoo_root(), "projects")


def index_path():
    return os.path.join(zoo_root(), "index.json")


def project_path(project_id):
    return os.path.join(projects_root(), project_id + ".json")


def path_for(sym):
    if sym == PROJ:
        return index_path()
    elif sym == DIR:
        return zoo_root()
    else:
        raise NotImplementedError


def _ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _read_json_file(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_file_atomic(path, data):
    _ensure_parent_dir(path)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def read_json(sym):
    return _read_json_file(path_for(sym))


def write_json(sym, data):
    _write_json_file_atomic(path_for(sym), data)


def read_index():
    return _read_json_file(index_path(), default=[])


def write_index(data):
    _write_json_file_atomic(index_path(), data)


def read_project(project_id):
    return _read_json_file(project_path(project_id))


def write_project(project_id, data):
    _write_json_file_atomic(project_path(project_id), data)


def windows_open_file(sym):
    p = path_for(sym)
    subprocess.call(["notepad", p])


def windows_open_dir(sym):
    p = path_for(sym)
    subprocess.Popen('explorer "{}"'.format(p))


def windows_open_project(project_id):
    p = project_path(project_id)
    subprocess.call(["notepad", p])

