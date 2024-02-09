from multiprocessing.pool import ThreadPool
from typing import Any
from uuid import UUID, uuid4

import pytest

from ioc._abstract import Provider
from ioc.scopes import is_scope_running, run_scope


class SomeProvider(Provider):
    def _resolve(self) -> Any:
        return uuid4()

    def __init__(
        self,
        reference,
        target,
        scope=None,
        thread_safe=False,
    ):
        super().__init__(reference=reference, scope=scope, thread_safe=thread_safe)
        self.target = target


def test_scoped_providers_resolve_singleton_during_scope_life():
    provider = SomeProvider(
        "scoped",
        "unused_var",
        "some_scope",
    )

    assert is_scope_running("some_scope") is False
    assert provider._scoped_instance is None
    with pytest.raises(Exception):
        provider.resolve()

    with run_scope("some_scope"):
        assert provider._scoped_instance is None
        assert is_scope_running("some_scope") is True
        returned_instance = provider.resolve()
        assert provider.resolve() is returned_instance
        assert provider._scoped_instance is returned_instance

    assert is_scope_running("some_scope") is False
    assert provider._scoped_instance is None
    with pytest.raises(Exception):
        provider.resolve()


def test_threadscoped_providers_resolve_singleton_during_scope_life():
    provider = SomeProvider(
        "scoped",
        "unused_var",
        "some_scope",
        thread_safe=True,
    )

    assert is_scope_running("some_scope") is False
    assert getattr(provider._threadlocal_instance, "instance", None) is None
    with pytest.raises(Exception):
        provider.resolve()

    with run_scope("some_scope"):
        assert provider._scoped_instance is None
        assert is_scope_running("some_scope") is True
        returned_instance = provider.resolve()
        assert provider.resolve() is returned_instance
        assert provider._threadlocal_instance.instance is returned_instance

    assert is_scope_running("some_scope") is False
    with run_scope("some_scope"):
        assert provider._scoped_instance is None
        assert is_scope_running("some_scope") is True
        returned_instance2 = provider.resolve()
        assert provider.resolve() is returned_instance2
        assert provider._threadlocal_instance.instance is returned_instance2

    assert returned_instance is not returned_instance2

    assert is_scope_running("some_scope") is False
    assert getattr(provider._threadlocal_instance, "instance", None) is None
    with pytest.raises(Exception):
        provider.resolve()


def test_threadscoped_provider_multithread_safety():
    provider = SomeProvider(
        "scoped",
        "unused_var",
        "some_scope",
        thread_safe=True,
    )

    with run_scope("some_scope"):
        returned_instance = provider.resolve()
        returned_instance2 = provider.resolve()
        pool = ThreadPool()
        threaded_instance = pool.apply(provider.resolve)
        pool.close()
    assert isinstance(returned_instance, UUID)
    assert isinstance(returned_instance2, UUID)
    assert isinstance(threaded_instance, UUID)
    assert returned_instance is returned_instance2
    assert returned_instance is not threaded_instance


def test_unscoped_providers_are_always_resolved():
    provider = SomeProvider(
        "unscoped",
        "unused_var",
    )

    assert provider.resolve() is not provider.resolve()
    assert provider.resolve() != provider.resolve()
