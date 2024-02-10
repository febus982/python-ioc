from typing import Any

from ioc._abstract import Container, Provider


class SomeProvider(Provider):
    def _resolve(self) -> Any:
        return None

    def validate_nested_dependencies(self, container: Container) -> None:
        pass

    def __init__(self, reference, scope=None):
        super().__init__(reference=reference, scope=scope)


def test_properties():
    o = SomeProvider("ref", "scope")

    assert o.scope == "scope"
    assert o.reference == "ref"
