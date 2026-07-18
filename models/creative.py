from pydantic import BaseModel, Field


class CreativeFeatures(BaseModel):
    ad_id: str
    provider: str
    detected_brand: str
    platforms: list[str] = Field(default_factory=list)
    hook: str = ""
    cta: str = ""
    pain_points: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    proof_points: list[str] = Field(default_factory=list)
    audience: list[str] = Field(default_factory=list)
    positioning: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    creative_format: str = "Unknown"
    opening_style: str = "Unknown"
    visual_style: str = "Unknown"
    tone: str = "Unknown"
    product_first: bool = False
    founder_led: bool = False
    comparison_hook: bool = False
    humor: bool = False
    fast_edits: bool = False
    confidence: float = 0.5
