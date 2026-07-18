from models.advertisement import Advertisement
from models.market import AdProvider, MarketQuery
from providers.base import ProviderAPIError, ProviderConfigurationError
from providers.foreplay.discovery import ForeplayDiscovery
from providers.foreplay.mapper import map_foreplay_ad
from providers.pipispy.adspy import PiPiSpyAdspy
from providers.pipispy.mapper import map_pipispy_ad


class AdCollector:
    def __init__(self) -> None:
        self.foreplay = ForeplayDiscovery()
        self.pipispy = PiPiSpyAdspy()

    def collect(self, query: MarketQuery, deduplicate: bool = True) -> list[Advertisement]:
        requested = self._resolve(query.provider)
        ads: list[Advertisement] = []

        for provider_name in requested:
            try:
                if provider_name == "foreplay":
                    ads.extend(
                        map_foreplay_ad(row, query)
                        for row in self.foreplay.search(query)
                    )
                elif provider_name == "pipispy":
                    ads.extend(
                        map_pipispy_ad(row, query)
                        for row in self.pipispy.search(query)
                    )
            except (ProviderAPIError, ProviderConfigurationError):
                continue

        if not ads:
            ads = self._sample_ads(query)
        if deduplicate:
            return self._deduplicate(ads)[: query.page_size]
        return ads

    def _resolve(self, provider: AdProvider) -> list[str]:
        if provider == AdProvider.FOREPLAY:
            return ["foreplay"]
        if provider == AdProvider.PIPISPY:
            return ["pipispy"]
        if provider == AdProvider.BOTH:
            return ["foreplay", "pipispy"]
        if provider == AdProvider.SAMPLE:
            return []
        resolved = []
        if self.foreplay.configured:
            resolved.append("foreplay")
        if self.pipispy.configured:
            resolved.append("pipispy")
        return resolved

    @staticmethod
    def _deduplicate(ads: list[Advertisement]) -> list[Advertisement]:
        unique: dict[str, Advertisement] = {}
        for ad in ads:
            identity = ad.video_url or ad.source_url or f"{ad.provider}:{ad.source_id}"
            unique.setdefault(identity, ad)
        return list(unique.values())

    @staticmethod
    def _sample_ads(query: MarketQuery) -> list[Advertisement]:
        return [
            Advertisement(
                source_id=f"sample-{i + 1}",
                provider="sample",
                brand=query.brand or "Sample Brand",
                category=query.category or "Sample Category",
                title=f"Sample creative {i + 1}",
                platforms=[query.platforms[i % len(query.platforms)]] if query.platforms else ["sample"],
                hook="Problem-solution hook",
                transcript="Sample transcript used until an API key is configured.",
                play_count=10000 - i * 100,
            )
            for i in range(query.page_size)
        ]
