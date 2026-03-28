"""cli.py  -- lionscliapp launcher for Zoo"""

from pathlib import Path
import sys

try:
    import lionscliapp as app
except ModuleNotFoundError:
    lionscliapp_src = Path(__file__).resolve().parents[3] / "lionscliapp" / "src"
    if lionscliapp_src.exists():
        sys.path.insert(0, str(lionscliapp_src))
    import lionscliapp as app

from . import go


def run():
    go.run()


app.declare_app("zoo", "2026.03")
app.describe_app("Browse and edit Zoo projects")
app.declare_projectdir(".zoo")
app.set_flag("search_upwards_for_project_dir", True)
app.set_flag("allow_execroot_override", False)
app.set_flag("allow_projectdir_override", False)

app.declare_cmd("", run)
app.describe_cmd("", "Launch the Zoo GUI")

app.declare_cmd("run", run)
app.describe_cmd("run", "Launch the Zoo GUI")


def main():
    app.main()
