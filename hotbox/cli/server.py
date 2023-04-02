import uvicorn
from typer import Option, Typer

from hotbox.const import SERVER_MODULE_NAME

app = Typer(
    name="server",
    help="Run the hotbox server.",
    no_args_is_help=True,
)


@app.command(
    "run",
    help="Run the hotbox server.",
)
def server(
    host: str = Option(
        "127.0.0.1",
        "--host",
        help="Bind socket to this host.",
    ),
    port: int = Option(
        8420,
        "--port",
        help="Bind socket to this port.",
    ),
    reload: bool = Option(
        False,
        help="Reload the server on code changes.",
    ),
    workers: int = Option(
        1,
        "--workers",
        help="Number of workers to run.",
    ),
) -> None:
    uvicorn.run(  # pragma: no cover
        app=SERVER_MODULE_NAME,
        port=port,
        host=host,
        reload=reload,
        workers=workers,
    )
