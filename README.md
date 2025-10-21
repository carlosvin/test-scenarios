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

Or with uv:

```bash
uv add pytest-scenarios --dev
```

Or with Poetry:

```bash
poetry add pytest-scenarios --group dev
```

## Configuration

Set the MongoDB connection URI via environment variable:

```bash
export MONGODB_URI="mongodb://localhost:27017"
```

## Getting started (pytest)

A simple test:

```python
def test_example(
    scenario_builder: ScenarioBuilder, db: Database
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
```

Run tests:

```bash
pytest -q
```

## Contributing

Contributions welcome. Please add tests for new features and follow the project's coding standards.

## License

MIT
