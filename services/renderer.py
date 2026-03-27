import os
import asyncio
import hashlib
import json
from jinja2 import Environment, FileSystemLoader
from config import settings

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("WARNING: Playwright not installed. PNG export will be unavailable.")

class Renderer:
    _browser = None
    _playwright = None
    _semaphore = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("templates"))
        self.output_dir = settings.output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def _get_semaphore(self):
        if Renderer._semaphore is None:
            # Initialize semaphore inside an async context to ensure it uses the correct event loop
            # On Windows, we need to be conservative with concurrency
            Renderer._semaphore = asyncio.Semaphore(2)
        return Renderer._semaphore

    async def _get_browser(self):
        async with Renderer._lock:
            if not Renderer._playwright:
                print("RENDERER: Starting Playwright...")
                Renderer._playwright = await async_playwright().start()
            if not Renderer._browser:
                print("RENDERER: Launching Chromium...")
                Renderer._browser = await Renderer._playwright.chromium.launch(
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
            return Renderer._browser

    def _generate_cache_key(self, variation: dict):
        # Create a stable hash based on visual properties
        props = {
            "template": variation.get("template"),
            "heading": variation.get("heading"),
            "content": variation.get("content"),
            "catchy_line": variation.get("catchy_line"),
            "theme_name": variation.get("theme", {}).get("name"),
            "ratio": variation.get("ratio"),
            "product_image": variation.get("product_image"),
            "bp": variation.get("brand_primary"),
            "bs": variation.get("brand_secondary"),
            "bt": variation.get("brand_accent")
        }
        return hashlib.md5(json.dumps(props, sort_keys=True).encode()).hexdigest()

    async def render_variation(self, variation: dict):
        """Renders a single variation to PNG using a pooled browser instance."""
        import traceback
        
        # Check Cache First
        cache_key = self._generate_cache_key(variation)
        output_path = os.path.join(self.output_dir, f"cache_{cache_key}.png")
        if os.path.exists(output_path):
            print(f"RENDERER: Cache Hit for {cache_key}")
            return output_path

        sem = await self._get_semaphore()
        async with sem:
            try:
                print(f"RENDERER: Rendering variation {cache_key}...")
                template = self.env.get_template(variation["template"])
                
                # Prepare image path
                product_image = variation.get("product_image")
                if product_image and os.path.exists(product_image):
                    product_image = "file://" + os.path.abspath(product_image).replace("\\", "/")

                html_content = template.render(
                    heading=variation.get("heading", ""),
                    content=variation.get("content", ""),
                    catchy_line=variation.get("catchy_line", ""),
                    cta=variation.get("cta", "SHOP NOW"),
                    theme=variation.get("theme", {}),
                    ratio=variation.get("ratio", {}),
                    product_image=product_image,
                    product_name=variation.get("product_name", "AdMorph"),
                    render_mode="static",
                    brand_primary=variation.get("brand_primary"),
                    brand_secondary=variation.get("brand_secondary"),
                    brand_accent=variation.get("brand_accent")
                )
                
                browser = await self._get_browser()
                context = await browser.new_context(
                    viewport={"width": variation["ratio"]["width"], "height": variation["ratio"]["height"]}
                )
                page = await context.new_page()
                
                try:
                    await page.set_content(html_content, wait_until="networkidle")
                    # Wait for entry animations to settle
                    await asyncio.sleep(1.2) 
                    await page.screenshot(path=output_path)
                finally:
                    await page.close()
                    await context.close()
                
                return output_path
            except Exception as e:
                msg = f"RENDER ERROR: {str(e)}\n{traceback.format_exc()}"
                print(msg)
                # Ensure the log file is updated with this error
                with open("render_error.log", "a") as f:
                    f.write(f"\n==================================================\n{msg}\n")
                raise e

    async def close(self):
        async with Renderer._lock:
            if Renderer._browser:
                await Renderer._browser.close()
                Renderer._browser = None
            if Renderer._playwright:
                await Renderer._playwright.stop()
                Renderer._playwright = None

    async def render_batch(self, variations: list):
        """Renders multiple variations. Semaphore handles parallel load."""
        tasks = [self.render_variation(v) for v in variations]
        return await asyncio.gather(*tasks)
