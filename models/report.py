from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from models.advertisement import Advertisement
from models.creative import CreativeFeatures


class EvidenceItem(BaseModel):
    label: str
    count: int
    percentage: int
    ad_ids: list[str] = Field(default_factory=list)


class MarketReport(BaseModel):
    query: dict[str, Any]
    generated_at: str
    collected_count: int
    unique_count: int
    duplicate_count: int
    duplicate_rate: int
    provider_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    active_count: int = 0
    video_count: int = 0
    total_views: int = 0
    data_quality_notes: list[str] = Field(default_factory=list)
    executive_summary: str
    metric_insights: dict[str, str] = Field(default_factory=dict)
    intelligence: dict[str, Any] = Field(default_factory=dict)
    winning_patterns: list[EvidenceItem] = Field(default_factory=list)
    opportunity_gaps: list[str] = Field(default_factory=list)
    top_hooks: list[EvidenceItem] = Field(default_factory=list)
    messaging_breakdown: dict[str, int] = Field(default_factory=dict)
    creative_dna: dict[str, str] = Field(default_factory=dict)
    market_scorecard: dict[str, int] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    creative_brief: dict[str, Any] = Field(default_factory=dict)
    script: list[dict[str, str]] = Field(default_factory=list)
    shot_list: list[dict[str, str]] = Field(default_factory=list)
    ads: list[Advertisement] = Field(default_factory=list)
    features: list[CreativeFeatures] = Field(default_factory=list)
