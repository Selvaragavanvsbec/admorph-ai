try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False
    print("WARNING: edge-tts not installed. Voice narration will be unavailable.")
import os
import hashlib
import asyncio

class VoiceEngine:
    def __init__(self, output_dir="generated/audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Concurrent Task Registry (prevents duplicate generation across multiple iframe requests)
        self._work_in_progress = {} # {filename: asyncio.Event}
        
        # Premium Voices for each template style
        self.voice_map = {
            "cyber_neon.html": "en-US-GuyNeural",        # Deep, digital
            "glassmorphism_vibe.html": "en-US-AriaNeural",# Soft, airy
            "brutalist_raw.html": "en-GB-RyanNeural",    # Industrial, bold
            "swiss_grid.html": "en-US-ChristopherNeural",# Precise, neutral
            "poster_template.html": "en-US-EricNeural",   # Professional, authoritative
            "retro_pop.html": "en-US-SteffanNeural",     # Vibrant, pop
            "minimal_premium.html": "en-US-JennyNeural", # Clean, minimalist
            "elegant_serif.html": "en-GB-SoniaNeural",   # Luxury, British
            "urban_collage.html": "en-US-BrianNeural"    # Street, rhythmic
        }

    async def generate_audio(self, text: str, template: str, voice_override: str = None):
        """Generates a high-quality MP3 for the given text with smart caching and concurrency control."""
        if not HAS_EDGE_TTS:
            return None
        if not text or len(text.strip()) < 2:
            return None

        # Use override if provided, else lookup from template map
        voice = voice_override if voice_override else self.voice_map.get(template, "en-US-EricNeural")
        clean_text = text.replace("//", " ").replace("_", " ").strip()
        
        # Stable Hashing for Caching — include voice in hash so different voices cache separately
        content_hash = hashlib.md5(f"{clean_text}_{voice}".encode()).hexdigest()[:12]
        filename = f"vo_{content_hash}.mp3"
        file_path = os.path.join(self.output_dir, filename)
        
        # 1. Quick Cache Hit Check
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return f"/generated/audio/{filename}"

        # 2. Concurrency Control (If another request is already generating this exact file, wait for it)
        if filename in self._work_in_progress:
            print(f"VOICE ENGINE: Waiting for concurrent generation of '{filename}'...")
            await self._work_in_progress[filename].wait()
            # Double check existence after wait
            if os.path.exists(file_path):
                return f"/generated/audio/{filename}"

        # 3. Cache Miss & Generation
        # Register work in progress
        completion_event = asyncio.Event()
        self._work_in_progress[filename] = completion_event
        
        try:
            print(f"VOICE ENGINE: Generating new clip for '{clean_text[:40]}...' ({voice})")
            communicate = edge_tts.Communicate(clean_text, voice)
            # 10s per-clip timeout to prevent hanging if Microsoft TTS is unreachable
            await asyncio.wait_for(communicate.save(file_path), timeout=10.0)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return f"/generated/audio/{filename}"
            return None
        except asyncio.TimeoutError:
            print(f"VOICE ENGINE TIMEOUT: '{filename}' took >10s - TTS server may be unreachable.")
            return None
        except Exception as e:
            print(f"VOICE ENGINE ERROR for '{filename}': {e}")
            return None
        finally:
            # Signal completion and cleanup
            completion_event.set()
            if filename in self._work_in_progress:
                del self._work_in_progress[filename]

voice_engine = VoiceEngine()
