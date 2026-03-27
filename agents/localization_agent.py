import json
import asyncio
from .llm_factory import get_llm
from .state import AdGenState
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
    print("WARNING: deep_translator not installed. Translation will be unavailable.")

class LocalizationGenerator:
    def __init__(self):
        self.llm = get_llm()
        self.lang_map = {
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "japanese": "ja",
            "portuguese": "pt",
            "korean": "ko",
            "hindi": "hi",
            "arabic": "ar",
            "english": "en"
        }

    async def translate_quick(self, text: str, target_language: str) -> str:
        """Uses a standard translation API for instant results."""
        if not HAS_TRANSLATOR:
            return text
        try:
            target_code = self.lang_map.get(target_language.lower(), "en")
            if target_code == "en": return text
            
            # Run in executor to avoid blocking the async loop
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                None, 
                lambda: GoogleTranslator(source='auto', target=target_code).translate(text)
            )
            return translated
        except Exception as e:
            print(f"Quick Translation Error: {e}")
            return text

    async def transcreate(self, copy_obj: dict, target_language: str, state: AdGenState) -> dict:
        """Adapts ad copy. Now uses Fast Translation primarily for speed."""
        if not target_language or target_language.lower() == 'english':
            return copy_obj

        # If it's a quick preview, use the fast API
        # In a real app, we might toggle this based on a 'mode' parameter
        h = await self.translate_quick(copy_obj.get('heading', ''), target_language)
        c = await self.translate_quick(copy_obj.get('content', ''), target_language)
        cl = await self.translate_quick(copy_obj.get('catchy_line', ''), target_language)
        
        return {
            "heading": h,
            "content": c,
            "catchy_line": cl
        }

    async def transcreate_ai_premium(self, copy_obj: dict, target_language: str, state: AdGenState) -> dict:
        """The original LLM-based transcreation logic for high-quality cultural adaptation."""
            
        prompt = [
            SystemMessage(content=(
                f"You are a Global Advertising Executive specializing in Transcreation (not just translation). "
                f"Your goal is to adapt the following English ad copy into {target_language} while preserving: "
                "1. Brand Tone & Authority. "
                "2. Emotional Resonance (cultural nuances). "
                "3. Punchiness and Wordplay (if applicable, adapt to target culture's idioms). "
                "4. Character limits: Keep headlines and catchy lines short and impactful for mobile ads. "
                "\nReturn valid JSON with 'heading', 'content', and 'catchy_line'."
            )),
            HumanMessage(content=(
                f"Product: {state.product_name}\n"
                f"Brand Tone: {state.brand_tone}\n"
                f"Target Audience: {state.target_audience}\n"
                f"Target Language: {target_language}\n"
                f"Original Copy:\n"
                f"Headline: {copy_obj.get('heading')}\n"
                f"Content: {copy_obj.get('content')}\n"
                f"Catchy Line: {copy_obj.get('catchy_line')}\n"
            ))
        ]

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.replace("```json", "").replace("```", "").strip()
            # Basic cleanup in case of extra text
            if "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            return json.loads(content)
        except Exception as e:
            print(f"Localization Error ({target_language}): {e}")
            # Fallback to simple label if LLM fails
            return {
                "heading": f"[{target_language}] " + copy_obj.get('heading', ''),
                "content": copy_obj.get('content', ''),
                "catchy_line": copy_obj.get('catchy_line', '')
            }

    async def transcreate_batch(self, copy_objects: list, languages: list, state: AdGenState):
        """Processes a list of copy objects for multiple languages."""
        results = {} # {language: [copy_objects]}
        
        # To avoid blowing up LLM quota, we only transcreate the ACTIVE variant or a small selection 
        # for the "Global Pack". Let's assume the user wants the CURRENT selected variants localized.
        
        tasks = []
        for lang in languages:
            for obj in copy_objects:
                tasks.append(self.transcreate(obj, lang, state))
        
        transcreated = await asyncio.gather(*tasks)
        
        # Re-group by language
        idx = 0
        for lang in languages:
            results[lang] = []
            for _ in range(len(copy_objects)):
                results[lang].append(transcreated[idx])
                idx += 1
        return results

localization_agent = LocalizationGenerator()
