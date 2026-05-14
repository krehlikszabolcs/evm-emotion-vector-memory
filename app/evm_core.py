from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

AXES = ["x", "y", "z", "g", "e"]
AXES_W = AXES + ["w"]
DEFAULT_BETA = 0.35
DEFAULT_ALPHA = 0.5
DEFAULT_BOUNDARY_PERSISTENCE = 6
EXTRACTOR_VERSION_ID = "evm_openai_web_1.0.0"
EXTRACTOR_CONFIG = {
    "schema": "entry_exit_strict_v1",
    "beta": DEFAULT_BETA,
    "alpha": DEFAULT_ALPHA,
    "boundary_persistence": DEFAULT_BOUNDARY_PERSISTENCE,
    "temperature": 0,
    "reasoning_effort": "medium",
}
EXTRACTOR_CONFIG_HASH = hashlib.sha256(
    json.dumps(EXTRACTOR_CONFIG, sort_keys=True).encode("utf-8")
).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_fev() -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
    lower = {"x": -80.0, "y": -70.0, "z": -40.0, "g": -30.0, "e": -35.0}
    upper = {"x": 90.0, "y": 80.0, "z": 85.0, "g": 70.0, "e": 45.0}
    center = {k: round((lower[k] + upper[k]) / 2.0, 6) for k in AXES}
    return lower, upper, center


def empty_identity() -> Dict[str, float]:
    return {k: 0.0 for k in AXES}


def empty_boundary_counts() -> Dict[str, int]:
    return {k: 0 for k in AXES}


def clamp(value: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, value)))


def clamp_endpoint(endpoint: Dict[str, float]) -> Dict[str, float]:
    out = {}
    for k in AXES:
        out[k] = round(clamp(float(endpoint[k]), -100.0, 100.0), 6)
    out["w"] = round(clamp(float(endpoint["w"]), 0.0, 100.0), 6)
    return out


def smooth(prev: Dict[str, float], endpoint: Dict[str, float], beta: float = DEFAULT_BETA) -> Dict[str, float]:
    return {k: round(beta * float(endpoint[k]) + (1.0 - beta) * float(prev[k]), 6) for k in AXES}


def enforce_fev(eev: Dict[str, float], fev_lower: Dict[str, float], fev_upper: Dict[str, float]) -> Dict[str, float]:
    return {k: round(clamp(float(eev[k]), float(fev_lower[k]), float(fev_upper[k])), 6) for k in AXES}


def apply_boundary_recovery(
    eev: Dict[str, float],
    fev_lower: Dict[str, float],
    fev_upper: Dict[str, float],
    fev_center: Dict[str, float],
    boundary_counts: Dict[str, int],
    alpha: float = DEFAULT_ALPHA,
    persistence_n: int = DEFAULT_BOUNDARY_PERSISTENCE,
):
    eev_new = deepcopy(eev)
    counts_new = deepcopy(boundary_counts)
    triggers: List[str] = []
    for axis in AXES:
        t_a = 0.8 * (float(fev_upper[axis]) - float(fev_lower[axis])) / 2.0
        if abs(float(eev_new[axis]) - float(fev_center[axis])) >= t_a:
            counts_new[axis] = int(counts_new.get(axis, 0)) + 1
        else:
            counts_new[axis] = 0
        if counts_new[axis] >= persistence_n:
            eev_new[axis] = round(alpha * float(eev_new[axis]) + (1.0 - alpha) * float(fev_center[axis]), 6)
            counts_new[axis] = 0
            triggers.append(axis)
    return eev_new, counts_new, triggers


def euclidean_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    return math.sqrt(sum((float(a[k]) - float(b[k])) ** 2 for k in AXES))


def fev_compliance_score(eev: Dict[str, float], fev_lower: Dict[str, float], fev_upper: Dict[str, float]) -> float:
    total = 0.0
    for axis in AXES:
        lo = float(fev_lower[axis])
        hi = float(fev_upper[axis])
        val = float(eev[axis])
        if lo <= val <= hi:
            total += 1.0
    return round((total / len(AXES)) * 100.0, 6)


def make_identity_hash(previous_hash: str | None, entry_endpoint: Dict[str, float], exit_endpoint: Dict[str, float], fev_profile_id: str, policy_id: str) -> str:
    payload = json.dumps(
        {
            "previous_hash": previous_hash or "",
            "entry": entry_endpoint,
            "exit": exit_endpoint,
            "fev_profile_id": fev_profile_id,
            "policy_id": policy_id,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_cis(chat_id: int, pev: Dict[str, float], eev: Dict[str, float], fev_center: Dict[str, float], identity_hash: str, previous_hash: str | None) -> Dict[str, Any]:
    return {
        "schema_id": "evm_cis_v1",
        "evm_version": "2.1",
        "metric_id": "euclidean_default",
        "axis_weights": [1, 1, 1, 1, 1],
        "fev_profile_id": f"default_chat_{chat_id}",
        "fev_center": [fev_center[k] for k in AXES],
        "pev_vector": [pev[k] for k in AXES],
        "eev_vector": [eev[k] for k in AXES],
        "snapshot_timestamp": utc_now_iso(),
        "extractor_version_id": EXTRACTOR_VERSION_ID,
        "extractor_config_hash": EXTRACTOR_CONFIG_HASH,
        "identity_state_hash": identity_hash,
        "previous_identity_state_hash": previous_hash,
    }


def stability_metrics(pev: Dict[str, float], eev: Dict[str, float], fev_center: Dict[str, float]) -> Dict[str, float]:
    return {
        "pev_norm_from_center": round(euclidean_distance(pev, fev_center), 6),
        "eev_norm_from_center": round(euclidean_distance(eev, fev_center), 6),
        "pev_eev_distance": round(euclidean_distance(pev, eev), 6),
    }
