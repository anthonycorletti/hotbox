import tempfile
from typing import List

import orjson
from typer import Exit, FileText, Option, Typer, echo

from hotbox.app import app_svc
from hotbox.ec2 import ec2_svc
from hotbox.types import Ec2Spec, Image, Language
from hotbox.utils import determine_lang, handle_filetext

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
    region: str = Option(
        None,
        "-r",
        "--region",
        help="AWS region.",
    ),
    key_name: str = Option(
        None,
        "-k",
        "--key-name",
        help="AWS key name. Should be in the region you specify.",
    ),
    security_group_ids: List[str] = Option(
        None,
        "-s",
        "--security-group-ids",
        help="AWS security group ids. Should be in the region you specify.",
    ),
    _filetext: FileText = Option(
        None,
        "-f",
        "--file",
        allow_dash=True,
        help="Path to the spec file. Accepts JSON strings as input too."
        " Overrides all other options.",
    ),
) -> None:
    """Create ec2 resources.

    This command creates ec2 resources. You can specify certain args directly as listed
    below, or you can specify a spec file with the `-f` or `--file` option. If you
    specify a spec file, all other options will be ignored.

    Args:
        firecracker_version (str, optional): Firecracker version. Defaults to "v1.3.1".
        region (str, optional): AWS region. Defaults to "us-east-1".
        key_name (str, optional): AWS key name. Should be in the region you specify.
            Defaults to None.
        security_group_ids (List[str], optional): AWS security group ids. Should be in
            the region you specify. Defaults to None.
        _filetext (FileText, optional): Path to the spec file. Accepts JSON strings as
            input too. Overrides all other options. Defaults to None.
    """
    echo("Creating ec2!")
    if _filetext is not None:
        content = Ec2Spec(**handle_filetext(str(_filetext)))
    else:
        content = Ec2Spec(
            region=region,
            key_name=key_name,
            security_group_ids=security_group_ids,
        )
    response = ec2_svc.create(
        spec=content,
        firecracker_version=firecracker_version,
    )
    echo(orjson.dumps(response))


@app.command(
    "app",
    help="Deploy apps.",
    no_args_is_help=True,
)
def create_app(
    app_name: str = Option(
        ...,
        "-n",
        "--name",
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
    fs_size_mib: int = Option(
        50,
        "-s",
        "--fs-size-mib",
        help="Size of the rootfs in MiB.",
    ),
) -> None:
    echo("Creating app!")
    lang = determine_lang(app_code_path=app_code_path)
    if lang is None:
        echo(
            message="Unsupported application content. "
            + "Please use a supported language: "
            + ",".join(list(map(lambda x: x.name, Language))),
            err=True,
        )
        raise Exit(1)
    build_image = getattr(Image, lang.name)
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_path = app_svc.create_app_bundle(
            app_name=app_name,
            app_code_path=app_code_path,
            build_image=build_image,
            vcpu_count=vcpu_count,
            mem_size_mib=mem_size_mib,
            tmpdir=tmpdir,
            fs_size_mib=fs_size_mib,
        )
        response = app_svc.upload_app_bundle(
            app_name=app_name,
            bundle_path=bundle_path,
        )
    if not response.is_success:
        echo(
            message=(
                "Failed to upload app bundle with status code "
                f"{response.status_code}, and message: "
                f"{response.json().get('message')}"
            ),
            err=True,
        )
        raise Exit(1)
    echo(response.json().get("message"))
