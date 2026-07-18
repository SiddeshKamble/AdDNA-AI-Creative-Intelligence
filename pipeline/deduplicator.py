from __future__ import annotations

from typing import Optional
import hashlib
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.parse import urlparse

from models.advertisement import Advertisement


@dataclass
class DeduplicationResult:
    unique_ads: list[Advertisement]
    duplicate_count: int
    groups: dict[str, list[str]]


class CreativeDeduplicator:
    """Content-aware deduplication that keeps the richest record in each group."""

    @staticmethod
    def _normalize(value: Optional[str]) -> str:
        if not value:
            return ""
        value = value.lower()
        value = re.sub(r"https?://\S+", " ", value)
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _domain(value: Optional[str]) -> str:
        if not value:
            return ""
        try:
            return urlparse(value).netloc.lower().removeprefix("www.")
        except ValueError:
            return ""

    def _fingerprint(self, ad: Advertisement) -> str:
        media = ad.video_url or ad.image_url or ad.thumbnail_url or ""
        if media:
            return "media:" + hashlib.sha256(media.encode()).hexdigest()
        payload = "|".join(
            [
                self._normalize(ad.title),
                self._normalize(ad.ad_copy),
                self._domain(ad.landing_page_url or ad.source_url),
            ]
        )
        return "text:" + hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def _richness(ad: Advertisement) -> int:
        fields = [
            ad.transcript,
            ad.hook,
            ad.cta_text,
            ad.thumbnail_url,
            ad.video_url,
            ad.image_url,
            ad.play_count,
            ad.impressions,
            ad.likes,
            ad.comments,
            ad.shares,
        ]
        return sum(value not in (None, "", [], {}) for value in fields)

    def _is_near_duplicate(self, left: Advertisement, right: Advertisement) -> bool:
        left_copy = self._normalize(left.ad_copy)
        right_copy = self._normalize(right.ad_copy)
        left_title = self._normalize(left.title)
        right_title = self._normalize(right.title)
        if left_copy and right_copy:
            copy_ratio = SequenceMatcher(None, left_copy, right_copy).ratio()
            title_ratio = SequenceMatcher(None, left_title, right_title).ratio() if left_title and right_title else 0
            same_domain = self._domain(left.landing_page_url or left.source_url) == self._domain(
                right.landing_page_url or right.source_url
            )
            return copy_ratio >= 0.94 or (copy_ratio >= 0.88 and title_ratio >= 0.85) or (same_domain and copy_ratio >= 0.90)
        return False

    def deduplicate(self, ads: list[Advertisement]) -> DeduplicationResult:
        unique: list[Advertisement] = []
        groups: dict[str, list[str]] = {}

        for ad in ads:
            exact_key = self._fingerprint(ad)
            matched_index = None
            matched_key = exact_key
            for index, existing in enumerate(unique):
                if self._fingerprint(existing) == exact_key or self._is_near_duplicate(existing, ad):
                    matched_index = index
                    matched_key = self._fingerprint(existing)
                    break

            if matched_index is None:
                unique.append(ad)
                groups.setdefault(exact_key, []).append(ad.source_id)
                continue

            groups.setdefault(matched_key, []).append(ad.source_id)
            if self._richness(ad) > self._richness(unique[matched_index]):
                unique[matched_index] = ad

        return DeduplicationResult(
            unique_ads=unique,
            duplicate_count=max(0, len(ads) - len(unique)),
            groups=groups,
        )
