import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, FastAPI, File, Form, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import Json

from hotbox import __version__
from hotbox.app import app_svc
from hotbox.const import API_V0, DESC, NAME
from hotbox.types import (
    CreateAppRequest,
    DeleteAppsResponse,
    GetAppsResponse,
    HealthcheckResponse,
)

os.environ["TZ"] = "UTC"

api = FastAPI(
    title=NAME,
    desc=DESC,
    version=__version__,
)

health_router = APIRouter(
    prefix=API_V0,
    tags=["health"],
)

app_router = APIRouter(
    prefix=API_V0,
    tags=["app"],
)


@health_router.get(
    "/healthcheck",
    response_model=HealthcheckResponse,
)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(
        message="ok",
        version=__version__,
        time=datetime.utcnow(),
    )


@app_router.post(
    "/apps",
    response_class=JSONResponse,
)
async def create_app(
    background_tasks: BackgroundTasks,
    create_app_request: Json = Form(...),
    upload_file: UploadFile = File(...),
) -> JSONResponse:
    _create_app_request = CreateAppRequest(**create_app_request)
    bundle_path = f"{_create_app_request.app_name}.tar.gz"
    with open(bundle_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    background_tasks.add_task(
        app_svc.unzip_and_run,
        bundle_path,
        _create_app_request.app_name,
    )
    return JSONResponse(
        status_code=200,
        content={"message": "App running in the cloud!"},
    )


@app_router.get(
    "/apps",
    response_model=GetAppsResponse,
)
async def get_apps(name: Optional[str] = None) -> GetAppsResponse:
    return app_svc.get_apps(name=name)


@app_router.delete(
    "/apps",
    response_model=DeleteAppsResponse,
)
async def delete_apps(
    bgt: BackgroundTasks, app_names: List[str] = Query(None)
) -> DeleteAppsResponse:
    bgt.add_task(app_svc.delete, app_names=app_names)
    return DeleteAppsResponse(deleted_apps=app_names)


api.include_router(health_router)
api.include_router(app_router)
