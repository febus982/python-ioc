import pytest

from ioc.container import Container
from ioc.providers import ObjectProvider
from ioc.wiring import Inject, enable_injection, wire


async def test_injector():
    c = Container()
    c.bind(
        ObjectProvider(
            "ref",
            "obj",
        ),
    )

    wire(c, packages=["tests"])

    assert Inject("ref").resolve() == "obj"
    with pytest.raises(Exception):
        Inject("noref").resolve()
    with pytest.raises(Exception):
        Inject("inexisting_scope").resolve()

    @enable_injection
    def foo(param=Inject("ref")):
        return param

    def bar(param=Inject("ref")):
        return param

    @enable_injection
    async def baz(param=Inject("ref")):
        return param

    assert foo() == "obj"
    assert await baz() == "obj"
    assert isinstance(bar(), Inject)
