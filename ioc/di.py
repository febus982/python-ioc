from functools import wraps
from inspect import _empty, getmodule, iscoroutinefunction, signature, stack
from types import ModuleType
from typing import Any, Callable, TypeVar, cast

from ._registry import provider_registry
from ._types import REFERENCE

F = TypeVar("F", bound=Callable[..., Any])


def _inject_dependencies(f: F, *args, **kwargs):
    module = getmodule(f)
    if module is None:
        # Not sure how to test this but getmodule could return None
        raise RuntimeError("Cannot identify source module")  # pragma: no cover
    sig = signature(f)

    for i, key in enumerate(sig.parameters.keys()):
        # Skip positional args, they have a value
        if i < len(args):
            continue

        if all([
            key not in kwargs,  # Has not been passed
            sig.parameters[key].default is _empty,  # Has no default
            (module, sig.parameters[key].annotation) in provider_registry
        ]):
            kwargs[key] = provider_registry[
                (module, sig.parameters[key].annotation)
            ][0].resolve()

    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    return [
        x.resolve() if isinstance(x, Require) else x
        for x in bound.args
    ], {
        k: (v.resolve() if isinstance(v, Require) else v)
        for (k, v) in bound.kwargs.items()
    }


def inject(f: F, p=None) -> F:
    if iscoroutinefunction(f):
        @wraps(f)  # type: ignore
        async def wrapper(*args, **kwargs):
            args, kwargs = _inject_dependencies(f, *args, **kwargs)
            return await f(*args, **kwargs)
    else:
        @wraps(f)
        def wrapper(*args, **kwargs):
            args, kwargs = _inject_dependencies(f, *args, **kwargs)
            return f(*args, **kwargs)
    return cast(F, wrapper)


class Require:
    _reference: REFERENCE
    _module: ModuleType

    def __init__(self, reference: REFERENCE):
        module = getmodule(stack()[1][0])
        if module is None:
            # Not sure how to test this but getmodule could return None
            raise RuntimeError("Cannot identify source module")  # pragma: no cover
        self._module = module
        self._reference = reference

    def resolve(self):
        # Identify in what module the function is called using inspect.stack()
        # Find the relevant container
        # raise Exception(_registry.get((self._module, self._reference), (None,))[0])

        try:
            provider = provider_registry[(self._module, self._reference)][0]
        except KeyError:
            raise Exception("Reference not wired for module")

        return provider.resolve()
