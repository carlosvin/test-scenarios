"""Tests for the scenario_fixture pytest plugin."""

from types import SimpleNamespace

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
        assert db[collection_name].find({}).to_list() == snapshot_json(
            name=collection_name, exclude=props("_id")
        )


def test_collections_empty_before_test(db: Database):
    """Test that the collections are empty before each test function."""
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        assert count == 0, f"Collection {collection_name} is not empty before test"


def test_create_raises_on_partial_insert(db, scenario_builder, monkeypatch):
    """If insert_many does not return all inserted ids, raise ValueError."""

    def fake_insert_many(self, docs, comment=None, **kwargs):
        # Return a result with fewer inserted ids than docs
        result = SimpleNamespace()
        result.inserted_ids = [1]
        return result

    # Patch the insert_many method on the Collection class so any collection instance will use it
    import pymongo.collection

    monkeypatch.setattr(pymongo.collection.Collection, "insert_many", fake_insert_many)

    scenario = {"customers": [{"name": "a"}, {"name": "b"}]}

    with pytest.raises(ValueError):
        list(scenario_builder.create(scenario))
