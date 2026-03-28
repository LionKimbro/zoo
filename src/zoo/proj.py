"""proj.py  -- data access (projects)"""

from symbols import *

import util
import paths
import listdict


g = {DATA: None,  # the raw JSON loaded
     UPDATE: None,  # update notice (None/int/ACTIVE), "the data has changed,"
     SEL: None}  # access to a single dictionary in the data, can be mediated


# keys in the PROJ.txt file (identified by symbol PROJ)
kID = "ID"
kTAG = "TAG"
kTITLE = "TITLE"
kCREATED = "CREATED"
kTAGS = "TAGS"
kLOC = "LOC"
kHOOK = "HOOK"


def setup():
    load()
    import gui
    gui.permtask_fn(update)


def load():
    g[DATA] = paths.read_json(PROJ)
    note_changed()

def save():
    paths.write_json(PROJ, g[DATA])

def nextid():
    return 1 + max([int(D[kID]) for D in g[DATA]])


# Change Notification & Update Cycle

def note_changed():
    """call this whenever the data is changed
    
    Call this even if you are going to immediately call delay_updates(),
    because I might want to do some other things here in the future
    as well, that are immediate.
    """
    g[UPDATE] = 0  # will set ACTIVE for one full cycle, immediately

def delay_updates():
    """call this to delay updates, because the user is typing or something"""
    g[UPDATE] = 5


def update():
    """called once per cycle, once setup()"""
    if g[UPDATE] == TODO:
        g[UPDATE] = ACTIVE  # set ACTIVE for one full cycle, ...
    elif type(g[UPDATE]) == int:  # countdown
        if g[UPDATE] > 0:
            g[UPDATE] -= 1
        else:
            g[UPDATE] = ACTIVE
    elif g[UPDATE] == ACTIVE:
        g[UPDATE] = None  # and then clear it


# Searching

def locate_id(nodeid):
    """Locate the entry with the given ID."""
    listdict.cue(g[DATA])
    listdict.req(kID, EQ, nodeid)
    return listdict.val01()

def locate_tagged(s):
    """Locate all entries with a particular set of tags.
    
    s: (str) white-space delimited list of tags
    returns: (list) entries within g[DATA] that include all of the tags
    """
    listdict.cue(g[DATA])
    for tag in s.split():
        listdict.req(kTAGS, CONTAINS, tag)
    return listdict.val()


# New

def new():
    id_str = str(nextid()).rjust(4,"0")  # ex: 13 -> "0013"
    D = {kID: id_str,
         kTAG: "",
         kTITLE: "",
         kCREATED: util.iso8601datelocal(),  # ex: "2022-03-30"
         kTAGS: [],
         kLOC: id_str,
         kHOOK: ""}
    paths.mkprojdir(id_str)
    g[DATA].append(D)
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

type_dict = {
    SEL: sel,
    GETLINE: get_line,
    SETLINE: set_line
}



