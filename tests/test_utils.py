# test_utils.py
# Unit tests for utils.load_safe() (src/utils.py).
#
# load_safe() wraps a zero-arg loader callable (e.g. load_profile,
# load_progress) and converts FileNotFoundError / json.JSONDecodeError into
# a None return value, while letting every other exception propagate
# unchanged. These tests exercise load_safe() directly with fake loaders —
# no monkeypatching of main.py or real file I/O is needed here, since
# load_safe() doesn't care what the loader actually does internally.
#
# Run with:  python -m pytest tests/test_utils.py -v
# (requires tests/conftest.py, which puts src/ on sys.path so `import utils`
# resolves the same way main.py resolves its own sibling imports.)

import json

import pytest

import utils


# --- Happy path -----------------------------------------------------------


def test_load_safe_returns_loader_result_when_loader_succeeds():
    sentinel = {"student_name": "Alice", "core_interests": ["chess"]}

    result = utils.load_safe(lambda: sentinel)

    assert result is sentinel


def test_load_safe_calls_loader_exactly_once():
    """load_safe() should not retry the loader — one call, one outcome."""
    call_count = {"n": 0}

    def _counting_loader():
        call_count["n"] += 1
        return {"ok": True}

    utils.load_safe(_counting_loader)

    assert call_count["n"] == 1


# --- Caught exceptions: missing / corrupt storage --------------------------


def test_load_safe_returns_none_when_loader_raises_file_not_found_error():
    def _raise_missing_file():
        raise FileNotFoundError("config/student_profile.json not found")

    result = utils.load_safe(_raise_missing_file)

    assert result is None


def test_load_safe_returns_none_when_loader_raises_json_decode_error():
    def _raise_bad_json():
        raise json.JSONDecodeError("Expecting value", doc="", pos=0)

    result = utils.load_safe(_raise_bad_json)

    assert result is None


# --- Except-clause scoping: everything else must propagate -----------------


def test_load_safe_does_not_catch_value_error():
    """Confirms the except clause is scoped to (FileNotFoundError,
    json.JSONDecodeError) and is NOT a bare except — an unrelated ValueError
    from inside the loader must propagate to the caller, not be swallowed
    into a silent None."""

    def _raise_value_error():
        raise ValueError("unexpected shape")

    with pytest.raises(ValueError):
        utils.load_safe(_raise_value_error)


def test_load_safe_does_not_catch_key_error():
    """A second, unrelated exception type (KeyError) as a sanity check that
    load_safe() isn't accidentally catching Exception broadly."""

    def _raise_key_error():
        raise KeyError("nodes")

    with pytest.raises(KeyError):
        utils.load_safe(_raise_key_error)


def test_load_safe_does_not_catch_permission_error():
    """PermissionError is a plausible real-world failure mode (locked file,
    restricted ACL) that is deliberately NOT part of load_safe()'s contract
    — it should surface loudly rather than be mistaken for 'uninitialized'."""

    def _raise_permission_error():
        raise PermissionError("access denied")

    with pytest.raises(PermissionError):
        utils.load_safe(_raise_permission_error)


# --- Falsy-but-not-None results must pass through untouched ----------------


def test_load_safe_returns_empty_dict_as_is_not_none():
    """An empty dict is falsy but semantically different from 'storage is
    uninitialized' (None) — callers checking `if profile is None` must be
    able to tell the two apart."""
    result = utils.load_safe(lambda: {})

    assert result == {}
    assert result is not None
