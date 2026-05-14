from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List


def _strip_accents(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", text or "") if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    return _strip_accents((text or "").lower())


STOPWORDS = {
    "a", "az", "es", "es", "hogy", "ez", "azt", "ezt", "akkor", "mert", "vagy", "van", "volt", "lesz",
    "en", "te", "mi", "ti", "ok", "oket", "is", "de", "ha", "mint", "mar", "meg", "csak", "igen",
    "nem", "mit", "mirol", "mikor", "hol", "ki", "be", "fel", "le", "ide", "oda", "itt", "ott",
    "most", "tegnap", "ma", "holnap", "korabban", "elobb", "elozo", "multkor", "beszeltunk", "mondtam", "kerdeztem",
    "the", "and", "that", "this", "with", "from", "what", "when", "where", "who", "why", "how", "about",
    "said", "asked", "please", "find", "show", "chat", "conversation", "during", "while", "work", "munka",
}

WORK_KEYWORDS = {
    "munka", "munkaban", "munkahely", "dolgoztam", "dolgozom", "dolgozni", "projekt", "feladat", "hatarido",
    "kod", "kodol", "debug", "hiba", "javitas", "log", "sqlite", "index", "flask", "python", "repo", "github",
    "modell", "llm", "openai", "lmstudio", "ollama", "evm", "pium", "pipeline", "publikal", "zenodo",
    "work", "working", "job", "task", "project", "deadline", "code", "coding", "fix", "bug", "debugging", "deploy",
    "analysis", "paper", "article", "manuscript", "research", "dataset", "galaxy", "sparc",
}

POSITIVE_WORDS = {
    "jo", "remek", "szuper", "orulok", "örülök", "boldog", "elegedett", "halad", "kesz", "siker", "pozitiv",
    "good", "great", "excellent", "happy", "glad", "progress", "done", "success", "positive", "nice",
}
NEGATIVE_WORDS = {
    "rossz", "ideges", "feszult", "duhos", "szar", "problema", "hiba", "elakadt", "faradt", "negativ",
    "bad", "angry", "tense", "stuck", "problem", "error", "tired", "negative", "frustrated",
}


def extract_keywords(*texts: str, limit: int = 12) -> List[str]:
    seen: List[str] = []
    for text in texts:
        for token in re.findall(r"[a-zA-Z0-9_áéíóöőúüűÁÉÍÓÖŐÚÜŰ]{3,}", text or ""):
            norm = normalize(token)
            if norm in STOPWORDS:
                continue
            if norm not in seen:
                seen.append(norm)
            if len(seen) >= limit:
                return seen
    return seen


def infer_context_tags(*texts: str) -> List[str]:
    merged = " ".join(texts)
    norm = normalize(merged)
    tags: List[str] = []
    if any(k in norm for k in WORK_KEYWORDS):
        tags.append("work")
    if any(k in norm for k in ("evm", "identity", "memory", "sqlite", "index", "log")):
        tags.append("system")
    if any(k in norm for k in ("pium", "galaxy", "sparc", "rotation", "kappa")):
        tags.append("research")
    if any(k in norm for k in ("publish", "publication", "paper", "zenodo", "manuscript", "preprint")):
        tags.append("publication")
    return tags


def infer_text_sentiment(*texts: str) -> float:
    merged = normalize(" ".join(texts))
    pos = sum(1 for w in POSITIVE_WORDS if w in merged)
    neg = sum(1 for w in NEGATIVE_WORDS if w in merged)
    raw = (pos - neg) * 12.5
    if raw > 100:
        raw = 100.0
    if raw < -100:
        raw = -100.0
    return round(raw, 3)


def summarize_turn(user_message: str, assistant_text: str, extracted: Dict[str, Any], turn_index: int) -> Dict[str, Any]:
    keywords = extract_keywords(user_message, assistant_text)
    context_tags = infer_context_tags(user_message, assistant_text)
    entry = dict(extracted.get("entry") or {})
    exit_ = dict(extracted.get("exit") or {})
    user_mood_e = float(entry.get("e", 0.0))
    assistant_mood_e = float(exit_.get("e", 0.0))
    lexical_sentiment = infer_text_sentiment(user_message, assistant_text)
    work_context = "work" in context_tags
    headline_parts = []
    if work_context:
        headline_parts.append("work")
    if keywords:
        headline_parts.append(", ".join(keywords[:4]))
    headline = " | ".join(headline_parts) if headline_parts else f"turn {turn_index} summary"
    return {
        "turn_index": int(turn_index),
        "headline": headline,
        "keywords": keywords,
        "context_tags": context_tags,
        "work_context": work_context,
        "user_mood_e": round(user_mood_e, 3),
        "assistant_mood_e": round(assistant_mood_e, 3),
        "lexical_sentiment": lexical_sentiment,
        "user_excerpt": (user_message or "")[:280],
        "assistant_excerpt": (assistant_text or "")[:280],
        "extractor_notes": (extracted.get("rationale_short") or "")[:280],
        "text": " | ".join(
            part for part in [
                headline,
                f"user_mood_e={round(user_mood_e, 3)}",
                f"assistant_mood_e={round(assistant_mood_e, 3)}",
                f"work_context={work_context}",
                f"keywords={', '.join(keywords[:8])}" if keywords else "",
            ] if part
        ),
    }


def detect_best_mood_work_query(text: str) -> bool:
    norm = normalize(text)
    mood_hits = any(p in norm for p in ["legjobb hangulat", "jo hangulat", "best mood", "best feeling", "legjobb kedv", "hangulatom"])
    work_hits = any(p in norm for p in ["munka", "munkaban", "munka kozben", "dolgoztam", "worked on", "while working", "at work"])
    return mood_hits and work_hits
