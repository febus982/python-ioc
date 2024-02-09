from importlib import import_module
from pkgutil import walk_packages
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Set, Tuple

from ioc._abstract import Container, Provider
from ioc._types import REFERENCE

_registry: Dict[Tuple[ModuleType, REFERENCE], Tuple[Provider, Container]] = {}


def register_container(
    container: Container,
    modules: Iterable[str] = tuple(),
    packages: Iterable[str] = tuple(),
) -> None:
    resolved_modules = _walk_imports(modules, packages)

    # Create a mapping with new providers to wire
    new_providers: Dict[Tuple[ModuleType, REFERENCE], Provider] = {
        (module, reference): provider
        for module in resolved_modules
        for reference, provider in container.provider_bindings.items()
    }

    # Check no already initialised modules/packages
    intersection: Set[Tuple[ModuleType, REFERENCE]] = set(
        new_providers.keys()
    ).intersection(_registry.keys())
    if intersection:
        # There might be multiple ones, but we're happy to return only one
        wired_reference = next(iter(intersection))
        raise ValueError(
            f"The reference {wired_reference[1]} is already wired"
            f" to module `{wired_reference[0].__name__}`."
        )

    # Register the references
    for module in resolved_modules:
        for reference, provider in container.provider_bindings.items():
            _registry[(module, reference)] = (provider, container)


def _walk_imports(modules: Iterable[str], packages: Iterable[str]) -> List[ModuleType]:
    if any(
        [
            _any_relative_string_imports(modules),
            _any_relative_string_imports(packages),
        ]
    ):
        raise ImportError("Relative imports are not supported.")
    # Resolve single modules
    resolved_modules = _resolve_string_imports(modules)
    # Walk packages and resolve their modules
    for p in _resolve_string_imports(packages):
        resolved_modules.extend(_get_package_modules(p))
    return resolved_modules


def unregister_container(
    container: Container,
    modules: Iterable[str] = tuple(),
    packages: Iterable[str] = tuple(),
) -> None:
    resolved_modules = _walk_imports(modules, packages)

    for module in resolved_modules:
        for reference, provider in container.provider_bindings.items():
            if _registry.get((module, reference)) == (provider, container):
                del _registry[(module, reference)]


def _any_relative_string_imports(modules: Iterable[str]) -> bool:
    return any([x.startswith(".") for x in modules if isinstance(x, str)])


def _resolve_string_imports(
    modules: Iterable[str], from_package: Optional[str] = None
) -> List[ModuleType]:
    return [
        import_module(module, from_package)
        for module in modules
        if isinstance(module, str)
    ]


def _get_package_modules(package: ModuleType) -> List[ModuleType]:
    modules = [package]
    if not hasattr(package, "__path__") or not hasattr(package, "__name__"):
        return modules

    modules.extend(
        [
            import_module(x.name)
            for x in walk_packages(
                path=package.__path__,
                prefix=package.__name__ + ".",
            )
        ]
    )

    return modules
