from typing import Dict, Type

from pyrocloud.app import pyro_app_service
from pyrocloud.ec2 import pyro_ec2_service
from pyrocloud.fc import (
    pyro_fc_bridge_service,
    pyro_fc_microvm_service,
    pyro_fc_tap_service,
)
from pyrocloud.types import (
    PyroAppSpec,
    PyroEc2Spec,
    PyroFcBridgeSpec,
    PyroFcMicrovmSpec,
    PyroFcTapSpec,
    PyroKind,
    PyroSpec,
    PyroVersion,
)

NAME = "pyrocloud"
DESC = "🔥 Run your apps on Firecracker MicroVMs in the cloud ☁️"

TYPE_MAP: Dict[PyroKind, Type[PyroSpec]] = {
    PyroKind.ec2: PyroEc2Spec,
    PyroKind.fc_microvm: PyroFcMicrovmSpec,
    PyroKind.fc_tap: PyroFcTapSpec,
    PyroKind.fc_bridge: PyroFcBridgeSpec,
    PyroKind.app: PyroAppSpec,
}

SERVICE_MAP = {
    PyroKind.ec2: pyro_ec2_service,
    PyroKind.fc_microvm: pyro_fc_microvm_service,
    PyroKind.fc_tap: pyro_fc_tap_service,
    PyroKind.fc_bridge: pyro_fc_bridge_service,
    PyroKind.app: pyro_app_service,
}

DEFAULTS = {
    PyroVersion: PyroVersion.v0alpha0,
}
