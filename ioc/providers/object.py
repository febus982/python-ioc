from typing import Any, Generic, Optional, Type, overload

from .._abstract import Provider
from .._types import R


class ObjectProvider(Generic[R], Provider[R]):
    __slots__ = ("target",)
    target: R

    @overload
    def __init__(
        self, reference: str, target: Any, scope: Optional[str] = None
    ) -> None: ...

    @overload
    def __init__(
        self, reference: Type[R], target: R, scope: Optional[str] = None
    ) -> None: ...

    def __init__(self, reference, target, scope=None):
        if isinstance(reference, type) and not isinstance(target, reference):
            raise TypeError(
                f"Provided target {repr(target)} is"
                f" not an instance of reference {repr(reference)}"
            )

        super().__init__(reference=reference, scope=scope)

        self.target = target

    def _resolve(self) -> R:
        return self.target
