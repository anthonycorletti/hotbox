from typing import Dict, Type

from hotbox.app import hb_app_service
from hotbox.ec2 import hb_ec2_service
from hotbox.fc import hb_fc_bridge_service, hb_fc_microvm_service, hb_fc_tap_service
from hotbox.types import (
    HotboxAppSpec,
    HotboxEc2Spec,
    HotboxFcBridgeSpec,
    HotboxFcMicrovmSpec,
    HotboxFcTapSpec,
    HotboxKind,
    HotboxSpec,
    HotboxVersion,
)

NAME = "hotbox"
DESC = "🔥 Run your apps on Firecracker MicroVMs in the cloud ☁️"

TYPE_MAP: Dict[HotboxKind, Type[HotboxSpec]] = {
    HotboxKind.ec2: HotboxEc2Spec,
    HotboxKind.fc_microvm: HotboxFcMicrovmSpec,
    HotboxKind.fc_tap: HotboxFcTapSpec,
    HotboxKind.fc_bridge: HotboxFcBridgeSpec,
    HotboxKind.app: HotboxAppSpec,
}

SERVICE_MAP = {
    HotboxKind.ec2: hb_ec2_service,
    HotboxKind.fc_microvm: hb_fc_microvm_service,
    HotboxKind.fc_tap: hb_fc_tap_service,
    HotboxKind.fc_bridge: hb_fc_bridge_service,
    HotboxKind.app: hb_app_service,
}

DEFAULTS = {
    HotboxVersion: HotboxVersion.v0alpha0,
}
