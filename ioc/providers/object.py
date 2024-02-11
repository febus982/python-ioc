from typing import Any, Generic, Optional, Type, overload

from .._abstract import Container, Provider
from .._signals import scope_terminated
from .._types import R


class ObjectProvider(Generic[R], Provider[R]):
    __slots__ = ("target",)
    target: R

    @overload
    def __init__(
        self,
        reference: str,
        target: Any,
        scope: Optional[str] = None,
        thread_safe: bool = False,
    ) -> None: ...

    @overload
    def __init__(
        self,
        reference: Type[R],
        target: R,
        scope: Optional[str] = None,
        thread_safe: bool = False,
    ) -> None: ...

    def __init__(self, reference, target, scope=None, thread_safe=False):
        if isinstance(reference, type) and not isinstance(target, reference):
            raise TypeError(
                f"Provided target {repr(target)} is"
                f" not an instance of reference {repr(reference)}"
            )

        super().__init__(reference=reference, scope=scope, thread_safe=thread_safe)

        self.target = target

    def _resolve(self) -> R:
        return self.target

    def validate_nested_dependencies(self, container: Container) -> None:
        pass
