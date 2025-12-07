import os

import pytest
from pymongo import MongoClient
from pymongo.database import Database

from pytest_scenarios.scenario import ScenarioBuilder
from pytest_scenarios.template_loader import load_templates_from_path


def _get_option(
    request: pytest.FixtureRequest, name: str, default: str | None = None
) -> str | None:
    """Resolve configuration value from CLI, environment, pytest.ini, or default."""

    config = request.config
    cli_value = config.getoption(f"--{name}", default=None)
    if cli_value is not None:
        value: str | None = cli_value
    else:
        env_key = name.upper().replace("-", "_")
        env_value = os.environ.get(env_key)
        if env_value is not None:
            value = env_value
        else:
            try:
                ini_value = config.getini(name)
            except (TypeError, ValueError):
                ini_value = None
            if isinstance(ini_value, str) and ini_value:
                value = ini_value
            else:
                value = default

    print(f"Using option {name}={value}")
    return value


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register pytest-scenarios custom command line and ini options."""

    group = parser.getgroup("pytest-scenarios")
    group.addoption(
        "--templates-path",
        action="store",
        dest="templates_path",
        default=None,
        help="Directory containing template modules for pytest-scenarios.",
    )
    group.addoption(
        "--db-url",
        action="store",
        dest="db_url",
        default=None,
        help="MongoDB connection string used by pytest-scenarios fixtures.",
    )
    group.addoption(
        "--db-name",
        action="store",
        dest="db_name",
        default=None,
        help="Database name used by pytest-scenarios fixtures.",
    )

    parser.addini(
        "templates-path",
        "Default directory containing template modules for pytest-scenarios.",
        default="tests/templates",
    )
    parser.addini(
        "db-url",
        "MongoDB connection string used by pytest-scenarios fixtures.",
        default="mongodb://127.0.0.1:27017/?directConnection=true",
    )
    parser.addini(
        "db-name",
        "Database name used by pytest-scenarios fixtures.",
        default="test_db",
    )


@pytest.fixture(scope="session")
def templates_path(request: pytest.FixtureRequest):
    return _get_option(request, "templates-path", default="tests/templates")


@pytest.fixture(scope="session")
def mongo_client(request: pytest.FixtureRequest):
    db_url = _get_option(
        request, "db-url", default="mongodb://127.0.0.1:27017/?directConnection=true"
    )
    with MongoClient(db_url) as client:
        yield client


@pytest.fixture(scope="session")
def db(request: pytest.FixtureRequest, mongo_client: MongoClient):
    db_name = _get_option(request, "db-name", default="test_db")
    yield mongo_client[db_name]


@pytest.fixture(scope="session")
def scenario_builder(db: Database, templates_path: str) -> ScenarioBuilder:
    templates = load_templates_from_path(templates_path)
    return ScenarioBuilder(db, templates)


@pytest.fixture(scope="function", autouse=True)
def cleanup_database(scenario_builder: ScenarioBuilder):
    """Clear all collections in the database before each test function."""
    scenario_builder.cleanup_collections()
