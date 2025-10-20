# Test Scenarios

Test Scenarios is a small Python library that simplifies writing integration tests by providing easy-to-use scenario definitions backed by MongoDB. It makes setup and teardown of test data explicit and repeatable, so your integration tests stay reliable and easy to reason about.

## Key features

- Minimal, opinionated API for defining scenarios (collections + documents)
- Easy pytest integration via fixtures
- Works with local or remote MongoDB instances
- Focused on readability and test determinism

## Installation

For development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

If published to PyPI, you can install the package:

```bash
pip install pytest-scenarios
```

## Configuration

Set the MongoDB connection URI via environment variable:

```bash
export MONGODB_URI="mongodb://localhost:27017"
```

## Getting started (pytest)

Example pytest configuration using the library and pymongo:

```python
# conftest.py
import os
import pytest
from pymongo import MongoClient
from test_scenarios import TestScenario

user_scenario = TestScenario(
    collection="users",
    documents=[
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ],
)

@pytest.fixture(scope="session")
def mongo_client():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    yield client
    client.close()

@pytest.fixture(autouse=True)
def apply_scenarios(mongo_client):
    db = mongo_client.get_database("test")
    user_scenario.setup(db)
    try:
        yield
    finally:
        user_scenario.teardown(db)
```

A simple test:

```python
# tests/test_users.py
def test_user_count(mongo_client):
    db = mongo_client.get_database("test")
    assert db.users.count_documents({}) == 2
```

Run tests:

```bash
pytest -q
```

## Local MongoDB (Docker)

Start a local MongoDB for testing:

```bash
docker run -d -p 27017:27017 --name mongo-test mongo:6
```

## Contributing

Contributions welcome. Please add tests for new features and follow the project's coding standards.

## License

MIT
