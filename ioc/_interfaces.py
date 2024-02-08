from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar, overload, Union, Generic, Optional


R = TypeVar("R")
REFERENCE = Union[str, Type[R]]


class Provider(Generic[R], ABC):
    __slots__ = '_scope', '_reference'
    _scope: Optional[str]
    _reference: REFERENCE

    def __init__(self, reference: REFERENCE, scope: Optional[str] = None):
        super().__init__()
        self._reference = reference
        self._scope = scope

    @abstractmethod
    def resolve(self) -> Any:
        ...

    @property
    def scope(self) -> Optional[str]:
        return self._scope

    @property
    def reference(self) -> REFERENCE:
        return self._reference


class Container(ABC):
    @abstractmethod
    def bind(self, provider: Provider) -> None:
        ...

    @overload
    def resolve(self, reference: str) -> Any:
        ...

    @overload
    def resolve(self, reference: Type[R]) -> R:
        ...

    @abstractmethod
    def resolve(self, reference):
        ...
