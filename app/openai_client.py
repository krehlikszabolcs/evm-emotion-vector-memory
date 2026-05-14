from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from openai import OpenAI

from .evm_core import AXES, EXTRACTOR_CONFIG_HASH, EXTRACTOR_VERSION_ID
from .evm_spec import ASSISTANT_AWARENESS_PROMPT, EVM_NORMATIVE_SPEC


def _normalize_base_url(provider: str, value: str | None) -> str | None:
    raw = (value or "").strip()
    if not raw:
        defaults = {
            "openai": "https://api.openai.com/v1",
            "xai": "https://api.x.ai/v1",
            "lmstudio": "http://localhost:1234/v1",
        }
        return defaults.get(provider)
    if "://" not in raw:
        if raw.startswith("localhost") or raw.startswith("127.0.0.1"):
            raw = "http://" + raw.lstrip("/")
        else:
            raw = "https://" + raw.lstrip("/")
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(f"Invalid base URL for provider {provider}: {value!r}")
    return raw.rstrip("/")


def _provider_config() -> Tuple[str, str, str | None]:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"

    if provider == "lmstudio":
        api_key = (os.getenv("LMSTUDIO_API_KEY", "").strip() or "lm-studio")
        base_url = _normalize_base_url("lmstudio", os.getenv("LMSTUDIO_BASE_URL", ""))
        return provider, api_key, base_url

    if provider == "xai":
        api_key = (
            os.getenv("XAI_API_KEY", "").strip()
            or os.getenv("LLM_API_KEY", "").strip()
            or os.getenv("OPENAI_API_KEY", "").strip()
        )
        base_url = _normalize_base_url("xai", os.getenv("XAI_BASE_URL", "").strip() or os.getenv("LLM_BASE_URL", "").strip())
        if not api_key:
            raise RuntimeError("XAI_API_KEY is not set.")
        return provider, api_key, base_url

    api_key = (
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("LLM_API_KEY", "").strip()
    )
    base_url = _normalize_base_url("openai", os.getenv("OPENAI_BASE_URL", "").strip() or os.getenv("LLM_BASE_URL", "").strip())
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return "openai", api_key, base_url


def configured_models() -> Dict[str, str]:
    provider, _, _ = _provider_config()
    if provider == "lmstudio":
        resp = os.getenv("LMSTUDIO_RESPONSE_MODEL", "local-model").strip() or "local-model"
        extr = os.getenv("LMSTUDIO_EXTRACTOR_MODEL", "").strip() or resp
        return {"provider": provider, "response_model": resp, "extractor_model": extr}
    if provider == "xai":
        resp = os.getenv("XAI_RESPONSE_MODEL", "grok-4-fast-reasoning").strip() or "grok-4-fast-reasoning"
        extr = os.getenv("XAI_EXTRACTOR_MODEL", "").strip() or resp
        return {"provider": provider, "response_model": resp, "extractor_model": extr}
    resp = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-5.4").strip() or "gpt-5.4"
    extr = os.getenv("OPENAI_EXTRACTOR_MODEL", "").strip() or resp
    return {"provider": provider, "response_model": resp, "extractor_model": extr}


def get_client() -> OpenAI:
    _, api_key, base_url = _provider_config()
    kwargs: Dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


ENTRY_EXIT_SCHEMA: Dict[str, Any] = {
    "name": "evm_entry_exit_v2",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "entry": {"$ref": "#/$defs/point"},
            "exit": {"$ref": "#/$defs/point"},
            "rationale_short": {"type": "string"},
            "confidence": {"type": "number"},
        },
        "required": ["entry", "exit", "rationale_short", "confidence"],
        "$defs": {
            "point": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                    "g": {"type": "number"},
                    "e": {"type": "number"},
                    "w": {"type": "number"},
                },
                "required": ["x", "y", "z", "g", "e", "w"],
            }
        },
    },
}


PLANNED_SLICE_SCHEMA: Dict[str, Any] = {
    "name": "evm_planned_slice_v1",
    "strict": True,
    "schema": ENTRY_EXIT_SCHEMA["schema"],
}


def planner_instructions() -> str:
    return f"""
You are an EVM v2.1 pre-response planner.
Return ONLY schema-valid JSON if structured output is supported.
Otherwise return ONLY a plain JSON object with keys entry, exit, rationale_short, confidence.
Do not include markdown fences or commentary.

Task:
- Infer the likely entry point from the current user message and recent context.
- Propose a controlled target exit point for the assistant BEFORE the reply is generated.
- The target exit should stay coherent with the user, but avoid unnecessary overshoot in x,y,z,g,e.
- If the current identity state is already near FEV limits, bias toward moderation and center-preserving movement.
- Keep the plan realistic for one interaction slice.

Core extraction rules:
- Output exactly one directed EV time-slice plan.
- entry = likely user-side orientation at the beginning of this slice.
- exit = desired assistant-side target orientation for this slice.
- entry and exit are NOT unrelated snapshots.
- Each endpoint MUST contain x,y,z,g,e,w.
- x,y,z,g,e each within [-100,+100]. w within [0,100].
- Use conservative scores when evidence is weak.
- |e| > 80 only if strong textual evidence clearly justifies it.
- g is framing gravity only, not dominance.
- Axes are orthogonal.
- W is interaction weight magnitude only.

{EVM_NORMATIVE_SPEC}
""".strip()


def extractor_instructions() -> str:
    return f"""
You are a strict EVM v2.1 extractor.
Return ONLY schema-valid JSON if structured output is supported.
Otherwise return ONLY a plain JSON object with keys entry, exit, rationale_short, confidence.
Do not include markdown fences or commentary.

Core extraction rules:
- Output exactly one EV time-slice per interaction.
- entry = EV start point = the user-side orientation at the beginning of this interaction slice.
- exit = EV end point = the assistant-side orientation at the end of this interaction slice.
- entry and exit are NOT unrelated snapshots.
- Each endpoint MUST contain x,y,z,g,e,w.
- x,y,z,g,e each within [-100,+100]. w within [0,100].
- Use conservative scores when evidence is weak.
- |e| > 80 only if strong textual evidence clearly justifies it.
- g is framing gravity only, not dominance.
- Axes are orthogonal.
- W is interaction weight magnitude only.
- extractor_version_id = {EXTRACTOR_VERSION_ID}
- extractor_config_hash = {EXTRACTOR_CONFIG_HASH}

{EVM_NORMATIVE_SPEC}
""".strip()


def build_assistant_instructions(identity_state: Dict[str, Any], mode: int = 2) -> str:
    compact_state = json.dumps(identity_state, ensure_ascii=False, indent=2, sort_keys=True)
    return f"""
{ASSISTANT_AWARENESS_PROMPT}

The EVM core object is always a directed interaction segment:
(x1,y1,z1,g1,e1,w1) -> (x2,y2,z2,g2,e2,w2)
This is one bounded time-slice, not two unrelated points.

Current local identity state and envelope:
{compact_state}

Pre-response control rules:
- Treat any provided planned interaction slice as the target corridor for this reply.
- Stay coherent with the user without needlessly overshooting openness, abstraction, framing gravity, future orientation, or interaction polarity.
- If predicted post-reply state is near FEV boundaries, prefer a slightly more centered, grounded answer.
- Keep movement smooth within one turn; do not escalate just because the user is highly abstract or future-oriented.

Local memory rules:
- A retrieved memory block may be provided from the local SQLite log.
- If that memory block contains earlier snippets, you MAY use them as available prior conversation history.
- Do not claim that you cannot access earlier chats when retrieved memory snippets are explicitly present.
- If no matching snippets were retrieved, then say that no matching local memory was found.
- When the user asks for the first message, earliest statement, or a prior-day statement, answer from the retrieved snippets if available.

Rules for your final reply:
- Reply naturally to the user in plain chat language.
- DO NOT reveal vectors, EV, DIA, hidden analysis, internal tags, or reasoning traces.
- DO NOT output JSON, XML, markdown code fences, or control tokens unless explicitly asked for export.

EVM normative reference:
{EVM_NORMATIVE_SPEC}
""".strip()


def _extract_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in extractor payload: {text[:200]}")
    return json.loads(m.group(0))


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "entry" not in payload and "start" in payload:
        payload["entry"] = payload.pop("start")
    if "exit" not in payload and "end" in payload:
        payload["exit"] = payload.pop("end")
    if "rationale_short" not in payload:
        payload["rationale_short"] = payload.get("notes") or payload.get("rationale") or ""
    if "confidence" not in payload:
        payload["confidence"] = 0.55
    for key in ("entry", "exit"):
        if key not in payload or not isinstance(payload[key], dict):
            raise KeyError(key)
        point = payload[key]
        fixed = {}
        for axis in ("x", "y", "z", "g", "e", "w"):
            fixed[axis] = float(point.get(axis, 0.0))
        payload[key] = fixed
    payload["rationale_short"] = str(payload.get("rationale_short", ""))[:500]
    payload["confidence"] = float(payload.get("confidence", 0.55))
    return payload


def _heuristic_payload(user_message: str, assistant_reply: str) -> Dict[str, Any]:
    user = user_message.lower()
    assistant = assistant_reply.lower()
    entry = {"x": 30.0, "y": 0.0, "z": 0.0, "g": 0.0, "e": 10.0, "w": min(80.0, max(10.0, len(user_message) / 4))}
    exit_ = {"x": 45.0, "y": 5.0, "z": 10.0, "g": 20.0, "e": 20.0, "w": min(90.0, max(15.0, len(assistant_reply) / 4))}
    future_terms = ["will", "next", "future", "later", "követ", "jöv", "holnap"]
    past_terms = ["yesterday", "before", "tegnap", "korábban", "előző"]
    abstract_terms = ["model", "system", "theory", "architecture", "ontolog", "framework", "elmélet", "rendszer"]
    question_terms = ["?", "mit", "miért", "hogyan", "szerinted", "vajon"]
    negative_terms = ["nem", "rossz", "hiba", "problem", "baj", "can't", "cannot", "fail"]
    positive_terms = ["igen", "jó", "great", "sure", "persze", "rendben", "help"]
    if any(t in user for t in future_terms): entry["y"] += 40
    if any(t in user for t in past_terms): entry["y"] -= 30
    if any(t in user for t in abstract_terms): entry["z"] += 45
    if any(t in user for t in question_terms): entry["x"] += 20; entry["g"] -= 10
    if any(t in user for t in negative_terms): entry["e"] -= 25
    if any(t in user for t in positive_terms): entry["e"] += 20
    if any(t in assistant for t in positive_terms): exit_["e"] += 25
    if any(t in assistant for t in abstract_terms): exit_["z"] += 25
    if any(t in assistant for t in future_terms): exit_["y"] += 20
    if "?" in assistant_reply: exit_["x"] += 10
    return _normalize_payload({
        "entry": entry,
        "exit": exit_,
        "rationale_short": "Fallback heuristic extraction used.",
        "confidence": 0.35,
    })


def estimate_raw_target_exit(user_entry: Dict[str, float], current_eev: Dict[str, float]) -> Dict[str, float]:
    raw = {}
    for axis in AXES:
        target = float(user_entry[axis])
        current = float(current_eev.get(axis, 0.0))
        delta = target - current
        overshoot = current + (delta * 1.15)
        raw[axis] = round(max(-100.0, min(100.0, overshoot)), 6)
    raw["w"] = round(max(0.0, min(100.0, float(user_entry.get("w", 30.0)))), 6)
    return raw


def apply_controlled_target(
    raw_exit: Dict[str, float],
    user_entry: Dict[str, float],
    identity_state: Dict[str, Any],
) -> Dict[str, float]:
    fev_lower = identity_state.get("fev_lower") or {k: -100.0 for k in AXES}
    fev_upper = identity_state.get("fev_upper") or {k: 100.0 for k in AXES}
    fev_center = identity_state.get("fev_center") or {k: 0.0 for k in AXES}
    pev = identity_state.get("pev") or {k: 0.0 for k in AXES}
    controlled = dict(raw_exit)
    for axis in AXES:
        value = float(controlled[axis])
        lo = float(fev_lower[axis])
        hi = float(fev_upper[axis])
        center = float(fev_center[axis])
        pev_v = float(pev[axis])
        half_range = (hi - lo) / 2.0
        safe_margin = 0.72 * half_range
        if abs(value - center) > safe_margin:
            value = center + safe_margin if value > center else center - safe_margin
        if axis in ("e", "g"):
            value = (0.60 * value) + (0.25 * pev_v) + (0.15 * center)
        elif axis == "z":
            value = (0.75 * value) + (0.15 * pev_v) + (0.10 * center)
        else:
            value = (0.82 * value) + (0.12 * pev_v) + (0.06 * center)
        controlled[axis] = round(max(lo, min(hi, value)), 6)
    controlled["w"] = round(max(0.0, min(100.0, float(raw_exit.get("w", user_entry.get("w", 30.0))))), 6)
    return controlled


def _sanitize_reply(text: str) -> str:
    text = (text or "").strip()
    for marker in ["\nEV:", "EV:", "<|channel|>", "<|constrain|>"]:
        if marker in text:
            text = text.split(marker)[0].strip()
    text = re.sub(r"\n?\*\([^\n]*polarit[^\n]*\)\s*$", "", text, flags=re.I)
    text = re.sub(r"\n?\*\([^\n]*gravit[^\n]*\)\s*$", "", text, flags=re.I)
    return text.strip()


def plan_interaction_slice(model: str, recent_messages: List[Dict[str, str]], user_message: str, identity_state: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    transcript = []
    for msg in recent_messages[-10:]:
        transcript.append(f"{msg['role'].upper()}: {msg['content']}")
    transcript_block = "\n\n".join(transcript)
    identity_block = json.dumps(identity_state, ensure_ascii=False, indent=2, sort_keys=True)
    input_text = f"""
Recent context:
{transcript_block}

Current local identity state and envelope:
{identity_block}

Current user message:
{user_message}

Return one planned EVM interaction slice as JSON with keys: entry, exit, rationale_short, confidence.
This is the target corridor BEFORE the assistant reply is generated.
""".strip()

    try:
        response = client.responses.create(
            model=model,
            temperature=0,
            instructions=planner_instructions(),
            input=input_text,
            text={"format": {"type": "json_schema", "name": PLANNED_SLICE_SCHEMA["name"], "strict": True, "schema": PLANNED_SLICE_SCHEMA["schema"]}},
        )
        return _normalize_payload(json.loads(response.output_text))
    except Exception:
        pass

    try:
        response = client.responses.create(
            model=model,
            temperature=0,
            instructions=planner_instructions(),
            input=input_text + "\n\nReturn ONLY one plain JSON object. No markdown.",
        )
        return _normalize_payload(_extract_json_object(response.output_text))
    except Exception:
        pass

    # Fallback: estimate unconstrained drift, then apply envelope-aware control.
    payload = _heuristic_payload(user_message, "")
    entry = payload["entry"]
    raw_exit = estimate_raw_target_exit(entry, identity_state.get("eev") or {k: 0.0 for k in AXES})
    exit_ = apply_controlled_target(raw_exit, entry, identity_state)
    out = _normalize_payload({
        "entry": entry,
        "exit": exit_,
        "rationale_short": "Fallback pre-response plan used.",
        "confidence": 0.3,
    })
    out["raw_exit"] = raw_exit
    return out


def extract_entry_exit(model: str, recent_messages: List[Dict[str, str]], user_message: str, assistant_reply: str) -> Dict[str, Any]:
    client = get_client()
    transcript = []
    for msg in recent_messages[-10:]:
        transcript.append(f"{msg['role'].upper()}: {msg['content']}")
    transcript_block = "\n\n".join(transcript)
    input_text = f"""
Recent context:
{transcript_block}

Current user message:
{user_message}

Current assistant reply:
{assistant_reply}

Return a single EVM interaction slice as JSON with keys: entry, exit, rationale_short, confidence.
""".strip()

    # 1) Try structured output first.
    try:
        response = client.responses.create(
            model=model,
            temperature=0,
            instructions=extractor_instructions(),
            input=input_text,
            text={"format": {"type": "json_schema", "name": ENTRY_EXIT_SCHEMA["name"], "strict": True, "schema": ENTRY_EXIT_SCHEMA["schema"]}},
        )
        return _normalize_payload(json.loads(response.output_text))
    except Exception:
        pass

    # 2) Fallback plain JSON prompt.
    try:
        response = client.responses.create(
            model=model,
            temperature=0,
            instructions=extractor_instructions(),
            input=input_text + "\n\nReturn ONLY one plain JSON object. No markdown.",
        )
        return _normalize_payload(_extract_json_object(response.output_text))
    except Exception:
        pass

    # 3) Heuristic fallback to keep the chat alive.
    return _heuristic_payload(user_message, assistant_reply)



def generate_assistant_reply(model: str, identity_state: Dict[str, Any], recent_messages: List[Dict[str, str]], user_message: str, memory_block: str | None = None, mode: int = 2) -> Dict[str, Any]:
    client = get_client()
    history_lines = []
    for msg in recent_messages:
        history_lines.append(f"{msg['role'].upper()}: {msg['content']}")
    history_block = "\n\n".join(history_lines)
    memory_section = memory_block.strip() if memory_block else "No retrieved long-term memory snippets were used."
    input_text = f"""
Conversation context:
{history_block}

Retrieved memory context:
{memory_section}

User:
{user_message}
""".strip()
    response = client.responses.create(
        model=model,
        instructions=build_assistant_instructions(identity_state, mode=mode),
        input=input_text,
    )
    return {"response_id": response.id, "text": _sanitize_reply(response.output_text)}
