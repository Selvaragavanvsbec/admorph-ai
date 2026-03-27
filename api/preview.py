import os
import time
import hashlib
import asyncio
from typing import Dict
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
from .routes import sessions

router = APIRouter()

# ─── Global Status Registry for Real-time SSE Updates ───
# {session_id: {ratio_id: queue}}
status_queues: Dict[str, Dict[str, asyncio.Queue]] = {}

# ─── Rate Limiting: Max 2 concurrent audio generation jobs ───
# Lazy-initialized to avoid loop mismatch on Windows
_audio_semaphore = None
_audio_lock = asyncio.Lock()

async def get_audio_semaphore():
    global _audio_semaphore
    async with _audio_lock:
        if _audio_semaphore is None:
            _audio_semaphore = asyncio.Semaphore(2)
        return _audio_semaphore

# ─── Response Cache: skip re-renders for identical requests ───
# {content_hash: html_string} — capped at 50 entries (LRU-style)
_render_cache: Dict[str, str] = {}
_RENDER_CACHE_MAX = 50

def _make_render_key(session_id, theme_name, ratio_id, heading, content, catchy_line, vo, voice, render_mode='dynamic', bp='', bs='', bt='', lang='English'):
    raw = f"{session_id}|{theme_name}|{ratio_id}|{heading}|{content}|{catchy_line}|{vo}|{voice}|{render_mode}|{bp}|{bs}|{bt}|{lang}"
    return hashlib.md5(raw.encode()).hexdigest()


@router.get("/render-status/{session_id}/{ratio_id}")
async def render_status(session_id: str, ratio_id: str):
    """Event stream for real-time rendering status updates."""
    if session_id not in status_queues:
        status_queues[session_id] = {}
    
    queue = asyncio.Queue()
    status_queues[session_id][ratio_id] = queue

    async def event_generator():
        try:
            while True:
                message = await queue.get()
                yield f"data: {message}\n\n"
                if message == "COMPLETED" or "ERROR" in message:
                    break
        finally:
            if session_id in status_queues and ratio_id in status_queues[session_id]:
                del status_queues[session_id][ratio_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def broadcast_status(session_id: str, ratio_id: str, status: str):
    """Sends a status update to the specific ratio's queue."""
    if session_id in status_queues and ratio_id in status_queues[session_id]:
        await status_queues[session_id][ratio_id].put(status)

@router.get("/render-html")
async def render_html(session_id: str, theme_name: str, ratio_id: str,
                      heading: str, content: str, catchy_line: str,
                      vo: bool = False, voice: str = None, 
                      render_mode: str = 'dynamic', _t: str = None,
                      bp: str = '', bs: str = '', bt: str = '',
                      lang: str = 'English'):
    """Returns the raw HTML for the variation to be rendered in an iframe."""
    # Note: _t is a cache-busting timestamp from Replay — used to invalidate render cache only
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session expired")
        
        state = sessions[session_id]

        # ── Localization Sync ──
        # If lang is not English, we need to ensure we render the localized version.
        if lang and lang.lower() != 'english':
            from agents.localization_agent import localization_agent
            copy_obj = {"heading": heading, "content": content, "catchy_line": catchy_line}
            # Transcreate on-the-fly for the preview iframe
            localized = await localization_agent.transcreate(copy_obj, lang, state)
            heading = localized.get("heading", heading)
            content = localized.get("content", content)
            catchy_line = localized.get("catchy_line", catchy_line)

        # ── Cache check: return immediately if same request was already rendered ──
        # _t is intentionally excluded from cache key — replay should bypass cache for fresh animations
        cache_key = _make_render_key(session_id, theme_name, ratio_id, heading, content, catchy_line, vo, voice, render_mode, bp, bs, bt, lang)
            
        if cache_key in _render_cache and not _t:  # Skip cache on replay (_t present)
            await broadcast_status(session_id, ratio_id, "COMPLETED")
            return HTMLResponse(content=_render_cache[cache_key])

        state = sessions[session_id]
        
        # Ratio logic
        ratios = [
            {'id': '1x1', 'width': 1080, 'height': 1080},
            {'id': '9x16', 'width': 1080, 'height': 1920},
            {'id': '4x5', 'width': 1080, 'height': 1350},
            {'id': '16x9', 'width': 1920, 'height': 1080},
            {'id': '1.91x1', 'width': 1200, 'height': 628}
        ]
        ratio = next((r for r in ratios if r['id'].lower() == ratio_id.lower()), ratios[0])
        
        # Theme logic
        theme_match = next((t for t in state.themes if t.get('name', '').strip().lower() == theme_name.strip().lower()), None)
        theme = theme_match or (state.themes[0] if state.themes else {})
        
        # Template map — covers all known theme name variants + fuzzy fallback
        template_map = {
            "cyber neon": "cyber_neon.html",
            "cyber": "cyber_neon.html",
            "neon": "cyber_neon.html",
            "midnight matrix": "cyber_neon.html",
            "midnight": "cyber_neon.html",
            "matrix": "cyber_neon.html",
            "glassmorphism": "glassmorphism_vibe.html",
            "glassmorphism vibe": "glassmorphism_vibe.html",
            "glassmorphism 2.0": "glassmorphism_vibe.html",
            "ultra glass": "glassmorphism_vibe.html",
            "glass": "glassmorphism_vibe.html",
            "ultra": "glassmorphism_vibe.html",
            "retro pop": "retro_pop.html",
            "retro kinetic": "retro_pop.html",
            "retro": "retro_pop.html",
            "pop": "retro_pop.html",
            "minimalist white": "minimal_premium.html",
            "minimal": "minimal_premium.html",
            "minimalist": "minimal_premium.html",
            "clean": "minimal_premium.html",
            "elegant gold": "editorial_magazine.html",
            "elegant serif": "editorial_magazine.html",
            "golden editorial": "editorial_magazine.html",
            "elegant": "editorial_magazine.html",
            "luxury dark": "editorial_magazine.html",
            "velvet noir": "editorial_magazine.html",
            "luxury": "editorial_magazine.html",
            "swiss modern": "bento_grid.html",
            "swiss grid": "bento_grid.html",
            "swiss": "bento_grid.html",
            "bento grid pro": "bento_grid.html",
            "bento": "bento_grid.html",
            "grid": "bento_grid.html",
            "liquid aurora": "liquid_aurora.html",
            "liquid": "liquid_aurora.html",
            "bauhaus": "bauhaus_modern.html",
            "bauhaus modern": "bauhaus_modern.html",
            "modern": "bauhaus_modern.html",
            "brutal raw": "brutalist_raw.html",
            "brutalist": "brutalist_raw.html",
            "brutal": "brutalist_raw.html",
            "neo-brutalist": "brutalist_raw.html",
            "raw": "brutalist_raw.html",
            "social mimic": "social_mimic.html",
            "social": "social_mimic.html",
            "mimic": "social_mimic.html",
            "tweet": "social_mimic.html",
            "chat": "social_mimic.html",
            "message": "social_mimic.html",
            "notif": "social_mimic.html",
            "notification": "social_mimic.html",
            "youthful mint": "urban_collage.html",
            "urban": "urban_collage.html",
            "collage": "urban_collage.html",
            "youthful": "urban_collage.html",
            "professional blue": "poster_template.html",
            "professional": "poster_template.html",
            "poster": "poster_template.html",
        }
        # Template resolution: use theme_name URL param directly (authoritative source)
        # theme object from state is used for colors/fonts only
        theme_name_lower = theme_name.strip().lower()
        selected_template = template_map.get(theme_name_lower)
        if not selected_template:
            for key, tmpl in template_map.items():
                if key in theme_name_lower or theme_name_lower in key:
                    selected_template = tmpl
                    break
        if not selected_template:
            selected_template = "glassmorphism_vibe.html"  # Fallback to best-looking template
        print(f"RENDER: {theme_name!r} → {selected_template} (ratio={ratio_id})")

        # Prepare image path with Intelligent Ratio Matching
        product_image = None
        
        # 1. Try to find the best match in the multiple assets pool
        if state.processed_image_assets:
            ad_ratio_val = ratio["width"] / ratio["height"]
            best_asset = min(state.processed_image_assets, key=lambda x: abs(x["ratio"] - ad_ratio_val))
            product_image = best_asset["path"]
        
        # 2. Fallback to primary or user URL
        if not product_image:
            product_image = state.processed_image_path or state.user_image_url

        # Path scrubbing for consistent local serving
        if product_image:
            # If it's a local full path (sometimes happens in edge cases), convert to relative/URL
            if os.path.exists(product_image) and not product_image.startswith("http"):
                if "assets" in product_image:
                    parts = product_image.split("assets")
                    product_image = "/assets" + parts[-1].replace("\\", "/")
                elif "generated" in product_image:
                    parts = product_image.split("generated")
                    product_image = "/generated" + parts[-1].replace("\\", "/")

        # 1. Start Phase
        await broadcast_status(session_id, ratio_id, "PREPARING_ENGINE")

        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template(selected_template)
        
        vo_urls = None
        if vo:
            # 2. VO Phase — rate-limited by semaphore (max 2 concurrent audio jobs)
            await broadcast_status(session_id, ratio_id, "SYNCHRONIZING_AUDIO")
            from engines.voice_engine import voice_engine
            try:
                sem = await get_audio_semaphore()
                async with sem:
                    # Max 2 ratios generating audio simultaneously
                    results = await asyncio.wait_for(
                        asyncio.gather(
                            voice_engine.generate_audio(catchy_line, selected_template, voice_override=voice),
                            voice_engine.generate_audio(heading, selected_template, voice_override=voice),
                            voice_engine.generate_audio(content, selected_template, voice_override=voice),
                            voice_engine.generate_audio("SHOP NOW", selected_template, voice_override=voice),
                            return_exceptions=True
                        ),
                        timeout=25.0  # Per-ratio audio budget
                    )
                vo_urls = {
                    "catchy":  results[0] if not isinstance(results[0], Exception) else None,
                    "heading": results[1] if not isinstance(results[1], Exception) else None,
                    "content": results[2] if not isinstance(results[2], Exception) else None,
                    "cta":     results[3] if not isinstance(results[3], Exception) else None,
                }
            except asyncio.TimeoutError:
                print(f"VO GEN TIMEOUT: {ratio_id} waited too long for semaphore or generation")
                vo_urls = None
            except Exception as vo_err:
                print(f"VO GEN WARNING [{ratio_id}]: {vo_err}")
                vo_urls = None

        # 3. Finalization Phase
        await broadcast_status(session_id, ratio_id, "FINALIZING_HTML")
        html_content = template.render(
            heading=heading,
            content=content,
            catchy_line=catchy_line,
            cta="SHOP NOW",
            theme=theme,
            ratio=ratio,
            product_image=product_image,
            product_name=state.product_name or "AdMorph",
            font_family=theme.get('font_family', 'Inter'),
            render_mode=render_mode,
            vo_urls=vo_urls,
            brand_primary=bp,
            brand_secondary=bs,
            brand_accent=bt
        )

        # ── Inject Canvas Edit Mode (drag + contentEditable) ──
        edit_script = """<script>
            (function() {
                // 1. Setup Bi-directional Sync
                window.addEventListener('message', function(e) {
                    if (!e.data) return;
                    
                    // Respond to Color Updates (Instant CSS Injection)
                    if (e.data.type === 'UPDATE_COLORS') {
                        const styleId = '__dynamic_colors__';
                        let styleEl = document.getElementById(styleId);
                        if (!styleEl) {
                            styleEl = document.createElement('style');
                            styleEl.id = styleId;
                            document.head.appendChild(styleEl);
                        }
                        const { primary, secondary, text } = e.data.colors;
                        styleEl.textContent = `:root { 
                            --primary: ${primary} !important; 
                            --secondary: ${secondary} !important; 
                            --text-color: ${text} !important;
                        }`;
                    }
                    
                    // Respond to Text Updates (Optional: If Parent wants to push text)
                    if (e.data.type === 'UPDATE_TEXT') {
                        const { field, value } = e.data;
                        const targets = {
                            'heading': 'h1',
                            'content': '.subheadline, p:not(.catchy-line)',
                            'catchy_line': '.catchy-line',
                            'cta': '.cta, .cta-btn, .cta-button'
                        };
                        const selector = targets[field];
                        if (selector) {
                            const el = document.querySelector(selector);
                            if (el) el.innerText = value;
                        }
                    }
                });

                // 2. Enable In-Canvas Editing (Direct Text Interaction)
                // We'll map DOM elements back to the "field keys" the parent expects
                const fieldMap = [
                    { selector: 'h1', key: 'heading' },
                    { selector: '.catchy-line', key: 'catchy_line' },
                    { selector: '.subheadline', key: 'content' },
                    { selector: 'p:not(.catchy-line)', key: 'content' },
                    { selector: '.cta', key: 'cta' },
                    { selector: '.cta-btn', key: 'cta' },
                    { selector: '.cta-button', key: 'cta' }
                ];

                fieldMap.forEach(({ selector, key }) => {
                    const el = document.querySelector(selector);
                    if (!el) return;

                    el.contentEditable = 'true';
                    el.style.outline = 'none';
                    el.style.cursor = 'text';

                    // Visual Feedback on Hover
                    el.addEventListener('mouseenter', () => { el.style.boxShadow = '0 0 0 2px rgba(139,92,246,0.5)'; el.style.borderRadius = '4px'; });
                    el.addEventListener('mouseleave', () => { el.style.boxShadow = 'none'; });

                    // Sync Changes Back to Parent instantly
                    el.addEventListener('input', () => {
                        window.parent.postMessage({
                            type: 'CANVAS_EDIT',
                            field: key,
                            value: el.innerText
                        }, '*');
                    });
                    
                    // Prevent drag/links while editing
                    el.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); });
                });
            })();
        </script>"""
        html_content = html_content.replace('</body>', edit_script + '\n</body>', 1)

        # ── Cache the rendered HTML (evict oldest if full) ──

        if len(_render_cache) >= _RENDER_CACHE_MAX:
            oldest_key = next(iter(_render_cache))
            del _render_cache[oldest_key]
        _render_cache[cache_key] = html_content

        await broadcast_status(session_id, ratio_id, "COMPLETED")
        return HTMLResponse(content=html_content)
            
    except Exception as e:
        await broadcast_status(session_id, ratio_id, f"ERROR: {str(e)}")
        print(f"HTML RENDER ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
