"""search.py  -- core interactive window: searching"""

from .symbols import *

from . import gui
from . import util

from . import proj
from . import projwin


tcl_code = """
ttk::frame $w.search
ttk::label $w.search.lbl -text "Tags Search:"
ttk::entry $w.search.e -width 50
ttk::frame $w.results
ttk::label $w.results.lbl -text "Results:"
ttk::treeview $w.results.tree -selectmode browse -columns "title created hook" -takefocus 1
ttk::scrollbar $w.results.slider -orient vertical -command "$w.results.tree yview"

$w.results.tree column #0 -width 60
$w.results.tree heading #0 -text "ID" -command searchwin_sort_id

$w.results.tree column title -width 300
$w.results.tree heading title -text "Title" -command searchwin_sort_title

$w.results.tree column created -width 100
$w.results.tree heading created -text "Created" -command searchwin_sort_created

$w.results.tree column hook -width 600
$w.results.tree heading hook -text "Hook" -command searchwin_sort_hook

grid $w.search -row 0 -column 0 -rowspan 1 -columnspan 1 -sticky nsew
grid $w.results -row 1 -column 0 -rowspan 1 -columnspan 1 -sticky nsew

grid $w.search.lbl -row 0 -column 0 -rowspan 1 -columnspan 1 -sticky nsew
grid $w.search.e -row 0 -column 1 -rowspan 1 -columnspan 1 -sticky nsew

grid $w.results.lbl -row 0 -column 0 -rowspan 1 -columnspan 2 -sticky nsew
grid $w.results.tree -row 1 -column 0 -rowspan 1 -columnspan 1 -sticky nsew
grid $w.results.slider -row 1 -column 1 -rowspan 1 -columnspan 1 -sticky nsew

bind $w.results.tree <FocusIn> {searchwin_tree_focusin}
bind $w.results.tree <Double-1> {searchwin_tree_doubleclick}
bind $w.results.tree <Return> {searchwin_tree_doubleclick}

grid rowconfigure $w 0 -weight 0
grid rowconfigure $w 1 -weight 1

grid rowconfigure $w.results 0 -weight 0
grid rowconfigure $w.results 1 -weight 1
"""


tkWIN = ".searchwin"
tkENTRY = ".searchwin.search.e"  # the search box
tkTREE = ".searchwin.results.tree"  # the results tree


# Functions -- Setup

def setup():
    gui.mkcmd("searchwin_tree_doubleclick", tree_doubleclick)
    gui.mkcmd("searchwin_tree_focusin", tree_focusin)
    gui.mkcmd("searchwin_sort_id", lambda: sort_by(proj.kID))
    gui.mkcmd("searchwin_sort_title", lambda: sort_by(proj.kTITLE))
    gui.mkcmd("searchwin_sort_created", lambda: sort_by(proj.kCREATED))
    gui.mkcmd("searchwin_sort_hook", lambda: sort_by(proj.kHOOK))
    gui.permtask_fn(update)
    # TODO: make it so that the enter key triggers a command that performs a search
    # gui.mkcmd("dosearch", repopulate)

def open_up():
    if gui.toplevel_unique(".searchwin", "Search Projects"):
        gui.tclexec(tcl_code)
        gui.cue(".searchwin.search.e")
        gui.lift()
        lasttime[0] = None

sort_key = [None]
sort_reverse = [False]

sort_headings = {
    proj.kID: ("#0", "ID"),
    proj.kTITLE: ("title", "Title"),
    proj.kCREATED: ("created", "Created"),
    proj.kHOOK: ("hook", "Hook"),
}


def sort_by(k):
    if sort_key[0] == k:
        sort_reverse[0] = not sort_reverse[0]
    else:
        sort_key[0] = k
        sort_reverse[0] = False
    repopulate()


def _sort_value(D, k):
    return str(D.get(k, "") or "").casefold()


def _sorted_rows(rows):
    if sort_key[0] is None:
        return rows
    return sorted(rows,
                  key=lambda D: (_sort_value(D, sort_key[0]),
                                 _sort_value(D, proj.kTITLE),
                                 _sort_value(D, proj.kID)),
                  reverse=sort_reverse[0])


def _refresh_sort_headings():
    for k, (column, label) in sort_headings.items():
        marker = ""
        if sort_key[0] == k:
            marker = " v" if sort_reverse[0] else " ^"
        gui.tclexec("{} heading {} -text {}".format(tkTREE, column, gui.quote(label + marker)))

# Callback -- repop(ulate)

def repopulate():
    """Clear & repopulate the search tree."""
    gui.cue(tkENTRY)
    txt = gui.text_get()
    gui.cue(tkTREE)
    selected_id = util.first(gui.tree_selected())
    gui.tree_clear()
    rows = _sorted_rows(list(proj.locate_tagged(txt)))
    row_ids = []
    for D in rows:
        row_id = D.get(proj.kID, "")
        row_ids.append(row_id)
        gui.tree_add(D.get(proj.kID, ""),
                     [D.get(proj.kTITLE, ""),
                      D.get(proj.kCREATED, ""),
                      D.get(proj.kHOOK, "")])
    _refresh_sort_headings()
    if selected_id in row_ids:
        gui.tree_select([selected_id])
        gui.tree_focus(selected_id)


# Periodic Updates (every 100ms)

lasttime = [None]  # lasttime[0] -- the search box

def exists():
    gui.cue(tkWIN)
    return gui.exists()

def update():
    if not exists():
        return
    gui.cue(tkENTRY)  # the search box
    # detect change:
    txt = gui.text_get()
    txt_changed = (txt != lasttime[0])
    if txt_changed or proj.g[UPDATE] == ACTIVE:
        repopulate()
    lasttime[0] = txt


def selection_to_proj():
    nodeid = util.first(gui.tree_selected())
    return proj.locate_id(nodeid) if nodeid else None

def tree_doubleclick():
    gui.cue(tkTREE)
    D = selection_to_proj()
    if D:
        projwin.open_up(D)

def tree_focusin():
    gui.cue(tkTREE)
    if gui.tree_selected():  # if there's something selected,
        pass  # no need to do anything - it'll work as expected
    else:
        L = gui.tree_items()
        if L:
            gui.tree_focus(L[-1])  # just focus the first one, which is listed last
        else:
            gui.cue(tkENTRY)  # there are no items, so focus the entry back again
            gui.focus()


