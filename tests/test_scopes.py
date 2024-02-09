from uuid import uuid4

import pytest

from ioc.scopes import _scope_registry, is_scope_running, run_scope


def test_cannot_initialise_same_scope_twice():
    # Scope is not initialised
    assert "some_scope" not in _scope_registry
    assert is_scope_running("some_scope") is False

    with run_scope("some_scope"):
        # Scope is initialised after first contextmanager invocation
        assert "some_scope" in _scope_registry
        assert is_scope_running("some_scope") is True

        # Nested contextmanager raises an Exception
        with pytest.raises(Exception):
            with run_scope("some_scope"):
                pass

        # Scope is still initialised after nested contextmanager ends
        assert "some_scope" in _scope_registry
        assert is_scope_running("some_scope") is True

    # Scope is not initialised after first contextmanager ends
    assert "some_scope" not in _scope_registry
    assert is_scope_running("some_scope") is False


def test_cannot_manually_execute_singleton_scope():
    # Scope is already initialised
    assert "singleton" in _scope_registry
    assert is_scope_running("singleton") is True
    # Contextmanager raises an Exception
    with pytest.raises(Exception):
        with run_scope("singleton"):
            pass
    # Scope is still initialised
    assert "singleton" in _scope_registry
    assert is_scope_running("singleton") is True


def test_is_scope_running():
    scope = str(uuid4())
    assert is_scope_running(scope) is False
    assert scope not in _scope_registry
    with run_scope(scope):
        assert is_scope_running(scope) is True
        assert scope in _scope_registry
    assert is_scope_running(scope) is False
    assert scope not in _scope_registry
