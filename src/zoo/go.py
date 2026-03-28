"""go.py  -- initialization & kick-off execution"""

from . import gui
from . import menubar
from . import proj
from . import searchwin
from . import projwin


def run():
    proj.setup()
    gui.setup()
    menubar.setup()

    searchwin.setup()
    projwin.setup()

    searchwin.open_up()
    gui.loop()


if __name__ == "__main__":
    run()

