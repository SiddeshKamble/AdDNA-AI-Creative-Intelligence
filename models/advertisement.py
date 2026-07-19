from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

class Advertisement(BaseModel):
    source_id: str
    provider: str
    brand: str = "Unknown"
    searched_brand: Optional[str] = None
    category: str = "Unknown"
    title: Optional[str] = None
    ad_copy: Optional[str] = None
    source_url: Optional[str] = None
    landing_page_url: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    platforms: list[str] = Field(default_factory=list)
    transcript: Optional[str] = None
    hook: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    cta_text: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    days_active: Optional[int] = None
    duration_seconds: Optional[int] = None
    play_count: Optional[int] = None
    impressions: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    raw_provider_data: dict[str, Any] = Field(default_factory=dict)

    @property
    def primary_platform(self) -> str:
        return self.platforms[0] if self.platforms else "unknown"

    @property
    def creative_text(self) -> str:
        return "\n".join(
            part.strip()
            for part in [self.title, self.hook, self.ad_copy, self.transcript]
            if part and part.strip()
        )
