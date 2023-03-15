from enum import Enum, unique
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


@unique
class HotboxKind(str, Enum):
    """HotboxKind is a type of api resource that Hotbox can manage."""

    ec2 = "ec2"
    fc_microvm = "fc_microvm"
    fc_tap = "fc_tap"
    fc_bridge = "fc_bridge"
    app = "app"


@unique
class HotboxVersion(str, Enum):
    """HotboxVersion is the version of the Hotbox API."""

    v0alpha0 = "v0alpha0"


@unique
class Ec2MetalType(str, Enum):
    """Ec2MetalType is the type of EC2 instance to use for Hotbox."""

    a1_metal = "a1.metal"
    i3_metal = "i3.metal"
    g4dn_metal = "g4dn.metal"


class HotboxSpec(BaseModel):
    kind: HotboxKind
    version: HotboxVersion


class HotboxAwsSpec(HotboxSpec):
    region: str


class HotboxEc2Spec(HotboxAwsSpec):
    image_id: Optional[str] = None
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


class HotboxFcMicrovmSpec(HotboxSpec):
    ...


class HotboxFcTapSpec(HotboxSpec):
    ...


class HotboxFcBridgeSpec(HotboxSpec):
    ...


class HotboxAppSpec(HotboxSpec):
    ...
