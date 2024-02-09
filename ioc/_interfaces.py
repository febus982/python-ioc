from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    overload,
)

R = TypeVar("R")
REFERENCE = Union[str, Type[R]]


class Provider(Generic[R], ABC):
    __slots__ = "scope", "reference"
    scope: Optional[str]
    reference: REFERENCE

    def __init__(self, reference: REFERENCE, scope: Optional[str] = None):
        super().__init__()
        self.reference = reference
        self.scope = scope

    @abstractmethod
    def resolve(self) -> R: ...


class Container(ABC):
    provider_bindings: Dict[REFERENCE, Provider]
    modules: Set[str] = set()
    packages: Set[str] = set()

    @abstractmethod
    def bind(self, provider: Provider) -> None: ...

    @overload
    def resolve(self, reference: str) -> Any: ...

    @overload
    def resolve(self, reference: Type[R]) -> R: ...

    @abstractmethod
    def resolve(self, reference): ...
