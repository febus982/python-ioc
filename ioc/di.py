from functools import wraps
from inspect import getmodule, iscoroutinefunction, signature, stack
from types import ModuleType
from typing import Any, Callable, TypeVar, cast

from ._interfaces import REFERENCE
from ._registry import ContainerRegistry

REF = TypeVar("REF")
F = TypeVar("F", bound=Callable[..., Any])


def enable_injection(f: F) -> F:
    sig = signature(f)

    if iscoroutinefunction(f):

        @wraps(f)  # type: ignore
        async def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            return await f(
                *[x.resolve() if isinstance(x, Inject) else x for x in bound.args],
                **{
                    k: (v.resolve() if isinstance(v, Inject) else v)
                    for (k, v) in bound.kwargs.items()
                }
            )

    else:

        @wraps(f)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            return f(
                *[x.resolve() if isinstance(x, Inject) else x for x in bound.args],
                **{
                    k: (v.resolve() if isinstance(v, Inject) else v)
                    for (k, v) in bound.kwargs.items()
                }
            )

    return cast(F, wrapper)


class Inject:
    _reference: REFERENCE
    _source: ModuleType

    def __init__(self, reference: REFERENCE):
        module = getmodule(stack()[1][0])
        if module is None:
            # Not sure how to test this but getmodule could return None
            raise RuntimeError("Cannot identify source module")  # pragma: no cover
        self._source = module
        self._reference = reference

    def resolve(self):
        # Identify in what module the function is called using inspect.stack()
        # Find the relevant container
        container = ContainerRegistry.get_container(self._source)
        return container.resolve(self._reference) if container else self
