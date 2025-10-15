"""Tests for the scenario_fixture pytest plugin."""

from test_scenarios.scenario import ScenarioBuilder
from pymongo.database import Database


def test_scenario_fixture_creation(scenario_fixture: ScenarioBuilder, db: Database):
    """Test that scenario_fixture allows scenario creation"""
    sc = ScenarioBuilder(db)
    sc.create(
        {
            "users": [{"name": "Alice"}, {"name": "Carlos"}],
            "orders": [{"item": "Book"}, {"item": "Car"}],
        }
    )
    assert db["users"].count_documents({}) == 2
    assert db["orders"].count_documents({}) == 2
