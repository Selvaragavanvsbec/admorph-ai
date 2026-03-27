from langchain_core.messages import HumanMessage, SystemMessage
import json
from .llm_factory import get_llm
from .state import AdGenState
from config import settings

class ThemeAgent:
    def __init__(self):
        self.llm = get_llm()

    async def run(self, state: AdGenState) -> dict:
        """Generates 30 unique visual themes (CSS variable sets) dynamically with strategic metadata."""
        print(f"DEBUG: ThemeAgent.run() starting for product: {state.product_name}")
        
        prompt = [
            SystemMessage(content=(
                "You are a World-Class Creative Director at a top-tier digital agency. "
                "Task: Generate exactly 30 unique, high-end visual themes for a digital ad campaign. "
                "Each theme must be a strategic masterpiece."
                
                "\n\nSTRUCTURE MAPPING:"
                "1. THEMES 1-5 (TRENDING): Must be 'Social Mimic' styles ('Viral Tweet', 'iMessage Thread', 'App Notification', 'LinkedIn Post', 'Instagram DM')."
                "2. THEMES 6-10 (MODERN TECH): Neo-Brutalism, Glassmorphism 2.0, Bento Grid, Silicon Dark, and Liquid Aurora."
                "3. THEMES 11-15 (LUXURY/PREMIUM): Golden Ratio, Editorial Serif, Minimal High-Fashion, Velvet Noir, and Arctic Clean."
                "4. THEMES 16-20 (CREATIVE/URBAN): Paper Collage, Street Graffiti, Retro Synthwave, Brutal Raw, and Pop Kinetic."
                "5. THEMES 21-30 (STRATEGIC): Industry-specific variations like 'Architectural Swiss', 'Developer Dark', 'Wellness Organic', etc."

                "\n\nFor each theme, define:"
                "1. name (Evocative and premium)"
                "2. primary_color, secondary_color, text_color (HEX codes)"
                "3. font_family (Inter, Montserrat, Roboto, or Playfair Display)"
                "4. border_radius (e.g., '0px', '12px', '40px', '100px')"
                "5. background_texture ('none', 'dots', 'grid', 'diagonal-lines', 'noise', 'gradient')"
                "6. strategy_fields: 'why_it_works', 'best_for', 'who_loves_it'"
            )),
            HumanMessage(content=(
                f"Product: {state.product_name}\nDescription: {state.product_description}\nTone: {state.brand_tone}\n\n"
                "Return exactly 30 themes in a JSON object with a 'themes' key. "
                "Ensure every theme feels like it was designed by a $500/hr specialist."
            ))
        ]
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            themes = data.get("themes", [])
            theme_names = [t.get('name') for t in themes]
            print(f"DEBUG: Successfully generated {len(themes)} themes: {theme_names}")
            
            return {"themes": themes}
        except Exception as e:
            print(f"Theme Generation API Error (using fallback): {e}")
            # Robust Fallback with Trend-First styles
            return {"themes": [
                 {"name": "Viral Tweet", "primary_color": "#1DA1F2", "secondary_color": "#ffffff", "text_color": "#0f1419", "font_family": "Inter", "border_radius": "16px", "background_texture": "none", "why_it_works": "Mimics viral social proof to bypass marketing 'blindness'.", "best_for": "X, LinkedIn", "who_loves_it": "The Intellects"},
                 {"name": "iMessage Thread", "primary_color": "#007AFF", "secondary_color": "#f0f2f5", "text_color": "#000000", "font_family": "Inter", "border_radius": "20px", "background_texture": "none", "why_it_works": "Personal chat bubbles build instant trust and peer-approval.", "best_for": "IG Stories, TikTok", "who_loves_it": "Gen-Z & Millennials"},
                 {"name": "App Notification", "primary_color": "#ffffff", "secondary_color": "#000000", "text_color": "#000000", "font_family": "Inter", "border_radius": "14px", "background_texture": "none", "why_it_works": "The 'iOS Alert' aesthetic creates a sense of high-priority urgency.", "best_for": "Mobile Feed", "who_loves_it": "High Achievers"},
                 {"name": "Neo-Brutalist", "primary_color": "#FFDE03", "secondary_color": "#000000", "text_color": "#000000", "font_family": "Montserrat", "border_radius": "0px", "background_texture": "noise", "why_it_works": "Bold, raw design that demands attention on a cluttered feed.", "best_for": "Streetwear, Tech", "who_loves_it": "Trendsetters"},
                 {"name": "Glassmorphism 2.0", "primary_color": "rgba(255, 255, 255, 0.2)", "secondary_color": "#6366f1", "text_color": "#1e293b", "font_family": "Inter", "border_radius": "30px", "background_texture": "noise", "why_it_works": "Frosted glass texture implies transparency and modern sophistication.", "best_for": "Fintech, SaaS", "who_loves_it": "Modern Early Adopters"},
                 {"name": "Bento Grid Pro", "primary_color": "#ffffff", "secondary_color": "#f8fafc", "text_color": "#0f172a", "font_family": "Inter", "border_radius": "20px", "background_texture": "grid", "why_it_works": "Modular layout allows for dense but clean information delivery.", "best_for": "Hardware, Real Estate", "who_loves_it": "The Organized"},
                 {"name": "Golden Editorial", "primary_color": "#d4af37", "secondary_color": "#1a1a1a", "text_color": "#d4af37", "font_family": "Playfair Display", "border_radius": "2px", "background_texture": "dots", "why_it_works": "Classical layout mirroring top-tier fashion and travel magazines.", "best_for": "Luxury Watch, Spirits", "who_loves_it": "The Elite"},
                 {"name": "Swiss Modern", "primary_color": "#e11d48", "secondary_color": "#ffffff", "text_color": "#000000", "font_family": "Roboto", "border_radius": "0px", "background_texture": "grid", "why_it_works": "Extreme white space and grid logic convey absolute confidence.", "best_for": "Architecture, Logistics", "who_loves_it": "Logical Thinkers"},
                 {"name": "Midnight Matrix", "primary_color": "#000000", "secondary_color": "#052e16", "text_color": "#22c55e", "font_family": "Roboto", "border_radius": "0px", "background_texture": "dots", "why_it_works": "Cybersecurity aesthetic that appeals to technical specialists.", "best_for": "DevTools, Security", "who_loves_it": "Backend Engineers"},
                 {"name": "Vaporwave Dream", "primary_color": "#ff71ce", "secondary_color": "#01cdfe", "text_color": "#fffb96", "font_family": "Montserrat", "border_radius": "0px", "background_texture": "diagonal-lines", "why_it_works": "Nostalgic retro-futurism that resonates with digital creatives.", "best_for": "Gaming, Music", "who_loves_it": "The Nostalgics"},
                 {"name": "Arctic Noise", "primary_color": "#f0f9ff", "secondary_color": "#e0f2fe", "text_color": "#0369a1", "font_family": "Inter", "border_radius": "16px", "background_texture": "noise", "why_it_works": "Clean, frosty texture that implies purity and efficiency.", "best_for": "Wellness, Cleaning", "who_loves_it": "The Purest"},
                 {"name": "Urban Collage", "primary_color": "#111111", "secondary_color": "#334155", "text_color": "#ffffff", "font_family": "Montserrat", "border_radius": "12px", "background_texture": "noise", "why_it_works": "Overlapping textures create a gritty, high-energy city vibe.", "best_for": "Apparel, Music", "who_loves_it": "City Dwellers"},
                 {"name": "Sleek Minimalism", "primary_color": "#ffffff", "secondary_color": "#f1f5f9", "text_color": "#000000", "font_family": "Inter", "border_radius": "50px", "background_texture": "none", "why_it_works": "Stripping away all noise identifies your brand as the expert choice.", "best_for": "Premium SaaS", "who_loves_it": "CEOs"},
                 {"name": "Digital Blueprint", "primary_color": "#1e3a8a", "secondary_color": "#1e40af", "text_color": "#ffffff", "font_family": "Roboto", "border_radius": "0px", "background_texture": "grid", "why_it_works": "Grid patterns imply engineering depth and structural logic.", "best_for": "Construciton, SaaS", "who_loves_it": "The Builders"},
                 {"name": "Retro Pop", "primary_color": "#fbbf24", "secondary_color": "#f59e0b", "text_color": "#000000", "font_family": "Montserrat", "border_radius": "12px", "background_texture": "diagonal-lines", "why_it_works": "High-contrast patterns boost scroll-stop potential by 40%.", "best_for": "Flash Sales, Food", "who_loves_it": "Impulse Buyers"},
                 {"name": "Velvet Noir", "primary_color": "#1a1a1a", "secondary_color": "#000000", "text_color": "#ffffff", "font_family": "Playfair Display", "border_radius": "4px", "background_texture": "noise", "why_it_works": "Dark organic noise creates a velvet tactile experience.", "best_for": "VIP Events, Beauty", "who_loves_it": "Socialites"},
                 {"name": "Silicon Valley", "primary_color": "#0ea5e9", "secondary_color": "#0f172a", "text_color": "#ffffff", "font_family": "Roboto", "border_radius": "8px", "background_texture": "grid", "why_it_works": "The 'Tech Startup' look that signals innovation and scale.", "best_for": "Software, AI", "who_loves_it": "CTOs"},
                 {"name": "Organic Mint", "primary_color": "#f0fdf4", "secondary_color": "#dcfce7", "text_color": "#166534", "font_family": "Inter", "border_radius": "100px", "background_texture": "dots", "why_it_works": "Breathable layouts for health and wellness industries.", "best_for": "Vitamins, Yoga", "who_loves_it": "The Conscious"},
                 {"name": "Deep Ocean", "primary_color": "#1e40af", "secondary_color": "#1e3a8a", "text_color": "#93c5fd", "font_family": "Inter", "border_radius": "10px", "background_texture": "dots", "why_it_works": "Calm, structured depth that implies scientific data reliability.", "best_for": "HealthTech, Data", "who_loves_it": "Scientists"},
                 {"name": "Steel Industrial", "primary_color": "#334155", "secondary_color": "#475569", "text_color": "#f8fafc", "font_family": "Inter", "border_radius": "2px", "background_texture": "grid", "why_it_works": "Cold, hard grids imply manufacturing durability.", "best_for": "Tools, Logistics", "who_loves_it": "Practical Minds"},
                 {"name": "Abstract Circuit", "primary_color": "#0f172a", "secondary_color": "#000000", "text_color": "#0ea5e9", "font_family": "Roboto", "border_radius": "4px", "background_texture": "grid", "why_it_works": "Electronic patterns create an 'Insiders Only' vibe.", "best_for": "Hardware, Crypto", "who_loves_it": "Early Adopters"},
                 {"name": "Modern Archive", "primary_color": "#0a0a0a", "secondary_color": "#171717", "text_color": "#e5e5e5", "font_family": "Inter", "border_radius": "0px", "background_texture": "noise", "why_it_works": "Premium documentary feel for legacy and heritage brands.", "best_for": "Luxury Apparel", "who_loves_it": "The Connoisseur"},
                 {"name": "Bubble Pop", "primary_color": "#ec4899", "secondary_color": "#f472b6", "text_color": "#ffffff", "font_family": "Montserrat", "border_radius": "60px", "background_texture": "dots", "why_it_works": "Playful, organic shapes that appeal to younger demographics.", "best_for": "Apps, Snacks", "who_loves_it": "The Young at Heart"},
                 {"name": "Desert Grain", "primary_color": "#451a03", "secondary_color": "#78350f", "text_color": "#fef3c7", "font_family": "Montserrat", "border_radius": "2px", "background_texture": "noise", "why_it_works": "Sandy texture that invokes adventure and the outdoors.", "best_for": "Travel, Gear", "who_loves_it": "Explorers"},
                 {"name": "Hacker Shell", "primary_color": "#020617", "secondary_color": "#000000", "text_color": "#22c55e", "font_family": "Roboto", "border_radius": "0px", "background_texture": "grid", "why_it_works": "The classic 'Root Access' look for dev-focused marketing.", "best_for": "SaaS, DevOps", "who_loves_it": "SysAdmins"},
                 {"name": "Zen Space", "primary_color": "#ffffff", "secondary_color": "#f8fafc", "text_color": "#1e293b", "font_family": "Inter", "border_radius": "100px", "background_texture": "none", "why_it_works": "Ultimate tranquility for luxury real estate or meditation.", "best_for": "SPA, Property", "who_loves_it": "The Dreamers"},
                 {"name": "Liquid Aurora", "primary_color": "#6366f1", "secondary_color": "#ec4899", "text_color": "#ffffff", "font_family": "Montserrat", "border_radius": "24px", "background_texture": "gradient", "why_it_works": "Dynamic gradients keep the ad feeling alive and interactive.", "best_for": "Design, NFT", "who_loves_it": "Gen-Alpha"},
                 {"name": "Royal Dotted", "primary_color": "#111111", "secondary_color": "#000000", "text_color": "#fbbf24", "font_family": "Playfair Display", "border_radius": "0px", "background_texture": "dots", "why_it_works": "Regal black-on-gold dot textures mirror prestige.", "best_for": "Jewelry, VIP", "who_loves_it": "The Elite"},
                 {"name": "Stealth Matte", "primary_color": "#121212", "secondary_color": "#0a0a0a", "text_color": "#94a3b8", "font_family": "Inter", "border_radius": "0px", "background_texture": "noise", "why_it_works": "Matte finish on black is the gold standard for premium tech.", "best_for": "Hardware, EV", "who_loves_it": "Executive Tier"},
                 {"name": "Monaco Club", "primary_color": "#1e1e1e", "secondary_color": "#0a0a0a", "text_color": "#fbbf24", "font_family": "Playfair Display", "border_radius": "2px", "background_texture": "dots", "why_it_works": "The feel of a high-end invitation or private club card.", "best_for": "Exotic, VIP", "who_loves_it": "Status Seekers"}
            ]}
