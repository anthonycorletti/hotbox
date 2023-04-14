import os
from typing import AsyncGenerator
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
                b'{"app_name": "test"}',
                "application/json",
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "App running in the cloud!"
    os.remove("test.tar.gz")


async def test_get_apps_empty(client: AsyncClient) -> None:
    response = await client.get(f"{API_V0}/apps")
    assert response.status_code == 200
    assert response.json() == {"apps": {}}


async def test_get_apps_many(
    client: AsyncClient, create_test_fc_config_files: AsyncGenerator
) -> None:
    response = await client.get(f"{API_V0}/apps")
    data = response.json()
    assert response.status_code == 200
    assert len(data["apps"]) == 2
    assert set(data["apps"].keys()) == {"ui", "api"}


async def test_get_apps_on(
    client: AsyncClient, create_test_fc_config_files: AsyncGenerator
) -> None:
    response = await client.get(f"{API_V0}/apps?name=ui")
    data = response.json()
    assert response.status_code == 200
    assert len(data["apps"]) == 1
    assert set(data["apps"].keys()) == {"ui"}


async def test_delete_apps(
    client: AsyncClient, create_test_fc_config_files: AsyncGenerator
) -> None:
    response = await client.get(f"{API_V0}/apps")
    data = response.json()
    assert response.status_code == 200
    assert len(data["apps"]) == 2
    response = await client.delete(f"{API_V0}/apps", params={"app_names": ["ui"]})
    assert response.status_code == 200
    assert response.json()["deleted_apps"] == ["ui"]
    response = await client.get(f"{API_V0}/apps")
    data = response.json()
    assert response.status_code == 200
    assert len(data["apps"]) == 1
    assert set(data["apps"].keys()) == {"api"}
