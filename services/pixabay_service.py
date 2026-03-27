import httpx
import random
import urllib.parse
from config import settings

class PixabayService:
    def __init__(self):
        # We use the Pixabay API Key from config
        self.api_key = settings.pixabay_api_key
        self.base_url = "https://pixabay.com/api/"

    async def search_image(self, query: str, image_type: str = "photo", orientation: str = "all", colors: str = None) -> str | None:
        """
        Searches for an image on Pixabay and returns a URL (largeImageURL).
        """
        params = {
            "key": self.api_key,
            "q": urllib.parse.quote(query),
            "image_type": image_type,
            "orientation": orientation,
            "safesearch": "true",
            "per_page": 20
        }
        
        if colors:
            params["colors"] = colors

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    # Return all high quality hits (up to 20 per request)
                    return [{
                        "url": h.get("largeImageURL"),
                        "width": h.get("imageWidth"),
                        "height": h.get("imageHeight"),
                        "ratio": h.get("imageWidth") / h.get("imageHeight") if h.get("imageHeight") else 1.0
                    } for h in hits]
        except Exception as e:
            print(f"Pixabay API Error: {e}")
        
        return None
