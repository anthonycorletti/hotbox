import os
import sys

from pydantic import BaseSettings, Field


class _Env(BaseSettings):
    HOTBOX_API_URL: str = Field(
        "http://localhost:8420/api/v0",
        env="HOTBOX_API_URL",
        description="hotbox API URL",
    )

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


if os.getenv("_", "").endswith("pytest") or "pytest" in "".join(sys.argv):
    _Env.Config.env_file = ".env.test"  # type: ignore

env = _Env()

# if the ENV_FILE environment variable is set, use it as an override
# this is useful for running alembic migrations against remote databases
if os.getenv("ENV_FILE") is not None:
    env = _Env(_env_file=os.environ["ENV_FILE"])  # pragma: no cover
