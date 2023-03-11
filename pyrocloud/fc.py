from typing import Dict, List

from pyrocloud.services import PyroService
from pyrocloud.types import PyroFcBridgeSpec, PyroFcMicrovmSpec, PyroFcTapSpec


class PyroFcBridgeService(PyroService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: PyroFcBridgeSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


class PyroFcMicrovmService(PyroService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: PyroFcMicrovmSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


class PyroFcTapService(PyroService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: PyroFcTapSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


pyro_fc_bridge_service = PyroFcBridgeService()
pyro_fc_microvm_service = PyroFcMicrovmService()
pyro_fc_tap_service = PyroFcTapService()
