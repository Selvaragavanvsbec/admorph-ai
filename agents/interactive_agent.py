from langchain_core.messages import HumanMessage, SystemMessage
import json
from .llm_factory import get_llm
from .state import AdGenState
from config import settings
import random

class BriefCollector:
    def __init__(self):
        self.llm = get_llm()

    async def run(self, state: AdGenState) -> dict:
        """Main entry point for the agent."""
        # Initial greeting and first question
        if not state.questions:
            return {
                "questions": ["What is the name of the product or service we are advertising?"],
                "answers": [],
                "interaction_complete": False
            }

        # Generate follow-up questions after the first answer
        if len(state.questions) == 1 and state.answers:
            product_name = state.answers[0]
            prompt = [
                SystemMessage(content=(
                    "You are an expert Ad Strategist for a creative agency. Generate exactly 5 profound, strategic follow-up questions to understand the product deeply. "
                    "Focus strictly on: 1. Core Unique Value Proposition (UVP), 2. Emotional Resonance/Feeling, 3. Target Audience Pain Points, 4. Primary Offer/CTA, 5. Competitor Differentiation. "
                    "Do NOT ask about image URLs yet. Return EXACTLY 5 questions."
                )),
                HumanMessage(content=f"Product: {product_name}\n\nReturn EXACTLY 5 questions in a flat JSON list of strings.")
            ]
            
            try:
                response = await self.llm.ainvoke(prompt)
                content = response.content.replace("```json", "").replace("```", "").strip()
                # Find the first [ and last ] to handle potential chatty LLM
                start = content.find("[")
                end = content.rfind("]") + 1
                if start != -1 and end != 0:
                    content = content[start:end]

                followups = json.loads(content)
                if not isinstance(followups, list) or len(followups) == 0:
                    raise ValueError("LLM did not return a list")
                
                # Truncate or pad to ensure exactly 5
                followups = followups[:5]
                while len(followups) < 5:
                    followups.append("Can you tell me more about your brand's unique style?")
            except Exception as e:
                print(f"Strategy Phase API Error (using Engine fallback): {e}")
                followups = self._generate_dynamic_questions(product_name)
            
            # Add the 6th fixed optional question for image
            followups.append("Optional: Upload an image of your product or paste a URL (or type 'skip' to let the AI find one for you).")
            
            return {
                "questions": state.questions + followups,
                "interaction_complete": False
            }

        # Check if we've reached the end (7 questions total: 1 name + 5 dynamic + 1 image)
        if len(state.answers) >= 7:
            # Capture optional image URL if provided in the last answer
            last_ans = state.answers[-1].lower().strip()
            image_url = None
            if any(x in last_ans for x in ["http", "https", "/", ".com", ".png", ".jpg"]):
                if "skip" not in last_ans:
                    image_url = state.answers[-1].strip()
            
            extracted_brief = await self._extract_brief(state)
            extracted_brief["user_image_url"] = image_url
            return extracted_brief

        # Default: Keep everything flowing
        return {
             "questions": state.questions,
             "interaction_complete": False
        }

    def _generate_dynamic_questions(self, product: str) -> list:
        """Dynamic local engine for strategy questions (Zero-AI fallback)."""
        pool = [
            f"What is the single biggest pain point {product} solves for its target audience?",
            f"If {product} were a feeling, what emotion should the customer experience?",
            f"What is the Core Unique Value Proposition (UVP) that makes {product} different?",
            f"What specific action or offer (e.g., '15% Off', 'Free Trial') should we highlight?",
            f"Why would a customer choose {product} over your biggest competitor?",
            f"What is the primary narrative or story we want to tell about {product}?",
            f"What specific transformation does {product} provide for the user?",
            f"If you had to summarize {product}'s brand identity in three words, what are they?",
            f"What is the most common objection people have before buying {product}, and how do we overcome it?",
            f"What is the ultimate success metric or goal for advertising {product} right now?"
        ]
        return random.sample(pool, 5)

    async def _extract_brief(self, state: AdGenState) -> dict:
        """Uses the LLM to extract a structured brief, headlines, and CTAs."""
        interaction_log = {q: a for q, a in zip(state.questions, state.answers)}
        
        prompt = [
            SystemMessage(content=(
                "You are an expert Advertising Strategist and Copywriter. Extract a structured brief from the conversation. "
                "CRITICAL: You must hunt for and summarize 5 advanced strategic parameters: "
                "1. 'funnel_stage' (e.g., Top/Awareness, Middle/Consideration, Bottom/Conversion) "
                "2. 'pain_points' (What psychological frustration is the user escaping?) "
                "3. 'usp' (What is the Unique Selling Proposition or competitor difference?) "
                "4. 'offer' (What is the core offer mechanics, e.g., 20% off, Free Trial, risk reversal?) "
                "5. 'brand_guidelines' (Tone constraints or negative keywords). "
                "Also, based on this information, generate EXACTLY 50 distinct and high-converting ad copy variations. "
                "Each variation must be an object containing: 'heading' (the main headline), 'content' (the body text expanding on the heading), and 'catchy_line' (a short, memorable hook). "
                "Also generate 5 Call-To-Action (CTA) phrases."
            )),
            HumanMessage(content=(
                f"Full Interaction Data (JSON): {json.dumps(interaction_log)}\n\n"
                "Return valid JSON with: product_name, product_description, target_audience, advertising_goal, brand_tone, "
                "funnel_stage, pain_points, usp, offer, brand_guidelines, "
                "image_descriptions (list of 5 visual themes), copy_objects (list of 50 objects containing 'heading', 'content', 'catchy_line'), and ctas (list of 5 strings)."
            ))
        ]
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            for key in ["product_name", "product_description", "target_audience", "advertising_goal", "brand_tone"]:
                if key in data and not isinstance(data[key], str):
                    data[key] = json.dumps(data[key])
                    
            data["interaction_complete"] = True
            return data
        except Exception as e:
            print(f"Brief Extraction API Error (using manual fallback): {e}")
            # Ensure we return a structured object even in fallback
            return self._manual_brief_extraction(state)

    def _manual_brief_extraction(self, state: AdGenState) -> dict:
        """Fallback method for brief extraction. Returns high-quality static copy."""
        ans = state.answers + [""] * (7 - len(state.answers))
        product = ans[0] or "Your Product"
        
        # Start with some premium-feeling objects
        fallback_objects = [
            {"heading": f"The Evolution of {product}", "content": f"Discover how {product} is redefining the industry standards for those who demand ultimate precision.", "catchy_line": "The future is here."},
            {"heading": f"Master Your Productivity", "content": f"With {product}, complexity becomes clarity. Transform your workflow today with our surgical-grade tools.", "catchy_line": "Zero compromise."},
            {"heading": f"Unleash {product}", "content": f"Built for professionals, designed for everyone. Experience the raw power of {product}.", "catchy_line": "Level up instantly."},
            {"heading": "Pure Minimalism. Total Power.", "content": f"Meet the new benchmark for excellence. {product} delivers everything you need and nothing you don't.", "catchy_line": "Less is more."},
            {"heading": "The Professional's Choice", "content": f"Join the global movement toward smarter operations with the all-new {product} ecosystem.", "catchy_line": "Lead the pack."},
        ]
        
        # Padded base objects for variety
        base_objects = [
            {"heading": f"Experience the New {product}", "content": f"Join thousands of others and discover why {product} is the industry leader today.", "catchy_line": "Do not get left behind."},
            {"heading": f"The Ultimate {product}", "content": f"Stop compromising. Get exactly what you need with the precision of {product}.", "catchy_line": "Perfection achieved."},
            {"heading": f"Upgrade to {product}", "content": f"Designed for those who demand excellence in every aspect of their work. Try {product}.", "catchy_line": "Level up your life."},
            {"heading": f"Precision Engineered: {product}", "content": "Every detail matters. We don't just build products; we craft experiences.", "catchy_line": "Excellence by design."},
            {"heading": f"The Smart Way to {product}", "content": "Unlock new possibilities with our intelligent features and intuitive interface.", "catchy_line": "Intelligent innovation."},
        ]
        
        # Combine and pad to exactly 50
        while len(fallback_objects) < 50:
             title_idx = len(fallback_objects) % len(base_objects)
             obj = base_objects[title_idx].copy()
             fallback_objects.append(obj)

        return {
            "product_name": product,
            "product_description": f"Ad campaign for {product} targeting {ans[1]} with a goal of {ans[2]}.",
            "target_audience": ans[1] or "General Audience",
            "advertising_goal": ans[2] or "Brand Awareness",
            "brand_tone": ans[3] or "Professional",
            
            # Advanced Strategic Context (Fallback Mocks)
            "funnel_stage": "Middle of Funnel (Consideration)",
            "pain_points": "Wasting time on manual tasks, feeling overwhelmed by complex tools.",
            "usp": "The only automated platform that works seamlessly across all devices without setup.",
            "offer": "14-Day Free Trial, No Credit Card Required.",
            "brand_guidelines": "Must be empowering and professional. Never use fear tactics.",

            "image_descriptions": [
                f"Modern high-quality visual for {product} style",
                f"Lifestyle shot for {product}",
                f"Close-up of {product} product",
                f"Artistic representation of {product}",
                f"Vibrant ad for {product}"
            ],
            "copy_objects": fallback_objects,
            "ctas": ["Shop Now", "Learn More", "Get Started", "Try Now", "Buy Now"],
            "interaction_complete": True
        }
