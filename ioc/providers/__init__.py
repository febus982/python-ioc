from typing import Any, Generic, Optional, Type, TypeVar, overload

from .._interfaces import Provider

T = TypeVar("T")


class ObjectProvider(Generic[T], Provider[T]):
    __slots__ = ("target",)
    target: T

    @overload
    def __init__(
        self, reference: str, target: Any, scope: Optional[str] = None
    ) -> None: ...

    @overload
    def __init__(
        self, reference: Type[T], target: T, scope: Optional[str] = None
    ) -> None: ...

    def __init__(self, reference, target, scope=None):
        if isinstance(reference, type) and not isinstance(target, reference):
            raise TypeError(
                f"Provided target {repr(target)} is"
                f" not an instance of reference {repr(reference)}"
            )

        super().__init__(reference=reference, scope=scope)

        self.target = target

    def resolve(self) -> T:
        return self.target
