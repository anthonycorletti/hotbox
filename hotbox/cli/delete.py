from typing import List

import orjson
from typer import Argument, Option, Typer, echo

from hotbox.app import app_svc
from hotbox.ec2 import ec2_svc

app = Typer(
    name="delete",
    help="Delete resources.",
    no_args_is_help=True,
)


@app.command(
    "ec2",
    help="Delete ec2 resources.",
    no_args_is_help=True,
)
def delete_ec2(
    ids: List[str] = Argument(
        ...,
        help="IDs of resources to delete.",
    ),
    region: str = Option(
        None,
        help="AWS Region.",
    ),
) -> None:
    response = ec2_svc.delete(ids, region)
    echo(orjson.dumps(response))


@app.command(
    "app",
    help="Delete apps.",
    no_args_is_help=True,
)
def delete_app(
    app_names: List[str] = Argument(
        ...,
        help="Names of apps to delete.",
    ),
) -> None:
    response = app_svc.make_delete_request(app_names=app_names)
    echo(f"Deleting apps: {','.join(response.json()['deleted_apps'])}")
