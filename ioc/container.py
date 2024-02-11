from typing import Any, Callable, Iterable, Optional, Type, overload

from ._abstract import (
    Container as AbstractContainer,
)
from ._abstract import Provider
from ._registry import register_container, unregister_container
from ._types import REFERENCE, R
from .providers import Factory, FactoryProvider, ObjectProvider


class Container(AbstractContainer):
    """
    Used to define the dependencies bindings.

    A single container has to be wired to specific python modules/packages.

    c = Container()
    c.bind(ClassInterface, Provider(...), life_scope="singleton")
    """

    def _bind(self, provider: Provider) -> None:
        if provider.reference in self.provider_bindings:
            raise Exception("Binding already registered")

        if provider.needs_nested_providers_check:
            provider.validate_nested_dependencies(self)

        self.provider_bindings[provider.reference] = provider

    def bind_object(
        self,
        reference: REFERENCE,
        obj: Any,
        _scope: Optional[str] = None,
        _threads: bool = False,
    ) -> None:
        if reference in self.provider_bindings:
            raise Exception("Reference already registered")

        self._bind(ObjectProvider(reference, obj, _scope, _threads))

    def bind_factory(
        self,
        reference: REFERENCE,
        factory: Callable[..., R],
        *args: Any,
        _scope: Optional[str] = None,
        _threads: bool = False,
        **kwargs: Any,
    ) -> None:
        if reference in self.provider_bindings:
            raise Exception("Reference already registered")

        f = Factory(
            callable=factory,
            args=args,
            kwargs=kwargs,
        )
        self._bind(FactoryProvider(
            # MyPy error: incompatible type "str | type[Any]"; expected "str"
            reference=reference,  # type: ignore
            factory=f,
            scope=_scope,
            thread_safe=_threads,
        ))

    @overload
    def resolve(self, reference: str) -> Any: ...

    @overload
    def resolve(self, reference: Type[R]) -> R: ...

    def resolve(self, reference):
        return self._resolve_reference(reference).resolve()

    def _resolve_reference(self, reference: str) -> Provider:
        try:
            return self.provider_bindings[reference]
        except KeyError:
            raise Exception("Binding not found")

    def provide(self, reference) -> Provider:
        return self._resolve_reference(reference)

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
