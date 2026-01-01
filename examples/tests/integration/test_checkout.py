"""Integration tests showing pytest-scenarios usage."""

from pymongo.database import Database

from pytest_scenarios.scenario import ScenarioBuilder


def test_checkout_happy_path(scenario_builder: ScenarioBuilder, db: Database):
    """A customer successfully checks out an order.
    Scenario:
        Given an active customer and a product in stock
        Then the order is created with status 'pending' and correct total amount.
    """
    list(
        scenario_builder.create(
            {
                "customers": [
                    {"customer_id": "customer_123", "status": "active"},
                ],
                "products": [
                    {"product_id": "sku-001", "price": 25.50},
                ],
                "orders": [
                    {
                        "id": "checkout_order",
                        "customer_id": "customer_123",
                        "items": [{"product_id": "sku-001", "quantity": 1}],
                        "total": 25.50,
                    }
                ],
            }
        )
    )

    # Verify that the scenario has been set up correctly
    order = db["orders"].find_one({"id": "checkout_order"})
    assert order["status"] == "pending"
    assert order["total"] == 25.50
    customer = db["customers"].find_one({"customer_id": "customer_123"})
    assert customer["status"] == "active"

    # You have to add the actual test assertions here


def test_checkout_rejects_out_of_stock_item(scenario_builder: ScenarioBuilder, db: Database):
    """
    Test scenario: There is a product that is out of stock.
    The order creation has failed.
    """
    # Verify that the previous scenario data has been cleaned up
    assert db["orders"].count_documents({}) == 0

    docs_iterable = scenario_builder.create(
        {
            "products": [
                {"product_id": "sku-003", "in_stock": False},
            ],
            "orders": [
                {
                    "id": "failed_checkout",
                    "items": [{"product_id": "sku-003", "quantity": 1}],
                }
            ],
        }
    )
    assert len(list(docs_iterable)) == 2

    # Verify that the scenario has been set up correctly in the database
    product = db["products"].find_one({"product_id": "sku-003"})
    assert product["in_stock"] is False
    order = db["orders"].find_one({"id": "failed_checkout"})
    assert order["items"][0]["product_id"] == "sku-003"

    # You have to add the actual test assertions here
