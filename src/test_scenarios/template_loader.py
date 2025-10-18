"""
A utility to dynamically load template dictionaries from modules in a given package.
"""

import importlib
import pkgutil
from types import ModuleType
from typing import Any, Dict


def load_templates_from_path(package: ModuleType) -> Dict[str, Any]:
    """
    Dynamically loads 'TEMPLATE' dictionaries from all modules in a given package.

    This function iterates through all modules in the specified package path,
    imports them, and looks for a variable named 'TEMPLATE'. If found, it adds
    the content of 'TEMPLATE' to a dictionary, using the submodule's name as the key.

    Args:
        package: The package to search for modules (e.g., tests.templates).

    Returns:
        A dictionary where keys are the submodule names and values are the
        'TEMPLATE' dictionaries from each module.
    """
    templates: Dict[str, Any] = {}
    if not hasattr(package, "__path__"):
        raise ImportError(f"'{package.__name__}' is not a package")

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        # Construct the full module path (e.g., 'tests.templates.customers')
        full_module_path = f"{package.__name__}.{module_name}"

        # Import the module
        module = importlib.import_module(full_module_path)

        # Get the TEMPLATE variable if it exists
        if hasattr(module, "TEMPLATE"):
            templates[module_name] = getattr(module, "TEMPLATE")

    return templates
