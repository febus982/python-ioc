from abc import ABC, abstractmethod

import pytest

from ioc.container import Container
from ioc.providers import Factory, FactoryProvider, ObjectProvider


def some_func(a: str) -> str:
    return a


class MyClassInterface(ABC):
    @abstractmethod
    def __init__(self, a: str) -> None:
        ...


class MyClass(MyClassInterface):
    def __init__(self, a: str) -> None:
        self.a = a


def test_container_allows_binding_only_if_dependencies_are_registered():
    c = Container()
    o = ObjectProvider("ref", "scope")
    f = FactoryProvider(
        "ref2",
        Factory(
            callable=some_func,
            args=(o,),
        ),
    )
    f2 = FactoryProvider(
        "ref3",
        Factory(
            callable=some_func,
            kwargs={"a": o},
        ),
    )

    with pytest.raises(Exception):
        c.bind(f)
    with pytest.raises(Exception):
        c.bind(f2)

    c.bind(o)
    c.bind(f)
    c.bind(f2)
    assert c.provide("ref2") is f
    assert c.provide("ref3") is f2


def test_factory_without_dependencies_are_registered():
    c = Container()
    f = FactoryProvider(
        "ref",
        Factory(callable=lambda: 1, ),
    )
    c.bind(f)
    assert c.provide("ref") is f


def test_factory_resolution():
    c = Container()
    o = ObjectProvider("ref", "scope")
    factory_function = FactoryProvider(
        "ref2",
        Factory(callable=some_func, args=(o,)),
    )
    factory_class = FactoryProvider(
        MyClassInterface,
        Factory(callable=MyClass, args=(o,)),
    )
    c.bind(o)
    c.bind(factory_function)
    c.bind(factory_class)
    assert c.resolve("ref2") == "scope"
    result = c.resolve(MyClassInterface)
    assert isinstance(result, MyClass)
    assert isinstance(result, MyClassInterface)
    assert result.a == "scope"
