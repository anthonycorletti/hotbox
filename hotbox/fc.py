from typing import Dict, List

from hotbox.services import HotboxService
from hotbox.types import HotboxFcBridgeSpec, HotboxFcMicrovmSpec, HotboxFcTapSpec


class HotboxFcBridgeService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: HotboxFcBridgeSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


class HotboxFcMicrovmService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: HotboxFcMicrovmSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


class HotboxFcTapService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create(self, spec: HotboxFcTapSpec) -> Dict:
        return {}

    def get(self) -> Dict:
        return {}

    def delete(self, ids: List[str]) -> Dict:
        return {}


hb_fc_bridge_service = HotboxFcBridgeService()
hb_fc_microvm_service = HotboxFcMicrovmService()
hb_fc_tap_service = HotboxFcTapService()
