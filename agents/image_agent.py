from .state import AdGenState
from services.image_service import ImageService
import os

class ImageAgent:
    def __init__(self):
        self.image_service = ImageService()
        from services.pixabay_service import PixabayService
        self.pixabay = PixabayService()

    async def run(self, state: AdGenState) -> dict:
        """
        Orchestrates image sourcing and processing.
        1. If user provided a URL, use it.
        2. Try to find a real professional photo on Pixabay.
        3. Fallback to AI generation (Pollinations) if Pixabay has no hits.
        4. Save locally and verify format.
        """
        # 1. Sourcing Layer
        candidates = []
        user_url = state.user_image_url
        if user_url:
            # User provided a single image
            candidates.append({"url": user_url, "width": 1024, "height": 1024, "ratio": 1.0})
        else:
            print(f"No image provided for {state.product_name}. Searching Pixabay...")
            pixabay_query = f"{state.product_name} product"
            try:
                # Attempt to get a batch of professional photos
                pixabay_results = await self.pixabay.search_image(pixabay_query)
                if pixabay_results:
                    candidates = pixabay_results[:10] # Process top 10 for variety
                    print(f"Sourced {len(candidates)} candidates via Pixabay.")
            except Exception as e:
                print(f"Pixabay search failed: {e}")

            # Fallback to AI generation if Pixabay finds nothing
            if not candidates:
                print("Pixabay yielded no results. Falling back to AI Generation (Pollinations)...")
                keyword = f"{state.product_name} product shot on solid white background".replace(" ", "%20")
                ai_url = f"https://image.pollinations.ai/prompt/{keyword}?width=1024&height=1024&nologo=true"
                candidates.append({"url": ai_url, "width": 1024, "height": 1024, "ratio": 1.0})

        # 2. Processing Layer (parallel/batch using gather)
        import asyncio
        async def process_item(cand):
            try:
                processed_path = await self.image_service.process_image_pipeline(cand["url"])
                if processed_path:
                    return {
                        "path": processed_path,
                        "width": cand["width"],
                        "height": cand["height"],
                        "ratio": cand["ratio"]
                    }
            except Exception as e:
                print(f"Failure processing asset {cand['url']}: {e}")
            return None

        # Execute all processing in parallel
        results = await asyncio.gather(*[process_item(c) for c in candidates])
        processed_assets = [r for r in results if r is not None]

        # Final State Update
        return {
            "processed_image_assets": processed_assets,
            # For backward compatibility, keep the first one as primary
            "processed_image_path": processed_assets[0]["path"] if processed_assets else None
        }
