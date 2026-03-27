from typing import List, Optional
from pydantic import BaseModel, Field

class AdGenState(BaseModel):
    """State management for the AdMorph generation pipeline."""
    # User Interaction
    questions: List[str] = Field(default_factory=list)
    answers: List[str] = Field(default_factory=list)
    cached_followups: List[str] = Field(default_factory=list)
    interaction_complete: bool = False
    
    # Ad Brief Details
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    target_audience: Optional[str] = None
    advertising_goal: Optional[str] = None
    brand_tone: Optional[str] = None
    
    # Advanced Strategic Context for MNC-Level Copy
    funnel_stage: Optional[str] = None
    pain_points: Optional[str] = None
    usp: Optional[str] = None
    offer: Optional[str] = None
    brand_guidelines: Optional[str] = None

    image_descriptions: List[str] = Field(default_factory=list)
    user_image_url: Optional[str] = None
    processed_image_path: Optional[str] = None
    processed_image_assets: List[dict] = Field(default_factory=list) # List of {"path": str, "ratio": float, "width": int, "height": int}
    
    # Generation Results
    copy_objects: List[dict] = Field(default_factory=list) # {"heading": str, "content": str, "catchy_line": str}
    ctas: List[str] = Field(default_factory=list)
    themes: List[dict] = Field(default_factory=list)
    variations: List[dict] = Field(default_factory=list)
    
    # Metadata
    current_step: str = "interaction"
    error: Optional[str] = None
