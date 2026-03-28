
from symbols import *

import gui


tcl_code = """
menu $w.menubar
$w configure -menu $w.menubar

menu $w.menubar.file
$w.menubar add cascade -menu $w.menubar.file -label File -underline 0

$w.menubar.file add command -label "New Project" -command "newproject" -underline 0
$w.menubar.file add command -label "Open Source" -command "opensource" -underline 0
$w.menubar.file add command -label "Open Source Dir" -command "opensourcedir" -underline 12
$w.menubar.file add command -label "Reload Source" -command "reloadsource" -underline 0
$w.menubar.file add command -label "Save" -command "savestate" -underline 0
$w.menubar.file add command -label "Close Window" -command "closewindow" -underline 0
$w.menubar.file add command -label "Exit" -command "exitprogram" -underline 1

$w.menubar add command -label "Search" -command "opensearch" -underline 0
"""

def opensearch():
    import searchwin
    searchwin.open_up()

def newproject():
    import proj
    import projwin
    projwin.open_up(proj.new())
    

def opensource():
    import paths
    paths.windows_open_file(PROJ)

def opensourcedir():
    import paths
    paths.windows_open_dir(DIR)

def reloadsource():
    import proj
    proj.load()

def savestate():
    import proj
    proj.save()

def closewindow():
    gui.cue()  # focuses the current focused window
    gui.task_closetop(gui.top())  # closes the top for the focused window


def setup():
    gui.mkcmd("opensearch", lambda: gui.task_fn(opensearch))
    gui.mkcmd("newproject", lambda: gui.task_fn(newproject))
    gui.mkcmd("opensource", lambda: gui.task_fn(opensource))
    gui.mkcmd("opensourcedir", lambda: gui.task_fn(opensourcedir))
    gui.mkcmd("reloadsource", lambda: gui.task_fn(reloadsource))
    gui.mkcmd("savestate", lambda: gui.task_fn(savestate))
    gui.mkcmd("closewindow", lambda: gui.task_fn(closewindow))
    gui.mkcmd("exitprogram", gui.task_exit)

def attach():
    gui.tclexec(tcl_code)

