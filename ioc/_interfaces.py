from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar, overload

from ioc.providers import Provider

REFERENCE_TYPE = TypeVar("REFERENCE_TYPE")


class Container(ABC):
    @abstractmethod
    def bind(self, provider: Provider) -> None:
        ...

    @overload
    def resolve(self, reference: str) -> Any:
        ...

    @overload
    def resolve(self, reference: Type[REFERENCE_TYPE]) -> REFERENCE_TYPE:
        ...

    @abstractmethod
    def resolve(self, reference):
        ...
