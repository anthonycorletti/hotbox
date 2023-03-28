from typing import Dict, List

from hotbox.services import HotboxService
from hotbox.types import AppSpec


class AppService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: AppSpec) -> Dict:
        return {}

    def get(self, ids: List[str]) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


app_svc = AppService()
