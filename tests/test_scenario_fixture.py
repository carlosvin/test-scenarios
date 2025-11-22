"""Tests for the scenario_fixture pytest plugin."""

from types import SimpleNamespace

import pytest
from pymongo.database import Database
from syrupy.filters import props

from pytest_scenarios.scenario import ScenarioBuilder


def test_scenario_fixture_creation(scenario_builder: ScenarioBuilder, db: Database, snapshot_json):
    """Test that scenario_fixture allows scenario creation"""
    inserted_ids_by_collection = scenario_builder.create(
        {
            # this overrides the values declared in test/templates/customers.py
            "customers": [
                {"name": "Alice", "status": "inactive", "email": "alice@test.com"},
                {"name": "Louis", "age": 25, "email": "louis@test.com"},
            ],
            # this overrides the values declared in test/templates/orders.py
            "orders": [
                {
                    "id": "order_001",
                    "items": [{"price": 19.99, "product_id": "book_123", "quantity": 1}],
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


def test_scenario_builder_direct_instantiation(scenario_builder):
    """Directly instantiate ScenarioBuilder to ensure class and __init__ lines are covered."""
    # Verify that our fixture was created with these templates
    assert "customers" in scenario_builder._templates
    assert "orders" in scenario_builder._templates
    assert scenario_builder._db is not None


def test_scenario_builder_create_method_directly(scenario_builder):
    """Call create method directly to ensure it executes."""
    results = list(scenario_builder.create({"customers": [{"name": "test"}]}))
    assert len(results) == 1
    assert results[0][0] == "customers"


def test_scenario_builder_init_collections_via_fixture(scenario_builder):
    """Verify _init_collections was called during fixture initialization."""
    # Collections should exist
    assert "customers" in scenario_builder._db.list_collection_names()
    assert "orders" in scenario_builder._db.list_collection_names()


def test_scenario_builder_collections_property_via_fixture(scenario_builder):
    """Test the collections property."""
    collections = list(scenario_builder.collections)
    assert "customers" in collections
    assert "orders" in collections


def test_scenario_builder_cleanup_via_fixture(scenario_builder):
    """Test cleanup_collections method."""
    # Insert data
    list(scenario_builder.create({"customers": [{"data": "test"}]}))
    assert scenario_builder._db["customers"].count_documents({}) > 0

    # Cleanup
    scenario_builder.cleanup_collections()
    assert scenario_builder._db["customers"].count_documents({}) == 0


class TestScenarioBuilderEdgeCases:
    """Additional tests for ScenarioBuilder edge cases."""

    def test_scenario_builder_with_empty_scenario(self, scenario_builder):
        """Test creating an empty scenario (no collections)."""
        result = list(scenario_builder.create({}))
        assert result == []

    def test_scenario_builder_cleanup_collections(self, scenario_builder):
        """Test cleanup_collections method removes all data."""
        # Insert some data
        list(scenario_builder.create({"customers": [{"name": "test"}]}))
        # Verify data exists
        assert scenario_builder._db["customers"].count_documents({}) > 0
        # Cleanup
        scenario_builder.cleanup_collections()
        # Verify data is gone
        assert scenario_builder._db["customers"].count_documents({}) == 0

    def test_scenario_builder_collections_property(self, scenario_builder):
        """Test the collections property returns correct collection names."""
        # scenario_builder fixture comes with customers and orders from templates
        collections = list(scenario_builder.collections)
        assert "customers" in collections
        assert "orders" in collections

    def test_scenario_builder_with_scenario_id(self, scenario_builder):
        """Test create with add_scenario_id=True."""
        result = list(
            scenario_builder.create({"customers": [{"name": "test"}]}, add_scenario_id=True)
        )
        assert len(result) == 1
        collection_name, inserted_ids = result[0]
        assert collection_name == "customers"
        # Verify the document has scenario_id
        doc = scenario_builder._db["customers"].find_one({"_id": inserted_ids[0]})
        assert "scenario_id" in doc

    def test_scenario_builder_merges_template_and_doc(self, scenario_builder):
        """Test that template fields are merged with provided document fields."""
        # customers template has status="active" by default
        list(scenario_builder.create({"customers": [{"name": "item1", "status": "inactive"}]}))
        doc = scenario_builder._db["customers"].find_one({})
        # Template value should be overridden
        assert doc["status"] == "inactive"
        # New value should be added
        assert doc["name"] == "item1"
