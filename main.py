import asyncio
import sys
import os

# Ultra-stable loop policy for Windows 10/11 with Uvicorn
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("INIT DEBUG: ProactorEventLoopPolicy set successfully.")
    except Exception as e:
        print(f"INIT ERROR: Failed to set loop policy: {e}")

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router
from api.preview import router as preview_router
from config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure output directory exists before app starts
    output_path = Path(settings.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure audio directory exists
    audio_path = Path(settings.output_dir) / "audio"
    audio_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure assets directories exist
    Path("assets/processed").mkdir(parents=True, exist_ok=True)
    Path("assets/uploads").mkdir(parents=True, exist_ok=True)
    
    # Verify the loop
    loop = asyncio.get_event_loop()
    print(f"LIFESPAN DEBUG: Event loop running: {type(loop)}")
    
    yield
    
    # Shutdown logic
    try:
        from services.renderer import Renderer
        renderer = Renderer()
        await renderer.close()
        print("LIFESPAN DEBUG: Renderer closed successfully.")
    except Exception as e:
        print(f"LIFESPAN DEBUG: Renderer cleanup skipped: {e}")

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# GLOBAL CORS - Allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "loop": str(type(asyncio.get_event_loop()))}

app.include_router(router)
app.include_router(preview_router)

# Static file serving
app.mount("/generated", StaticFiles(directory=settings.output_dir), name="generated")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Serve frontend static files in production
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
STATIC_DIR = os.path.join(FRONTEND_DIST, "static")

if os.path.exists(FRONTEND_DIST):
    # If standard static folder exists, explicitly mount it for proper JS/CSS MIME types
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="frontend-static")
        
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA - catch-all route for client-side routing."""
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path) and not full_path.startswith("static/"):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"SYSTEM DEBUG: Starting on {sys.platform} at {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False, workers=1)
