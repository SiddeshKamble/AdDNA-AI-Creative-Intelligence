from enum import Enum
from pydantic import BaseModel, Field


class AdProvider(str, Enum):
    AUTO = "auto"
    FOREPLAY = "foreplay"
    PIPISPY = "pipispy"
    BOTH = "both"
    SAMPLE = "sample"


class MarketQuery(BaseModel):
    brand: str = ""
    category: str = ""
    country: str = "US"
    keywords: list[str] = Field(default_factory=list)
    provider: AdProvider = AdProvider.AUTO
    platforms: list[str] = Field(default_factory=lambda: ["facebook", "tiktok"])
    active_only: bool = True
    english_only: bool = True
    language_confidence: float = Field(default=0.72, ge=0.0, le=1.0)
    page_size: int = Field(default=20, ge=1, le=100)
    current_page: int = Field(default=1, ge=1)
    sort: int = 2
    sort_type: str = "desc"
