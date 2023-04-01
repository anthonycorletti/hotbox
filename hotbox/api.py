import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from hotbox import __version__
from hotbox.const import API_V0, DESC, NAME
from hotbox.types import CreateAppRequest, HealthcheckResponse

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


@health_router.get("/health", response_model=HealthcheckResponse)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(
        message="ok",
        version=__version__,
        time=datetime.utcnow(),
    )


@app_router.post("/apps", response_class=JSONResponse)
async def create_app(
    background_tasks: BackgroundTasks,
    create_app_request: CreateAppRequest = Form(...),
    upload_file: UploadFile = File(...),
) -> JSONResponse:
    pass
