from typing import Any

from ioc.providers import Provider


class SomeProvider(Provider):
    def resolve(self) -> Any:
        return None

    def __init__(self, reference, scope=None):
        super().__init__(reference=reference, scope=scope)


def test_properties():
    o = SomeProvider("ref", "scope")

    assert o.scope == "scope"
    assert o.reference == "ref"
