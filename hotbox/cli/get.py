import json

from typer import Option, Typer, echo

from hotbox.ec2 import ec2_svc
from hotbox.utils import json_serializer

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
    echo(
        json.dumps(
            response,
            default=json_serializer,
        )
    )
