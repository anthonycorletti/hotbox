import json
from unittest import mock

from httpx import Response
from typer.testing import CliRunner

from hotbox.cli.main import app


@mock.patch(
    "httpx.post",
    return_value=Response(
        status_code=200,
        json={"message": "ok"},
    ),
)
async def test_create_app_success(
    mock_upload_app_bundle_post: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "app",
            "-n",
            "test-app",
            "-c",
            "tests/assets/code/go",
        ],
    )
    assert result.exit_code == 0


@mock.patch(
    "httpx.post",
    return_value=Response(
        status_code=500,
        json={"message": "oh shit"},
    ),
)
async def test_create_app_fails(
    mock_upload_app_bundle_post: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "app",
            "-n",
            "test-app",
            "-c",
            "tests/assets/code/go",
        ],
    )
    assert result.exit_code == 1
    assert result.output == "Creating app!\n"
    assert result.stderr == (
        "Failed to upload app " "bundle with status code 500, " "and message: oh shit\n"
    )


@mock.patch(
    "httpx.post",
    return_value=Response(
        status_code=500,
        json={"message": "oh shit"},
    ),
)
async def test_create_app_fails_unsupported_lang(
    mock_upload_app_bundle_post: mock.MagicMock,
    runner: CliRunner,
) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "app",
            "-n",
            "test-app",
            "-c",
            "tests/assets/code/hoon",
        ],
    )
    assert result.exit_code == 1
    assert result.stdout == "Creating app!\n"
    assert result.stderr.startswith("Unsupported application content.")


@mock.patch("httpx.get", return_value=Response(status_code=200, json={"apps": []}))
async def test_get_apps(mock_get_response: mock.MagicMock, runner: CliRunner) -> None:
    result = runner.invoke(app, ["get", "app"])
    assert result.exit_code == 0
    assert json.loads(result.stdout.strip()) == {"apps": []}


@mock.patch(
    "httpx.delete",
    return_value=Response(status_code=200, json={"deleted_apps": ["my-app"]}),
)
async def test_delete_apps(
    mock_delete_response: mock.MagicMock, runner: CliRunner
) -> None:
    result = runner.invoke(app, ["delete", "app", "my-app"])
    assert result.exit_code == 0
    assert result.stdout == "Deleting apps: my-app\n"
