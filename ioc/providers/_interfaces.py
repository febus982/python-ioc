from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar, Union

REFERENCE_TYPE = TypeVar("REFERENCE_TYPE")
REFERENCE = Union[str, Type[REFERENCE_TYPE]]


class Provider(Generic[REFERENCE_TYPE], ABC):
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
