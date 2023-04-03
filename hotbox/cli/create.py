import json
import tempfile

from typer import Argument, Exit, FileText, Option, Typer, echo

from hotbox.app import app_svc
from hotbox.ec2 import ec2_svc
from hotbox.types import Ec2Spec, Image
from hotbox.utils import (
    determine_lang,
    generate_app_id,
    handle_filetext,
    json_serializer,
)

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
    app_name: str = Argument(
        ...,
        help="Name of the app.",
    ),
    app_code_path: str = Option(
        ...,
        "-c",
        "--code",
        help="Path to the app code.",
    ),
    vcpu_count: int = Option(
        1,
        "-v",
        "--vcpu-count",
        help="Number of vcpus.",
    ),
    mem_size_mib: int = Option(
        256,
        "-m",
        "--mem-size-mib",
        help="Memory size in MiB.",
    ),
) -> None:
    echo("Creating app!")
    app_id = generate_app_id()
    lang = determine_lang(app_code_path=app_code_path)
    build_image = getattr(Image, lang.name)
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_path = app_svc.create_app_bundle(
            app_id=app_id,
            app_code_path=app_code_path,
            build_image=build_image,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            tmpdir=tmpdir,
        )
        response = app_svc.upload_app_bundle(
            app_id=app_id,
            bundle_path=bundle_path,
        )
    if response is None:
        echo("Failed to upload app bundle!")
        raise Exit(1)
    return json.loads(response).get("message")
