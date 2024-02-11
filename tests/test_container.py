from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from ioc._abstract import Provider
from ioc.container import Container
from ioc.providers import ObjectProvider, FactoryProvider


class SomeProvider(Provider):
    def _resolve(self) -> Any:
        return uuid4()

    def validate_nested_dependencies(self, container: Container) -> None:
        pass

    def __init__(self, reference, target, scope=None):
        super().__init__(reference=reference, scope=scope)
        self.target = target


def test_cannot_bind_twice_the_same_reference():
    ref = str(uuid4())
    c = Container()
    c._bind(
        SomeProvider(
            ref,
            "unused_var",
            "some_scope",
        ),
    )
    with pytest.raises(Exception):
        c._bind(
            SomeProvider(
                ref,
                "another_var",
            ),
        )


def test_resolve_calls_provider_resolver():
    c = Container()
    p = SomeProvider(
        "scoped",
        "unused_var",
        "some_scope",
    )
    c._bind(p)
    with patch.object(p, "resolve") as mock_resolve:
        c.resolve("scoped")
        mock_resolve.assert_called_once()


def test_resolving_not_existing_binding_raises_exception():
    c = Container()
    with pytest.raises(Exception):
        c.resolve("some_reference")


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


def test_bind_object_binds_object_provider():
    ref = str(uuid4())
    c = Container()
    with patch.object(c, "_bind", return_value=None) as mock_bind:
        c.bind_object(
            ref,
            "unused_var",
        )

    mock_bind.assert_called_once()
    assert isinstance(mock_bind.call_args[0][0], ObjectProvider)
    c.bind_object(
        ref,
        "unused_var",
    )
    assert isinstance(c.provider_bindings[ref], ObjectProvider)
    assert c.provider_bindings[ref].reference == ref
    assert c.provider_bindings[ref].resolve() == "unused_var"


def test_bind_factory_binds_factory_provider():
    ref = str(uuid4())
    c = Container()
    with patch.object(c, "_bind", return_value=None) as mock_bind:
        c.bind_factory(
            ref,
            lambda: "some_value",
        )

    mock_bind.assert_called_once()
    assert isinstance(mock_bind.call_args[0][0], FactoryProvider)
    c.bind_factory(
        ref,
        lambda: "some_value",
    )
    assert c.provider_bindings[ref].reference == ref
    assert c.provider_bindings[ref].resolve() == "some_value"
