from fastapi import APIRouter, HTTPException, Body, BackgroundTasks, UploadFile, File
import asyncio
import sys
import uuid
import os
import shutil
from typing import Dict, Any
from config import settings

router = APIRouter()

# In-memory storage for active sessions (in a real app, use Redis/DB)
sessions: Dict[str, Any] = {}

def get_graph():
    from agents.graph import AdGenGraph
    return AdGenGraph()

def get_state_obj(data):
    from agents.state import AdGenState
    return AdGenState(**data)

@router.post("/start-campaign")
async def start_campaign():
    """Starts a new ad generation session."""
    session_id = uuid.uuid4().hex
    state = get_state_obj({})
    sessions[session_id] = state
    
    print(f"DEBUG: Started new session {session_id}")
    
    # Truly Instant Start: Just return the hardcoded first question.
    # No graph initialization here to prevent blocking the single worker.
    first_question = "What is the name of the product or service we are advertising?"
    state.questions = [first_question]
    
    return {
        "session_id": session_id,
        "next_question": first_question
    }

async def run_dev_background(session_id: str, state_dict: dict):
    """Specialized background task for Dev Mode - skips regenerating content but processes images & variants."""
    from agents.state import AdGenState
    from agents.image_agent import ImageAgent
    from engines.variant_engine import VariantGenerator
    try:
        current_state = AdGenState(**state_dict)
        
        # 1. Image Sourcing (Prefer Pixabay)
        print(f"DEBUG: Dev Background - Sourcing Images for {session_id}")
        image_agent = ImageAgent()
        image_results = await image_agent.run(current_state)
        state_dict.update(image_results)
        
        # PERSIST PROGRESS: Update session with images so variations can start using them immediately
        sessions[session_id] = AdGenState(**state_dict)
        print(f"DEBUG: Dev Background - Images ready for {session_id}")
        
        # 2. Variant Expansion
        print(f"DEBUG: Dev Background - Expanding Variants for {session_id}")
        current_state = AdGenState(**state_dict)
        variant_gen = VariantGenerator()
        variant_results = await variant_gen.run(current_state)
        state_dict.update(variant_results)
        
        sessions[session_id] = AdGenState(**state_dict)
        print(f"Dev background processing complete for {session_id}")
    except Exception as e:
        print(f"Error in dev background processing for {session_id}: {e}")

async def run_generation_background(session_id: str, state_dict: dict):
    from agents.state import AdGenState
    from agents.theme_agent import ThemeAgent
    try:
        # 1. Run Theme Agent
        theme_agent = ThemeAgent()
        current_state = AdGenState(**state_dict)
        print(f"DEBUG: Background - Generating Themes for {session_id}")
        theme_results = await theme_agent.run(current_state)
        state_dict.update(theme_results)
        sessions[session_id] = AdGenState(**state_dict)

        # 2. Run Copy Agent
        from agents.copy_agent import CopyGenerator
        copy_agent = CopyGenerator()
        print(f"DEBUG: Background - Generating Copy for {session_id}")
        copy_results = await copy_agent.run(AdGenState(**state_dict))
        state_dict.update(copy_results)
        sessions[session_id] = AdGenState(**state_dict)

        # 3. Finally run the full graph for variants/rendering
        print(f"DEBUG: Background - Running full graph for {session_id}")
        graph = get_graph()
        result = await graph.run(state_dict)
        sessions[session_id] = AdGenState(**result)
        print(f"Background generation complete for {session_id}")
    except Exception as e:
        print(f"Error in background generation for {session_id}: {e}")

from agents.state import AdGenState

@router.post("/submit-answer/{session_id}")
async def submit_answer(session_id: str, background_tasks: BackgroundTasks, answer: str = Body(..., embed=True)):
    """Submits an answer and gets the next question or starts generation."""
    print(f"DEBUG: Received answer for session {session_id}. Active sessions: {list(sessions.keys())}")
    
    if session_id not in sessions:
        print(f"DEBUG: Session {session_id} NOT FOUND in active sessions.")
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    state.answers.append(answer)
    print(f"DEBUG: Current answer count: {len(state.answers)}")
    
    if len(state.answers) < 7:
        try:
            graph = get_graph()
            result = await graph.run(state.model_dump())
            new_state = AdGenState(**result)
            sessions[session_id] = new_state
            
            # CRITICAL FIX: Pick the CURRENT question based on answer count
            # questions[0] = name
            # questions[1..5] = followups
            # questions[6] = image
            next_q = "Thinking..."
            if len(new_state.questions) > len(new_state.answers):
                next_q = new_state.questions[len(new_state.answers)]
            
            return {
                "status": "in_progress",
                "next_question": next_q,
                "progress": f"{len(new_state.answers) + 1}/7"
            }
        except Exception as e:
            error_msg = str(e)
            state.answers.pop()
            if "429" in error_msg or "quota" in error_msg.lower():
                raise HTTPException(status_code=429, detail="AI API Rate Limit Exceeded. Please wait a moment and try again.")
            raise HTTPException(status_code=500, detail=f"Generation failed: {error_msg}")
    else:
        try:
            # 1. Get brief extraction synchronously
            graph = get_graph()
            print(f"DEBUG: Extracting brief for {session_id}...")
            brief_data = await graph.brief_collector._extract_brief(state)
            new_state_dict = state.model_dump()
            new_state_dict.update(brief_data)
            
            # 2. PROACTIVE FIX: Generate themes and copy SYNC so Visuals page works instantly
            # Update state dict as we go to preserve partial results in case of later failures
            temp_state = AdGenState(**new_state_dict)
            
            print(f"DEBUG: Generating themes synchronously for {session_id}...")
            try:
                theme_results = await graph.theme_agent.run(temp_state)
                new_state_dict.update(theme_results)
            except Exception as theme_err:
                print(f"Sync Theme Gen Error: {theme_err}")

            print(f"DEBUG: Generating copy synchronously for {session_id}...")
            try:
                # copy_agent might generate better ones than interactive_agent fallback
                copy_results = await graph.copy_generator.run(AdGenState(**new_state_dict))
                new_state_dict.update(copy_results)
            except Exception as copy_err:
                print(f"Sync Copy Gen Error: {copy_err}")
            
            # Ensure the image URL from the 6th answer is preserved if provided
            last_ans = state.answers[-1] if state.answers else ""
            if any(x in last_ans.lower() for x in ["http", "/", ".png", ".jpg", ".jpeg"]):
                if "skip" not in last_ans.lower():
                    new_state_dict["user_image_url"] = last_ans.strip()

            new_state = AdGenState(**new_state_dict)
            new_state.interaction_complete = True # Explicitly ensure this
            sessions[session_id] = new_state
            print(f"DEBUG: Synchronous generation complete for {session_id}. Headlines: {len(new_state.copy_objects)}")
        except Exception as e:
            error_msg = str(e)
            print(f"Critical Sync Gen Error: {error_msg}")
            # Ensure interaction_complete so user isn't stuck in questionnaire
            new_state_dict = state.model_dump()
            new_state_dict["interaction_complete"] = True
            # Try to at least give some headlines if they aren't there
            if not new_state_dict.get("copy_objects"):
                 from agents.interactive_agent import BriefCollector
                 collector = BriefCollector()
                 new_state_dict["copy_objects"] = collector._manual_brief_extraction(state).get("copy_objects", [])
            
            new_state = AdGenState(**new_state_dict)
            sessions[session_id] = new_state
        
        if new_state.error:
            return {"status": "error", "message": new_state.error}
            
        # Start the slow Image and Variant processing in background
        background_tasks.add_task(run_generation_background, session_id, new_state.model_dump())
        
        return {
            "status": "complete",
            "message": "Interaction complete. 2,500 variations are being generated.",
            "brief": {
                "product": new_state.product_name,
                "audience": new_state.target_audience
            }
        }

from fastapi.responses import FileResponse, JSONResponse
import uuid

@router.get("/preview-render")
async def preview_render(session_id: str, theme_name: str, ratio_id: str, heading: str, content: str, catchy_line: str):
    """Returns the actual PNG image for live preview in the Dashboard UI."""
    try:
        if session_id not in sessions:
            # For previews, we can be more lenient or return a placeholder if session is lost
            raise HTTPException(status_code=404, detail="Session expired")
        
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
        
        # Template map
        template_map = {
            "cyber neon": "cyber_neon.html",
            "midnight matrix": "cyber_neon.html",
            "glassmorphism 2.0": "glassmorphism_vibe.html",
            "glassmorphism": "glassmorphism_vibe.html",
            "retro pop": "retro_pop.html",
            "retro kinetic": "retro_pop.html",
            "minimalist white": "minimal_premium.html",
            "sleek minimalism": "minimal_premium.html",
            "elegant gold": "editorial_magazine.html",
            "golden editorial": "editorial_magazine.html",
            "luxury dark": "editorial_magazine.html",
            "velvet noir": "editorial_magazine.html",
            "swiss modern": "bento_grid.html",
            "bento grid pro": "bento_grid.html",
            "liquid aurora": "liquid_aurora.html",
            "brutal raw": "brutalist_raw.html",
            "neo-brutalist": "brutalist_raw.html",
            "youthful mint": "urban_collage.html",
            "professional blue": "poster_template.html",
            "viral tweet": "social_mimic.html",
            "imessage thread": "social_mimic.html",
            "app notification": "social_mimic.html",
            "sleek notification": "social_mimic.html"
        }
        selected_template = template_map.get(theme.get('name', '').lower(), "poster_template.html")

        variation = {
            "id": f"preview_{uuid.uuid4().hex[:8]}",
            "template": selected_template,
            "heading": heading,
            "content": content,
            "catchy_line": catchy_line,
            "cta": "SHOP NOW",
            "theme": theme,
            "ratio": ratio,
            "product_image": state.processed_image_path or state.user_image_url,
            "product_name": state.product_name or "AdMorph"
        }
        
        from services.renderer import Renderer
        renderer = Renderer()
        file_path = await renderer.render_variation(variation)
        
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="image/png")
        raise HTTPException(status_code=404, detail="Render failed")
            
    except Exception as e:
        print(f"PREVIEW RENDER ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/render-single")
async def render_single(session_id: str, theme_name: str, ratio_id: str, heading: str, content: str, catchy_line: str, bp: str = None, bs: str = None, bt: str = None):
    """Renders a specific dynamic variation to PNG for manual export."""
    try:
        print(f"DEBUG: EXPORT REQUEST - Session: {session_id}, Theme: {theme_name}, Ratio: {ratio_id}")
        if session_id not in sessions:
            print(f"ERROR: Session {session_id} not found.")
            raise HTTPException(status_code=404, detail="Session expired due to backend reload. Please refresh and restart.")
        
        state = sessions[session_id]
        
        # Find ratio info
        ratios = [
            {'id': '1x1', 'width': 1080, 'height': 1080},
            {'id': '9x16', 'width': 1080, 'height': 1920},
            {'id': '4x5', 'width': 1080, 'height': 1350},
            {'id': '16x9', 'width': 1920, 'height': 1080},
            {'id': '1.91x1', 'width': 1200, 'height': 628}
        ]
        ratio_match = next((r for r in ratios if r['id'].lower() == ratio_id.lower()), None)
        if not ratio_match:
            print(f"DEBUG: Ratio {ratio_id} NOT FOUND, using fallback 1x1")
            ratio = ratios[0]
        else:
            ratio = ratio_match
            print(f"DEBUG: Matched Ratio: {ratio['id']} ({ratio['width']}x{ratio['height']})")
        
        # Find theme info. themes is a list of dicts.
        if not state.themes:
             print("DEBUG: NO THEMES in state!")
             raise HTTPException(status_code=400, detail="No themes generated yet.")
             
        # Robust case-insensitive search
        target_name = theme_name.strip().lower()
        theme_match = next((t for t in state.themes if t.get('name', '').strip().lower() == target_name), None)
        
        if not theme_match:
            print(f"DEBUG: Theme '{theme_name}' NOT FOUND in { [t.get('name') for t in state.themes] }. Using fallback.")
            theme = state.themes[0]
        else:
            theme = theme_match
            print(f"DEBUG: Matched Theme: {theme['name']}")
        
        # Dynamic Template Mapping based on theme name
        template_map = {
            "cyber neon": "cyber_neon.html",
            "midnight matrix": "cyber_neon.html",
            "glassmorphism 2.0": "glassmorphism_vibe.html",
            "glassmorphism": "glassmorphism_vibe.html",
            "retro pop": "retro_pop.html",
            "retro kinetic": "retro_pop.html",
            "minimalist white": "minimal_premium.html",
            "sleek minimalism": "minimal_premium.html",
            "elegant gold": "elegant_serif.html",
            "golden editorial": "elegant_serif.html",
            "luxury dark": "elegant_serif.html",
            "swiss modern": "swiss_grid.html",
            "bento grid pro": "swiss_grid.html",
            "brutal raw": "brutalist_raw.html",
            "neo-brutalist": "brutalist_raw.html",
            "youthful mint": "urban_collage.html",
            "professional blue": "poster_template.html",
            "viral tweet": "social_mimic.html",
            "imessage thread": "social_mimic.html",
            "app notification": "social_mimic.html",
            "sleek notification": "social_mimic.html"
        }
        selected_template = template_map.get(theme.get('name', '').lower(), "poster_template.html")
        print(f"DEBUG: Using Template: {selected_template}")
        variation = {
            "id": f"export_{uuid.uuid4().hex[:8]}",
            "template": selected_template,
            "heading": heading,
            "content": content,
            "catchy_line": catchy_line,
            "cta": "SHOP NOW",
            "theme": theme,
            "ratio": ratio,
            "product_image": state.processed_image_path or state.user_image_url,
            "product_name": state.product_name or "AdMorph",
            "brand_primary": bp,
            "brand_secondary": bs,
            "brand_accent": bt
        }
        
        from services.renderer import Renderer
        renderer = Renderer()
        file_path = await renderer.render_variation(variation)
        
        filename = os.path.basename(file_path)
        print(f"DEBUG: EXPORT SUCCESS: {filename}")
        return {"url": f"{settings.api_base_url}/generated/{filename}"}
    except Exception as e:
        import traceback
        from services.renderer import Renderer
        print(f"CRITICAL EXPORT ERROR for session {session_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-pack")
async def export_pack(session_id: str, theme_name: str, heading: str, content: str, catchy_line: str, bp: str = None, bs: str = None, bt: str = None):
    """Renders all standard ratios for a theme/headline as a single ZIP archive."""
    try:
        import zipfile
        from services.renderer import Renderer
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session expired")
        
        state = sessions[session_id]
        
        # 1. Resolve theme
        target_name = theme_name.strip().lower()
        if not state.themes:
             raise HTTPException(status_code=400, detail="No themes available for this session.")
        theme = next((t for t in state.themes if t.get('name', '').strip().lower() == target_name), state.themes[0])
        
        # 2. Template mapping (re-use logic from single render)
        template_map = {
            "cyber neon": "cyber_neon.html",
            "midnight matrix": "cyber_neon.html",
            "glassmorphism 2.0": "glassmorphism_vibe.html",
            "glassmorphism": "glassmorphism_vibe.html",
            "retro pop": "retro_pop.html",
            "retro kinetic": "retro_pop.html",
            "minimalist white": "minimal_premium.html",
            "sleek minimalism": "minimal_premium.html",
            "elegant gold": "editorial_magazine.html",
            "golden editorial": "editorial_magazine.html",
            "luxury dark": "editorial_magazine.html",
            "velvet noir": "editorial_magazine.html",
            "swiss modern": "bento_grid.html",
            "bento grid pro": "bento_grid.html",
            "liquid aurora": "liquid_aurora.html",
            "brutal raw": "brutalist_raw.html",
            "neo-brutalist": "brutalist_raw.html",
            "youthful mint": "urban_collage.html",
            "professional blue": "poster_template.html",
            "viral tweet": "social_mimic.html",
            "imessage thread": "social_mimic.html",
            "app notification": "social_mimic.html",
            "sleek notification": "social_mimic.html"
        }
        selected_template = template_map.get(theme.get('name', '').lower(), "poster_template.html")
        
        # 3. Standard ratios
        ratios = [
            {'id': '1x1', 'name': 'Square', 'width': 1080, 'height': 1080},
            {'id': '9x16', 'name': 'Story', 'width': 1080, 'height': 1920},
            {'id': '4x5', 'name': 'Portrait', 'width': 1080, 'height': 1350},
            {'id': '16x9', 'name': 'Landscape', 'width': 1920, 'height': 1080},
            {'id': '1.91x1', 'name': 'Link_Preview', 'width': 1200, 'height': 628}
        ]
        
        # 4. Prepare variations
        variations = []
        for r in ratios:
            variations.append({
                "id": f"pack_{r['id']}_{uuid.uuid4().hex[:4]}",
                "template": selected_template,
                "heading": heading,
                "content": content,
                "catchy_line": catchy_line,
                "cta": "SHOP NOW",
                "theme": theme,
                "ratio": r,
                "product_image": state.processed_image_path or state.user_image_url,
                "product_name": state.product_name or "AdMorph",
                "brand_primary": bp,
                "brand_secondary": bs,
                "brand_accent": bt
            })
            
        # 5. Batch Render
        renderer = Renderer()
        file_paths = await renderer.render_batch(variations)
        
        # 6. Create ZIP
        zip_filename = f"AdMorph_Pack_{uuid.uuid4().hex[:8]}.zip"
        zip_path = os.path.join(settings.output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path, r in zip(file_paths, ratios):
                # Using short clean names inside zip
                arcname = f"{r['name']}_{r['width']}x{r['height']}.png"
                zipf.write(path, arcname)
                
        return {"url": f"{settings.api_base_url}/generated/{zip_filename}"}
        
    except Exception as e:
        import traceback
        print(f"CRITICAL PACK EXPORT ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcreate-preview")
async def transcreate_preview(session_id: str, heading: str, content: str, catchy_line: str, target_lang: str):
    """Real-time transcreation for a single preview request."""
    try:
        from agents.localization_agent import localization_agent
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session expired")
        
        state = sessions[session_id]
        copy_obj = {"heading": heading, "content": content, "catchy_line": catchy_line}
        
        # Transcreate using the specialized agent
        transcreated = await localization_agent.transcreate(copy_obj, target_lang, state)
        return transcreated
    except Exception as e:
        print(f"TRANS_PREVIEW ERROR: {e}")
        return {"heading": heading, "content": content, "catchy_line": catchy_line, "error": str(e)}

@router.get("/export-global")
async def export_global(session_id: str, theme_name: str, heading: str, content: str, catchy_line: str, bp: str = None, bs: str = None, bt: str = None):
    """
    Renders the current ad for a set of major world languages.
    Creates a ZIP with sub-folders for each language.
    """
    try:
        import zipfile
        from services.renderer import Renderer
        from agents.localization_agent import localization_agent
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session expired")
        
        state = sessions[session_id]
        
        # 1. Resolve Theme
        target_name = theme_name.strip().lower()
        if not state.themes:
             raise HTTPException(status_code=400, detail="No themes available for this session.")
        theme = next((t for t in state.themes if t.get('name', '').strip().lower() == target_name), state.themes[0])
        
        template_map = {
            "cyber neon": "cyber_neon.html",
            "midnight matrix": "cyber_neon.html",
            "glassmorphism 2.0": "glassmorphism_vibe.html",
            "glassmorphism": "glassmorphism_vibe.html",
            "retro pop": "retro_pop.html",
            "retro kinetic": "retro_pop.html",
            "minimalist white": "minimal_premium.html",
            "sleek minimalism": "minimal_premium.html",
            "elegant gold": "editorial_magazine.html",
            "golden editorial": "editorial_magazine.html",
            "luxury dark": "editorial_magazine.html",
            "velvet noir": "editorial_magazine.html",
            "swiss modern": "bento_grid.html",
            "bento grid pro": "bento_grid.html",
            "liquid aurora": "liquid_aurora.html",
            "brutal raw": "brutalist_raw.html",
            "neo-brutalist": "brutalist_raw.html",
            "youthful mint": "urban_collage.html",
            "professional blue": "poster_template.html",
            "viral tweet": "social_mimic.html",
            "imessage thread": "social_mimic.html",
            "app notification": "social_mimic.html",
            "sleek notification": "social_mimic.html"
        }
        selected_template = template_map.get(theme.get('name', '').lower(), "poster_template.html")
        
        # 2. Define Language Set
        languages = ["Spanish", "French", "German", "Japanese", "Portuguese", "Korean", "Hindi", "Arabic"]
        
        # 3. Transcreate Copy (In Parallel)
        original_copy = {"heading": heading, "content": content, "catchy_line": catchy_line}
        
        print(f"DEBUG: Starting Global Transcreation for {len(languages)} languages...")
        transcreation_tasks = [localization_agent.transcreate(original_copy, lang, state) for lang in languages]
        localized_copies = await asyncio.gather(*transcreation_tasks)
        
        # Mapping lang -> transcreated_obj
        lang_copy_map = dict(zip(languages, localized_copies))
        
        # 4. Standard ratios
        ratios = [
            {'id': '1x1', 'name': 'Square', 'width': 1080, 'height': 1080},
            {'id': '9x16', 'name': 'Story', 'width': 1080, 'height': 1920},
            {'id': '4x5', 'name': 'Portrait', 'width': 1080, 'height': 1350},
            {'id': '16x9', 'name': 'Landscape', 'width': 1920, 'height': 1080},
            {'id': '1.91x1', 'name': 'Link_Preview', 'width': 1200, 'height': 628}
        ]
        
        # 5. Prepare Mass Rendering Batch (5 ratios * X languages)
        variations = []
        variation_metadata = [] # To map results back to folders
        
        for lang in languages:
            copy = lang_copy_map[lang]
            for r in ratios:
                variations.append({
                    "id": f"global_{lang}_{r['id']}_{uuid.uuid4().hex[:4]}",
                    "template": selected_template,
                    "heading": copy.get("heading", ""),
                    "content": copy.get("content", ""),
                    "catchy_line": copy.get("catchy_line", ""),
                    "cta": "SHOP NOW", # Could also translate this, but for now stay consistent
                    "theme": theme,
                    "ratio": r,
                    "product_image": state.processed_image_path or state.user_image_url,
                    "product_name": state.product_name or "AdMorph",
                    "brand_primary": bp,
                    "brand_secondary": bs,
                    "brand_accent": bt
                })
                variation_metadata.append({"lang": lang, "ratio_name": r['name']})
        
        # 6. Massive Batch Render
        # Renderer's Semaphore(2) will prevent crashing the machine
        print(f"DEBUG: Starting massive Global Render ({len(variations)} variations)...")
        renderer = Renderer()
        file_paths = await renderer.render_batch(variations)
        
        # 7. Create Structured ZIP
        zip_filename = f"AdMorph_Global_Pack_{uuid.uuid4().hex[:8]}.zip"
        zip_path = os.path.join(settings.output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path, meta in zip(file_paths, variation_metadata):
                # Organize by language folder inside zip
                arcname = f"{meta['lang']}/{meta['ratio_name']}.png"
                zipf.write(path, arcname)
        
        print(f"DEBUG: Global Pack Created: {zip_filename}")
        return {"url": f"{settings.api_base_url}/generated/{zip_filename}"}

    except Exception as e:
        import traceback
        print(f"CRITICAL GLOBAL PACK ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Handles local image uploads."""
    os.makedirs("assets/uploads", exist_ok=True)
    file_path = f"assets/uploads/{uuid.uuid4().hex}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_path": os.path.abspath(file_path)}

@router.get("/status/{session_id}")
async def get_status(session_id: str):
    """Checks the status of the generation."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    
    # Extract just the headings for the frontend status view to prevent breakage
    headings = [obj.get("heading", "") for obj in state.copy_objects]
    
    return {
        "interaction_complete": state.interaction_complete,
        "variants_count": len(state.variations),
        "headlines_count": len(headings),
        "themes_count": len(state.themes),
        "headlines": headings,
        "copy_objects": state.copy_objects,
        "themes": state.themes,
        "product_image": state.processed_image_path,
        "product_name": state.product_name
    }

@router.post("/dev-start")
async def dev_start(background_tasks: BackgroundTasks):
    """Starts a Dev Mode session, bypassing LLM questionnaire and injecting mock MNC data directly."""
    print("DEBUG: dev_start RECEIVED (ULTRA FAST MODE)")
    session_id = uuid.uuid4().hex
    
    try:
        # Array of high-quality copy objects for Dev Mode (MNC level)
        dev_copy = [
            {"heading": "Silence the World. Hear the Future.", "content": "The Aura Pro noise-cancelling headphones mathematically delete background noise, leaving only pure, high-fidelity sound.", "catchy_line": "Pure sound. Zero pressure."},
            {"heading": "Your Focus, Reimagined.", "content": "Designed for remote professionals who need absolute silence. Aura Pro creates a deep focus zone anywhere.", "catchy_line": "The ultimate work companion."},
            {"heading": "Master Your Sound Environment.", "content": "With 45 hours of battery life and dual-chip ANC, Aura Pro is the new benchmark for wireless audio.", "catchy_line": "Luxury you can hear."},
            {"heading": "True Minimalism. Absolute Clarity.", "content": "Experience the industry's first dual-chip ANC that delete frequencies without pressure. Meet Aura Pro.", "catchy_line": "Audio engineering at its finest."},
            {"heading": "Elevate Your Audio Experience.", "content": "From deep bass to crisp highs, every note is delivered with surgical precision. Try Aura Pro today.", "catchy_line": "Hear what you've been missing."},
            {"heading": "Engineered for Excellence.", "content": "Aerospace-grade materials meet world-class audio engineering. This is the new standard.", "catchy_line": "Built to last."},
            {"heading": "A Symphony of Silence.", "content": "Escape the chaos of the city. Aura Pro delivers a sanctuary of sound wherever you go.", "catchy_line": "Find your zen."},
            {"heading": "The Professional Choice.", "content": "Crystal clear calls and absolute focus. The only headphones you'll ever need for work.", "catchy_line": "Work better."},
            {"heading": "Sound That Moves You.", "content": "Experience music exactly as the artist intended. Rich, immersive, and breathtakingly clear.", "catchy_line": "Live the music."},
            {"heading": "Unrivaled Comfort.", "content": "Memory foam ear cushions and a lightweight frame. Wear them all day without fatigue.", "catchy_line": "Feel the cloud."},
            {"heading": "Wireless Liberty.", "content": "Seamless connectivity across all your devices. Switch from your phone to laptop instantly.", "catchy_line": "Stay connected."},
            {"heading": "The Power of Sound.", "content": "Unleash the full potential of your favorite tracks with the specialized drivers in Aura Pro.", "catchy_line": "Power your ears."},
            {"heading": "Design That Inspires.", "content": "Minimalist aesthetics that complement your style. Audio technology has never looked this good.", "catchy_line": "A work of art."},
            {"heading": "Hear Every Detail.", "content": "From the softest whisper to the deepest bass, catch everything you've been missing.", "catchy_line": "Precision audio."},
            {"heading": "The Gift of Silence.", "content": "The perfect companion for travel, work, or relaxation. Aura Pro is the ultimate gift.", "catchy_line": "Quiet the world."},
            {"heading": "Smarter Noise Control.", "content": "Adaptive ANC that reacts to your environment in real-time. Smart sound for a smart world.", "catchy_line": "Intelligent audio."},
            {"heading": "A Benchmark for Audio.", "content": "Setting the bar for wireless noise-cancelling headphones. Experience the Aura Pro difference.", "catchy_line": "The gold standard."},
            {"heading": "Unplug and Unwind.", "content": "Leave the wires behind. Enjoy total freedom with industry-leading battery life.", "catchy_line": "Infinite sound."},
            {"heading": "The Sound of Success.", "content": "Used by the world's most productive professionals to achieve absolute clarity.", "catchy_line": "Achieve more."},
            {"heading": "Ready for Anything.", "content": "Durable, foldable, and powerful. Aura Pro is ready to accompany you on any journey.", "catchy_line": "Your daily driver."}
        ]

        # Deep MNC Brief
        dev_data = {
            "product_name": "Aura Pro Noise-Cancelling Headphones",
            "product_description": "Next-gen audio with dual-chip active noise cancellation and premium aerospace-grade materials.",
            "target_audience": "Audiophiles and Remote Professionals",
            "advertising_goal": "Maximize premium sales and brand authority.",
            "brand_tone": "Luxurious, minimal, and authoritative.",
            "interaction_complete": True,
            "funnel_stage": "Bottom of Funnel (Direct Conversion)",
            "pain_points": "Distracted by background noise at work or home, leading to lost focus and stress.",
            "usp": "The industry's first dual-chip active noise cancellation that mathematically deletes background frequencies without pressure.",
            "offer": "Save $50 Today Only + Free Premium Carrying Case.",
            "brand_guidelines": "Never use cheap urgency words like 'HURRY' or 'GRAB'. maintain Apple-level minimalism.",
            "copy_objects": dev_copy,
            "ctas": ["Shop Now", "Learn More", "Order Aura Pro", "Unlock Silence", "Upgrade Now", "Buy Now", "Get Started", "Explore Aura", "Join the Elite", "Save Today"],
            "themes": [
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
             ],
            "image_descriptions": [
                "Hero shot of premium headphones in a minimal studio",
                "Close up of CNC textured metal finish",
                "Professional using headphones in a modern glass office",
                "Abstract sound wave visualization in gold",
                "Lifestyle shot of headphones on a mahogany desk"
            ]
        }
        
        print("DEBUG: dev_start - Creating dev_state object...")
        dev_state = get_state_obj(dev_data)
        
        # Register Session
        sessions[session_id] = dev_state
        print(f"DEBUG: dev_start - Session {session_id} registered instantly.")
        
        # Re-enable background tasks to process images (Pixabay) and expand variants
        background_tasks.add_task(run_dev_background, session_id, dev_state.model_dump())
        
        return {
            "session_id": session_id,
            "status": "dev_mode_ready",
            "message": "Dev Mode started instantly. Engine is warming up in background.",
            "next_question": None
        }
    except Exception as e:
        import traceback
        print(f"ERROR: dev_start FAILED: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Dev Mode initialization failed: {str(e)}")
