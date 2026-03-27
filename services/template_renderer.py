import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont

from config import settings
from utils.platform import normalize_platform


class TemplateRenderer:
    def __init__(self) -> None:
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_env = Environment(loader=FileSystemLoader("templates"))

    def _template_name(self, platform: str) -> str:
        platform = normalize_platform(platform)
        if platform in {"instagram", "facebook", "linkedin"}:
            return f"{platform}.html"
        return "instagram.html"

    def _render_html(self, variant: dict, platform: str, filename_stem: str) -> Path:
        template = self.template_env.get_template(self._template_name(platform))
        html = template.render(variant=variant)
        html_path = self.output_dir / f"{filename_stem}.html"
        html_path.write_text(html, encoding="utf-8")
        return html_path

    def _render_png_playwright(self, html_path: Path, png_path: Path, width: int, height: int) -> bool:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(html_path.resolve().as_uri())
                page.screenshot(path=str(png_path), full_page=True)
                browser.close()
            return True
        except Exception:
            return False

    def _render_png_fallback(self, variant: dict, png_path: Path, width: int, height: int) -> None:
        image = Image.new("RGB", (width, height), variant["visual"]["background"])
        draw = ImageDraw.Draw(image)
        headline_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()

        draw.text((40, 40), variant["headline"], fill=variant["visual"]["text_color"], font=headline_font)
        draw.rectangle([(40, height - 90), (280, height - 30)], fill=variant["visual"]["accent"])
        draw.text((50, height - 75), variant["cta"], fill="#111111", font=cta_font)
        image.save(png_path)

    def render(self, variants: list[dict], platform: str) -> list[dict]:
        dimensions = {
            "instagram": (1080, 1080),
            "facebook": (1080, 1350),
            "linkedin": (1200, 628),
            "youtube": (1280, 720),
        }
        width, height = dimensions.get(normalize_platform(platform), (1080, 1080))

        for idx, variant in enumerate(variants, start=1):
            stem = f"ad_{normalize_platform(platform)}_{idx}"
            html_path = self._render_html(variant, platform, stem)
            png_path = self.output_dir / f"{stem}.png"

            ok = self._render_png_playwright(html_path, png_path, width, height)
            if not ok:
                self._render_png_fallback(variant, png_path, width, height)

            variant["html_path"] = str(html_path)
            variant["image_path"] = str(png_path)
            variant["image_url"] = f"{settings.api_base_url}/generated/{os.path.basename(png_path)}"
        return variants
