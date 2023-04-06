from typing import List

import orjson
from typer import Argument, Option, Typer, echo

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
