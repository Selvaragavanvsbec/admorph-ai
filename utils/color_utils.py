def parse_brand_colors(brand_colors: str) -> tuple[str, str]:
    if not brand_colors:
        return "#0F172A", "#F8FAFC"
    parts = [p.strip() for p in brand_colors.split(",") if p.strip()]
    primary = parts[0] if parts else "#0F172A"
    secondary = parts[1] if len(parts) > 1 else "#F8FAFC"
    return primary, secondary


def infer_contrast_text(bg: str) -> str:
    bg = bg.lstrip("#")
    if len(bg) != 6:
        return "#FFFFFF"
    r, g, b = int(bg[:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0B0B0B" if luminance > 0.6 else "#FFFFFF"
