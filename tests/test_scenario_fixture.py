"""Tests for the scenario_fixture pytest plugin."""

import pytest
from test_scenarios.scenario import ScenarioBuilder
from pymongo.database import Database
from syrupy.filters import props


def test_scenario_fixture_creation(
    scenario_builder: ScenarioBuilder, db: Database, snapshot_json
):
    """Test that scenario_fixture allows scenario creation"""
    inserted_ids_by_collection = scenario_builder.create(
        {
            "customers": [
                {"name": "Alice", "status": "inactive"},
                {"name": "Louis", "age": 25},
            ],
            "orders": [
                {
                    "id": "order_001",
                    "items": [
                        {"price": 19.99, "product_id": "book_123", "quantity": 1}
                    ],
                },
                {
                    "id": "order_002",
                    "items": None,
                    "tax": 0.2,
                },
            ],
        }
    )
    for collection_name, inserted_ids in inserted_ids_by_collection:
        assert len(inserted_ids) == 2
    assert db["customers"].find({}).to_list() == snapshot_json(
        name="customers", exclude=props("_id")
    )
    assert db["orders"].find({}).to_list() == snapshot_json(
        name="orders", exclude=props("_id")
    )
