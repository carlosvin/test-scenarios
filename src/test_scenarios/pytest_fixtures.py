from pymongo import MongoClient
from pymongo.database import Database
import pytest
import os

from test_scenarios.scenario import ScenarioBuilder


def _get_option(request: pytest.FixtureRequest, name: str, default=None):
    return request.config.getoption(
        f"--{name}", default=os.environ.get(name.upper().replace("-", "_"), default)
    )


@pytest.fixture(scope="session")
def mongo_client(request: pytest.FixtureRequest):
    db_url = _get_option(request, "db-url", default="mongodb://localhost:27017")
    with MongoClient(db_url) as client:
        yield client


@pytest.fixture(scope="function")
def db(request: pytest.FixtureRequest, mongo_client: MongoClient):
    db_name = _get_option(request, "db-name", default="test_db")
    db = mongo_client[db_name]
    for name in db.list_collection_names():
        db[name].delete_many({})
    yield db


@pytest.fixture
def scenario_fixture(db: Database):
    return ScenarioBuilder(db)
