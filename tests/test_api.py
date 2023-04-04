import os

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
