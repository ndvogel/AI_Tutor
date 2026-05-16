# utils.py
# Shared utility functions: JSON I/O, token budget helpers, logging.
import os
import json
from datetime import datetime
from typing import Dict, Any, List

PROFILE_PATH = os.path.join("config", "student_profile.json")
PROGRESS_PATH = os.path.join("config", "learning_progress.json")


def initialize_storage() -> None:
    """Initializes empty JSON storage files if they don't exist."""
    os.makedirs("config", exist_ok=True)

    if not os.path.exists(PROFILE_PATH):
        save_profile({
            "student_name": "",
            "target_subject": "",
            "generational_bracket": "",
            "core_interests": [],
            "preferred_delivery": "",
            "custom_mental_models": [],
            "no_analogy_nodes": []
        })

    if not os.path.exists(PROGRESS_PATH):
        save_progress({
            "current_node_id": None,
            "nodes": {},
            "friction_cycle_count": 0,
            "session_turn_count": 0,
            "last_3_turns": []
        })


def load_profile() -> Dict[str, Any]:
    """Reads and returns the student profile."""
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(data: Dict[str, Any]) -> None:
    """Saves the student profile."""
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_progress() -> Dict[str, Any]:
    """Reads and returns the learning progress."""
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(data: Dict[str, Any]) -> None:
    """Saves the learning progress."""
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_node(node_id: str, node_data: Dict[str, Any]) -> None:
    """Updates or inserts a node in learning_progress.json.
    Preserves any optional blocks (e.g. 'remediation') that live outside the canonical schema."""
    progress = load_progress()
    existing = progress["nodes"].get(node_id, {})
    record: Dict[str, Any] = {
        "node_id": node_id,
        "title": node_data.get("title", "Unknown Concept"),
        "prerequisites": node_data.get("prerequisites", []),
        "status": node_data.get("status", "locked"),
        "friction_cycle_count": node_data.get("friction_cycle_count", 0),
        "consecutive_failures": node_data.get("consecutive_failures", 0),
        "attempts": node_data.get("attempts", 0),
        "success_rate": node_data.get("success_rate", 0.0),
        "active_interest_used": node_data.get("active_interest_used", None),
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }
    if "remediation" in existing:
        record["remediation"] = existing["remediation"]
    progress["nodes"][node_id] = record
    save_progress(progress)


def save_remediation(node_id: str, remediation_data: Dict[str, Any]) -> None:
    """Writes the optional remediation block into a node record without touching the 9 canonical fields."""
    progress = load_progress()
    if node_id in progress["nodes"]:
        progress["nodes"][node_id]["remediation"] = remediation_data
        save_progress(progress)


def clear_remediation(node_id: str) -> None:
    """Removes the remediation block from a node record."""
    progress = load_progress()
    if node_id in progress["nodes"]:
        progress["nodes"][node_id].pop("remediation", None)
        save_progress(progress)


def unlock_dependents(mastered_node_id: str) -> List[str]:
    """Unlocks any locked nodes whose prerequisites are all now mastered."""
    progress = load_progress()
    newly_unlocked = []
    for nid, node in progress["nodes"].items():
        if node["status"] != "locked":
            continue
        prereqs = node.get("prerequisites", [])
        if mastered_node_id not in prereqs:
            continue
        if all(progress["nodes"].get(p, {}).get("status") == "mastered" for p in prereqs):
            node["status"] = "unlocked"
            node["last_updated"] = datetime.utcnow().isoformat() + "Z"
            newly_unlocked.append(nid)
    if newly_unlocked:
        save_progress(progress)
    return newly_unlocked


def append_turn(role: str, content: str) -> None:
    """Appends a turn to last_3_turns, evicting oldest if over 3."""
    progress = load_progress()
    buffer: List[Dict[str, str]] = progress.get("last_3_turns", [])
    buffer.append({"role": role, "content": content})
    if len(buffer) > 3:
        buffer.pop(0)
    progress["last_3_turns"] = buffer
    save_progress(progress)


def increment_turn_count() -> bool:
    """Increments turn count. Returns True if threshold of 5 is reached."""
    progress = load_progress()
    count = progress.get("session_turn_count", 0) + 1
    progress["session_turn_count"] = count
    if count >= 5:
        progress["session_turn_count"] = 0
        save_progress(progress)
        return True
    save_progress(progress)
    return False
