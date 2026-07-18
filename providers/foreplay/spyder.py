from typing import Any
from core.settings import settings
from models.market import MarketQuery
from providers.foreplay.client import ForeplayClient


class ForeplaySpyder:
    def __init__(self) -> None:
        self.client = ForeplayClient()

    def search_brand_ads(self, query: MarketQuery) -> list[dict[str, Any]]:
        payload = self.client.get(
            settings.foreplay_spyder_path,
            {"brand": query.brand, "limit": query.page_size},
        )
        data = payload.get("data", payload)
        if isinstance(data, dict):
            for key in ("ads", "data", "results"):
                if isinstance(data.get(key), list):
                    return data[key]
        return data if isinstance(data, list) else []
