import asyncio
import contextlib
import os
import shutil
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
    app_names = ["api", "ui"]
    for app_name in app_names:
        with open(f"fc-{app_name}-config.json", "w") as f:
            f.write(
                """{ "network-interfaces":
                [{ "iface_id": "eth0", "host_dev_name": "test" }] }"""
            )
        with open(f"{app_name}.tar.gz", "w") as f:
            f.write("test")
        with open(f"{app_name}_fs", "w") as f:
            f.write("test")
        with open(f"{app_name}_run_app.sh", "w") as f:
            f.write("test")
        os.makedirs(f"{app_name}_code", exist_ok=True)
        with open(f"{app_name}_code/test.go", "w") as f:
            f.write("test")
        os.makedirs(f"{app_name}_image", exist_ok=True)
        with open(f"{app_name}_image/Dockerfile", "w") as f:
            f.write("test")
    yield
    for app_name in app_names:
        with contextlib.suppress(FileNotFoundError):
            os.remove(f"fc-{app_name}-config.json")
            os.remove(f"{app_name}.tar.gz")
            os.remove(f"{app_name}_fs")
            os.remove(f"{app_name}_run_app.sh")
        shutil.rmtree(f"{app_name}_code", ignore_errors=True)
        shutil.rmtree(f"{app_name}_image", ignore_errors=True)
