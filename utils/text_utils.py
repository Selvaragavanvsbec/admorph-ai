import re


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def readability_score(text: str) -> float:
    words = re.findall(r"\w+", text)
    if not words:
        return 0.0
    avg_word_len = sum(len(w) for w in words) / len(words)
    # Sweet spot around 5 chars average.
    score = 1.0 - abs(avg_word_len - 5.0) / 6.0
    return clamp(score)


def urgency_score(text: str) -> float:
    urgent_tokens = {"now", "today", "limited", "fast", "instant", "hurry", "last", "quick"}
    text_l = text.lower()
    matches = sum(token in text_l for token in urgent_tokens)
    punct = 0.1 if "!" in text else 0.0
    return clamp((matches / 3.0) + punct)


def emotion_score(text: str) -> float:
    emotional_tokens = {"boost", "power", "energy", "unstoppable", "excitement", "fearless", "win", "amazing"}
    text_l = text.lower()
    matches = sum(token in text_l for token in emotional_tokens)
    return clamp(matches / 3.0)


def brand_alignment_score(text: str, tone: str) -> float:
    tone = (tone or "").lower()
    text_l = text.lower()
    if not tone:
        return 0.5
    tone_tokens = set(re.findall(r"\w+", tone))
    if not tone_tokens:
        return 0.5
    matches = sum(token in text_l for token in tone_tokens)
    return clamp(0.4 + (matches / max(len(tone_tokens), 1)))
