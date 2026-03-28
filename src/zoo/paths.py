"""paths.py  -- path resolution, and basic file access"""

from symbols import *

import json
import subprocess
import os


def path_for(sym):
    if sym == PROJ:
        return "F:\\bigfiles\\onedrive2022\\OneDrive\\origins\\2021\\data\\lists\\PROJ\\PROJ.txt"
    elif sym == DIR:
        return "F:\\bigfiles\\onedrive2022\\OneDrive\\origins\\2021\\data\\lists\\PROJ\\"
    else:
        raise NotImplementedError

def path_for_projdir(dirname):
    return path_for(DIR) + dirname


def read_json(sym):
    return json.load(open(path_for(sym), "r", encoding="utf-8"))

def write_json(sym, data):
    json.dump(data, open(path_for(sym), "w", encoding="utf-8"), indent=2)


def windows_open_file(sym):
    p = path_for(sym)
    subprocess.call(["notepad", p])

def windows_open_dir(sym):
    p = path_for(sym)
    subprocess.Popen('explorer "{}"'.format(p))

def windows_open_projdir(dirname):
    """NOTE: This isn't used yet, but you should be able to open a specific project's directory."""
    p = path_for_projdir(dirname)
    subprocess.Popen('explorer "{}"'.format(p))


def mkprojdir(dirname):
    p = path_for_projdir(dirname)
    os.mkdir(p)

