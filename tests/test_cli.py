from multiprocessing import Process

from typer.testing import CliRunner

from hotbox import __version__
from hotbox.cli.main import app


async def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output == __version__


async def test_cli_start_server(runner: CliRunner) -> None:
    p = Process(target=runner.invoke, args=(app, ["server"]))
    p.start()
    p.terminate()
    p.join()
