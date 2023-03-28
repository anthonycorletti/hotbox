from enum import Enum, unique
from typing import Any, Dict, List

from pydantic import BaseModel


@unique
class Ec2MetalType(str, Enum):
    """Ec2MetalType is the type of EC2 instance to use for Hotbox."""

    a1_metal = "a1.metal"
    i3_metal = "i3.metal"
    g4dn_metal = "g4dn.metal"


class HotboxSpec(BaseModel):
    ...


class AwsSpec(HotboxSpec):
    region: str


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


class AppSpec(HotboxSpec):
    ...
