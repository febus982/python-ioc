from typing import Any, Dict, Iterable, Type, overload

from ._interfaces import REFERENCE, R
from ._interfaces import (
    Container as AbstractContainer,
)
from .providers import Provider
from .registry import register_container, unregister_container
from .scopes import get_scoped_instances


class Container(AbstractContainer):
    """
    Used to define the dependencies bindings.

    A single container has to be wired to specific python modules/packages.

    c = Container()
    c.bind(ClassInterface, Provider(...), life_scope="singleton")
    """

    def __init__(self):
        self.provider_bindings: Dict[REFERENCE, Provider] = {}

    def bind(self, binding: Provider) -> None:
        if binding.reference in self.provider_bindings:
            raise Exception("Binding already registered")
        else:
            self.provider_bindings[binding.reference] = binding

    @overload
    def resolve(self, reference: str) -> Any: ...

    @overload
    def resolve(self, reference: Type[R]) -> R: ...

    def resolve(self, reference):
        try:
            provider = self.provider_bindings[reference]
        except KeyError:
            raise Exception("Binding not found")

        if provider.scope:
            try:
                instances = get_scoped_instances(provider.scope)
            except KeyError:
                raise Exception("Scope not found")

            instance = instances.get(reference)
            if not instance:
                instance = instances[reference] = provider.resolve()

            return instance
        else:
            return provider.resolve()

    def wire(
        self,
        modules: Iterable[str] = tuple(),
        packages: Iterable[str] = tuple(),
    ) -> None:
        register_container(container=self, modules=modules, packages=packages)
        self.modules = self.modules.union(modules)
        self.packages = self.packages.union(packages)

    def unwire(
        self,
        modules: Iterable[str] = (),
        packages: Iterable[str] = (),
    ) -> None:
        unregister_container(container=self, modules=modules, packages=packages)
