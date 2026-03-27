class PerformancePredictor:
    def predict_ctr(self, variant: dict) -> float:
        # Placeholder model output.
        return round(0.8 * variant.get("score", 0.5), 3)


class BanditOptimizer:
    def suggest_next(self, variants: list[dict]) -> dict:
        # Placeholder for Thompson Sampling or UCB policy.
        return variants[0] if variants else {}


class BrandGuard:
    def validate(self, variant: dict, banned_terms: list[str] | None = None) -> bool:
        # Placeholder for brand-safety policy checks.
        banned_terms = banned_terms or []
        text = f"{variant.get('headline', '')} {variant.get('cta', '')}".lower()
        return not any(term.lower() in text for term in banned_terms)
