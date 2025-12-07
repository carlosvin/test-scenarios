"""Tests that reload pytest_scenarios modules so coverage records definition lines."""

import importlib

import pytest_scenarios


def test_reload_pytest_scenarios_init_module():
    """Reload the package __init__ to execute the pytest_plugins assignment under coverage."""
    module = importlib.reload(pytest_scenarios)
    assert hasattr(module, "pytest_plugins")
    assert module.pytest_plugins == ["pytest_scenarios.pytest_fixtures"]


def test_reload_pytest_fixtures_module():
    """Reload the fixtures module to execute fixture definitions after coverage is active."""
    module = importlib.import_module("pytest_scenarios.pytest_fixtures")
    reloaded = importlib.reload(module)
    assert hasattr(reloaded, "_get_option")
    assert hasattr(reloaded, "templates_path")
    assert hasattr(reloaded, "mongo_client")
    assert hasattr(reloaded, "db")
    assert hasattr(reloaded, "scenario_builder")
    assert hasattr(reloaded, "cleanup_database")


def test_reload_scenario_module():
    """Reload the scenario module so the ScenarioBuilder definition is counted by coverage."""
    module = importlib.import_module("pytest_scenarios.scenario")
    reloaded = importlib.reload(module)
    assert hasattr(reloaded, "ScenarioBuilder")


def test_reload_template_loader_module():
    """Reload template_loader so load_templates_from_path definition executes under coverage."""
    module = importlib.import_module("pytest_scenarios.template_loader")
    reloaded = importlib.reload(module)
    assert hasattr(reloaded, "load_templates_from_path")
