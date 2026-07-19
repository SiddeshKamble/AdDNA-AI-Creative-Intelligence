from pydantic import BaseModel, Field

class PatternCluster(BaseModel):
    name: str
    ad_ids: list[str] = Field(default_factory=list)
    shared_hooks: list[str] = Field(default_factory=list)
    shared_formats: list[str] = Field(default_factory=list)
    insight: str = ""
