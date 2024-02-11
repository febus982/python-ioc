from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Optional,
    Type,
    Union,
    overload,
)

from .._abstract import Container, Provider
from .._signals import scope_terminated
from .._types import R


class Factory(Generic[R]):
    __slots__ = "callable", "args", "kwargs"
    callable: Callable[..., R]
    args: Iterable[Any]
    kwargs: Dict[str, Any]

    def __init__(
        self,
        callable: Callable[..., R],
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        self.callable = callable
        self.args = args or ()
        self.kwargs = kwargs or {}


class FactoryProvider(Generic[R], Provider[R]):
    __slots__ = ("factory",)
    factory: Factory[Union[R, Any]]

    @overload
    def __init__(
        self,
        reference: str,
        factory: Factory[Any],
        scope: Optional[str] = None,
        thread_safe: bool = False,
    ) -> None: ...

    @overload
    def __init__(
        self,
        reference: Type[R],
        factory: Factory[R],
        scope: Optional[str] = None
    ) -> None: ...

    def __init__(self, reference, factory: Factory, scope=None, thread_safe=False):
        # Can we check factory callable typing returns the same type as reference?
        super().__init__(reference=reference, scope=scope, thread_safe=thread_safe)
        self.factory = factory
        self.needs_nested_providers_check = True

        if scope is not None:
            scope_terminated.connect(self._cleanup_scopes, sender=scope)

    def _resolve(self) -> R:
        return self.factory.callable(
            *[
                (x.resolve() if isinstance(x, Provider) else x)
                for x in self.factory.args
            ],
            **{
                k: (v.resolve() if isinstance(v, Provider) else v)
                for k, v in self.factory.kwargs.items()
            },
        )

    def validate_nested_dependencies(self, container: Container) -> None:
        dependencies = [x for x in self.factory.args if isinstance(x, Provider)]
        dependencies.extend(
            [x for x in self.factory.kwargs.values() if isinstance(x, Provider)]
        )

        for dependency in dependencies:
            container.provide(dependency.reference)
