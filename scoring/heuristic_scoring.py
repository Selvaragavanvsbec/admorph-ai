from utils.text_utils import brand_alignment_score, emotion_score, readability_score, urgency_score


class HeuristicScoringEngine:
    def score_variant(self, variant: dict, tone: str) -> dict:
        full_text = f"{variant['headline']} {variant['cta']}"
        urgency = urgency_score(full_text)
        emotion = emotion_score(full_text)
        readability = readability_score(full_text)
        alignment = brand_alignment_score(full_text, tone)
        score = (0.3 * urgency) + (0.3 * emotion) + (0.2 * readability) + (0.2 * alignment)
        variant["heuristics"] = {
            "urgency": round(urgency, 3),
            "emotion": round(emotion, 3),
            "readability": round(readability, 3),
            "brand_alignment": round(alignment, 3),
        }
        variant["score"] = round(score, 3)
        return variant

    def run(self, variants: list[dict], tone: str) -> list[dict]:
        scored = [self.score_variant(v, tone) for v in variants]
        return sorted(scored, key=lambda item: item["score"], reverse=True)
