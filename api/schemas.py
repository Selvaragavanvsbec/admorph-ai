from datetime import datetime

from pydantic import BaseModel, Field


class GenerateAdsRequest(BaseModel):
    product: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    audience: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    platform: str = Field(..., min_length=1)
    brand_colors: str = Field(default="#0F172A,#F8FAFC")
    tone: str = Field(..., min_length=1)


class AdVariantResponse(BaseModel):
    headline: str
    cta: str
    layout: str
    visual_theme: str
    score: float
    image_url: str
    predicted_ctr: float


class GenerateAdsResponse(BaseModel):
    campaign_id: int
    strategy: dict
    best_variant: dict
    variants: list[AdVariantResponse]


class EditVariantRequest(BaseModel):
    variant: dict
    command: str


class CampaignResponse(BaseModel):
    id: int
    product: str
    audience: str
    goal: str
    platform: str
    created_at: datetime

    class Config:
        from_attributes = True
