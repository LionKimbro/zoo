"""proj.py  -- data access (projects)"""

from symbols import *

import uuid

import util
import paths
import listdict


PROJECTS = "PROJECTS"  # project_id -> full project dict
DIRTY = "DIRTY"  # set(project ids) that need persistence


g = {
    DATA: None,  # in-memory index summaries
    PROJECTS: {},  # loaded full project records
    DIRTY: set(),
    UPDATE: None,  # update notice (None/int/ACTIVE)
    SEL: None
}


# keys in a project json file
kID = "id"
kTAG = "tag"
kTITLE = "title"
kCREATED = "created"
kTAGS = "tags"
kDESCRIPTION = "description"
kHOOK = "hook"

SUMMARY_FIELDS = [kID, kTITLE, kTAG, kTAGS, kCREATED, kHOOK]


def setup():
    load()
    import gui
    gui.permtask_fn(update)


def load():
    g[DATA] = paths.read_index()
    if g[DATA] is None:
        g[DATA] = []
    g[PROJECTS].clear()
    g[DIRTY].clear()
    note_changed()


def _summary_for(D):
    return {k: D[k] for k in SUMMARY_FIELDS if k in D}


def _sync_summary(project_id):
    summary = _summary_for(g[PROJECTS][project_id])
    for i, existing in enumerate(g[DATA]):
        if existing[kID] == project_id:
            g[DATA][i] = summary
            return
    g[DATA].append(summary)


def save():
    for project_id in list(g[DIRTY]):
        paths.write_project(project_id, g[PROJECTS][project_id])

    fresh_index = paths.read_index()
    if fresh_index is None:
        fresh_index = []
    by_id = {D[kID]: D for D in fresh_index}
    for project_id in g[DIRTY]:
        by_id[project_id] = _summary_for(g[PROJECTS][project_id])

    g[DATA] = list(by_id.values())
    paths.write_index(g[DATA])
    g[DIRTY].clear()
    note_changed()


# Change Notification & Update Cycle

def note_changed():
    """Call this whenever the data is changed."""
    g[UPDATE] = 0


def delay_updates():
    """Call this to delay updates, because the user is typing or something."""
    g[UPDATE] = 5


def update():
    """Called once per cycle, once setup()."""
    if g[UPDATE] == TODO:
        g[UPDATE] = ACTIVE
    elif type(g[UPDATE]) == int:
        if g[UPDATE] > 0:
            g[UPDATE] -= 1
        else:
            g[UPDATE] = ACTIVE
    elif g[UPDATE] == ACTIVE:
        g[UPDATE] = None


# Searching

def _normalize_nodeid(nodeid):
    return str(nodeid)


def locate_id(nodeid):
    """Locate and load the project with the given ID."""
    project_id = _normalize_nodeid(nodeid)
    if project_id in g[PROJECTS]:
        return g[PROJECTS][project_id]

    D = paths.read_project(project_id)
    if D is None:
        return None
    g[PROJECTS][project_id] = D
    return D


def locate_tagged(s):
    """Locate all index summaries with a particular set of tags."""
    listdict.cue(g[DATA])
    for tag in s.split():
        listdict.req(kTAGS, CONTAINS, tag)
    return listdict.val()


# New

def new():
    project_id = str(uuid.uuid4())
    D = {
        kID: project_id,
        kTAG: "",
        kTITLE: "",
        kCREATED: util.iso8601datelocal(),
        kTAGS: [],
        kDESCRIPTION: "",
        kHOOK: ""
    }
    g[PROJECTS][project_id] = D
    g[DIRTY].add(project_id)
    _sync_summary(project_id)
    note_changed()
    return D


# Mediated Access

def sel(D):
    g[SEL] = D


def get_line(k):
    raw = g[SEL].get(k, "")
    if k == kTAGS:
        return " ".join(raw)
    else:
        return raw


def set_line(k, s):
    if k == kTAGS:
        g[SEL][k] = s.split()
    else:
        if k not in g[SEL] and not bool(s):
            pass
        else:
            g[SEL][k] = s

    project_id = g[SEL][kID]
    g[PROJECTS][project_id] = g[SEL]
    g[DIRTY].add(project_id)
    _sync_summary(project_id)


type_dict = {
    SEL: sel,
    GETLINE: get_line,
    SETLINE: set_line
}
