from typer import Typer, echo

from hotbox import __version__
from hotbox.cli import create, delete, get, server
from hotbox.const import DESC, NAME

app = Typer(
    name=NAME,
    help=DESC,
    no_args_is_help=True,
)


@app.callback()
def main_callback() -> None:
    pass


main_callback.__doc__ = NAME


@app.command("version")
def _version() -> None:
    """Prints the version."""
    echo(__version__, nl=False)


app.add_typer(create.app)
app.add_typer(get.app)
app.add_typer(delete.app)
app.add_typer(server.app)
