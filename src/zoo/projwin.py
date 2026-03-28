"""projwin.py  -- window displaying a single project"""

from .symbols import *

from . import gui
from . import util
from . import guiutil

from . import proj
from .proj import kTAG, kTITLE, kCREATED, kTAGS, kHOOK  # kID -- name conflict


tcl_code = """
ttk::labelframe $top.basics -text "basics"
ttk::label $top.basics.id_k -text "id:"
ttk::entry $top.basics.id_v -width 40 -state readonly
ttk::label $top.basics.uritag_k -text "URI tag:"
ttk::entry $top.basics.uritag_v -width 70
ttk::label $top.basics.title_k -text "title:"
ttk::entry $top.basics.title_v -width 80
ttk::label $top.basics.created_k -text "created:"
ttk::entry $top.basics.created_v -width 20 -state readonly
ttk::label $top.basics.tags_k -text "tags:"
ttk::entry $top.basics.tags_v -width 100
ttk::label $top.basics.hook_k -text "hook:"
ttk::entry $top.basics.hook_v -width 80
ttk::labelframe $top.ops -text "operations"
ttk::button $top.ops.open -text "open json" -command projwin_openproj
ttk::labelframe $top.info -text "info"
ttk::label $top.info.hint

grid $top.basics -row 0 -column 0 -sticky nsew
grid $top.ops -row 1 -column 0 -sticky nsew
grid $top.info -row 2 -column 0 -sticky nsew

grid $top.basics.id_k -row 0 -column 0 -sticky e
grid $top.basics.id_v -row 0 -column 1 -sticky w
grid $top.basics.uritag_k -row 1 -column 0 -sticky e
grid $top.basics.uritag_v -row 1 -column 1 -sticky w
grid $top.basics.title_k -row 2 -column 0 -sticky e
grid $top.basics.title_v -row 2 -column 1 -sticky w
grid $top.basics.created_k -row 3 -column 0 -sticky e
grid $top.basics.created_v -row 3 -column 1 -sticky w
grid $top.basics.tags_k -row 4 -column 0 -sticky e
grid $top.basics.tags_v -row 4 -column 1 -sticky w
grid $top.basics.hook_k -row 5 -column 0 -sticky e
grid $top.basics.hook_v -row 5 -column 1 -sticky w

grid $top.ops.open -row 0 -column 0

grid $top.info.hint
"""

source_code = """
$top
  basics [lf] "basics"
    id_k "id:"
    id_v [ent:6]
    uritag_k "URI tag:"
    uritag_v [ent:70]
    title_k "title:"
    title_v [ent:80]
    created_k "created:"
    created_v [ent:20]
    tags_k "tags:"
    tags_v [ent:100]
    loc_k "loc:"
    loc_v [ent:6]
    hook_k "hook:"
    hook_v [ent:80]
  ops [lf] "operations"
    open [btn] "open"
  info [lf] "info"
     hint [lbl]

--------------------

$top

$top.basics [0,0] {nsew}
$top.ops [0,1] {nsew}
$top.info [0,2] {nsew}

$top.basics.id_k [0,0] {e}
$top.basics.id_v [1,0] {w}
$top.basics.uritag_k [0,1] {e}
$top.basics.uritag_v [1,1] {w}
$top.basics.title_k [0,2] {e}
$top.basics.title_v [1,2] {w}
$top.basics.created_k [0,3] {e}
$top.basics.created_v [1,3] {w}
$top.basics.tags_k [0,4] {e}
$top.basics.tags_v [1,4] {w}
$top.basics.loc_k [0,5] {e}
$top.basics.loc_v [1,5] {w}
$top.basics.hook_k [0,6] {e}
$top.basics.hook_v [1,6] {w}

$top.ops.open [0,0]

$top.info.hint


REMEMBER to REMOVE from output:
  grid $top
...or else Tk will complain,
   that you're managing a top-level window...
"""


tkROOT = ".projwin"  # base name for projwin windows
tkID = "$top.basics.id_v"  # the project ID for this window
tkTITLE = "$top.basics.title_v"  # the Title entry for this window
tkHINT = "$top.info.hint"  # the hint label (NOT USED YET)


# Functions -- Setup

def setup():
    gui.mkcmd("projwin_openproj", openproj)
    gui.permtask_fn(update)


def open_up(D):  # open with a particular project description
    D = proj.locate_id(D[proj.kID]) or D
    gui.toplevel_recurring(tkROOT)
    gui.tclexec(tcl_code)
    gui.title(D[proj.kID])
    brand(D[proj.kID])
    first_time.append(gui.top())


# Identification

def brand(projid):
    """brand the window with a project ID
    
    This should only ever be called once -- during open_up(D).
    """
    gui.cue(tkID)
    gui.text_rw()
    gui.text_set(projid)
    gui.text_ro()

def curid():
    gui.cue(tkID)
    return gui.text_get()

def curproj():
    return proj.locate_id(curid())


# Callbacks

def openproj():
    from . import paths
    paths.windows_open_project(curproj()[proj.kID])


# Update Cycle

first_time = []  # list of tknames for which this is the first time showing

bindings = guiutil.mkbindings(
    ["$top.basics.uritag_v", kTAG, True,
     "$top.basics.title_v", kTITLE, True,
     "$top.basics.created_v", kCREATED, False,
     "$top.basics.tags_v", kTAGS, True,
     "$top.basics.hook_v", kHOOK, True]
)

def update():
    gui.cue(".")
    for tkname in gui.children():
        if tkname.startswith(tkROOT):
            gui.cue(tkname)
            gui.cue_top()
            update_win()

def update_win():
    """update fn, with $top set to a specific window"""
    tkname = gui.top()
    D = curproj()
    if D is None:
        return
    guiutil.use_bindings(bindings)
    guiutil.use_data(D, proj.type_dict)
    if tkname in first_time:
        first_time.remove(tkname)
        guiutil.fill_repopulate()
        # After it's been populated, put the focus on the title.
        # If you focus on the title earlier, it won't populate,
        # because it'll yield to an in-progress editing..!
        gui.cue(tkTITLE)
        gui.focus()
    elif guiutil.notice_changes():  # are contents of gui widgets changed?
        guiutil.update_from_changes()  # update project data (D) with changes
        proj.note_changed()  # tell proj that something (an "anything") changed
    elif proj.g[UPDATE] == ACTIVE:
        guiutil.fill_repopulate()


