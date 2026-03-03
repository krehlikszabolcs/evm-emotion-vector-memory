import json
import hashlib
from typing import Dict, Any, Optional

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def make_identity_hash(previous_hash: str, entry_endpoint, exit_endpoint, fev_profile_id: str, policy_id: str) -> str:
    payload = f"{previous_hash}|{entry_endpoint}|{exit_endpoint}|{fev_profile_id}|{policy_id}"
    return "sha256:" + sha256_hex(payload)

def cis_snapshot(evm_version: str,
                 metric_id: str,
                 axis_weights,
                 fev_profile_id: str,
                 fev_center,
                 pev_vector,
                 eev_vector,
                 snapshot_timestamp: str,
                 extractor_version_id: str,
                 extractor_config_hash: str,
                 identity_state_hash: str,
                 previous_identity_state_hash: Optional[str]) -> Dict[str, Any]:
    return {
        "schema_id": "evm_cis_v1",
        "evm_version": evm_version,
        "metric_id": metric_id,
        "axis_weights": axis_weights,
        "fev_profile_id": fev_profile_id,
        "fev_center": fev_center,
        "pev_vector": pev_vector,
        "eev_vector": eev_vector,
        "snapshot_timestamp": snapshot_timestamp,
        "extractor_version_id": extractor_version_id,
        "extractor_config_hash": extractor_config_hash,
        "identity_state_hash": identity_state_hash,
        "previous_identity_state_hash": previous_identity_state_hash
    }

def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
