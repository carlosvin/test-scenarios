"""
Tests for the template_loader utility.
"""

from test_scenarios.template_loader import load_templates_from_path
from tests.templates import customers, products, orders


def test_load_templates_successfully():
    """
    Tests that templates are loaded correctly from the specified package.
    """
    expected_templates = {
        "customers": customers.TEMPLATE,
        "products": products.TEMPLATE,
        "orders": orders.TEMPLATE,
    }
    loaded_templates = load_templates_from_path("tests/templates")
    assert loaded_templates == expected_templates
