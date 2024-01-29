import sys

import pytest

from ioc._registry import ContainerRegistry
from ioc.container import Container


def test_container_registration_processes_to_single_module():
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()

    c = Container()
    ContainerRegistry.register_container(c, modules=(__name__,))
    assert ContainerRegistry.get_container(sys.modules[__name__]) is c
    assert sys.modules[__name__] in ContainerRegistry._registry.keys()

    ContainerRegistry.unregister_container(c)
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()


def test_container_registration_processes_navigates_packages():
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()
    assert sys.modules["tests.registry"] not in ContainerRegistry._registry.keys()

    c = Container()
    ContainerRegistry.register_container(c, packages=("tests.registry",))
    assert ContainerRegistry.get_container(sys.modules[__name__]) is c
    assert sys.modules[__name__] in ContainerRegistry._registry.keys()
    assert sys.modules["tests.registry"] in ContainerRegistry._registry.keys()

    ContainerRegistry.unregister_container(c)
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()
    assert sys.modules["tests.registry"] not in ContainerRegistry._registry.keys()


def test_container_registration_processes_doesnt_navigate_single_modules():
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()

    c = Container()
    ContainerRegistry.register_container(c, packages=(__name__,))
    assert ContainerRegistry.get_container(sys.modules[__name__]) is c
    assert sys.modules[__name__] in ContainerRegistry._registry.keys()

    ContainerRegistry.unregister_container(c)
    assert ContainerRegistry.get_container(sys.modules[__name__]) is None
    assert sys.modules[__name__] not in ContainerRegistry._registry.keys()


def test_relative_imports_are_not_allowed():
    c = Container()
    with pytest.raises(ImportError):
        ContainerRegistry.register_container(c, modules=("..tests",))
    with pytest.raises(ImportError):
        ContainerRegistry.register_container(c, packages=("..tests",))


def test_cannot_register_multiple_times_against_same_module():
    c = Container()
    c2 = Container()
    ContainerRegistry.register_container(c, modules=("tests.registry.test_registry",))

    # Same container
    with pytest.raises(ValueError):
        ContainerRegistry.register_container(c, modules=("tests.registry.test_registry",))
    # Another container
    with pytest.raises(ValueError):
        ContainerRegistry.register_container(c2, modules=("tests.registry.test_registry",))
