import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import AsyncClient
from typer.testing import CliRunner

from hotbox.api import api

TEST_BASE_URL = "http://testserver:8001"


@pytest.fixture(scope="function")
def runner() -> Generator:
    runner = CliRunner(mix_stderr=False)
    yield runner


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=api,
        base_url=TEST_BASE_URL,
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def event_loop(request: Request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def create_test_fc_config_files() -> AsyncGenerator:
    with open("fc-ui-config.json", "w") as f:
        f.write("{}")
    with open("fc-api-config.json", "w") as f:
        f.write("{}")
    yield
    os.remove("fc-ui-config.json")
    os.remove("fc-api-config.json")
