# test_view_progress.py
# Tests for main.view_progress() (src/main.py).
#
# view_progress() is pure console output driven by utils.load_progress(), so
# every test here monkeypatches main.load_progress (the name bound into
# main's module namespace via `from utils import ... load_progress ...`)
# rather than touching the real learning_progress.json file. Output is
# captured via pytest's `capsys` fixture.
#
# Run with:  python -m pytest tests/test_view_progress.py -v
# (requires tests/conftest.py, which puts src/ on sys.path so `import main`
# resolves the same way main.py resolves its own sibling imports.)

import json

import pytest

import main


def _progress(nodes):
    """Builds a minimal learning_progress.json-shaped dict with the given nodes."""
    return {
        "current_node_id": None,
        "nodes": nodes,
        "friction_cycle_count": 0,
        "session_turn_count": 0,
        "last_3_turns": [],
    }


def _node(title=None, status=None, node_id="some_node", prerequisites=None):
    """Builds a canonical node record; omits title/status if None so callers
    can exercise the .get(...) fallback paths in view_progress()."""
    record = {
        "node_id": node_id,
        "prerequisites": prerequisites or [],
        "friction_cycle_count": 0,
        "consecutive_failures": 0,
        "attempts": 0,
        "success_rate": 0.0,
        "active_interest_used": None,
        "last_updated": "2026-05-16T22:33:19.049447Z",
    }
    if title is not None:
        record["title"] = title
    if status is not None:
        record["status"] = status
    return record


# --- Happy path ---------------------------------------------------------


def test_view_progress_prints_header_and_all_nodes_when_nodes_present(monkeypatch, capsys):
    nodes = {
        "introduction_to_apis": _node(title="Introduction to APIs", status="mastered"),
        "http_fundamentals": _node(title="HTTP Fundamentals", status="unlocked"),
    }
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "=== Curriculum Progress ===" in out
    # "mastered" and "unlocked" are exactly 8 chars, so {status:8} adds no padding
    assert "[mastered] introduction_to_apis — Introduction to APIs" in out
    assert "[unlocked] http_fundamentals — HTTP Fundamentals" in out


def test_view_progress_prints_nodes_in_dict_insertion_order(monkeypatch, capsys):
    nodes = {
        "z_node": _node(title="Z Node", status="locked"),
        "a_node": _node(title="A Node", status="mastered"),
    }
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    z_index = out.index("z_node")
    a_index = out.index("a_node")
    assert z_index < a_index, "expected dict insertion order (z_node before a_node), not sorted"


# --- Empty / boundary cases ---------------------------------------------


def test_view_progress_prints_no_nodes_message_when_nodes_dict_is_empty(monkeypatch, capsys):
    monkeypatch.setattr(main, "load_progress", lambda: _progress({}))

    main.view_progress()

    out = capsys.readouterr().out
    assert out.strip() == "No curriculum nodes found. Run option 1 first."
    assert "=== Curriculum Progress ===" not in out


def test_view_progress_treats_none_nodes_as_empty(monkeypatch, capsys):
    """Malformed storage: 'nodes' present but explicitly null instead of {}.
    `if not nodes` is falsy for None too, so this should hit the same
    'no nodes' branch rather than crash."""
    monkeypatch.setattr(main, "load_progress", lambda: _progress(None))

    main.view_progress()

    out = capsys.readouterr().out
    assert "No curriculum nodes found. Run option 1 first." in out
    assert "=== Curriculum Progress ===" not in out


def test_view_progress_single_node_boundary_case(monkeypatch, capsys):
    nodes = {"only_node": _node(title="Only Node", status="unlocked")}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "=== Curriculum Progress ===" in out
    assert "[unlocked] only_node — Only Node" in out
    # exactly one node line was printed (header line + 1 node line, plus the
    # leading blank line from the print("\n=== ... ===") call)
    non_blank_lines = [line for line in out.splitlines() if line.strip()]
    assert len(non_blank_lines) == 2


# --- Missing-field fallbacks ---------------------------------------------


def test_view_progress_falls_back_to_unknown_concept_when_title_missing(monkeypatch, capsys):
    nodes = {"mystery_node": _node(title=None, status="locked")}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "[locked  ] mystery_node — Unknown Concept" in out


def test_view_progress_falls_back_to_unknown_status_when_status_missing(monkeypatch, capsys):
    nodes = {"mystery_node": _node(title="Mystery Node", status=None)}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "[unknown ] mystery_node — Mystery Node" in out


def test_view_progress_falls_back_for_both_missing_title_and_status(monkeypatch, capsys):
    nodes = {"blank_node": _node(title=None, status=None)}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "[unknown ] blank_node — Unknown Concept" in out


# --- Unusual / future status strings -------------------------------------


@pytest.mark.parametrize(
    "status",
    ["conditionally_skipped", "force_locked", "pending_review", ""],
)
def test_view_progress_prints_unusual_status_strings_verbatim(monkeypatch, capsys, status):
    """Status is printed as-is, not filtered, validated, or translated
    against a known set of statuses."""
    nodes = {"weird_node": _node(title="Weird Node", status=status)}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    # Check the exact formatted line, not just substring containment of
    # `status` — that would be trivially true for status == "" against any
    # output. This also pins down exact padding for every case: e.g. an
    # empty status must render as 8 literal spaces inside the brackets
    # ("[        ]"), not as an empty or missing field.
    expected_line = f"  [{status:8}] weird_node — Weird Node"
    assert expected_line in out


def test_view_progress_does_not_truncate_status_longer_than_field_width(monkeypatch, capsys):
    nodes = {"weird_node": _node(title="Weird Node", status="conditionally_skipped")}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    assert "[conditionally_skipped] weird_node — Weird Node" in out


def test_view_progress_pads_short_status_to_width_eight(monkeypatch, capsys):
    nodes = {"n": _node(title="N", status="locked")}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    main.view_progress()

    out = capsys.readouterr().out
    # "locked" is 6 chars; format spec {status:8} left-aligns by default for
    # strings and pads with 2 trailing spaces.
    assert "[locked  ] n — N" in out


# --- Malformed storage / sequencing bugs ---------------------------------


def test_view_progress_raises_keyerror_when_nodes_key_missing_entirely():
    """Malformed progress.json (or a stub returned by a bad mock) that lacks
    the 'nodes' key entirely should surface as a KeyError, not be silently
    swallowed into an empty-progress message."""
    malformed = {"current_node_id": None}

    orig_load_progress = main.load_progress
    main.load_progress = lambda: malformed
    try:
        with pytest.raises(KeyError):
            main.view_progress()
    finally:
        main.load_progress = orig_load_progress


def test_view_progress_raises_when_a_node_value_is_not_a_dict(monkeypatch):
    """Partial/corrupted state: a node entry that's a bare string instead of
    a record dict should blow up loudly (AttributeError on .get) rather than
    print something misleading."""
    nodes = {"corrupt_node": "this should be a dict"}
    monkeypatch.setattr(main, "load_progress", lambda: _progress(nodes))

    with pytest.raises(AttributeError):
        main.view_progress()


def test_view_progress_prints_graceful_message_when_storage_uninitialized(monkeypatch, capsys):
    """Sequencing bug guard: if initialize_storage() was never run (or the
    file was deleted/became unreadable mid-session) and learning_progress.json
    doesn't exist, load_progress() raises FileNotFoundError. view_progress()
    now routes the load through utils.load_safe(), which catches that and
    returns None, so view_progress() should print a clear guidance message
    and return normally instead of letting the exception propagate."""

    def _raise_missing_file():
        raise FileNotFoundError("learning_progress.json not found")

    monkeypatch.setattr(main, "load_progress", _raise_missing_file)

    main.view_progress()

    out = capsys.readouterr().out
    assert out.strip() == "Storage not initialized. Please run option 1 (Onboarding) first."
    assert "=== Curriculum Progress ===" not in out


def test_view_progress_prints_graceful_message_when_storage_corrupt(monkeypatch, capsys):
    """If learning_progress.json exists but contains invalid JSON,
    load_progress() (via json.load) raises json.JSONDecodeError. view_progress()
    now routes the load through utils.load_safe(), which catches that and
    returns None, so view_progress() should print a clear guidance message
    and return normally instead of letting the exception propagate."""

    def _raise_bad_json():
        raise json.JSONDecodeError("Expecting value", doc="", pos=0)

    monkeypatch.setattr(main, "load_progress", _raise_bad_json)

    main.view_progress()

    out = capsys.readouterr().out
    assert out.strip() == "Storage not initialized. Please run option 1 (Onboarding) first."
    assert "=== Curriculum Progress ===" not in out
