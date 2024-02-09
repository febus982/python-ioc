from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from ioc._abstract import Provider
from ioc.container import Container


class SomeProvider(Provider):
    def _resolve(self) -> Any:
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


def test_resolve_calls_provider_resolver():
    c = Container()
    p = SomeProvider(
        "scoped",
        "unused_var",
        "some_scope",
    )
    c.bind(p)
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
