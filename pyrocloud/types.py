from enum import Enum, unique
from typing import Any, Dict, List

from pydantic import BaseModel


@unique
class PyroKind(str, Enum):
    """PyroKind is a type of api resource that Pyro can manage."""

    ec2 = "ec2"
    fc_microvm = "fc_microvm"
    fc_tap = "fc_tap"
    fc_bridge = "fc_bridge"
    app = "app"


@unique
class PyroVersion(str, Enum):
    """PyroVersion is the version of the Pyro API."""

    v0alpha0 = "v0alpha0"


@unique
class Ec2MetalType(str, Enum):
    """Ec2MetalType is the type of EC2 instance to use for Pyro."""

    a1_metal = "a1.metal"
    i3_metal = "i3.metal"
    g4dn_metal = "g4dn.metal"


class PyroSpec(BaseModel):
    kind: PyroKind
    version: PyroVersion


class PyroAwsSpec(PyroSpec):
    region: str


class PyroEc2Spec(PyroAwsSpec):
    image_id: str
    key_name: str
    security_group_ids: List[str]
    instance_type: Ec2MetalType = Ec2MetalType.a1_metal
    min_count: int = 1
    max_count: int = 1
    monitoring_enabled: Dict[str, Any] = {"Enabled": False}
    block_device_mappings: List[Dict[str, Any]] = [
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {"DeleteOnTermination": True, "VolumeSize": 8, "VolumeType": "gp2"},
        },
    ]


class PyroFcMicrovmSpec(PyroSpec):
    ...


class PyroFcTapSpec(PyroSpec):
    ...


class PyroFcBridgeSpec(PyroSpec):
    ...


class PyroAppSpec(PyroSpec):
    ...
