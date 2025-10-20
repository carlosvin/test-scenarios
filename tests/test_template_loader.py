"""
Tests for the template_loader utility.
"""

import importlib
from types import SimpleNamespace
from pytest_scenarios.template_loader import load_templates_from_path
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


def test_spec_none_and_no_loader_skipped(tmp_path, monkeypatch):
    """Test that modules with None spec or no loader are properly skipped during template loading.

    This test verifies the robustness of the template loading mechanism when encountering
    problematic Python modules that cannot be properly imported. It covers two specific
    edge cases:

    1. Modules where importlib.util.spec_from_file_location returns None
    2. Modules where the spec object has a None loader attribute

    The test creates three test modules in a temporary directory:
    - good.py: A valid module that should be loaded successfully
    - bad_none.py: Simulates a module that returns None from spec_from_file_location
    - bad_noloader.py: Simulates a module with a spec that has no loader

    The test uses monkeypatching to mock importlib.util.spec_from_file_location to
    simulate these failure conditions without actually creating corrupted files.

    Expected behavior:
    - The good module should be loaded and present in the returned templates
    - Both problematic modules (bad_none and bad_noloader) should be silently
        skipped and not appear in the final templates dictionary

    This ensures that the template loader gracefully handles import failures
    and doesn't crash when encountering modules that cannot be loaded.
    """
    # Create three modules: good, bad_none, bad_noloader
    good = tmp_path / "good.py"
    bad_none = tmp_path / "bad_none.py"
    bad_noloader = tmp_path / "bad_noloader.py"

    good.write_text("TEMPLATE = {'ok': True}\n")
    bad_none.write_text("TEMPLATE = {'ok': False}\n")
    bad_noloader.write_text("TEMPLATE = {'ok': False}\n")

    orig = importlib.util.spec_from_file_location

    def fake_spec(name, location, *args, **kwargs):
        # Simulate spec_from_file_location returning None for bad_none
        if name == "bad_none":
            return None
        # Simulate spec with no loader for bad_noloader
        if name == "bad_noloader":
            return SimpleNamespace(loader=None)
        return orig(name, location, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "spec_from_file_location", fake_spec)

    templates = load_templates_from_path(str(tmp_path))

    assert "good" in templates
    assert "bad_none" not in templates
    assert "bad_noloader" not in templates


def test_missing_template_skipped(tmp_path):
    """Modules that don't define TEMPLATE should be ignored."""
    no_template = tmp_path / "no_template.py"
    no_template.write_text("# no TEMPLATE here\nVAR = 123\n")

    templates = load_templates_from_path(str(tmp_path))

    assert "no_template" not in templates
