from importlib import import_module
from pkgutil import walk_packages
from types import ModuleType
from typing import Dict, Iterable, List, Optional

from ioc._interfaces import Container


class ContainerRegistry:
    _registry: Dict[ModuleType, Container] = {}

    @classmethod
    def get_container(cls, module: ModuleType) -> Optional[Container]:
        return cls._registry.get(module)

    @classmethod
    def wire(
        cls,
        container: Container,
        modules: Iterable[str] = tuple(),
        packages: Iterable[str] = tuple(),
    ) -> None:
        # The same container can be wired to multiple modules
        # We cannot wire multiple containers to the same module
        if any(
            [
                cls._any_relative_string_imports(modules),
                cls._any_relative_string_imports(packages),
            ]
        ):
            raise ImportError("Relative imports are not supported.")

        # Resolve single modules
        resolved_modules = cls._resolve_string_imports(modules)

        # Walk packages and resolve their modules
        for p in cls._resolve_string_imports(packages):
            resolved_modules.extend(cls._get_package_modules(p))

        # Check no already initialised modules/packages
        intersection = set(resolved_modules).intersection(cls._registry.keys())
        if intersection:
            raise ValueError("Cannot wire more than one container to a module.")

        # bind container to list of modules/packages
        cls._registry.update(dict.fromkeys(resolved_modules, container))
        # cls._registry["aaa"] = container

    @staticmethod
    def _any_relative_string_imports(modules: Iterable[str]) -> bool:
        return any([x.startswith(".") for x in modules if isinstance(x, str)])

    @staticmethod
    def _resolve_string_imports(
        modules: Iterable[str], from_package: Optional[str] = None
    ) -> List[ModuleType]:
        return [
            import_module(module, from_package)
            for module in modules
            if isinstance(module, str)
        ]

    @staticmethod
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
