"""guiutil.py  -- various utilities (for the GUI)"""

from .symbols import *

from . import util
from . import gui


g = {BINDINGS: None,  # bindings source
     DATA: None,  # data dictionary, for store/load values
     TYPE: None,  # type dictionary for DATA
     CHANGES: []}  # list of bindings for which changes have been identified

prior_txt = {}  # tkname -> txt


"""BINDINGS: a list of bindings dictionaries

keys:
  TKNAME: -- path to the tk widget (can include $top)
  KEY: -- data dictionary key
  RW: True/False -- is this widget supposed to be read-write?
"""

def use_bindings(bindings):
    g[BINDINGS] = bindings

def use_data(data, typedict):
    g[DATA] = data
    g[TYPE] = typedict


def mkbinding(tkname, k, rw):
    """Use this fn while defining bindings."""
    return {TKNAME: tkname,
            KEY: k,
            RW: rw}

def mkbindings(data):
    """Make a collection of bindings from a DATA source.
    
    ex:
      ["$top.bas
    """
    L = []
    util.data(data)
    while util.dmore():
        L.append(mkbinding(util.READ(),
                           util.READ(),
                           util.READ()))
    return L


def notice_changes():
    """Review bindings, and note value changes.
    
    in:
      g[BINDINGS]  -- the bindings to check for changes;
                      call use_bindings to specify for use
      GUI $top  -- gui.cue_top should be positioned to the window
                   that you want to notice changes in, and it
                   should match the bindings used
      prior_txt  -- the dictionary of prior values for the widgets

    out:
      g[CHANGES]  -- a list of bindings for which changes were
                     noted since the last call
      prior_txt  -- the dictionary is updated with the immediate
                    values
    
    Returns: (bool) True if changes were observed,
                    False otherwise
    """
    g[CHANGES][:] = []
    for bindD in g[BINDINGS]:
        w = bindD[TKNAME]
        gui.cue(w)
        w2 = gui.cur()  # get the RESOLVED name (w/o $top)
        found = gui.text_get()
        if w2 in prior_txt:  # do I know about it?
            if prior_txt[w2] != found:
                prior_txt[w2] = found
                g[CHANGES].append(bindD)
        else:
            prior_txt[w2] = found  # first time seeing
    return bool(g[CHANGES])


def update_from_changes():
    """If called after notice_changes(), updates g[DATA] for changed items.
    
    Iterates through g[CHANGES], and stores values found into g[DATA].
    
    in:
      (all of the inputs for notice_changes)
      g[DATA]  -- the dictionary that updates will be written into;
                  set with use_data(D)
    
    out:
      g[DATA]  -- the data values read from the GUI will be poked into
                  this dictionary in accordance with the bindings
                  KEY value

    If the contents of a GUI text field changed since the last call,
    (a comparison made via notice_changes(),) it will be written to
    the GUI changed since th changed store a value into the dictionary.
    """
    g[TYPE][SEL](g[DATA])
    for bindD in g[CHANGES]:
        gui.cue(bindD[TKNAME])
        g[TYPE][SETLINE](bindD[KEY], gui.text_get())


#    TODO("make a system that cleans out data for which a window no longer exists")
#    TODO("  - make an update function in here")
#    TODO("  - rename this to guibindings.py")
#    TODO("  - make a setup() fn that registers w/ the gui system")


def fill_repopulate():
    """Perform a raw fill, populating from the data dictionary.
    
    g[BINDINGS]  -- the bindings to use (use_bindings to fill)
    g[DATA]  -- the data to populate from (use_data to fill)
    """
    if g[DATA] is None:
        fill_clear()
        return
    g[TYPE][SEL](g[DATA])
    for bindD in g[BINDINGS]:
        w, k, rw = bindD[TKNAME], bindD[KEY], bindD[RW]
        gui.cue(w)
        if gui.is_focused():
            continue  # SKIP, because user is actively working in here
        if not rw:
            gui.text_rw()
        gui.text_set(g[TYPE][GETLINE](k))
        if not rw:
            gui.text_ro()


def fill_clear():
    """Perform a raw clear."""
    for bindD in g[BINDINGS]:
        w, k, rw = bindD[TKNAME], bindD[KEY], bindD[RW]
        gui.cue(w)
        if not rw:
            gui.text_rw()
        gui.text_set("")
        if not rw:
            gui.text_ro()

