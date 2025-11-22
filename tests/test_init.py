"""Test the init module where the pytest_plugins variable is defined."""


def test_pytest_plugins_import():
    """Test that pytest_plugins is correctly set in __init__.py."""
    # Import the __init__ module to trigger line 1 coverage
    import pytest_scenarios

    # Verify that the module has pytest_plugins defined
    assert hasattr(pytest_scenarios, "pytest_plugins")
    assert pytest_scenarios.pytest_plugins == ["pytest_scenarios.pytest_fixtures"]


def test_init_module_has_plugins_attribute():
    """Test that the module exports pytest_plugins for plugin registration."""
    # This ensures the __init__.py line gets executed in coverage
    from pytest_scenarios import pytest_plugins

    assert isinstance(pytest_plugins, list)
    assert len(pytest_plugins) > 0
