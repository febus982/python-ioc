import sys

import pytest

from ioc.container import Container
from ioc.providers import ObjectProvider
from ioc.registry import _registry, register_container, unregister_container


def test_container_registration_processes_to_single_module():
    c = Container()
    provider = ObjectProvider(
        "ref",
        "value",
    )
    c.bind(provider)

    assert (sys.modules[__name__], "ref") not in _registry

    register_container(c, modules=(__name__,))
    assert (sys.modules[__name__], "ref") in _registry
    assert _registry[(sys.modules[__name__], "ref")] == (provider, c)

    unregister_container(c, modules=(__name__,))
    assert (sys.modules[__name__], "ref") not in _registry


def test_container_registration_processes_navigates_packages():
    c = Container()
    provider = ObjectProvider(
        "ref",
        "value",
    )
    c.bind(provider)

    assert (sys.modules[__name__], "ref") not in _registry
    assert (sys.modules["tests.registry"], "ref") not in _registry

    register_container(c, packages=("tests.registry",))

    assert (sys.modules[__name__], "ref") in _registry
    assert (sys.modules["tests.registry"], "ref") in _registry

    unregister_container(c, packages=("tests.registry",))

    assert (sys.modules[__name__], "ref") not in _registry
    assert (sys.modules["tests.registry"], "ref") not in _registry


def test_container_registration_processes_doesnt_navigate_single_modules():
    c = Container()
    provider = ObjectProvider(
        "ref",
        "value",
    )
    c.bind(provider)

    assert (sys.modules[__name__], "ref") not in _registry

    register_container(c, packages=(__name__,))
    assert (sys.modules[__name__], "ref") in _registry
    assert _registry[(sys.modules[__name__], "ref")] == (provider, c)

    unregister_container(c, packages=(__name__,))
    assert (sys.modules[__name__], "ref") not in _registry


def test_relative_imports_are_not_allowed():
    c = Container()
    with pytest.raises(ImportError):
        register_container(c, modules=("..tests",))
    with pytest.raises(ImportError):
        register_container(c, packages=("..tests",))


def test_cannot_register_multiple_times_against_same_module():
    c = Container()
    c2 = Container()
    c.bind(ObjectProvider("test", "result"))
    c2.bind(ObjectProvider("test", "result2"))
    register_container(c, modules=(__name__,))

    # Same container
    with pytest.raises(ValueError):
        register_container(c, modules=(__name__,))
    # Another container
    with pytest.raises(ValueError):
        register_container(c2, modules=(__name__,))
