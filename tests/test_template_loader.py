"""
Tests for the template_loader utility.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the src directory to the Python path to allow for absolute imports
sys.path.insert(0, "/Users/carlos/workspace/test-scenarios/src")

from test_scenarios.template_loader import load_templates_from_path
import tests.templates as templates_package
from tests.templates import customers, products


def test_load_templates_successfully():
    """
    Tests that templates are loaded correctly from the specified package.
    """
    expected_templates = {
        "customers": customers.TEMPLATE,
        "products": products.TEMPLATE,
        "orders": products.TEMPLATE,
    }
    loaded_templates = load_templates_from_path(templates_package)
    assert loaded_templates == expected_templates


def test_package_not_found(self):
    """
    Tests that an ImportError is raised if the package does not exist.
    """
    with self.assertRaises(ImportError):
        # Create a mock for a non-existent package
        non_existent_package = MagicMock()
        non_existent_package.__name__ = "non_existent_package"
        # Remove __path__ to simulate a non-package module
        del non_existent_package.__path__
        load_templates_from_path(non_existent_package)


@patch("importlib.import_module")
def test_module_without_template_variable(self, mock_import_module):
    """
    Tests that modules without a 'TEMPLATE' variable are skipped.
    """
    # Mock a module without the TEMPLATE attribute
    mock_module = MagicMock()
    del mock_module.TEMPLATE
    mock_import_module.return_value = mock_module

    # Create a mock package to control the modules found
    mock_package = MagicMock()
    mock_package.__name__ = "mock_package"
    mock_package.__path__ = ["/fake/path"]

    with patch(
        "pkgutil.iter_modules", return_value=[(None, "no_template_module", None)]
    ):
        templates = load_templates_from_path(mock_package)
        self.assertEqual(templates, {})


@patch("importlib.import_module", side_effect=ImportError("Mock import error"))
def test_import_error_handling(self, mock_import_module):
    """
    Tests that the function handles ImportErrors gracefully when a submodule fails to import.
    """
    # Create a mock package to control the modules found
    mock_package = MagicMock()
    mock_package.__name__ = "mock_package"
    mock_package.__path__ = ["/fake/path"]

    with patch("pkgutil.iter_modules", return_value=[(None, "failing_module", None)]):
        templates = load_templates_from_path(mock_package)
        # Expect that no templates are loaded because the import fails
        self.assertEqual(templates, {})
        # Check that the import was attempted
        mock_import_module.assert_called_with("mock_package.failing_module")
