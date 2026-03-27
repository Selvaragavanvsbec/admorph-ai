from services.openai_service import openai_service


class StrategyAgent:
    def run(self, brief: dict) -> dict:
        fallback = {
            "audience_profile": f"{brief['audience']} looking for {brief['goal']}",
            "emotional_trigger": "aspiration and momentum",
            "tone": brief["tone"],
            "value_proposition": f"{brief['product']} helps users achieve {brief['goal']}",
            "persuasion_angle": "benefit-first social proof",
        }
        prompt = f"""
Analyze this ad brief and return a compact strategy JSON.
Brief: {brief}
Keys required: audience_profile, emotional_trigger, tone, value_proposition, persuasion_angle
"""
        return openai_service.generate_json(
            system_prompt="You are a performance marketing strategist.",
            user_prompt=prompt,
            fallback=fallback,
        )
