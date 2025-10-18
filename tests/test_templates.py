from test_scenarios.templates import load
from tests.templates import orders


def test_load_template():
    """Test loading a template module."""

    template = load("tests.templates", "orders")
    assert template == orders.TEMPLATE
