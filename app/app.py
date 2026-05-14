from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

APP_METADATA = {
    "author": "Szabolcs Krehlik",
    "year": "2026",
    "license": "CC-BY-NC-ND 4.0",
    "copyright": "© 2026 Szabolcs Krehlik",
    "email": "szabolcs.krehlik@gmail.com",
}

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for

from . import db
from .evm_core import (
    EXTRACTOR_CONFIG_HASH,
    EXTRACTOR_VERSION_ID,
    apply_boundary_recovery,
    clamp_endpoint,
    default_fev,
    empty_boundary_counts,
    empty_identity,
    enforce_fev,
    fev_compliance_score,
    make_cis,
    make_identity_hash,
    smooth,
    stability_metrics,
    utc_now_iso,
)
from .indexing import detect_best_mood_work_query, summarize_turn
from .memory import build_memory_block, retrieve_memory
from .openai_client import configured_models, estimate_raw_target_exit, extract_entry_exit, generate_assistant_reply, plan_interaction_slice

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.template_filter("from_json")
def from_json_filter(value: str):
    return db.loads(value)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


ACTIVE_TURN_WINDOW = max(1, int(os.getenv("ACTIVE_TURN_WINDOW", "4")))
SHOW_DEBUG_PANEL = os.getenv("SHOW_DEBUG_PANEL", "1") == "1"
SHOW_EV = os.getenv("SHOW_EV", "1") == "1"
SHOW_DIA = os.getenv("SHOW_DIA", "1") == "1"
SHOW_SNAPSHOT = os.getenv("SHOW_SNAPSHOT", "1") == "1"
DEFAULT_MODE = 2 if os.getenv("DEFAULT_MODE", "2").strip() != "1" else 1

def current_models() -> Dict[str, str]:
    return configured_models()


def mirror_table_event(table_name: str, payload: Dict[str, Any]) -> None:
    db.safe_append_jsonl(f"{table_name}.ndjson", payload)


def insert_index_log(chat_id: int | None, created_at: str, category: str, payload: Dict[str, Any]) -> int:
    row_id = db.execute(
        "INSERT INTO index_log (chat_id, created_at, category, payload_json) VALUES (?, ?, ?, ?)",
        (chat_id, created_at, category, db.dumps(payload)),
    )
    mirror_table_event("index_log", {
        "id": row_id,
        "chat_id": chat_id,
        "created_at": created_at,
        "category": category,
        "payload": payload,
    })
    return row_id


def chat_messages(chat_id: int) -> List[Dict[str, str]]:
    rows = db.fetch_all(
        "SELECT role, content, created_at FROM messages WHERE chat_id = ? ORDER BY id ASC",
        (chat_id,),
    )
    return [{"role": r["role"], "content": r["content"], "created_at": r["created_at"]} for r in rows]


def get_chat(chat_id: int) -> Dict[str, Any]:
    row = db.fetch_one("SELECT * FROM chats WHERE id = ?", (chat_id,))
    if not row:
        raise ValueError(f"Chat not found: {chat_id}")
    return db.row_to_chat_dict(row)


def create_chat(title: str | None = None) -> int:
    created_at = now_iso()
    fev_lower, fev_upper, fev_center = default_fev()
    models = current_models()
    chat_id = db.execute(
        """
        INSERT INTO chats (
            title, created_at, updated_at, response_model, extractor_model,
            previous_response_id, pev_json, eev_json, fev_lower_json, fev_upper_json,
            fev_center_json, boundary_counts_json, last_identity_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title or "New Conversation",
            created_at,
            created_at,
            models["response_model"],
            models["extractor_model"],
            None,
            db.dumps(empty_identity()),
            db.dumps(empty_identity()),
            db.dumps(fev_lower),
            db.dumps(fev_upper),
            db.dumps(fev_center),
            db.dumps(empty_boundary_counts()),
            None,
        ),
    )
    insert_index_log(chat_id, created_at, "chat_created", {"title": title or "New Conversation", "provider": models["provider"]})
    return chat_id


def compact_chat_view(chat_id: int) -> Dict[str, Any]:
    return {"chat": get_chat(chat_id), "messages": chat_messages(chat_id)}


def format_endpoint(endpoint: Dict[str, Any], include_w: bool = True) -> str:
    keys = ["x", "y", "z", "g", "e"] + (["w"] if include_w else [])
    return "(" + ", ".join(f"{float(endpoint[k]):.1f}" for k in keys) + ")"


def format_segment(start: Dict[str, Any], end: Dict[str, Any], include_w: bool = True) -> str:
    return f"{format_endpoint(start, include_w=include_w)} → {format_endpoint(end, include_w=include_w)}"


def latest_snapshot_transitions(chat_id: int) -> Dict[str, Any] | None:
    rows = db.fetch_all(
        "SELECT id, created_at, pev_json, eev_json, stability_json, fev_compliance_score, cis_json FROM snapshots WHERE chat_id = ? ORDER BY id DESC LIMIT 2",
        (chat_id,),
    )
    if not rows:
        return None
    latest = rows[0]
    previous_pev = db.loads(rows[1]["pev_json"]) if len(rows) > 1 else empty_identity()
    previous_eev = db.loads(rows[1]["eev_json"]) if len(rows) > 1 else empty_identity()
    latest_pev = db.loads(latest["pev_json"])
    latest_eev = db.loads(latest["eev_json"])
    return {
        "created_at": latest["created_at"],
        "pev_prev": previous_pev,
        "pev_new": latest_pev,
        "pev_segment": format_segment(previous_pev, latest_pev, include_w=False),
        "eev_prev": previous_eev,
        "eev_new": latest_eev,
        "eev_segment": format_segment(previous_eev, latest_eev, include_w=False),
        "stability_json": latest["stability_json"],
        "fev_compliance_score": latest["fev_compliance_score"],
        "cis_json": latest["cis_json"],
    }




def axis_distance_breakdown(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    return {k: round(abs(float(a[k]) - float(b[k])), 6) for k in ["x", "y", "z", "g", "e", "w"]}


def axis_signed_correction(raw_target: Dict[str, float], controlled_target: Dict[str, float]) -> Dict[str, float]:
    return {k: round(float(controlled_target[k]) - float(raw_target[k]), 6) for k in ["x", "y", "z", "g", "e", "w"]}


def normalize_alignment_percent(total_distance: float) -> float:
    max_distance = (5 * (200.0 ** 2)) ** 0.5
    return round(min(100.0, (float(total_distance) / max_distance) * 100.0), 4)


def build_diagnostics_payload(
    user_message: str,
    planned_slice: Dict[str, Any],
    raw_target_exit: Dict[str, float],
    controlled_target_exit: Dict[str, float],
    alignment_percent: float,
    axis_alignment: Dict[str, float],
    axis_correction: Dict[str, float],
    predicted_post_eev: Dict[str, float],
    predicted_boundary_counts: Dict[str, int],
    memory_info: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    dominant_axes = sorted(axis_alignment.items(), key=lambda kv: kv[1], reverse=True)
    dominant_axes = [k.upper() for k, v in dominant_axes if v > 0.01][:3]
    notes = []
    if dominant_axes:
        notes.append(f"Primary moderation axes: {', '.join(dominant_axes)}.")
    if alignment_percent >= 40:
        notes.append("High moderation pressure before reply generation.")
    elif alignment_percent >= 20:
        notes.append("Moderate moderation pressure before reply generation.")
    else:
        notes.append("Low moderation pressure before reply generation.")
    hot_boundaries = [k.upper() for k, v in predicted_boundary_counts.items() if int(v) > 0]
    if hot_boundaries:
        notes.append(f"Boundary watch active on: {', '.join(hot_boundaries)}.")
    signed_dominant = sorted(axis_correction.items(), key=lambda kv: abs(kv[1]), reverse=True)
    signed_notes = []
    for axis, value in signed_dominant:
        if abs(value) < 0.01:
            continue
        direction = "raised" if value > 0 else "reduced"
        signed_notes.append(f"{axis.upper()} {direction} by {abs(value):.2f}")
    if signed_notes:
        notes.append("Constraint actions: " + "; ".join(signed_notes[:6]) + ".")
    return {
        "user_message": user_message,
        "raw_intent_estimate": "Estimated unconstrained target derived from current state and user entry vector.",
        "planner_notes": planned_slice.get("rationale_short", ""),
        "raw_target_exit": raw_target_exit,
        "controlled_target_exit": controlled_target_exit,
        "predicted_post_reply_eev": predicted_post_eev,
        "predicted_boundary_counts": predicted_boundary_counts,
        "alignment_percent": alignment_percent,
        "axis_alignment": axis_alignment,
        "axis_correction": axis_correction,
        "dominant_axes": dominant_axes,
        "constraint_actions": signed_notes,
        "summary": " ".join(notes).strip(),
        "memory": memory_info or {"used": False, "hits": 0},
    }


def latest_diagnostics(chat_id: int) -> Dict[str, Any] | None:
    row = db.fetch_one(
        "SELECT created_at, payload_json FROM index_log WHERE chat_id = ? AND category = ? ORDER BY id DESC LIMIT 1",
        (chat_id, "diagnostic_trace"),
    )
    if not row:
        return None
    payload = db.loads(row["payload_json"])
    payload["created_at"] = row["created_at"]
    return payload

def identity_state_for_prompt(
    chat: Dict[str, Any],
    latest_ev: Dict[str, Any] | None = None,
    planned_slice: Dict[str, Any] | None = None,
    predicted_post_eev: Dict[str, Any] | None = None,
    predicted_boundary_counts: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ev_interpretation": "Every EV is one directed interaction time-slice: entry(start) -> exit(end).",
        "pev": chat["pev"],
        "eev": chat["eev"],
        "fev_lower": chat["fev_lower"],
        "fev_upper": chat["fev_upper"],
        "fev_center": chat["fev_center"],
        "boundary_counts": chat["boundary_counts"],
    }
    if latest_ev:
        payload["latest_ev"] = {
            "turn_index": latest_ev["turn_index"],
            "entry": db.loads(latest_ev["entry_json"]),
            "exit": db.loads(latest_ev["exit_json"]),
            "segment": format_segment(db.loads(latest_ev["entry_json"]), db.loads(latest_ev["exit_json"])),
        }
    if planned_slice:
        payload["planned_slice"] = {
            "entry": planned_slice["entry"],
            "target_exit": planned_slice["exit"],
            "segment": format_segment(planned_slice["entry"], planned_slice["exit"]),
            "confidence": planned_slice.get("confidence"),
            "rationale_short": planned_slice.get("rationale_short", ""),
        }
    if predicted_post_eev:
        payload["predicted_post_reply_eev"] = predicted_post_eev
    if predicted_boundary_counts:
        payload["predicted_boundary_counts"] = predicted_boundary_counts
    return payload


def save_turn(chat_id: int, user_message: str, assistant_text: str, extracted: Dict[str, Any], diagnostics: Dict[str, Any] | None = None) -> Dict[str, Any]:
    chat = get_chat(chat_id)
    created_at = now_iso()

    previous_pev = dict(chat["pev"])
    previous_eev = dict(chat["eev"])
    entry = clamp_endpoint(extracted["entry"])
    exit_ = clamp_endpoint(extracted["exit"])
    ev = {"start": entry, "end": exit_}

    new_pev = smooth(chat["pev"], entry)
    new_eev = smooth(chat["eev"], exit_)
    new_eev = enforce_fev(new_eev, chat["fev_lower"], chat["fev_upper"])
    recovered_eev, counts, triggers = apply_boundary_recovery(
        new_eev,
        chat["fev_lower"],
        chat["fev_upper"],
        chat["fev_center"],
        chat["boundary_counts"],
    )
    recovered_eev = enforce_fev(recovered_eev, chat["fev_lower"], chat["fev_upper"])

    previous_hash = chat["last_identity_hash"]
    identity_hash = make_identity_hash(previous_hash, entry, exit_, f"default_chat_{chat_id}", "evm_policy_default")
    cis = make_cis(chat_id, new_pev, recovered_eev, chat["fev_center"], identity_hash, previous_hash)
    stability = stability_metrics(new_pev, recovered_eev, chat["fev_center"])
    compliance = fev_compliance_score(recovered_eev, chat["fev_lower"], chat["fev_upper"])

    title = chat["title"]
    if title == "New Conversation":
        title = (user_message[:60] + "...") if len(user_message) > 60 else user_message

    db.execute_many(
        "INSERT INTO messages (chat_id, role, content, created_at, openai_response_id) VALUES (?, ?, ?, ?, ?)",
        [
            (chat_id, "user", user_message, created_at, None),
            (chat_id, "assistant", assistant_text, created_at, None),
        ],
    )
    mirror_table_event("messages", {"chat_id": chat_id, "role": "user", "content": user_message, "created_at": created_at})
    mirror_table_event("messages", {"chat_id": chat_id, "role": "assistant", "content": assistant_text, "created_at": created_at})

    turn_index_row = db.fetch_one("SELECT COALESCE(MAX(turn_index), 0) AS max_turn FROM ev_records WHERE chat_id = ?", (chat_id,))
    turn_index = int(turn_index_row["max_turn"]) + 1
    notes = extracted.get("rationale_short", "")

    ev_row_id = db.execute(
        """
        INSERT INTO ev_records (
            chat_id, turn_index, created_at, entry_json, exit_json, ev_json,
            extractor_version_id, extractor_config_hash, extraction_timestamp, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            turn_index,
            created_at,
            db.dumps(entry),
            db.dumps(exit_),
            db.dumps(ev),
            EXTRACTOR_VERSION_ID,
            EXTRACTOR_CONFIG_HASH,
            utc_now_iso(),
            notes,
        ),
    )
    mirror_table_event("ev_records", {
        "id": ev_row_id,
        "chat_id": chat_id,
        "turn_index": turn_index,
        "created_at": created_at,
        "entry": entry,
        "exit": exit_,
        "ev": ev,
        "extractor_version_id": EXTRACTOR_VERSION_ID,
        "extractor_config_hash": EXTRACTOR_CONFIG_HASH,
        "notes": notes,
    })

    snapshot_row_id = db.execute(
        """
        INSERT INTO snapshots (
            chat_id, created_at, pev_json, eev_json, fev_center_json,
            stability_json, fev_compliance_score, cis_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            created_at,
            db.dumps(new_pev),
            db.dumps(recovered_eev),
            db.dumps(chat["fev_center"]),
            db.dumps(stability),
            compliance,
            db.dumps(cis),
        ),
    )
    mirror_table_event("snapshots", {
        "id": snapshot_row_id,
        "chat_id": chat_id,
        "created_at": created_at,
        "pev": new_pev,
        "eev": recovered_eev,
        "fev_center": chat["fev_center"],
        "stability": stability,
        "fev_compliance_score": compliance,
        "cis": cis,
    })

    db.execute(
        """
        UPDATE chats
        SET title = ?, updated_at = ?, pev_json = ?, eev_json = ?, boundary_counts_json = ?, last_identity_hash = ?
        WHERE id = ?
        """,
        (
            title,
            created_at,
            db.dumps(new_pev),
            db.dumps(recovered_eev),
            db.dumps(counts),
            identity_hash,
            chat_id,
        ),
    )

    insert_index_log(
        chat_id,
        created_at,
        "turn_committed",
        {
            "turn_index": turn_index,
            "boundary_recovery_axes": triggers,
            "confidence": extracted.get("confidence"),
            "ev_segment": format_segment(entry, exit_),
        },
    )
    turn_summary = summarize_turn(user_message, assistant_text, extracted, turn_index)
    insert_index_log(chat_id, created_at, "turn_summary", turn_summary)
    if diagnostics is not None:
        diagnostics_payload = dict(diagnostics)
        diagnostics_payload["turn_index"] = turn_index
        insert_index_log(chat_id, created_at, "diagnostic_trace", diagnostics_payload)

    return {
        "created_at": created_at,
        "turn_index": turn_index,
        "entry": entry,
        "exit": exit_,
        "notes": notes,
        "ev_segment": format_segment(entry, exit_),
        "pev_prev": previous_pev,
        "pev": new_pev,
        "pev_segment": format_segment(previous_pev, new_pev, include_w=False),
        "eev_prev": previous_eev,
        "eev": recovered_eev,
        "eev_segment": format_segment(previous_eev, recovered_eev, include_w=False),
        "fev_lower": chat["fev_lower"],
        "fev_upper": chat["fev_upper"],
        "fev_center": chat["fev_center"],
        "fev_segment": format_segment(chat["fev_lower"], chat["fev_upper"], include_w=False),
        "boundary_counts": counts,
        "stability": stability,
        "fev_compliance_score": compliance,
        "boundary_recovery_axes": triggers,
        "cis": cis,
        "diagnostics": diagnostics,
    }


def state_payload(chat_id: int) -> Dict[str, Any]:
    payload = compact_chat_view(chat_id)
    ev_rows_raw = db.fetch_all(
        "SELECT turn_index, created_at, entry_json, exit_json, notes FROM ev_records WHERE chat_id = ? ORDER BY turn_index DESC LIMIT 20",
        (chat_id,),
    )
    ev_rows = []
    for row in ev_rows_raw:
        d = dict(row)
        d["entry"] = db.loads(d["entry_json"])
        d["exit"] = db.loads(d["exit_json"])
        d["ev_segment"] = format_segment(d["entry"], d["exit"])
        ev_rows.append(d)
    latest_ev = ev_rows[0] if ev_rows else None
    latest_snapshot = latest_snapshot_transitions(chat_id)
    latest_dia = latest_diagnostics(chat_id)
    models = current_models()
    return {
        "chat": payload["chat"],
        "messages": payload["messages"],
        "latest_ev": latest_ev,
        "latest_snapshot": latest_snapshot,
        "latest_dia": latest_dia,
        "app_metadata": APP_METADATA,
        "ev_rows": ev_rows,
        "provider": models["provider"],
        "response_model": models["response_model"],
        "extractor_model": models["extractor_model"],
    }


@app.route("/")
def index():
    chats = db.fetch_all("SELECT id, title, updated_at FROM chats ORDER BY updated_at DESC")
    current_id = request.args.get("chat_id", type=int)
    if current_id is None:
        if chats:
            return redirect(url_for("index", chat_id=chats[0]["id"]))
        current_id = create_chat()
        return redirect(url_for("index", chat_id=current_id))

    payload = state_payload(current_id)
    return render_template(
        "index.html",
        chats=chats,
        current_chat=payload["chat"],
        messages=payload["messages"],
        ev_rows=payload["ev_rows"],
        latest_ev=payload["latest_ev"],
        latest_snapshot=payload["latest_snapshot"],
        api_key_present=bool((os.getenv("OPENAI_API_KEY", "") + os.getenv("XAI_API_KEY", "") + os.getenv("LLM_API_KEY", "")).strip()),
        provider=payload["provider"],
        response_model=payload["response_model"],
        extractor_model=payload["extractor_model"],
        show_debug_panel=SHOW_DEBUG_PANEL,
        show_ev=SHOW_EV,
        show_dia=SHOW_DIA,
        show_snapshot=SHOW_SNAPSHOT,
        app_metadata=payload["app_metadata"],
        fmt_endpoint=format_endpoint,
        fmt_segment=format_segment,
    )


@app.post("/api/new_chat")
def api_new_chat():
    title = (request.json or {}).get("title")
    chat_id = create_chat(title)
    return jsonify({"chat_id": chat_id})


@app.get("/api/state")
def api_state():
    chat_id = request.args.get("chat_id", type=int)
    if not chat_id:
        return jsonify({"error": "chat_id missing"}), 400
    return jsonify(state_payload(chat_id))


@app.post("/api/send")
def api_send():
    try:
        body = request.json or {}
        chat_id = int(body.get("chat_id"))
        user_message = (body.get("message") or "").strip()
        if not user_message:
            return jsonify({"error": "Empty message."}), 400

        mode = 2
        chat = get_chat(chat_id)
        recent = chat_messages(chat_id)
        latest_ev = db.fetch_one(
            "SELECT turn_index, entry_json, exit_json FROM ev_records WHERE chat_id = ? ORDER BY turn_index DESC LIMIT 1",
            (chat_id,),
        )
        memory_block = None
        memory = None
        recent_window = ACTIVE_TURN_WINDOW * 2
        if mode == 2:
            memory = retrieve_memory(chat_id, user_message)
            memory_block = build_memory_block(memory)
        else:
            recent_window = max(2, min(ACTIVE_TURN_WINDOW * 2, 4))
        models = current_models()

        planning_state = identity_state_for_prompt(chat, dict(latest_ev) if latest_ev else None)
        planned_slice = plan_interaction_slice(
            model=models["extractor_model"],
            recent_messages=recent[-recent_window:],
            user_message=user_message,
            identity_state=planning_state,
        )
        raw_target_exit = estimate_raw_target_exit(planned_slice["entry"], chat["eev"])
        controlled_target_exit = dict(planned_slice["exit"])
        axis_alignment = axis_distance_breakdown(raw_target_exit, controlled_target_exit)
        axis_correction = axis_signed_correction(raw_target_exit, controlled_target_exit)
        alignment_total = sum(v * v for v in axis_alignment.values()) ** 0.5
        alignment_percent = normalize_alignment_percent(alignment_total)

        predicted_post_eev = smooth(chat["eev"], controlled_target_exit)
        predicted_post_eev = enforce_fev(predicted_post_eev, chat["fev_lower"], chat["fev_upper"])
        predicted_post_eev, predicted_counts, _ = apply_boundary_recovery(
            predicted_post_eev,
            chat["fev_lower"],
            chat["fev_upper"],
            chat["fev_center"],
            chat["boundary_counts"],
        )
        predicted_post_eev = enforce_fev(predicted_post_eev, chat["fev_lower"], chat["fev_upper"])
        diagnostics = build_diagnostics_payload(
            user_message=user_message,
            planned_slice=planned_slice,
            raw_target_exit=raw_target_exit,
            controlled_target_exit=controlled_target_exit,
            alignment_percent=alignment_percent,
            axis_alignment=axis_alignment,
            axis_correction=axis_correction,
            predicted_post_eev=predicted_post_eev,
            predicted_boundary_counts=predicted_counts,
            memory_info={
                "used": bool(memory and memory.used),
                "reason": getattr(memory, "reason", None),
                "hits": len(memory.snippets) if memory else 0,
                "date_filter": list(memory.date_filter) if memory and memory.date_filter else None,
                "search_terms": memory.search_terms if memory else [],
            },
        )
        identity_state = identity_state_for_prompt(
            chat,
            dict(latest_ev) if latest_ev else None,
            planned_slice=planned_slice,
            predicted_post_eev=predicted_post_eev,
            predicted_boundary_counts=predicted_counts,
        )
        identity_state["diagnostic_trace"] = diagnostics

        reply = generate_assistant_reply(
            model=models["response_model"],
            identity_state=identity_state,
            recent_messages=recent[-recent_window:],
            user_message=user_message,
            memory_block=memory_block,
            mode=mode,
        )
        assistant_text = reply["text"].strip()

        extracted = extract_entry_exit(
            model=models["extractor_model"],
            recent_messages=(recent + [{"role": "user", "content": user_message}])[-(ACTIVE_TURN_WINDOW*2+1):],
            user_message=user_message,
            assistant_reply=assistant_text,
        )
        state = save_turn(chat_id, user_message, assistant_text, extracted, diagnostics=diagnostics)
        return jsonify({"assistant": assistant_text, "evm": state, "mode": mode, "diagnostics": diagnostics})
    except Exception as exc:
        app.logger.exception("/api/send failed")
        return jsonify({"error": str(exc)}), 500


@app.get("/api/search")
def api_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"results": []})

    if detect_best_mood_work_query(q):
        idx_rows = db.fetch_all(
            """
            SELECT i.chat_id, c.title, i.category, i.payload_json, i.created_at
            FROM index_log i
            LEFT JOIN chats c ON c.id = i.chat_id
            WHERE i.category = 'turn_summary' AND json_extract(i.payload_json, '$.work_context') = 1
            ORDER BY CAST(json_extract(i.payload_json, '$.user_mood_e') AS REAL) DESC, i.created_at DESC
            LIMIT 25
            """
        )
        enriched = []
        for row in idx_rows:
            payload = db.loads(row["payload_json"])
            enriched.append(
                {
                    "chat_id": row["chat_id"],
                    "title": row["title"],
                    "category": row["category"],
                    "created_at": row["created_at"],
                    "payload_json": row["payload_json"],
                    "content": f"mood={payload.get('user_mood_e')} | topics={', '.join(payload.get('keywords') or [])} | user={payload.get('user_excerpt','')}",
                    "summary": payload.get("headline"),
                    "user_mood_e": payload.get("user_mood_e"),
                    "work_context": payload.get("work_context"),
                    "keywords": payload.get("keywords"),
                    "user_excerpt": payload.get("user_excerpt"),
                    "assistant_excerpt": payload.get("assistant_excerpt"),
                }
            )
        return jsonify({"results": {"messages": [], "index_log": enriched, "ev_notes": []}})

    like = f"%{q}%"
    msg_rows = db.fetch_all(
        """
        SELECT m.chat_id, c.title, m.role, m.content, m.created_at
        FROM messages m
        JOIN chats c ON c.id = m.chat_id
        WHERE m.content LIKE ?
        ORDER BY m.created_at DESC
        LIMIT 100
        """,
        (like,),
    )
    idx_rows = db.fetch_all(
        """
        SELECT i.chat_id, c.title, i.category, i.payload_json, i.created_at
        FROM index_log i
        LEFT JOIN chats c ON c.id = i.chat_id
        WHERE i.payload_json LIKE ? OR i.category LIKE ?
        ORDER BY i.created_at DESC
        LIMIT 100
        """,
        (like, like),
    )
    ev_rows = db.fetch_all(
        """
        SELECT e.chat_id, c.title, 'ev_segment' AS role,
               ('Turn ' || e.turn_index || ' ' || e.entry_json || ' -> ' || e.exit_json || ' Notes: ' || COALESCE(e.notes,'')) AS content,
               e.created_at
        FROM ev_records e
        JOIN chats c ON c.id = e.chat_id
        WHERE e.notes LIKE ? OR e.entry_json LIKE ? OR e.exit_json LIKE ?
        ORDER BY e.created_at DESC
        LIMIT 100
        """,
        (like, like, like),
    )
    return jsonify(
        {
            "results": {
                "messages": [dict(r) for r in msg_rows],
                "index_log": [dict(r) for r in idx_rows],
                "ev_notes": [dict(r) for r in ev_rows],
            }
        }
    )


@app.get("/api/export/cis/<int:chat_id>")
def api_export_cis(chat_id: int):
    row = db.fetch_one(
        "SELECT cis_json FROM snapshots WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
        (chat_id,),
    )
    if not row:
        return jsonify({"error": "Nincs snapshot ehhez a chathez."}), 404
    return jsonify(db.loads(row["cis_json"]))


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/health")
def health():
    return jsonify({"ok": True})


def create_app() -> Flask:
    db.init_db()
    return app


if __name__ == "__main__":
    db.init_db()
    port = int(os.getenv("PORT", "8765"))
    app.run(host="127.0.0.1", port=port, debug=False)
