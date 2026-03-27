import os
import requests
from PIL import Image
try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    print("WARNING: rembg not installed. Background removal will be skipped.")
import io
import uuid
from typing import Optional

class ImageService:
    def __init__(self, output_dir: str = "assets/processed"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def download_image(self, url: str) -> Optional[bytes]:
        """Downloads an image from a URL or reads from local path."""
        # Handle local paths
        if os.path.exists(url):
            try:
                with open(url, "rb") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading local image: {e}")
                return None

        # Handle remote URLs
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=15.0)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            print(f"Error downloading image: {e}")
        return None

    def remove_background(self, image_bytes: bytes) -> bytes:
        """Removes the background from an image using rembg, with safety checks."""
        if not HAS_REMBG:
            print("WARNING: rembg not available. Returning original image.")
            return image_bytes
        try:
            # Safety: Check disk space before allowing rembg (it downloads a 176MB model)
            import shutil
            total, used, free = shutil.disk_usage("C:\\")
            if free < 500 * 1024 * 1024: # Less than 500MB free
                print("WARNING: Low disk space (<500MB). Skipping AI Background Removal to prevent hang.")
                return image_bytes

            input_image = Image.open(io.BytesIO(image_bytes))
            # Ensure image is in RGB or RGBA
            if input_image.mode not in ("RGB", "RGBA"):
                input_image = input_image.convert("RGB")
                
            output_image = remove(input_image)
            
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"Error removing background: {e}")
            return image_bytes

    def save_processed_image(self, image_bytes: bytes, filename: str = None) -> str:
        """Saves the processed image to the assets folder and returns the relative path."""
        if not filename:
            filename = f"prod_{uuid.uuid4().hex[:8]}.png"
        
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        # Return path relative to project root for internal consistency
        # Example: assets/processed/prod_123.png
        return f"assets/processed/{filename}"

    async def process_image_pipeline(self, image_url: str) -> Optional[str]:
        """Downloads and saves the image directly, skipping background removal."""
        print(f"Sourcing image from: {image_url}")
        img_bytes = await self.download_image(image_url)
        if not img_bytes:
            return None
            
        print("Skipping background removal (FastPath)...")
        
        # Ensure it's a valid image and convert to RGB/RGBA if needed via PIL
        try:
            input_image = Image.open(io.BytesIO(img_bytes))
            if input_image.mode not in ("RGB", "RGBA"):
                input_image = input_image.convert("RGB")
            
            img_byte_arr = io.BytesIO()
            # Save as PNG by default for consistency
            input_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
        except Exception as e:
            print(f"Image validation error: {e}")
            # Continue with raw bytes if conversion fails
        
        path = self.save_processed_image(img_bytes)
        print(f"Image processed and saved to: {path}")
        return path
