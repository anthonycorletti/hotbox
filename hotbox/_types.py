from datetime import datetime
from enum import Enum, unique
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, StrictStr


@unique
class Language(str, Enum):
    go = "go"
    # python = "py"


@unique
class Image(str, Enum):
    """Image is the name of the Docker image to use for hotbox."""

    go = "golang:1.20"
    # python = "python:3.11-slim"


class Routes(str, Enum):
    apps = "/apps"


@unique
class Ec2MetalType(str, Enum):
    """Ec2MetalType is the type of EC2 instance to use for hotbox."""

    a1_metal = "a1.metal"
    i3_metal = "i3.metal"
    g4dn_metal = "g4dn.metal"


class HotboxSpec(BaseModel):
    ...


class AwsSpec(HotboxSpec):
    region: str


class Ec2InstanceTag(BaseModel):
    Key: StrictStr
    Value: StrictStr


class Ec2Spec(AwsSpec):
    key_name: str
    security_group_ids: List[str]
    instance_type: Ec2MetalType = Ec2MetalType.a1_metal
    min_count: int = 1
    max_count: int = 1
    monitoring_enabled: Dict[str, Any] = {
        "Enabled": False,
    }
    block_device_mappings: List[Dict[str, Any]] = [
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeSize": 8,
                "VolumeType": "gp2",
            },
        },
    ]
    tag_specifications: List[Dict[str, Any]] = [
        {
            "ResourceType": "instance",
            "Tags": [
                {
                    "Key": "hotboxed",
                    "Value": "yes",
                },
            ],
        },
    ]


class HealthcheckResponse(BaseModel):
    message: StrictStr
    version: StrictStr
    time: datetime


class CreateAppRequest(BaseModel):
    app_name: StrictStr


class GetAppsResponse(BaseModel):
    apps: Dict[str, Dict] = dict()


class DeleteAppsResponse(BaseModel):
    deleted_apps: List[str] = list()


class ContainerSpec(BaseModel):
    image: Union[StrictStr, Image]
    install: Optional[StrictStr]
    entrypoint: Optional[StrictStr]
    build: Optional[StrictStr]


class GoContainerSpec(ContainerSpec):
    image: Image = Image.go
    build: StrictStr = "CGO_ENABLED=0 go build -o /tmp/overlay/usr/local/bin/fcvm-app"
    install: StrictStr = "go get"
    entrypoint: StrictStr = "/usr/local/bin/fcvm-app"


DEFAULT_CONTAINERS: Dict[Image, ContainerSpec] = {Image.go: GoContainerSpec()}
