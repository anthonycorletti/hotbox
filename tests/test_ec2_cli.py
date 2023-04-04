from unittest import mock

from typer.testing import CliRunner

from hotbox.cli.main import app
from tests.mocks import MockEc2Service


@mock.patch(
    "hotbox.ec2.ec2_svc.ec2_client",
    return_value=MockEc2Service(),
)
def test_create_ec2(
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
def test_get_ec2(
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
def test_delete_ec2(
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
