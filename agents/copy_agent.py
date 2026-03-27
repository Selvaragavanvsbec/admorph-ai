from langchain_core.messages import HumanMessage, SystemMessage
import json
from .llm_factory import get_llm
from .state import AdGenState
from config import settings

class CopyGenerator:
    def __init__(self):
        self.llm = get_llm()

    async def run(self, state: AdGenState) -> dict:
        """Generates 100 unique headlines and 5 CTAs (skips if already provided)."""

        # Check if copy objects are already generated during brief extraction
        if state.copy_objects and len(state.copy_objects) >= 100:
            print("--- Skipping Copy Generation (Copy objects already present) ---")
            return {}
            
        prompt = [
            SystemMessage(content=(
                "You are an Elite Copywriter for an MNC Advertising Agency. Generate exactly 100 distinct and high-converting ad copy variations for the given product. "
                "CRITICAL MNC GUIDELINES: "
                "1. Funnel Stage: All copy must align with the provided Funnel Stage (Awareness, Consideration, or Conversion). "
                "2. Pain Points: Agitate the user's specific psychological pain points instead of just listing features. "
                "3. USP: Highlight the Unique Selling Proposition and distinct advantage over competitors. "
                "4. Offer Mechanics: Embed the designated Offer/Mechanic into the CTAs and urgency factors. "
                "5. Brand Safety: strictly follow any negative keywords or constraints provided. "
                "Each variation must be an object containing: 'heading' (the main headline), 'content' (the body text expanding on the heading), and 'catchy_line' (a short, memorable hook or punchline). "
                "Also generate 10 distinct Call-To-Action (CTA) phrases."
            )),
            HumanMessage(content=(
                f"Product: {state.product_name}\nBrief: {state.product_description}\nAudience: {state.target_audience}\nTone: {state.brand_tone}\n"
                f"Funnel Stage: {state.funnel_stage}\nPain Points: {state.pain_points}\nUSP: {state.usp}\nOffer: {state.offer}\nBrand Guidelines: {state.brand_guidelines}\n\n"
                "Return valid JSON with 'copy_objects' (list of 100 objects containing 'heading', 'content', 'catchy_line') and 'ctas' (list of 10 strings)."
            ))
        ]
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            # Ensure it structured correctly
            copy_objs = data.get("copy_objects", [])
            for obj in copy_objs:
                if 'headline' in obj and 'heading' not in obj:
                    obj['heading'] = obj['headline'] # Catch slight LLM variations
            return {"copy_objects": copy_objs, "ctas": data.get("ctas", [])}
        except Exception as e:
            print(f"Copy Generation API Error (using Engine fallback): {e}")
            return self._generate_dynamic_copy(state)

    def _generate_dynamic_copy(self, state: AdGenState) -> dict:
        """Dynamic local engine for ad copy (Zero-AI fallback)."""
        product = state.product_name or "this product"
        audience = state.target_audience or "everyone"
        
        # Array of manually crafted, high-quality copy objects mapped to advanced strategic concepts
        usp = state.usp or "industry-leading performance"
        pain_point = state.pain_points or "feeling overwhelmed"
        offer = state.offer or "Try it today"
        
        fallback_objects = [
            {"heading": f"Escape from {pain_point}", "content": f"Join thousands of others and discover how {product} eliminates {pain_point} forever.", "catchy_line": "Do not get left behind."},
            {"heading": f"The Ultimate {product}", "content": f"Stop compromising. Get exactly what you need with the {usp} of {product}.", "catchy_line": "Perfection achieved."},
            {"heading": f"Upgrade to {product}", "content": f"Designed for those who demand excellence. Claim your {offer} now.", "catchy_line": "Level up your life."},
            {"heading": f"Discover {product}", "content": f"The reviews are in. Everyone agrees that the {usp} makes {product} worth every penny.", "catchy_line": "See what the hype is about."},
            {"heading": f"Master Your Day with {product}", "content": f"Stop {pain_point} immediately. Our new formula ensures maximum results.", "catchy_line": "Take back your time."},
            {"heading": f"Future-Proof With {product}", "content": f"Make the smart choice today and future-proof yourself with {product}.", "catchy_line": "Built for tomorrow."},
            {"heading": f"Invest in {product}. {offer}", "content": f"It's not just a product. It's an investment in your potential. {offer}.", "catchy_line": "Your best move yet."},
            {"heading": f"The {product} Difference", "content": f"Feel the quality from the first day. Built to last to the very end.", "catchy_line": "Quality you can feel."},
            {"heading": f"Never Settle. Choose {product}", "content": f"You deserve the best. Stop settling for less and choose {product}.", "catchy_line": "Demand the best."},
            {"heading": f"Transform with {product}", "content": f"Transform your workflow with the completely redesigned {product} experience.", "catchy_line": "A complete revolution."},
            {"heading": f"Unbeatable {product}", "content": f"Industry-leading performance. Unbeatable reliability.", "catchy_line": "Simply the best."},
            {"heading": f"Take Control: {product}", "content": f"Take control with {product}. The professional's choice.", "catchy_line": "You are the master."},
            {"heading": f"True Innovation: {product}", "content": f"Experience true innovation without the premium price tag. Meet {product}.", "catchy_line": "Genius inside."},
            {"heading": f"Don't Wait on {product}", "content": f"Don't wait. Upgrade your life today and never look back.", "catchy_line": "The time is now."},
            {"heading": f"Stress Less with {product}", "content": f"Reduce stress and increase productivity in seconds with {product}.", "catchy_line": "Breathe easy."},
            {"heading": f"Style Meets {product}", "content": f"Because you shouldn't have to choose between style and substance.", "catchy_line": "Beautifully powerful."},
            {"heading": f"Master IT with {product}", "content": f"Mastering your craft has never been easier. Thanks to {product}.", "catchy_line": "Become an expert."},
            {"heading": f"Functional {product}", "content": f"Where cutting-edge technology meets beautiful, functional design.", "catchy_line": "Form and function."},
            {"heading": f"The Reliable {product}", "content": f"The reliable, powerful solution you've been waiting for is finally here.", "catchy_line": "Always ready."},
            {"heading": f"Hidden Benefits of {product}", "content": f"Discover the hidden benefits of the new {product} system.", "catchy_line": "More than meets the eye."},
            {"heading": f"Flawless {product}", "content": f"Flawlessly constructed to handle whatever you throw at it.", "catchy_line": "Tough as nails."},
            {"heading": f"Next Level: {product}", "content": f"Take your daily routine to the absolute next level.", "catchy_line": "Ascend today."},
            {"heading": f"Precision {product}", "content": f"Precision. Performance. Perfection. The hallmark of {product}.", "catchy_line": "Hit the mark."},
            {"heading": f"See clearly with {product}", "content": f"Change the way you view the world. See it through {product}.", "catchy_line": "A new perspective."},
            {"heading": f"Simple. It's {product}", "content": f"No manuals needed. It just works, beautifully.", "catchy_line": "Plug and play."},
            {"heading": f"Voted #1 {product}", "content": f"Voted the #1 choice by experts and users alike.", "catchy_line": "The people have spoken."},
            {"heading": f"Maximize {product}", "content": f"Maximize your potential without maximizing your effort.", "catchy_line": "Work smarter."},
            {"heading": f"Success with {product}", "content": f"Start your journey to success backed by the power of {product}.", "catchy_line": "Your secret weapon."},
            {"heading": f"Save Time. {product}", "content": f"Do more in less time. That's the promise of {product}.", "catchy_line": "Tick tock."},
            {"heading": f"Welcome Home to {product}", "content": f"Welcome to the future. Make yourself at home with {product}.", "catchy_line": "You belong here."},
            {"heading": f"A Modern {product}", "content": f"The modern solution for modern problems. Designed specifically for you.", "catchy_line": "Built for today."},
            {"heading": f"Trust {product}", "content": f"Trust the process. Trust the product. Trust {product}.", "catchy_line": "We've got you."},
            {"heading": f"Creative {product}", "content": f"Unleash a wave of creativity you never knew you had.", "catchy_line": "Spark your mind."},
            {"heading": f"Target {product}", "content": f"Your next big breakthrough is just one {product} away.", "catchy_line": "Almost there."},
            {"heading": f"Redefine {product}", "content": f"Redefining the impossible, one feature at a time.", "catchy_line": "No limits."},
            {"heading": f"Bold {product}", "content": f"Built for the bold. Designed for the professionals.", "catchy_line": "Stand out."},
            {"heading": f"Exceeding {product}", "content": f"Exceeding expectations every single day.", "catchy_line": "Above and beyond."},
            {"heading": f"Feel {product}", "content": f"Feel the difference. You'll wonder how you ever lived without it.", "catchy_line": "A physical change."},
            {"heading": f"Global {product}", "content": f"Setting the new global benchmark for excellence.", "catchy_line": "World class."},
            {"heading": f"Game Changer: {product}", "content": f"A true game changer that easily lives up to the hype.", "catchy_line": "Believe it."},
            {"heading": f"Skyrocket with {product}", "content": f"Skyrocket your productivity and beat your deadlines.", "catchy_line": "Up, up, and away."},
            {"heading": f"Essential {product}", "content": f"The most essential tool you will use this decade.", "catchy_line": "A must-have."},
            {"heading": f"Play to win: {product}", "content": f"Crafted specifically for those who play to win.", "catchy_line": "Victory is yours."},
            {"heading": f"Superior {product}", "content": f"Unapologetically superior in every conceivable metric.", "catchy_line": "No apologies."},
            {"heading": f"Overwhelming {product}", "content": f"The first step on your new path to overwhelming success.", "catchy_line": "Take the leap."},
            {"heading": f"Impeccable {product}", "content": f"Let the impeccable performance of {product} speak for itself.", "catchy_line": "Silent power."},
            {"heading": f"Loved {product}", "content": f"Loved by enthusiasts. Trusted by professionals.", "catchy_line": "Everyone loves it."},
            {"heading": f"Statement {product}", "content": f"Make a statement without saying a single word.", "catchy_line": "Loud action."},
            {"heading": f"Engineered {product}", "content": f"Expertly engineered to deliver optimal results, every time.", "catchy_line": "Science in motion."},
            {"heading": f"Dependable {product}", "content": f"The most dependable choice you can make today is {product}.", "catchy_line": "Rock solid."}
        ]
        
        return {
            "copy_objects": fallback_objects, 
            "ctas": ["Shop Now", "Learn More", "Get Started", "Try Now", "Buy Now"]
        }
