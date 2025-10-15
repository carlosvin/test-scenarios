from typing import Iterable
from pymongo.database import Database


class ScenarioBuilder:
    def __init__(self, db: Database):
        self._db = db

    def create(self, scenario: dict[str, Iterable[dict]]) -> Iterable[dict]:
        """Create a scenario with the given steps.
        The scenario is a dictionary where keys are collection names
        and values are iterables of documents to insert into those collections."""
        for collection_name, docs in scenario.items():
            collection = self._db[collection_name]
            for doc in docs:
                result = collection.insert_one(doc, comment="ScenarioBuilder")
                if result.inserted_id is None:
                    raise ValueError("Failed to insert document")
                yield doc
