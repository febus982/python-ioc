from contextlib import contextmanager
from threading import local
from typing import Any, Dict, Iterator, Union

from ioc._interfaces import REFERENCE

_scoped_instances = local()


@contextmanager
def run_scope(scope: str) -> Iterator[None]:
    instances = _scoped_instances.__dict__
    if scope in instances:
        raise Exception(f"Scope `{scope}` already initialised")

    instances[scope] = {}
    yield None
    if scope != "singleton":
        del instances[scope]


def get_scoped_instances(scope: str) -> Dict[Union[str, None], Dict[REFERENCE, Any]]:
    try:
        return _scoped_instances.__dict__[scope]
    except KeyError:
        if scope == "singleton":
            _scoped_instances.__dict__[scope] = {}
        return _scoped_instances.__dict__[scope]
