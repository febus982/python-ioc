from typing import Any, Dict, Iterable, Type, overload

from ._abstract import (
    Container as AbstractContainer,
)
from ._abstract import Provider
from ._types import REFERENCE, R
from .registry import register_container, unregister_container


class Container(AbstractContainer):
    """
    Used to define the dependencies bindings.

    A single container has to be wired to specific python modules/packages.

    c = Container()
    c.bind(ClassInterface, Provider(...), life_scope="singleton")
    """
    __slots__ = "provider_bindings"
    provider_bindings: Dict[REFERENCE, Provider]

    def __init__(self):
        self.provider_bindings = {}

    def bind(self, provider: Provider) -> None:
        if provider.reference in self.provider_bindings:
            raise Exception("Binding already registered")

        if provider.supports_provider_dependencies:
            provider.validate_nested_dependencies(self)

        self.provider_bindings[provider.reference] = provider

    @overload
    def resolve(self, reference: str) -> Any: ...

    @overload
    def resolve(self, reference: Type[R]) -> R: ...

    def resolve(self, reference):
        return self.provide(reference).resolve()

    def provide(self, reference) -> Provider:
        try:
            provider = self.provider_bindings[reference]
        except KeyError:
            raise Exception("Binding not found")

        return provider

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
