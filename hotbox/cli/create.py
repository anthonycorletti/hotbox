import json

from typer import Exit, FileText, Option, Typer, echo

from hotbox.ec2 import ec2_svc
from hotbox.types import Ec2Spec
from hotbox.utils import handle_filetext, json_serializer

app = Typer(
    name="create",
    help="Create resources.",
    no_args_is_help=True,
)


@app.command(
    "ec2",
    help="Create ec2 resources.",
    no_args_is_help=True,
)
def create_ec2(
    firecracker_version: str = Option(
        "v1.3.1",
        "-fcv",
        "--firecracker-version",
        help="Firecracker version.",
    ),
    _filetext: FileText = Option(
        ...,
        "-f",
        "--file",
        allow_dash=True,
    ),
) -> None:
    if _filetext is None:
        echo("Please provide a spec.")
        raise Exit(1)
    content = Ec2Spec(**handle_filetext(_filetext))
    response = ec2_svc.create(
        spec=content,
        firecracker_version=firecracker_version,
    )
    echo(
        json.dumps(
            response,
            default=json_serializer,
        )
    )


@app.command(
    "app",
)
def create_app(
    app_name: str,
) -> None:
    # given an instance id, deploy n instances of the application to the instance
    # based on the options we provide (see userdata)
    # things to think about – where is the rootfs actually built? locally? in kubernetes? on the instance?
    # if its on the instance it can be faster, with kubernetes it can be a bit more systematic
    # let's try on the instance first
    # so the following needs to happen
    # ⭐️ hm maybe instead of shipping the code over ssh, send it to an API endpoint in k8s and it does the scanning and image building
    # 1. the code is packaged up and uploaded to the instance at a location (id location) (adhering to some ignore, gitignore and dockerignore by default)
    # 2. the code is built on the ec2 instance with docker and the rootfs is left in a location (id location)
    # 3. the rootfs is then built and passed to firecracker to be used as the rootfs with all the relevant configs passed to it (via code - no configs!)
    # 4. the app is run on a fc microvm
    # 5. the app does its thing and then shuts down
    echo("Creating app!")
