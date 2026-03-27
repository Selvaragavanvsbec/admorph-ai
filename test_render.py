import asyncio
import uuid
from agents.state import AdGenState
from services.renderer import Renderer

async def test():
    state = AdGenState(product_name="Test Product")
    state.themes = [{"name": "Glassmorphism", "primary_color": "rgba(255, 255, 255, 0.2)", "secondary_color": "#6366f1", "text_color": "#1e293b", "font_family": "Inter", "border_radius": "24px", "background_texture": "gradient"}]
    
    variation = {
        "id": f"test_export_{uuid.uuid4().hex[:8]}",
        "template": "poster_template.html",
        "heading": "Test Headline",
        "content": "Test Content",
        "catchy_line": "Test Hook",
        "cta": "SHOP NOW",
        "theme": state.themes[0],
        "ratio": {'id': '1x1', 'width': 300, 'height': 300}, # small for speed
        "product_image": None
    }
    
    print("Starting renderer...")
    renderer = Renderer()
    try:
        path = await renderer.render_variation(variation)
        print(f"Success! Exported to: {path}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
