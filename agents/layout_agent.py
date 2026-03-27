from utils.platform import get_platform_constraints


class LayoutAgent:
    def run(self, variants: list[dict], platform: str) -> list[dict]:
        constraints = get_platform_constraints(platform)
        ratio = constraints["ratio"]
        safe_zone = constraints["safe_zone"]
        recommended_layouts = set(constraints["recommended_layouts"])

        for variant in variants:
            variant["aspect_ratio"] = ratio
            variant["safe_zone"] = safe_zone
            variant["cta_visibility"] = "high"
            variant["overlap_risk"] = "low"
            if variant["layout"] not in recommended_layouts:
                variant["layout"] = next(iter(recommended_layouts))
        return variants
