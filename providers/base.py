from abc import ABC, abstractmethod
from typing import Any
from models.market import MarketQuery

class ProviderConfigurationError(RuntimeError):
    pass

class ProviderAPIError(RuntimeError):
    pass

class AdProviderClient(ABC):
    name: str

    @property
    @abstractmethod
    def configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: MarketQuery) -> list[dict[str, Any]]:
        raise NotImplementedError
