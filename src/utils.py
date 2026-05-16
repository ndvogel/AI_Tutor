import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Define file paths relative to the project root
PROFILE_PATH = os.path.join("config", "student_profile.json")
PROGRESS_PATH = os.path.join("config", "learning_progress.json")


def initialize_storage() -> None:
    """Initializes empty JSON storage files matching the Section 8 schemas if they don't exist."""
    # Ensure config directory exists
    os.makedirs("config", exist_ok=True)

    if not os.path.exists(PROFILE_PATH):
        default_profile = {
            "student_name": "",
            "target_subject": "",
            "generational_bracket": "",
            "core_interests": [],
            "preferred_delivery": "",
            "custom_mental_models": [],
            "no_analogy_nodes": []
        }
        save_profile(default_profile)

    if not os.path.exists(PROGRESS_PATH):
        default_progress = {
            "current_node_id": None,
            "nodes": {},
            "friction_cycle_count": 0,
            "session_turn_count": 0,
            "last_3_turns": []
        }
        save_progress(default_progress)


# ==========================================
# 💾 CORE FILE I/O OPERATIONS
# ==========================================

def load_profile() -> Dict[str, Any]:
    """Reads and returns the student profile configuration."""
    with open(PROFILE_PATH, "r" if os.path.exists(PROFILE_PATH) else "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(data: Dict[str, Any]) -> None:
    """Safely overwrites the student profile configuration."""
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_progress() -> Dict[str, Any]:
    """Reads and returns the learning progress configuration."""
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(data: Dict[str, Any]) -> None:
    """Safely overwrites the learning progress configuration."""
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ==========================================
# 🔄 SECTION 8 STATE MUTATION FUNCTIONS
# ==========================================

def save_node(node_id: str, node_data: Dict[str, Any]) -> None:
    """Updates or inserts a specific node in learning_progress.json.

    Guarantees Section 8.1 schema adherence.
    """
    progress = load_progress()

    # Enforce Section 8.1 Canonical Node Schema fields
    required_fields = {
        "node_id": node_id,
        "title": node_data.get("title", "Unknown Concept"),
        "prerequisites": node_data.get("prerequisites", []),
        "status": node_data.get("status", "locked"),
        "friction_cycle_count": node_data.get("friction_cycle_count", 0),
        "consecutive_failures": node_data.get("consecutive_failures", 0),
        "attempts": node_data.get("attempts", 0),
        "success_rate": node_data.get("success_rate", 0.0),
        "active_interest_used": node_data.get("active_interest_used", None),
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    progress["nodes"][node_id] = required_fields
    save_progress(progress)


def append_turn(role: str, content: str) -> None:
    """Appends a turn to last_3_turns, evicting oldest if buffer exceeds 3 (Section 8.3)."""
    progress = load_progress()
    buffer: List[Dict[str, str]] = progress.get("last_3_turns", [])

    buffer.append({"role": role, "content": content})

    # Evict oldest turn if we cross the maximum context window cap
    if len(buffer) > 3:
        buffer.pop(0)

    progress["last_3_turns"] = buffer
    save_progress(progress)


def increment_turn_count() -> bool:
    """Increments session_turn_count. Returns True if truncation threshold (5) is reached."""
    progress = load_progress()
    count = progress.get("session_turn_count", 0) + 1

    progress["session_turn_count"] = count

    # Reset loop tracker if we cross threshold limit
    if count >= 5:
        progress["session_turn_count"] = 0
        save_progress(progress)
        return True

    save_progress(progress)
    return False
