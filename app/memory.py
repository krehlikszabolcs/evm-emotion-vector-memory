from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from . import db
from .indexing import detect_best_mood_work_query


def _strip_accents(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", text or "") if not unicodedata.combining(ch))


HU_STOPWORDS = {
    "a", "az", "es", "és", "hogy", "ez", "azt", "ezt", "akkor", "mert", "vagy", "van", "volt", "lesz",
    "en", "én", "te", "mi", "ti", "ok", "ők", "ő", "is", "de", "ha", "mint", "mar", "már", "meg", "csak", "igen",
    "nem", "mit", "mirol", "miről", "mikor", "hol", "ki", "be", "fel", "le", "ide", "oda", "itt", "ott",
    "most", "tegnap", "ma", "holnap", "korabban", "korábban", "elobb", "előbb", "elozo", "előző", "multkor", "múltkor",
    "beszeltunk", "beszéltünk", "mondtam", "kerdeztem", "kérdeztem", "keresd", "nezd", "nézd", "logban", "adatot",
    "tudja", "ho", "hó", "napra", "napon", "honap", "hónap", "elseje", "elsejen", "elsején", "elsejere", "szerint",
}
EN_STOPWORDS = {
    "the", "and", "that", "this", "with", "from", "what", "when", "where", "who", "why", "how",
    "yesterday", "today", "tomorrow", "earlier", "before", "previous", "remember", "search", "logs", "talked",
    "about", "said", "asked", "please", "find", "show", "chat", "conversation", "since", "full", "entire",
}


def _normalize_terms(terms: set[str]) -> set[str]:
    return {_strip_accents(t.lower()) for t in terms}


HU_STOPWORDS_NORM = _normalize_terms(HU_STOPWORDS)
EN_STOPWORDS_NORM = _normalize_terms(EN_STOPWORDS)

MEMORY_TRIGGER_PATTERNS = [
    r"\btegnap\b", r"\bma\b", r"\bholnap\b", r"\bkorabban\b", r"\belozo\b", r"\bmultkor\b",
    r"mir[oó]l besz[eé]lt", r"mit mondtam", r"mit kerdeztem", r"keresd ki", r"olv[aá]sd be", r"mem[oó]ria",
    r"\byesterday\b", r"\btoday\b", r"\bearlier\b", r"\bprevious\b", r"\bbefore\b", r"\bmemory\b",
    r"what did we talk", r"what did i say", r"search the log", r"search the chat", r"read the memory", r"remember",
    r"elso mondat", r"elso uzenet", r"first sentence", r"first message", r"chat legele", r"timestamp",
]

BROWSE_PATTERNS = [
    r"teljes mem[oó]ria", r"az egesz mem[oó]ria", r"olv[aá]sd be a teljes mem[oó]ri", r"tegnapt[oó]l",
    r"scroll", r"teker", r"videokazett", r"folyamatosan", r"idoben", r"timestamp", r"teljes elozmeny", r"teljes elozmeny",
    r"full memory", r"entire memory", r"read the full memory", r"since yesterday", r"from yesterday", r"browse history",
    r"timeline", r"chronological", r"all messages since",
]


@dataclass
class RetrievedMemory:
    used: bool
    reason: str
    snippets: List[Dict[str, Any]]
    search_terms: List[str]
    date_filter: Optional[Tuple[str, str]]
    browse_mode: bool = False



def normalize(text: str) -> str:
    return _strip_accents((text or "").lower())



def should_trigger_memory(user_message: str) -> bool:
    n = normalize(user_message)
    return any(re.search(pattern, n) for pattern in MEMORY_TRIGGER_PATTERNS)



def detect_browse_mode(user_message: str) -> bool:
    n = normalize(user_message)
    return any(re.search(pattern, n) for pattern in BROWSE_PATTERNS)



def _is_first_message_query(user_message: str) -> bool:
    n = normalize(user_message)
    return any(
        phrase in n
        for phrase in [
            "elso uzenet",
            "legelso uzenet",
            "elso kerdes",
            "a beszelgetes elejen",
            "a legelejen",
            "amikor elkezdtuk",
            "first message",
            "very first message",
            "start of the conversation",
            "at the beginning",
        ]
    )



def extract_search_terms(user_message: str) -> List[str]:
    n = normalize(user_message)
    words = re.findall(r"[a-z0-9_áéíóöőúüű]+", n)
    terms: List[str] = []
    for word in words:
        if len(word) < 3:
            continue
        stripped = _strip_accents(word.lower())
        if stripped in HU_STOPWORDS_NORM or stripped in EN_STOPWORDS_NORM:
            continue
        if stripped not in terms:
            terms.append(stripped)
    return terms[:12]



def _parse_month_day(n: str, now: datetime) -> Optional[Tuple[str, str]]:
    patterns = [
        r"\b(?P<month>\d{1,2})\s*[./-]\s*(?P<day>\d{1,2})\b",
        r"\b(?P<month>\d{1,2})\s*(?:ho|ho\.|honap|honapban)\s*(?P<day>\d{1,2})\b",
        r"\b(?P<month>\d{1,2})\s*(?:ho|ho\.|honap|honapban)\s*(?P<day>\d{1,2})\s*[-.]?e?re\b",
    ]
    for pat in patterns:
        m = re.search(pat, n)
        if not m:
            continue
        month = int(m.group("month"))
        day = int(m.group("day"))
        if not (1 <= month <= 12):
            continue
        try:
            start_dt = datetime(now.year, month, day, tzinfo=timezone.utc)
        except ValueError:
            continue
        end_dt = start_dt + timedelta(days=1)
        return start_dt.date().isoformat(), end_dt.date().isoformat()
    return None



def detect_date_filter(user_message: str, now: Optional[datetime] = None) -> Optional[Tuple[str, str]]:
    now = now or datetime.now(timezone.utc)
    n = normalize(user_message)
    explicit = _parse_month_day(n, now)
    if explicit:
        return explicit
    if "tegnaptol" in n or "since yesterday" in n or "from yesterday" in n:
        start = (now - timedelta(days=1)).date().isoformat()
        end = (now + timedelta(days=1)).date().isoformat()
        return start, end
    if "tegnap" in n or "yesterday" in n:
        start = (now - timedelta(days=1)).date().isoformat()
        end = now.date().isoformat()
        return start, end
    if re.search(r"\bma\b", n) or "today" in n:
        start = now.date().isoformat()
        end = (now + timedelta(days=1)).date().isoformat()
        return start, end
    return None



def _candidate_rows(chat_id: int, date_filter: Optional[Tuple[str, str]], limit_messages: int = 1600, limit_ev: int = 400, limit_index: int = 800) -> List[Dict[str, Any]]:
    params: List[Any] = []
    date_sql = ""
    if date_filter:
        start, end = date_filter
        date_sql = " AND m.created_at >= ? AND m.created_at < ?"
        params.extend([f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"])

    msg_rows = db.fetch_all(
        f"""
        SELECT m.chat_id, c.title, m.role, m.content, m.created_at,
               'message' AS source_type,
               NULL AS turn_index,
               NULL AS notes,
               NULL AS entry_json,
               NULL AS exit_json,
               NULL AS category,
               NULL AS payload_json,
               CASE WHEN m.chat_id = ? THEN 1 ELSE 0 END AS current_chat
        FROM messages m
        JOIN chats c ON c.id = m.chat_id
        WHERE 1=1 {date_sql}
        ORDER BY m.created_at DESC
        LIMIT {int(limit_messages)}
        """,
        tuple([chat_id] + params),
    )

    ev_params: List[Any] = [chat_id]
    ev_date_sql = ""
    if date_filter:
        start, end = date_filter
        ev_date_sql = " AND e.created_at >= ? AND e.created_at < ?"
        ev_params.extend([f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"])

    ev_rows = db.fetch_all(
        f"""
        SELECT e.chat_id, c.title, NULL AS role, e.notes AS content, e.created_at,
               'ev_segment' AS source_type,
               e.turn_index AS turn_index,
               e.notes AS notes,
               e.entry_json AS entry_json,
               e.exit_json AS exit_json,
               NULL AS category,
               NULL AS payload_json,
               CASE WHEN e.chat_id = ? THEN 1 ELSE 0 END AS current_chat
        FROM ev_records e
        JOIN chats c ON c.id = e.chat_id
        WHERE 1=1 {ev_date_sql}
        ORDER BY e.created_at DESC
        LIMIT {int(limit_ev)}
        """,
        tuple(ev_params),
    )

    idx_params: List[Any] = [chat_id]
    idx_date_sql = ""
    if date_filter:
        start, end = date_filter
        idx_date_sql = " AND i.created_at >= ? AND i.created_at < ?"
        idx_params.extend([f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"])

    idx_rows = db.fetch_all(
        f"""
        SELECT i.chat_id, COALESCE(c.title, 'System') AS title, NULL AS role, i.payload_json AS content, i.created_at,
               'index_log' AS source_type,
               NULL AS turn_index,
               NULL AS notes,
               NULL AS entry_json,
               NULL AS exit_json,
               i.category AS category,
               i.payload_json AS payload_json,
               CASE WHEN i.chat_id = ? THEN 1 ELSE 0 END AS current_chat
        FROM index_log i
        LEFT JOIN chats c ON c.id = i.chat_id
        WHERE 1=1 {idx_date_sql}
        ORDER BY i.created_at DESC
        LIMIT {int(limit_index)}
        """,
        tuple(idx_params),
    )

    return [dict(r) for r in msg_rows] + [dict(r) for r in ev_rows] + [dict(r) for r in idx_rows]



def _score_row(row: Dict[str, Any], terms: List[str], chat_id: int, trigger: bool = False, prioritize_user: bool = False) -> float:
    score = 0.0
    content = normalize(str(row.get("content") or ""))
    title = normalize(str(row.get("title") or ""))
    category = normalize(str(row.get("category") or ""))
    if row.get("chat_id") == chat_id:
        score += 1.25
    if row.get("source_type") == "index_log":
        score += 0.35
    if prioritize_user and row.get("role") == "user":
        score += 0.5
    for term in terms:
        if term in content:
            score += 2.0
        if term in title:
            score += 0.6
        if term in category:
            score += 0.8
    if trigger:
        score += 0.25
    if row.get("created_at"):
        score += 0.000001
    return round(score, 6)



def _build_snippet(row: Dict[str, Any], score: float) -> Dict[str, Any]:
    category = row.get("category")
    if row.get("source_type") == "ev_segment":
        content = f"Turn {row.get('turn_index')} {row.get('entry_json')} -> {row.get('exit_json')}"
        if row.get("notes"):
            content += f" Notes: {row['notes']}"
    else:
        content = (row.get("content") or "").strip()
    if len(content) > 500:
        content = content[:500] + "..."
    return {
        "score": round(score, 3),
        "chat_id": row.get("chat_id"),
        "title": row.get("title"),
        "role": row.get("role"),
        "created_at": row.get("created_at"),
        "source_type": row.get("source_type"),
        "turn_index": row.get("turn_index"),
        "category": category,
        "content": content,
    }



def _retrieve_best_mood_work(chat_id: int, user_message: str, limit: int, date_filter: Optional[Tuple[str, str]]) -> RetrievedMemory:
    params: List[Any] = []
    date_sql = ""
    if date_filter:
        start, end = date_filter
        date_sql = " AND i.created_at >= ? AND i.created_at < ?"
        params.extend([f"{start}T00:00:00+00:00", f"{end}T00:00:00+00:00"])
    rows = db.fetch_all(
        f"""
        SELECT i.chat_id, COALESCE(c.title, 'System') AS title, NULL AS role,
               i.payload_json AS content, i.created_at, 'index_log' AS source_type,
               json_extract(i.payload_json, '$.turn_index') AS turn_index,
               NULL AS notes, NULL AS entry_json, NULL AS exit_json,
               i.category AS category, i.payload_json AS payload_json,
               CASE WHEN i.chat_id = ? THEN 1 ELSE 0 END AS current_chat
        FROM index_log i
        LEFT JOIN chats c ON c.id = i.chat_id
        WHERE i.category = 'turn_summary' AND json_extract(i.payload_json, '$.work_context') = 1 {date_sql}
        ORDER BY CAST(json_extract(i.payload_json, '$.user_mood_e') AS REAL) DESC, i.created_at DESC
        LIMIT {int(max(limit * 4, 12))}
        """,
        tuple([chat_id] + params),
    )
    snippets: List[Dict[str, Any]] = []
    for row in rows:
        payload = {}
        try:
            payload = db.loads(row["payload_json"] or "{}")
        except Exception:
            payload = {}
        what = payload.get("headline") or payload.get("text") or ""
        content = {
            "chat_id": row["chat_id"],
            "title": row["title"],
            "role": None,
            "created_at": row["created_at"],
            "source_type": "index_log",
            "turn_index": payload.get("turn_index"),
            "category": "turn_summary",
            "content": (
                f"Best-work-mood candidate | mood={payload.get('user_mood_e')} | "
                f"topics={', '.join(payload.get('keywords') or [])} | "
                f"headline={what} | user={payload.get('user_excerpt','')} | assistant={payload.get('assistant_excerpt','')}"
            ),
        }
        score = float(payload.get("user_mood_e") or 0.0)
        snippets.append(_build_snippet(content, score))
    return RetrievedMemory(bool(snippets), "best_mood_work", snippets[:limit], extract_search_terms(user_message), date_filter, browse_mode=False)



def retrieve_memory(chat_id: int, user_message: str, limit: int = 8) -> RetrievedMemory:
    trigger = should_trigger_memory(user_message)
    browse_mode = detect_browse_mode(user_message)
    terms = extract_search_terms(user_message)
    date_filter = detect_date_filter(user_message)
    prioritize_first = _is_first_message_query(user_message)

    if detect_best_mood_work_query(user_message):
        return _retrieve_best_mood_work(chat_id, user_message, limit, date_filter)

    if not trigger and not terms and not browse_mode:
        return RetrievedMemory(False, "no_trigger", [], [], date_filter, browse_mode=False)

    rows = _candidate_rows(chat_id, date_filter, limit_messages=2200 if browse_mode else 1400)

    if prioritize_first:
        msg_rows = [r for r in rows if r.get("source_type") == "message"]
        msg_rows.sort(key=lambda r: (r.get("created_at") or "", 0 if r.get("role") == "user" else 1))
        snippets = []
        for row in msg_rows[: max(limit * 4, 40)]:
            score = _score_row(row, terms, chat_id, trigger=trigger, prioritize_user=True)
            if terms and score <= 0:
                continue
            snippets.append(_build_snippet(row, score if score > 0 else 1.0))
        snippets = snippets[:limit]
        return RetrievedMemory(bool(snippets), "first_message_lookup", snippets, terms, date_filter, browse_mode=False)

    if browse_mode:
        msg_rows = [r for r in rows if r.get("source_type") == "message"]
        msg_rows.sort(key=lambda r: (r.get("created_at") or "", 0 if r.get("role") == "user" else 1))
        snippets: List[Dict[str, Any]] = []
        for row in msg_rows:
            score = _score_row(row, terms, chat_id, trigger=True)
            if terms and score <= 0 and row.get("chat_id") != chat_id:
                continue
            snippets.append(_build_snippet(row, score if score > 0 else 0.8))
        if date_filter and snippets:
            snippets = snippets[-min(max(limit * 8, 36), 120):]
        else:
            snippets = snippets[-min(max(limit * 6, 24), 80):]
        return RetrievedMemory(bool(snippets), "chronological_browse", snippets, terms, date_filter, browse_mode=True)

    scored: List[Tuple[float, Dict[str, Any]]] = []
    seen = set()
    for row in rows:
        score = _score_row(row, terms, chat_id, trigger=trigger)
        if trigger and not terms:
            score += 1.0
        if score <= 0:
            continue
        key = (row.get("chat_id"), row.get("created_at"), row.get("source_type"), row.get("content"), row.get("turn_index"))
        if key in seen:
            continue
        seen.add(key)
        scored.append((score, row))

    scored.sort(key=lambda item: (item[0], item[1].get("created_at", "")), reverse=True)
    snippets = [_build_snippet(row, score) for score, row in scored[:limit]]
    return RetrievedMemory(bool(snippets), "triggered" if trigger else "keyword_overlap", snippets, terms, date_filter, browse_mode=False)



def build_memory_block(memory: RetrievedMemory) -> str:
    if not memory.used:
        return (
            "No matching long-term memory snippets were found in the local SQLite log. "
            "If the user asks about earlier chats or dates, say that no matching local memory was retrieved."
        )

    lines = [
        "Local memory recall is available and was retrieved from the local DATA storage.",
        "Treat the snippets below as usable prior conversation records.",
        "When the user asks what was said earlier, answer from these snippets directly instead of claiming that you cannot access earlier chats.",
        f"Trigger reason: {memory.reason}",
        f"Search terms: {', '.join(memory.search_terms) if memory.search_terms else '(none)'}",
        f"Browse mode: {'enabled' if memory.browse_mode else 'disabled'}",
    ]
    if memory.date_filter:
        lines.append(f"Date filter UTC: {memory.date_filter[0]} to {memory.date_filter[1]}")
    if memory.browse_mode:
        lines.append("The following snippets are chronological browse results. Read them as a timeline and summarize them in time order when helpful.")
    lines.append("Retrieved snippets:")
    for idx, item in enumerate(memory.snippets, start=1):
        role = item.get("role") or item.get("source_type")
        turn = f" turn={item['turn_index']}" if item.get("turn_index") is not None else ""
        category = f" category={item['category']}" if item.get("category") else ""
        lines.append(
            f"[{idx}] chat_id={item['chat_id']} title={item['title']} role={role}{turn}{category} created_at={item['created_at']} score={item['score']}\n{item['content']}"
        )
    lines.append("If several snippets conflict, prefer the most date-relevant match, then the highest score.")
    return "\n".join(lines)
