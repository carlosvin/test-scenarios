# pytest-scenarios demo

This folder contains a runnable example demonstrating how to use `pytest-scenarios` for isolated integration tests. It's referenced in the article [Isolated Integration Tests with pytest-scenarios](https://carlosvin.github.io/pytest-scenarios-isolated-integration-tests).

## Project Structure

```
examples/
├── src/
│   └── checkout.py      # Business logic being tested
├── tests/
│   ├── integration/
│   │   └── test_checkout.py   # Integration tests
│   └── templates/
│       ├── customers.py       # Default customer document
│       ├── products.py        # Default product document
│       └── orders.py          # Default order document
└── pyproject.toml
```

### The Checkout Class

The `src/checkout.py` module contains a simple e-commerce checkout system that:

- Validates customer status (must be active)
- Checks product availability (must be in stock)
- Calculates order totals
- Updates order status

This is the **business logic** we're testing.

### Templates

Templates define default values for your test documents. When creating scenarios, you only need to specify the fields that differ from the defaults:

```python
# templates/customers.py
TEMPLATE = {
    "name": "John Doe",
    "email": "john.doe@example.test",
    "status": "active",  # Default: customers are active
}
```

### Test Scenarios

Each test creates its own isolated scenario using `ScenarioBuilder`:

```python
def test_checkout_happy_path(scenario_builder: ScenarioBuilder, db: Database):
    # Arrange: Set up the scenario
    scenario_builder.create({
        "customers": [{"customer_id": "cust_1", "status": "active"}],
        "products": [{"product_id": "prod_1", "in_stock": True}],
        "orders": [{"id": "order_1", "customer_id": "cust_1", ...}],
    })

    # Act: Run the business logic
    checkout = Checkout(db)
    result = checkout.process(order_id="order_1")

    # Assert: Verify the outcome
    assert result.success is True
```

## Requirements

- [uv](https://github.com/astral-sh/uv) 0.4 or newer
- Docker (to spin up a disposable MongoDB instance)

## Getting Started

```bash
# Navigate to the examples directory
cd examples

# Install dependencies
uv sync

# Start MongoDB (runs in background, auto-removes on stop)
docker run --rm --name mongo-test -p 27017:27017 -d mongo:8

# Run the tests
uv run pytest tests/integration -v
```

## Key Concepts

### 1. Automatic Cleanup

The pytest plugin cleans up collections **before every test**, ensuring isolation even when tests fail.

### 2. Template Inheritance

Scenarios inherit from templates, so you only specify what's different:

```python
# Template defines: {"status": "active", "name": "John Doe", ...}
# Test only overrides what matters:
{"customer_id": "suspended_user", "status": "suspended"}
```

### 3. Declarative Scenarios

Focus on **what state you need**, not how to create it:

```python
scenario_builder.create({
    "customers": [...],
    "products": [...],
    "orders": [...],
})
```

### 4. Real Database Integration

Tests run against a real MongoDB instance, catching issues that mocks would miss.

## Stopping MongoDB

```bash
docker stop mongo-test
```
