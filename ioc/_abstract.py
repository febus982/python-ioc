from abc import ABC, abstractmethod
from threading import local
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Set,
    Type,
    overload,
)

from ._signals import scope_terminated
from ._types import REFERENCE, R
from .scopes import is_scope_running


class Provider(Generic[R], ABC):
    __slots__ = (
        "scope",
        "reference",
        "thread_safe",
        "needs_nested_providers_check",
        "_scoped_instance",
        "_threadlocal_instance",
        "__weakref__",
    )
    scope: Optional[str]
    reference: REFERENCE
    thread_safe: bool
    needs_nested_providers_check: bool
    _scoped_instance: Optional[R]
    _threadlocal_instance: local

    def __init__(
        self,
        reference: REFERENCE,
        scope: Optional[str] = None,
        thread_safe: bool = False,
    ):
        super().__init__()
        self.reference = reference
        self.scope = scope
        self.thread_safe = thread_safe
        self.needs_nested_providers_check = False
        self._cleanup_scopes()
        if scope is not None:
            scope_terminated.connect(self._cleanup_scopes, sender=scope)

    def resolve(self) -> R:
        if self.scope:
            if not is_scope_running(self.scope):
                raise RuntimeError("Scope is not running")
            if self.thread_safe:
                return self._resolve_threadlocal_instance()
            else:
                return self._resolve_scoped_instance()

        return self._resolve()

    def _resolve_scoped_instance(self) -> R:
        if self._scoped_instance is None:
            self._scoped_instance = self._resolve()
        return self._scoped_instance

    def _resolve_threadlocal_instance(self) -> R:
        instance = getattr(self._threadlocal_instance, "instance", None)
        if not instance:
            instance = self._resolve()
            self._threadlocal_instance.instance = instance
        return instance

    def _cleanup_scopes(self, scope: Optional[str] = None) -> None:
        self._threadlocal_instance = local()
        self._scoped_instance = None

    @abstractmethod
    def validate_nested_dependencies(self, container: "Container") -> None: ...

    @abstractmethod
    def _resolve(self) -> R: ...


class Container(ABC):
    __slots__ = "provider_bindings", "modules", "packages"
    provider_bindings: Dict[REFERENCE, Provider]
    modules: Set[str]
    packages: Set[str]

    def __init__(self):
        self.provider_bindings = {}
        self.modules = set()
        self.packages = set()

    @abstractmethod
    def bind_object(
        self,
        reference: REFERENCE,
        obj: Any,
        _scope: Optional[str] = None,
        _threads: bool = False,
    ) -> None:
        ...

    @abstractmethod
    def bind_factory(
        self,
        reference: REFERENCE,
        factory: Callable[..., R],
        *args: Any,
        _scope: Optional[str] = None,
        _threads: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    @overload
    def resolve(self, reference: str) -> Any: ...

    @overload
    def resolve(self, reference: Type[R]) -> R: ...

    @abstractmethod
    def resolve(self, reference): ...

    @abstractmethod
    def provide(self, reference: REFERENCE) -> Provider: ...
