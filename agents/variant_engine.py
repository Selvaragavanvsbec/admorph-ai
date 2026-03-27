from itertools import product


class VariantEngine:
    def __init__(self) -> None:
        self.layouts = ["center-focus", "split-top", "left-copy", "hero-bottom", "clean-professional"]
        self.visual_themes = ["bold-gradient", "minimal-clean", "high-contrast", "photo-overlay", "kinetic-shapes"]

    def run(self, headlines: list[str], ctas: list[str], max_variants: int = 50) -> list[dict]:
        variants = []
        combos = product(headlines, ctas, self.layouts, self.visual_themes)
        for headline, cta, layout, visual_theme in combos:
            variants.append(
                {
                    "headline": headline,
                    "cta": cta,
                    "layout": layout,
                    "visual_theme": visual_theme,
                }
            )
            if len(variants) >= max_variants:
                break
        return variants
