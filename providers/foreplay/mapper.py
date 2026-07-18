import hashlib
from typing import Any, Optional

from models.advertisement import Advertisement
from models.market import MarketQuery


def _int(value: Any) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, dict):
        for key, divisor in (("days", 1), ("hours", 24), ("minutes", 1440), ("seconds", 86400)):
            if isinstance(value.get(key), (int, float)):
                return int(value[key] / divisor)
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    return str(value).strip().lower() in {"true", "1", "yes", "active", "live"}


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if x not in (None, "")]
    if isinstance(value, str):
        return [value.strip().lower()] if value.strip() else []
    return [str(value).strip().lower()]


def map_foreplay_ad(row: dict[str, Any], query: MarketQuery) -> Advertisement:
    def pick(*keys: str):
        for key in keys:
            value = row.get(key)
            if value not in (None, ""):
                return value
        return None

    source_id = pick("id", "_id", "ad_id", "creative_id")
    if source_id is None:
        source_id = hashlib.sha256(str(row).encode()).hexdigest()[:20]

    # Search terms are not treated as detected advertiser identity.
    detected_brand = pick("brand_name", "brand", "advertiser_name", "page_name") or "Unknown"
    platforms = _list(pick("publisher_platform", "publisher_platforms", "platform", "platforms"))

    return Advertisement(
        source_id=str(source_id),
        provider="foreplay",
        brand=str(detected_brand),
        searched_brand=query.brand or None,
        category=str(pick("category", "industry") or query.category or "Unknown"),
        title=pick("headline", "title", "name"),
        ad_copy=pick("body", "description", "primary_text", "copy"),
        source_url=pick("ad_url", "url", "original_url"),
        landing_page_url=pick("landing_page_url", "link_url", "destination_url"),
        video_url=pick("video_url", "media_url", "asset_url"),
        image_url=pick("image_url", "image"),
        thumbnail_url=pick("thumbnail_url", "cover_url", "thumbnail"),
        platforms=platforms,
        transcript=pick("transcription", "transcript"),
        hook=pick("hook", "main_hook"),
        tags=_list(pick("tags", "creative_tags")),
        cta_text=pick("cta", "call_to_action", "cta_text"),
        language=pick("language", "ad_language"),
        is_active=_bool(pick("live", "is_active", "active")),
        days_active=_int(pick("days_active", "running_duration")),
        duration_seconds=_int(pick("duration", "duration_seconds")),
        impressions=_int(pick("impressions", "estimated_impressions")),
        play_count=_int(pick("play_count", "views", "video_views")),
        likes=_int(pick("likes", "like_count")),
        shares=_int(pick("shares", "share_count")),
        comments=_int(pick("comments", "comment_count")),
        raw_provider_data=row,
    )
