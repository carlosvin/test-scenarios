from collections.abc import Iterable

from bson import ObjectId
from pymongo.database import Database


class ScenarioBuilder:
    def __init__(self, db: Database, templates: dict[str, dict]):
        """Initialize the ScenarioBuilder with a MongoDB database and templates.
        Args:
            db: The MongoDB database instance.
            templates: A dictionary of templates to be used as blueprints for creating documents.
            The keys are collection names and the values are the template documents.
            We also create the collections in the database.
        """
        self._db = db
        self._templates = templates
        self._init_collections()

    def _create(
        self, scenario: dict[str, Iterable[dict]], add_scenario_id=False
    ) -> Iterable[tuple[str, list[ObjectId]]]:
        """Create a scenario with the given steps.
        The scenario is a dictionary where keys are collection names
        and values are iterables of documents to insert into those collections.
        This method yields tuples of collection name and list of inserted document IDs.
        They are only created when iterating over the returned iterable."""
        scenario_id = ObjectId()
        scenario_doc = {"scenario_id": scenario_id} if add_scenario_id else {}
        for collection_name, docs in scenario.items():
            collection = self._db[collection_name]
            template = self._templates.get(collection_name, {})
            docs_to_insert = [template | doc | scenario_doc for doc in docs]
            if not docs_to_insert:
                yield collection_name, []
                continue

            result = collection.insert_many(
                docs_to_insert, comment=f"ScenarioBuilder {scenario_id}"
            )
            if len(result.inserted_ids) != len(docs_to_insert):
                raise ValueError("Failed to insert all documents")

            yield collection_name, result.inserted_ids

    def create(
        self, scenario: dict[str, Iterable[dict]], add_scenario_id=False
    ) -> dict[str, list[ObjectId]]:
        """Create a test scenario by inserting documents into MongoDB collections.

        A scenario definition specifies document data that **overrides** template defaults.
        Each document in the scenario is merged with its collection's template using the
        pattern: template | scenario_document. This means:
        - Fields specified in the scenario **override** template values
        - Fields **not specified** in the scenario use template defaults
        - Fields only in the template are automatically included

        Args:
            scenario: Dictionary mapping collection names to lists of document overrides.
                Keys must correspond to existing template files (e.g., "customers"
                requires a customers.py template). Values are lists of partial documents
                that override specific template fields.

                Merge behavior:
                    final_document = TEMPLATE | scenario_document

                Example with template {"status": "active", "age": 18}:
                    {
                        "customers": [
                            # Overrides age, keeps status="active"
                            {"name": "Alice", "age": 25},
                            # Keeps both status="active" and age=18
                            {"name": "Bob"}
                        ],
                        "orders": [
                            # Merged with orders template
                            {"customer_id": "alice_123", "total": 99.99}
                        ]
                    }

            add_scenario_id: If True, adds a unique "scenario_id" ObjectId field to all
                inserted documents across all collections. Useful for tracking which
                documents belong to the same test scenario or for cleanup purposes.
                The scenario_id is added after template-scenario merging, so it won't
                be overridden by either.

        Returns:
            Dictionary mapping collection names to lists of inserted ObjectIds.
            For example: {"customers": [ObjectId(...), ObjectId(...)], "orders": [ObjectId(...)]}
            Empty document lists return empty ObjectId lists.

        Raises:
            ValueError: If the number of inserted documents doesn't match the number requested.
                This indicates a database error during insertion.

        Example:
            >>> # Template: {"status": "active", "balance": 0.0}
            >>> result = scenario_builder.create({
            ...     "customers": [
            ...         # Gets status="active", balance=0.0 from template
            ...         {"name": "Alice"},
            ...         # Gets status="active", overrides balance
            ...         {"name": "Bob", "balance": 100}
            ...     ]
            ... })
            >>> assert len(result["customers"]) == 2
            >>> # Alice has {name: "Alice", status: "active", balance: 0.0}
            >>> # Bob has {name: "Bob", status: "active", balance: 100}
        """
        inserted_ids_by_collection = {}
        for collection_name, inserted_ids in self._create(
            scenario, add_scenario_id=add_scenario_id
        ):
            inserted_ids_by_collection[collection_name] = inserted_ids
        return inserted_ids_by_collection

    def _init_collections(self) -> Iterable[dict]:
        """Register templates in the database.
        The templates is a dictionary where keys are collection names
        and values are iterables of documents to insert into those collections."""
        for collection_name in self._templates:
            self._db.create_collection(collection_name, check_exists=False)

    @property
    def collections(self) -> Iterable[str]:
        """Return the collection names managed by this ScenarioBuilder."""
        return self._templates.keys()

    def cleanup_collections(self):
        """Clear all collections managed by this ScenarioBuilder."""
        for name in self.collections:
            self._db[name].delete_many({})
