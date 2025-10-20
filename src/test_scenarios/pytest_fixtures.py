from pymongo import MongoClient
from pymongo.database import Database
import pytest
import os

from test_scenarios.scenario import ScenarioBuilder
from test_scenarios.template_loader import load_templates_from_path


def _get_option(request: pytest.FixtureRequest, name: str, default=None):
    value = request.config.getoption(
        f"--{name}", default=os.environ.get(name.upper().replace("-", "_"), default)
    )
    print(f"Using option {name}={value}")
    return value


@pytest.fixture(scope="session")
def templates_path(request: pytest.FixtureRequest):
    return _get_option(request, "templates-path", default="tests/templates")


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
        print(f"Clearing collection {name} before test")
        db[name].delete_many({})
    yield db


@pytest.fixture
def scenario_builder(db: Database, templates_path: str) -> ScenarioBuilder:
    templates = load_templates_from_path(templates_path)
    return ScenarioBuilder(db, templates)
