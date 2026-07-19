from typing import Any
from core.settings import settings
from models.market import MarketQuery
from providers.foreplay.client import ForeplayClient

class ForeplayDiscovery:
    name = "foreplay"

    def __init__(self) -> None:
        self.client = ForeplayClient()

    @property
    def configured(self) -> bool:
        return self.client.configured

    def search(self, query: MarketQuery) -> list[dict[str, Any]]:
        terms = " ".join(
            value for value in [query.brand, query.category, *query.keywords] if value
        )
        params: dict[str, Any] = {
            "query": terms,
            "limit": query.page_size,
            "live": str(query.active_only).lower(),
        }
        if query.platforms:
            params["publisher_platform"] = query.platforms[0]

        payload = self.client.get(settings.foreplay_discovery_path, params)
        return self._extract_rows(payload)

    @staticmethod
    def _extract_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
        for key in ("data", "ads", "results", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                for nested in ("data", "ads", "results", "items"):
                    rows = value.get(nested)
                    if isinstance(rows, list):
                        return rows
        return []
