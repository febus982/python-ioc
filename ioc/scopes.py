from contextlib import contextmanager
from typing import Iterator, List

from ioc._signals import scope_terminated

_scope_registry: List[str] = ["singleton"]


@contextmanager
def run_scope(scope: str) -> Iterator[None]:
    if scope == "singleton":
        raise RuntimeError(f"Scope {scope} cannot be initialised manually")

    if scope in _scope_registry:
        raise Exception(f"Scope `{scope}` already initialised")

    _scope_registry.append(scope)
    yield None
    _scope_registry.remove(scope)
    scope_terminated.send(scope)


def is_scope_running(scope: str) -> bool:
    return scope in _scope_registry
