# Test Scenarios

Test Scenarios is a small Python library that simplifies writing integration tests by providing easy-to-use scenario definitions backed by MongoDB. It makes setup and teardown of test data explicit and repeatable, so your integration tests stay reliable and easy to reason about.

## Key features

- Minimal, opinionated API for defining scenarios (collections + documents)
- Easy pytest integration via fixtures
- Works with local or remote MongoDB instances
- Focused on readability and test determinism

## Installation

```bash
pip install pytest-scenarios
```

Or with uv:

```bash
uv add pytest-scenarios --dev
```

Or with Poetry:

```bash
poetry add pytest-scenarios --group dev
```

## Templates

The templates are documents with predefined values that will be used to create scenarios.

A template corresponds with a MongoDB collection.

Check the example at [tests/templates](./tests/templates) where we have `customers`, `orders` and `products`.

Every template should module consists of a dictionary assigned to a constant named `TEMPLATE`.

```python
# tests/templates/orders.py

TEMPLATE = {
    "id": "123456789abcdef01234567",
    "customer_id": "customer_001",
    "items": [
        {"product_id": "product_001", "quantity": 2, "price": 19.99},
        {"product_id": "product_002", "quantity": 1, "price": 9.99},
    ],
    "tax": 0.15,
}
```

## Configuration

The configuration can be set via environment variables or via pytest init options.

### DB Connection

Set the MongoDB connection URI via environment variable.

```bash
# environment var
DB_URL=mongodb://localhost:27017
DB_NAME=test_db
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
db-url="mongodb://localhost:27017"
db-name="test_db"
```

```ini
# pytest.ini
[pytest]
db-url=mongodb://localhost:27017
db-name=test_db
```

### Templates path

The location of the templates used to generate the database documents.

```bash
# environment var
TEMPLATES_PATH=tests/templates
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
templates-path="tests/templates"
```

```ini
# pytest.ini
[pytest]
templates-path=tests/templates
```

## Getting started (pytest)

A simple test:

```python
def test_example(
    scenario_builder: ScenarioBuilder, db: Database
):
    """Test that the scenario is created correctly, in this case it creates 2 customers and 2 orders"""
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
        # in the scenario above we are inserting 2 documents by collection
        assert len(inserted_ids) == 2, collection_name
```

You can check some examples of of the generated documents here:

- [customers](./tests/__snapshots__/test_scenario_fixture/test_scenario_fixture_creation[customers].json)
- [orders](./tests/__snapshots__/test_scenario_fixture/test_scenario_fixture_creation[orders].json)

## Contributing

Contributions welcome. Please add tests for new features and follow the project's coding standards.

## License

MIT
