from unittest import mock

from typer.testing import CliRunner

from hotbox.cli.main import app
from tests.mocks import MockEc2Service


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
async def test_create_ec2(
    mock_ec2_svc: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "ec2",
            "-f",
            '{"region": "us-east-1", "key_name": "fc-demo",'
            ' "security_group_ids": ["sg-0000"]}',
        ],
    )
    assert result.exit_code == 0
    assert result.output is not None


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
async def test_create_ec2_from_file(
    mock_ec2_svc: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "ec2",
            "-f",
            "./tests/assets/files/ec2.json",
        ],
    )
    assert result.exit_code == 0
    assert result.output is not None


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
async def test_create_ec2_from_stdin(
    mock_ec2_svc: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app=app,
        args=[
            "create",
            "ec2",
            "-f",
            "-",
        ],
        input='{"region": "us-east-1", "key_name": "fc-demo",'
        ' "security_group_ids": ["sg-0000"]}',
    )
    assert result.exit_code == 0
    assert result.output is not None


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
async def test_get_ec2(
    mock_ec2_svc: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "get",
            "ec2",
            "--region",
            "us-east-1",
        ],
    )
    assert result.exit_code == 0
    assert result.output is not None


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
async def test_delete_ec2(
    mock_ec2_svc: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "delete",
            "ec2",
            "i-0000",
            "--region",
            "us-east-1",
        ],
    )
    assert result.exit_code == 0
    assert result.output is not None


async def test_create_ec2_catch_no_file(
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "ec2",
            "-fcv",
            "v1.3.1",
        ],
    )
    assert result.exit_code == 1
