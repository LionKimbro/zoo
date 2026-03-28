"""go.py  -- initialization & kick-off execution"""

import gui
import menubar
import proj
import searchwin
import projwin


proj.setup()
gui.setup()
menubar.setup()

searchwin.setup()
projwin.setup()


searchwin.open_up()
gui.loop()

