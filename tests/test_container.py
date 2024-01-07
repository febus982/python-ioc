from typing import Any
from uuid import uuid4

import pytest

from ioc._interfaces import Provider
from ioc.container import Container


class SomeProvider(Provider):
    def resolve(self) -> Any:
        return uuid4()

    @property
    def reference(self):
        return self._reference

    def __init__(self, reference, target, scope=None):
        super().__init__(reference=reference, scope=scope)
        self._target = target


def test_cannot_bind_twice_the_same_reference():
    c = Container()
    c.bind(
        SomeProvider(
            "scoped",
            "unused_var",
            "some_scope",
        ),
    )
    with pytest.raises(Exception):
        c.bind(
            SomeProvider(
                "scoped",
                "unused_var",
                "some_scope",
            ),
        )


def test_inexisting_binding_raises_exception():
    c = Container()
    with pytest.raises(Exception):
        c.resolve("some_reference")


def test_cannot_initialise_same_scope_twice():
    c = Container()
    with c.scope("some_scope"):
        with pytest.raises(Exception):
            with c.scope("some_scope"):
                pass


def test_scoped_bindings_are_singleton_during_scope_life():
    c = Container()
    c.bind(
        SomeProvider(
            "scoped",
            "unused_var",
            "some_scope",
        ),
    )

    with pytest.raises(Exception):
        assert "some_scope" not in c._get_scoped_instances()
        c.resolve("scoped")

    with c.scope("some_scope"):
        assert "some_scope" in c._get_scoped_instances()
        assert c.resolve("scoped") is c.resolve("scoped")

    with pytest.raises(Exception):
        assert "some_scope" not in c._get_scoped_instances()
        c.resolve("scoped")


def test_singleton_scope_is_always_active():
    c = Container()
    c.bind(
        SomeProvider(
            "singleton",
            "unused_var",
            "singleton",
        ),
    )

    assert c.resolve("singleton") is c.resolve("singleton")


def test_unscoped_bindings_get_always_resolved():
    c = Container()
    c.bind(
        SomeProvider(
            "unscoped",
            "unused_var",
        ),
    )
    assert c.resolve("unscoped") is not c.resolve("unscoped")
    assert c.resolve("unscoped") != c.resolve("unscoped")
