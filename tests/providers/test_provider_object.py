from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, Type, runtime_checkable

import pytest

from ioc.providers import ObjectProvider


class MyInterface(ABC):
    @abstractmethod
    def a(self) -> int: ...


class MyProtocol(Protocol):
    def a(self) -> int: ...


@runtime_checkable
class RuntimeProtocol(Protocol):
    def a(self) -> int: ...


class Concrete(MyInterface):
    def a(self) -> int:
        return 4


class NonMatchingConcrete:
    def b(self) -> int:
        return 4


@pytest.mark.parametrize(
    ["reference", "target", "exception"],
    [
        # Scenarios where target type matches reference
        ("str", Concrete(), None),
        (Concrete, Concrete(), None),
        (MyInterface, Concrete(), None),
        (RuntimeProtocol, Concrete(), None),
        (MyProtocol, Concrete(), TypeError),
        # Scenarios where target type doesn't match reference
        ("str", NonMatchingConcrete(), None),
        (Concrete, NonMatchingConcrete(), TypeError),
        (MyInterface, NonMatchingConcrete(), TypeError),
        (RuntimeProtocol, NonMatchingConcrete(), TypeError),
        (MyProtocol, NonMatchingConcrete(), TypeError),
    ],
)
def test_object_provider_raises_exception_if_target_and_reference_not_match(
    reference: Any, target: Any, exception: Optional[Type[Exception]]
):
    if exception:
        with pytest.raises(exception):
            ObjectProvider(reference, target)
    else:
        binding = ObjectProvider(reference, target)
        assert binding.resolve() is target
