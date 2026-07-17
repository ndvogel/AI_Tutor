# test_storage_guards.py
# Tests for the storage-uninitialized guards added to run_onboarding(),
# run_curriculum_generation(), change_profile_context(), and run_lesson()
# in src/main.py. Each of these now routes its initial profile/progress
# read through utils.load_safe(...) and bails out early with a fixed
# message when load_safe returns None, instead of letting a
# FileNotFoundError / json.JSONDecodeError from load_profile()/
# load_progress() propagate and crash the dev menu.
#
# Following the convention established in tests/test_view_progress.py:
# monkeypatch the names as imported into main's namespace (main.load_profile,
# main.load_progress, main.save_profile, ...), not utils.load_profile etc.,
# since main.py binds them via `from utils import ...` at import time.
#
# Run with:  python -m pytest tests/test_storage_guards.py -v
# (requires tests/conftest.py, which puts src/ on sys.path so `import main`
# resolves the same way main.py resolves its own sibling imports.)

import json

import pytest

import main


def _raise_file_not_found():
    raise FileNotFoundError("storage file not found")


def _raise_json_decode_error():
    raise json.JSONDecodeError("Expecting value", doc="", pos=0)


# Both exception types are funneled through the same load_safe() except
# clause, so every guard should behave identically for either one.
BROKEN_LOADERS = [
    pytest.param(_raise_file_not_found, id="file_not_found"),
    pytest.param(_raise_json_decode_error, id="json_decode_error"),
]


def _fail_if_called(name):
    """Returns a stand-in that raises AssertionError if invoked — used to
    prove a later step (e.g. save_profile, generate_curriculum, input())
    was never reached because the guard returned early."""

    def _inner(*_args, **_kwargs):
        raise AssertionError(f"{name} should not be called when the storage guard fires")

    return _inner


def _progress(nodes):
    """Builds a minimal learning_progress.json-shaped dict."""
    return {
        "current_node_id": None,
        "nodes": nodes,
        "friction_cycle_count": 0,
        "session_turn_count": 0,
        "last_3_turns": [],
    }


def _node(title="Some Node", status="unlocked", node_id="some_node"):
    return {
        "node_id": node_id,
        "title": title,
        "prerequisites": [],
        "status": status,
        "friction_cycle_count": 0,
        "consecutive_failures": 0,
        "attempts": 0,
        "success_rate": 0.0,
        "active_interest_used": None,
        "last_updated": "2026-05-16T22:33:19.049447Z",
    }


# --- run_onboarding() -------------------------------------------------------


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_run_onboarding_prints_storage_unreadable_message_and_returns_when_profile_load_fails(
    monkeypatch, capsys, broken_loader
):
    # Supply every prompt run_onboarding() collects BEFORE it ever touches
    # storage: name, subject, generation choice ("1"), delivery choice ("1"),
    # one interest, then blank to stop collecting interests.
    answers = iter(["Alice", "Python", "1", "1", "reading", ""])
    monkeypatch.setattr("builtins.input", lambda *_a: next(answers))

    monkeypatch.setattr(main, "load_profile", broken_loader)
    monkeypatch.setattr(main, "save_profile", _fail_if_called("save_profile"))

    main.run_onboarding()

    out = capsys.readouterr().out
    assert main.STORAGE_UNREADABLE_MSG in out
    assert main.STORAGE_UNINITIALIZED_MSG not in out
    assert "Profile saved" not in out


# --- run_curriculum_generation() -------------------------------------------


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_run_curriculum_generation_prints_storage_unreadable_message_and_returns_when_profile_load_fails(
    monkeypatch, capsys, broken_loader
):
    monkeypatch.setattr(main, "load_profile", broken_loader)
    monkeypatch.setattr(main, "generate_curriculum", _fail_if_called("generate_curriculum"))

    main.run_curriculum_generation()

    out = capsys.readouterr().out
    assert main.STORAGE_UNREADABLE_MSG in out
    assert main.STORAGE_UNINITIALIZED_MSG not in out
    assert "Generating curriculum" not in out


# --- change_profile_context() -----------------------------------------------


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_change_profile_context_prints_storage_uninitialized_message_and_returns_when_profile_load_fails(
    monkeypatch, capsys, broken_loader
):
    monkeypatch.setattr(main, "load_profile", broken_loader)
    # If the guard didn't fire, the function would immediately call
    # _prompt_choice(...) -> input(...); failing loudly here proves it
    # returned before ever prompting.
    monkeypatch.setattr("builtins.input", _fail_if_called("input"))

    main.change_profile_context()

    out = capsys.readouterr().out
    assert main.STORAGE_UNINITIALIZED_MSG in out
    assert main.STORAGE_UNREADABLE_MSG not in out
    assert "=== Update Profile Context ===" not in out


def test_change_profile_context_does_not_loop_when_profile_load_fails(monkeypatch, capsys):
    """Regression guard against an infinite `while True:` loop: the load
    failure must reach `return`, not just `continue`/retry indefinitely.
    A call counter on the broken loader proves load_profile was consulted
    exactly once, not repeatedly."""
    call_count = {"n": 0}

    def _raise_once_tracked():
        call_count["n"] += 1
        raise FileNotFoundError("storage file not found")

    monkeypatch.setattr(main, "load_profile", _raise_once_tracked)
    monkeypatch.setattr("builtins.input", _fail_if_called("input"))

    main.change_profile_context()

    assert call_count["n"] == 1


# --- run_lesson() ------------------------------------------------------------


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_run_lesson_prints_storage_uninitialized_message_when_profile_load_fails(
    monkeypatch, capsys, broken_loader
):
    monkeypatch.setattr(main, "load_profile", broken_loader)
    monkeypatch.setattr(main, "load_progress", lambda: _progress({"some_node": _node()}))
    monkeypatch.setattr(main, "generate_lesson", _fail_if_called("generate_lesson"))

    main.run_lesson("some_node")

    out = capsys.readouterr().out
    assert main.STORAGE_UNINITIALIZED_MSG in out
    assert "Generating lesson for" not in out


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_run_lesson_prints_storage_uninitialized_message_when_progress_load_fails(
    monkeypatch, capsys, broken_loader
):
    monkeypatch.setattr(main, "load_profile", lambda: {"student_name": "Alice"})
    monkeypatch.setattr(main, "load_progress", broken_loader)
    monkeypatch.setattr(main, "generate_lesson", _fail_if_called("generate_lesson"))

    main.run_lesson("some_node")

    out = capsys.readouterr().out
    assert main.STORAGE_UNINITIALIZED_MSG in out
    assert "Generating lesson for" not in out


@pytest.mark.parametrize("broken_loader", BROKEN_LOADERS)
def test_run_lesson_prints_storage_uninitialized_message_when_both_loads_fail(
    monkeypatch, capsys, broken_loader
):
    monkeypatch.setattr(main, "load_profile", broken_loader)
    monkeypatch.setattr(main, "load_progress", broken_loader)
    monkeypatch.setattr(main, "generate_lesson", _fail_if_called("generate_lesson"))

    main.run_lesson("some_node")

    out = capsys.readouterr().out
    assert main.STORAGE_UNINITIALIZED_MSG in out
    assert "Generating lesson for" not in out


def test_run_lesson_calls_both_loaders_even_when_profile_load_fails_first(monkeypatch, capsys):
    """`profile = load_safe(load_profile)` and `progress = load_safe(load_progress)`
    are two unconditional statements, not a short-circuited `and`/`or` — so
    even when the profile load already failed, load_progress() must still
    be invoked (not skipped) before the combined None-check runs."""
    progress_call_count = {"n": 0}

    def _tracked_progress_loader():
        progress_call_count["n"] += 1
        return _progress({"some_node": _node()})

    monkeypatch.setattr(main, "load_profile", _raise_file_not_found)
    monkeypatch.setattr(main, "load_progress", _tracked_progress_loader)
    monkeypatch.setattr(main, "generate_lesson", _fail_if_called("generate_lesson"))

    main.run_lesson("some_node")

    assert progress_call_count["n"] == 1
    out = capsys.readouterr().out
    assert main.STORAGE_UNINITIALIZED_MSG in out
