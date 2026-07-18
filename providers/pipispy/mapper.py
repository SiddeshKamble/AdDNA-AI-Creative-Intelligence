from typing import Any, Optional

from models.advertisement import Advertisement
from models.market import MarketQuery

PIPISPY_PLATFORM_MAP = {1: "facebook", 2: "instagram", 3: "tiktok"}


def _int(value: Any) -> Optional[int]:
    try:
        return int(float(value)) if value is not None else None
    except (TypeError, ValueError):
        return None


def map_pipispy_ad(row: dict[str, Any], query: MarketQuery) -> Advertisement:
    source_id = str(row.get("video_id") or row.get("id") or row.get("ad_id") or "unknown")
    carousel = row.get("carousel") or []
    first_carousel = carousel[0] if carousel and isinstance(carousel[0], dict) else {}
    platform = PIPISPY_PLATFORM_MAP.get(row.get("platform"), "unknown")
    return Advertisement(
        source_id=source_id,
        provider="pipispy",
        brand=row.get("app_name") or "Unknown",
        searched_brand=query.brand or None,
        category=query.category or "Unknown",
        title=row.get("app_title") or first_carousel.get("title"),
        ad_copy=row.get("desc") or first_carousel.get("body"),
        source_url=row.get("pack_url"),
        landing_page_url=first_carousel.get("link_url") or row.get("pack_url"),
        video_url=row.get("video_url") or first_carousel.get("video_url"),
        image_url=row.get("image") or first_carousel.get("image"),
        thumbnail_url=row.get("cover") or first_carousel.get("cover"),
        platforms=[platform],
        transcript=row.get("ai_analysis_script"),
        hook=row.get("ai_analysis_main_hook"),
        tags=row.get("ai_analysis_tags") or [],
        cta_text=row.get("button_text") or first_carousel.get("cta_text"),
        language=row.get("ai_analysis_language"),
        days_active=_int(row.get("put_days")),
        duration_seconds=_int(row.get("duration") or first_carousel.get("duration")),
        play_count=_int(row.get("play_count")),
        likes=_int(row.get("digg_count")),
        shares=_int(row.get("share_count")),
        comments=_int(row.get("comment_count")),
        raw_provider_data=row,
    )
