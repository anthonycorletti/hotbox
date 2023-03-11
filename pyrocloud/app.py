from typing import Dict, List

from pyrocloud.services import PyroService
from pyrocloud.types import PyroAppSpec


class PyroAppService(PyroService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: PyroAppSpec) -> Dict:
        return {}

    def get(self, ids: List[str]) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


pyro_app_service = PyroAppService()
