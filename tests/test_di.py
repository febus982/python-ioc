import pytest

from ioc.container import Container
from ioc.di import Inject, enable_injection
from ioc.providers import ObjectProvider


async def test_injector():
    # Not nice but we do all in a single test
    # to make sure we don't wire multiple times
    # if tests run in parallel
    c = Container()
    c.bind(
        ObjectProvider(
            "ref",
            "obj",
        ),
    )
    c.wire(modules=[__name__])

    # Test manual Inject resolution
    assert Inject("ref").resolve() == "obj"
    with pytest.raises(Exception):
        Inject("noref").resolve()
    with pytest.raises(Exception):
        Inject("inexisting_scope").resolve()

    # test decorator on sync function
    @enable_injection
    def foo(param: str = Inject("ref")):
        return param

    assert foo() == "obj"
    # test param can be bypassed
    assert foo("param") == "param"

    # test without decorator on sync function
    def bar(param: str = Inject("ref")):
        return param

    assert bar() != "obj"
    assert isinstance(bar(), Inject)
    # test param can be bypassed
    assert bar("param") == "param"

    # test with decorator on async function
    @enable_injection
    async def baz(param: str = Inject("ref")):
        return param

    assert await baz() == "obj"
    # test param can be bypassed
    assert await baz("param") == "param"

    # test without decorator on async function
    async def bat(param: str = Inject("ref")):
        return param

    assert await bat() != "obj"
    assert isinstance((await bat()), Inject)
    # test param can be bypassed
    assert await bat("param") == "param"

    c.unwire()
