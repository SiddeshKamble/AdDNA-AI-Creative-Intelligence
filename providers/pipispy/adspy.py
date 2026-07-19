from typing import Any
from core.settings import settings
from models.market import MarketQuery
from providers.pipispy.client import PiPiSpyClient


PLATFORM_MAP = {
    "facebook": 2,
    "instagram": 2,
    "tiktok": 1,
}

class PiPiSpyAdspy:
    name = "pipispy"

    def __init__(self) -> None:
        self.client = PiPiSpyClient()

    @property
    def configured(self) -> bool:
        return self.client.configured

    def search(self, query: MarketQuery) -> list[dict[str, Any]]:
        keywords = [
            {"type": 1, "keyword": term}
            for term in [query.brand, query.category, *query.keywords]
            if term
        ]

        params: dict[str, Any] = {
            "current_page": query.current_page,
            "page_size": query.page_size,
            "sort": query.sort,
            "sort_type": query.sort_type,
            "region": [query.country],
            "formate_type": [1],
            "is_participle": False,
        }

        if keywords:
            params["extend_keywords"] = keywords
            params["search_type"] = 1

        if query.platforms:
            selected = query.platforms[0].lower()
            if selected in PLATFORM_MAP:
                params["plat_type"] = PLATFORM_MAP[selected]

        if query.active_only:
            params["ad_state"] = 1

        body = self.client.post_operation(
            uri=settings.pipispy_adspy_uri,
            params=params,
        )
        data = body.get("data", {})
        return data.get("data", []) if isinstance(data, dict) else []
