import json
from typing import List, Optional

from typer import Argument, FileText, Option, Typer, echo

from hotbox.const import DEFAULTS, DESC, NAME, SERVICE_MAP, TYPE_MAP
from hotbox.types import HotboxKind, HotboxVersion
from hotbox.utils import handle_spec, json_serializer

app = Typer(
    name=NAME,
    help=DESC,
    no_args_is_help=True,
)


@app.callback()
def main_callback() -> None:
    pass


main_callback.__doc__ = NAME


@app.command(
    "create",
    help="Create resources.",
    no_args_is_help=True,
)
def create(
    kind: HotboxKind,
    spec: FileText = Option(
        ...,
        allow_dash=True,
    ),
) -> None:
    _spec = handle_spec(spec)
    _spec["kind"] = kind
    if "version" not in _spec:
        _spec["version"] = DEFAULTS[HotboxVersion]
    content = TYPE_MAP[kind](**_spec)
    assert (
        type(content) == TYPE_MAP[kind]
    ), f"Invalid spec for resource, {TYPE_MAP[kind]}."
    service = SERVICE_MAP[kind]
    response = service.create(content)
    echo(
        json.dumps(
            response,
            default=json_serializer,
        )
    )


@app.command(
    "get",
    help="Get resources.",
    no_args_is_help=True,
)
def get(
    kind: HotboxKind,
    region: Optional[str] = Option(
        None,
        help="AWS Region of resources to delete.",
    ),
) -> None:
    service = SERVICE_MAP[kind]
    response = service.get(region=region)
    echo(
        json.dumps(
            response,
            default=json_serializer,
        )
    )


@app.command(
    "delete",
    help="Delete resources.",
    no_args_is_help=True,
)
def delete(
    kind: HotboxKind,
    ids: List[str] = Argument(..., help="IDs of resources to delete."),
    region: Optional[str] = Option(
        None,
        help="AWS Region of resources to delete.",
    ),
) -> None:
    service = SERVICE_MAP[kind]
    response = service.delete(ids, region)
    echo(
        json.dumps(
            response,
            default=json_serializer,
        )
    )
