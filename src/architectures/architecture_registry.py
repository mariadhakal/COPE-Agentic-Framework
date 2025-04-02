from typing import Dict, List, Callable, Any
import importlib
import os
import glob
import inspect


class ArchitectureRegistry:
    """Registry for architecture-specific analyzers."""

    _registry: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register an architecture analyzer."""

        def decorator(arch_class):
            cls._registry[name] = arch_class
            return arch_class

        return decorator

    @classmethod
    def get_analyzer(cls, name: str):
        """Get an architecture analyzer by name."""
        if name not in cls._registry:
            raise ValueError(f"Unknown architecture: {name}")
        return cls._registry[name]

    @classmethod
    def list_architectures(cls) -> List[str]:
        """List all registered architectures."""
        return list(cls._registry.keys())

    @classmethod
    def auto_discover(cls):
        """Automatically discover and register architecture analyzers."""
        # Get the directory where architecture implementations should be
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Find all Python files that aren't this registry
        py_files = glob.glob(os.path.join(current_dir, "*.py"))
        module_files = [f for f in py_files if os.path.basename(f) != "architecture_registry.py"
                        and not os.path.basename(f).startswith("__")]

        # Import each module
        for module_file in module_files:
            module_name = os.path.basename(module_file)[:-3]  # Remove .py extension
            module = importlib.import_module(f"src.architectures.{module_name}")

            # Find architecture analyzer classes
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'ARCHITECTURE_NAME'):
                    cls._registry[obj.ARCHITECTURE_NAME] = obj