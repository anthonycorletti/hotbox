import os
from unittest import mock

from httpx import AsyncClient

from hotbox import __version__
from hotbox.const import API_V0


async def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


async def test_healthcheck(client: AsyncClient) -> None:
    response = await client.get(f"{API_V0}/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "ok"
    assert response.json()["version"] == __version__


@mock.patch(
    "hotbox.app.app_svc.unzip_and_run",
    return_value=None,
)
async def test_create_app(
    mock_unzip_and_run: mock.MagicMock, client: AsyncClient
) -> None:
    response = await client.post(
        f"{API_V0}/apps",
        files={
            "upload_file": (
                "test.tar.gz",
                b"test",
                "application/gzip",
            ),
            "create_app_request": (
                None,
                b'{"app_id": "test"}',
                "application/json",
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "App running in the cloud!"
