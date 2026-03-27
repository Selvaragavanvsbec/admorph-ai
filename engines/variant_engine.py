import itertools
from agents.state import AdGenState

class VariantGenerator:
    def __init__(self):
        # 5 standard ad ratios/dimensions
        self.ratios = [
            {"name": "Square (1:1)", "width": 1080, "height": 1080},
            {"name": "Story/Vertical (9:16)", "width": 1080, "height": 1920},
            {"name": "Landscape (16:9)", "width": 1920, "height": 1080},
            {"name": "Portrait (4:5)", "width": 1080, "height": 1350},
            {"name": "Banner (2:1)", "width": 1000, "height": 500},
            {"name": "Social Vertical (2:3)", "width": 1080, "height": 1620},
            {"name": "Link Preview (1.91:1)", "width": 1200, "height": 628}
        ]

    async def run(self, state: AdGenState) -> dict:
        """
        Generates 21,000 unique variations (100 Headlines x 30 Themes x 7 Ratios).
        """
        copy_objs = state.copy_objects[:100]
        # Ensure we have 100 headlines (fallback if less)
        if len(copy_objs) < 100:
            copy_objs += [{
                "heading": f"Premium quality for {state.product_name or 'you'}",
                "content": f"Discover the standard of quality you deserve.",
                "catchy_line": "Do not settle."
            } for _ in range(100 - len(copy_objs))]
            
        themes = state.themes[:30]
        # Ensure we have 30 themes
        if len(themes) < 30:
            themes += [{"name": "Default", "primary_color": "#000000", "secondary_color": "#ffffff", "text_color": "#ffffff", "font_family": "Inter", "border_radius": "4px"}] * (30 - len(themes))
            
        ratios = self.ratios[:7]
        ctas = state.ctas if state.ctas else state.answers[:5]
        if not ctas:
            ctas = ["Shop Now"]
            
        # Design Library Mapping
        library = {
            "luxury": ["elegant_serif.html", "minimal_premium.html"],
            "tech": ["cyber_neon.html", "glassmorphism_vibe.html", "swiss_grid.html"],
            "youthful": ["retro_pop.html", "urban_collage.html"],
            "professional": ["swiss_grid.html", "poster_template.html", "minimal_premium.html"],
            "artistic": ["bauhaus_modern.html", "brutalist_raw.html", "urban_collage.html"],
            "urgent": ["brutalist_raw.html", "retro_pop.html"]
        }
        
        # Determine the primary tone
        tone = (state.brand_tone or "professional").lower()
        selected_templates = library.get(tone, ["poster_template.html", "minimal_premium.html", "glassmorphism_vibe.html"])
        # All available templates for fallback/rotation
        all_templates = [
            "poster_template.html", "minimal_premium.html", "glassmorphism_vibe.html",
            "retro_pop.html", "cyber_neon.html", "bauhaus_modern.html",
            "elegant_serif.html", "brutalist_raw.html", "swiss_grid.html", "urban_collage.html"
        ]

        variations = []
        # Combinatorial explosion: 50 x 10 x 5 = 2,500
        for idx, (copy_obj, theme, ratio) in enumerate(itertools.product(copy_objs, themes, ratios)):
            # Pick template: prioritize tone-matched ones, then rotate through others for variety
            if idx < 500: # First 500 variants highly focused on tone
                template = selected_templates[idx % len(selected_templates)]
            else:
                template = all_templates[idx % len(all_templates)]

            # Intelligent Asset Selection: Match image ratio to ad format ratio
            selected_img = state.processed_image_path
            
            if state.processed_image_assets:
                ad_ratio_val = ratio["width"] / ratio["height"]
                # Find the asset with the closest ratio to the ad format
                best_asset = min(state.processed_image_assets, key=lambda x: abs(x["ratio"] - ad_ratio_val))
                selected_img = best_asset["path"]

            variation = {
                "id": f"v_{idx}",
                "heading": copy_obj.get("heading", ""),
                "content": copy_obj.get("content", ""),
                "catchy_line": copy_obj.get("catchy_line", ""),
                "cta": ctas[idx % len(ctas)],
                "theme": theme,
                "ratio": ratio,
                "template": template,
                "image_description": state.image_descriptions[idx % len(state.image_descriptions)] if state.image_descriptions else "",
                "product_image": selected_img # Smart-matched asset
            }
            variations.append(variation)

        return {"variations": variations}
