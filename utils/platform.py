PLATFORM_CONSTRAINTS = {
    "instagram": {"ratio": "1:1", "safe_zone": "8%", "recommended_layouts": ["center-focus", "split-top"]},
    "youtube": {"ratio": "16:9", "safe_zone": "10%", "recommended_layouts": ["left-copy", "hero-bottom"]},
    "linkedin": {"ratio": "1.91:1", "safe_zone": "9%", "recommended_layouts": ["clean-professional", "left-copy"]},
    "facebook": {"ratio": "4:5", "safe_zone": "8%", "recommended_layouts": ["center-focus", "split-top"]},
}


def normalize_platform(platform: str) -> str:
    return (platform or "instagram").strip().lower()


def get_platform_constraints(platform: str) -> dict:
    normalized = normalize_platform(platform)
    return PLATFORM_CONSTRAINTS.get(normalized, PLATFORM_CONSTRAINTS["instagram"])
