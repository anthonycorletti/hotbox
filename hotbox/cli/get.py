from typing import Optional

import httpx
import orjson
from typer import Option, Typer, echo

from hotbox.ec2 import ec2_svc
from hotbox.settings import env
from hotbox.types import Routes

app = Typer(
    name="get",
    help="Get resources.",
    no_args_is_help=True,
)


@app.command(
    "ec2",
    help="Get ec2 resources.",
    no_args_is_help=True,
)
def get_ec2(
    region: str = Option(
        None,
        help="AWS Region.",
    ),
) -> None:
    response = ec2_svc.get(
        region=region,
    )
    echo(orjson.dumps(response))


@app.command(
    "app",
    help="Get apps.",
)
def get_apps(
    app_name: Optional[str] = Option(
        None,
        "-n",
        "--name",
        help="App name.",
    )
) -> None:
    response = httpx.get(
        url=env.HOTBOX_API_URL + Routes.apps,
    )
    echo(orjson.dumps(response.json()))
