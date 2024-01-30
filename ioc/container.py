from contextlib import contextmanager
from threading import local
from typing import Any, Dict, Iterable, Iterator, Type, Union, overload

from ._interfaces import (
    Container as AbstractContainer,
)
from ._registry import ContainerRegistry
from .providers import Provider
from .providers._interfaces import REFERENCE, REFERENCE_TYPE


class Container(AbstractContainer):
    """
    Used to define the dependencies bindings.

    A single container has to be wired to specific python modules/packages.

    c = Container()
    c.bind(ClassInterface, Class, life_scope="singleton")
    """

    _bindings: Dict[REFERENCE, Provider]
    _scoped_instances: local

    def __init__(self):
        self._bindings = {}
        self._scoped_instances = local()

    def bind(self, binding: Provider) -> None:
        if self._bindings.get(binding.reference):
            raise Exception("Binding already registered")
        else:
            self._bindings[binding.reference] = binding

    @overload
    def resolve(self, reference: str) -> Any:
        ...

    @overload
    def resolve(self, reference: Type[REFERENCE_TYPE]) -> REFERENCE_TYPE:
        ...

    def resolve(self, reference):
        try:
            binding = self._bindings[reference]
        except KeyError:
            raise Exception("Binding not found")

        instances = self._get_scoped_instances()
        if binding.scope:
            if binding.scope not in instances:
                raise Exception("Scope not found")

            instance = instances[binding.scope].get(reference)
            if not instance:
                instance = instances[binding.scope][reference] = binding.resolve()

            return instance
        else:
            return binding.resolve()

    @contextmanager
    def scope(self, scope: str) -> Iterator[None]:
        instances = self._get_scoped_instances()
        if scope in instances:
            raise Exception(f"Scope `{scope}` already initialised")

        instances[scope] = {}
        yield None
        del instances[scope]

    def _get_scoped_instances(self) -> Dict[Union[str, None], Dict[REFERENCE, Any]]:
        try:
            return getattr(self._scoped_instances, "instances")
        except AttributeError:
            self._scoped_instances.instances = {"singleton": {}}
            return getattr(self._scoped_instances, "instances")

    def wire(
        self,
        modules: Iterable[str] = tuple(),
        packages: Iterable[str] = tuple(),
    ) -> None:
        ContainerRegistry.register_container(
            container=self,
            modules=modules,
            packages=packages,
        )

    def unwire(self) -> None:
        ContainerRegistry.unregister_container(container=self)
