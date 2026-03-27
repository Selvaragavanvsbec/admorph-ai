from utils.color_utils import infer_contrast_text, parse_brand_colors


class VisualAgent:
    def run(self, variants: list[dict], brand_colors: str) -> list[dict]:
        primary, secondary = parse_brand_colors(brand_colors)
        text_color = infer_contrast_text(primary)

        for variant in variants:
            variant["visual"] = {
                "background": primary,
                "accent": secondary,
                "text_color": text_color,
                "hierarchy": "headline > visual > cta",
                "contrast_ok": True,
            }
        return variants
