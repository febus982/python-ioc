import sys
from uuid import uuid4

import pytest

from ioc._registry import provider_registry, register_container, unregister_container
from ioc.container import Container
from ioc.providers import ObjectProvider


def test_container_registration_handles_single_modules():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)

    assert (sys.modules[__name__], ref) not in provider_registry

    register_container(c, modules=(__name__,))
    assert (sys.modules[__name__], ref) in provider_registry
    assert provider_registry[(sys.modules[__name__], ref)] == (provider, c)

    unregister_container(c, modules=(__name__,))
    assert (sys.modules[__name__], ref) not in provider_registry


def test_container_registration_handles_single_modules_via_the_packages_param():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)

    assert (sys.modules[__name__], ref) not in provider_registry

    register_container(c, packages=(__name__,))
    assert (sys.modules[__name__], ref) in provider_registry
    assert provider_registry[(sys.modules[__name__], ref)] == (provider, c)

    unregister_container(c, modules=(__name__,))
    assert (sys.modules[__name__], ref) not in provider_registry


def test_container_deregistration_navigates_packages():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        str(ref),
        "value",
    )
    c._bind(provider)
    register_container(c, packages=("tests.registry",))

    assert (sys.modules[__name__], ref) in provider_registry
    assert (sys.modules["tests.registry"], ref) in provider_registry

    unregister_container(c, packages=("tests.registry",))

    assert (sys.modules[__name__], ref) not in provider_registry
    assert (sys.modules["tests.registry"], ref) not in provider_registry


def test_container_deregistration_handles_single_modules():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)
    register_container(c, packages=("tests.registry",))

    assert (sys.modules[__name__], ref) in provider_registry
    assert (sys.modules["tests.registry"], ref) in provider_registry

    unregister_container(c, modules=("tests.registry",))

    assert (sys.modules[__name__], ref) in provider_registry
    assert (sys.modules["tests.registry"], ref) not in provider_registry


def test_cannot_register_same_reference_to_same_modules():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)
    c2 = Container()
    provider2 = ObjectProvider(
        ref,
        "another_value",
    )
    c2._bind(provider2)

    assert (sys.modules[__name__], ref) not in provider_registry

    register_container(c, modules=(__name__,))
    assert (sys.modules[__name__], ref) in provider_registry
    assert provider_registry[(sys.modules[__name__], ref)] == (provider, c)

    # Same container
    with pytest.raises(ValueError):
        register_container(c, modules=(__name__,))

    # Another container with same reference
    with pytest.raises(ValueError):
        register_container(c2, modules=(__name__,))


def test_cannot_register_using_relative_imports():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)

    with pytest.raises(ImportError):
        register_container(c, modules=("../test_scopes.py",))

    with pytest.raises(ImportError):
        register_container(c, packages=("../test_scopes.py",))


def test_cannot_unregister_same_reference_with_different_container():
    ref = str(uuid4())
    c = Container()
    provider = ObjectProvider(
        ref,
        "value",
    )
    c._bind(provider)
    c2 = Container()
    c2._bind(provider)

    assert (sys.modules[__name__], ref) not in provider_registry

    register_container(c, modules=(__name__,))
    # reference is registered
    assert (sys.modules[__name__], ref) in provider_registry
    assert provider_registry[(sys.modules[__name__], ref)] == (provider, c)

    unregister_container(c2, modules=(__name__,))
    # reference is still there
    assert (sys.modules[__name__], ref) in provider_registry
    assert provider_registry[(sys.modules[__name__], ref)] == (provider, c)
