from typing import Dict, List

from hotbox.services import HotboxService
from hotbox.types import HotboxAppSpec


class HotboxAppService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: HotboxAppSpec) -> Dict:
        return {}

    def get(self, ids: List[str]) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


hb_app_service = HotboxAppService()
