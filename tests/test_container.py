from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from ioc._interfaces import Provider
from ioc.container import Container
from ioc.scopes import _scoped_instances, run_scope


class SomeProvider(Provider):
    def resolve(self) -> Any:
        return uuid4()

    def __init__(self, reference, target, scope=None):
        super().__init__(reference=reference, scope=scope)
        self.target = target


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
                "another_var",
            ),
        )


def test_resolving_not_existing_binding_raises_exception():
    c = Container()
    with pytest.raises(Exception):
        c.resolve("some_reference")


def test_cannot_initialise_same_scope_twice():
    with run_scope("some_scope"):
        with pytest.raises(Exception):
            with run_scope("some_scope"):
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
        assert "some_scope" not in _scoped_instances.__dict__
        c.resolve("scoped")

    with run_scope("some_scope"):
        assert "some_scope" in _scoped_instances.__dict__
        assert c.resolve("scoped") is c.resolve("scoped")

    with pytest.raises(Exception):
        assert "some_scope" not in _scoped_instances.__dict__
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


def test_cannot_manually_execute_singleton_scope():
    with pytest.raises(Exception):
        with run_scope("singleton"):
            pass


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


def test_wire_registers_container_in_registry():
    c = Container()
    modules = ("random_module",)
    packages = ("random_packages",)

    with patch(
        "ioc.container.register_container", return_value=None
    ) as mock_register_container:
        c.wire(modules=modules, packages=packages)

    mock_register_container.assert_called_once_with(
        container=c, modules=modules, packages=packages
    )


def test_unwire_unregisters_container_from_registry():
    c = Container()

    with patch(
        "ioc.container.unregister_container", return_value=None
    ) as mock_unregister_container:
        c.unwire()

    mock_unregister_container.assert_called_once_with(
        container=c, modules=(), packages=()
    )
