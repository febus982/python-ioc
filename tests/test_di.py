from abc import ABC

import pytest

from ioc.container import Container
from ioc.di import Require, inject
from ioc.providers import Factory, FactoryProvider, ObjectProvider


class Interface(ABC):
    pass


class Concrete(Interface):
    pass


class Concrete2(Interface):
    pass


async def test_inject_using_interface():
    c = Container()
    c._bind(
        FactoryProvider(
            Interface,
            Factory(
                callable=Concrete
            )
        ),
    )
    c.wire(modules=[__name__])

    # Fake injector to test Inject default has precedence
    # over the typing
    fake_inject = Require(Interface)
    fake_inject.resolve = lambda: 5

    # test decorator on sync function
    @inject
    def foo(
        param: Interface,
        param2: Interface = fake_inject,
        param3: Interface = Require(Interface),
        param4: Interface = Concrete2(),
    ):
        return param, param2, param3, param4

    assert isinstance(foo()[0], Concrete)
    assert foo()[1] == 5
    assert isinstance(foo()[2], Concrete)
    assert isinstance(foo()[3], Concrete2)
    # Check manual params have priority
    assert foo(param=1, param2=2, param3=3, param4=4) == (1, 2, 3, 4)

    # test decorator on coroutine function
    @inject
    async def foo(
        param: Interface,
        param2: Interface = fake_inject,
        param3: Interface = Require(Interface),
        param4: Interface = Concrete2(),
    ):
        return param, param2, param3, param4

    assert isinstance((await foo())[0], Concrete)
    assert (await foo())[1] == 5
    assert isinstance((await foo())[2], Concrete)
    assert isinstance((await foo())[3], Concrete2)
    # Check manual params have priority
    assert await foo(param=1, param2=2, param3=3, param4=4) == (1, 2, 3, 4)


async def test_injector():
    # Not nice but we do all in a single test
    # to make sure we don't wire multiple times
    # against this module if tests run in parallel
    c = Container()
    c._bind(
        ObjectProvider(
            "ref",
            "obj",
        ),
    )
    c.wire(modules=[__name__])

    # Test manual Inject resolution
    assert Require("ref").resolve() == "obj"
    with pytest.raises(Exception):
        Require("noref").resolve()

    # test decorator on sync function
    @inject
    def foo(param: str = Require("ref")):
        return param

    assert foo() == "obj"
    # test param can be bypassed
    assert foo("param") == "param"

    # test without decorator on sync function
    def bar(param: str = Require("ref")):
        return param

    assert bar() != "obj"
    assert isinstance(bar(), Require)
    # test param can be bypassed
    assert bar("param") == "param"

    # test with decorator on async function
    @inject
    async def baz(param: str = Require("ref")):
        return param

    assert await baz() == "obj"
    # test param can be bypassed
    assert await baz("param") == "param"

    # test without decorator on async function
    async def bat(param: str = Require("ref")):
        return param

    assert await bat() != "obj"
    assert isinstance((await bat()), Require)
    # test param can be bypassed
    assert await bat("param") == "param"

    c.unwire(modules=[__name__])
