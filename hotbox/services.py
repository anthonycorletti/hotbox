from abc import ABC, abstractmethod
from typing import Any


class HotboxService(ABC):
    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Must implement create().")

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Must implement get().")

    @abstractmethod
    def delete(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Must implement delete().")
