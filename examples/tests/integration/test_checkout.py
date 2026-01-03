"""
Integration tests demonstrating pytest-scenarios usage.

These tests show how to use ScenarioBuilder to set up isolated test data,
then run real business logic against that data.

Key concepts:
    - Each test gets a clean database (collections are cleared automatically)
    - ScenarioBuilder creates documents from templates + overrides
    - Tests focus on behavior, not data setup boilerplate
"""

from pymongo.database import Database
from src.checkout import Checkout

from pytest_scenarios.scenario import ScenarioBuilder


class TestCheckoutHappyPath:
    """Tests for successful checkout scenarios."""

    def test_checkout_processes_valid_order(self, scenario_builder: ScenarioBuilder, db: Database):
        """
        Scenario: A customer successfully checks out an order.

        Given:
            - An active customer exists
            - A product is in stock
            - An order links them together

        When:
            - The checkout is processed

        Then:
            - The checkout succeeds
            - The order status becomes 'completed'
        """
        # Arrange: Set up the scenario
        scenario_builder.create(
            {
                "customers": [
                    {"customer_id": "customer_123", "status": "active"},
                ],
                "products": [
                    {"product_id": "sku-001", "price": 25.50, "in_stock": True},
                ],
                "orders": [
                    {
                        "id": "order_happy",
                        "customer_id": "customer_123",
                        "items": [{"product_id": "sku-001", "quantity": 2}],
                    }
                ],
            }
        )

        # Act: Run the business logic
        checkout = Checkout(db)
        result = checkout.process(order_id="order_happy")

        # Assert: Verify the outcome
        assert result.success is True
        assert result.order_id == "order_happy"
        assert result.error is None

        # Verify the order was updated in the database
        order = db["orders"].find_one({"id": "order_happy"})
        assert order["status"] == "completed"
        assert order["total"] == 51.0  # 25.50 * 2

    def test_checkout_uses_precalculated_total(
        self, scenario_builder: ScenarioBuilder, db: Database
    ):
        """
        Scenario: Order has a pre-calculated total (e.g., with discounts).

        When the order already has a total, checkout preserves it
        rather than recalculating from item prices.
        """
        # Arrange
        scenario_builder.create(
            {
                "customers": [
                    {"customer_id": "vip_customer", "status": "active"},
                ],
                "products": [
                    {"product_id": "premium-item", "price": 100.0, "in_stock": True},
                ],
                "orders": [
                    {
                        "id": "discounted_order",
                        "customer_id": "vip_customer",
                        "items": [{"product_id": "premium-item", "quantity": 1}],
                        "total": 80.0,  # 20% VIP discount applied
                    }
                ],
            }
        )

        # Act
        checkout = Checkout(db)
        result = checkout.process(order_id="discounted_order")

        # Assert
        assert result.success is True
        order = db["orders"].find_one({"id": "discounted_order"})
        assert order["total"] == 80.0  # Discount preserved


class TestCheckoutValidation:
    """Tests for checkout validation and error handling."""

    def test_checkout_rejects_inactive_customer(
        self, scenario_builder: ScenarioBuilder, db: Database
    ):
        """
        Scenario: Customer account is suspended.

        Checkout should fail with a clear error message when
        the customer's status is not 'active'.
        """
        # Arrange
        scenario_builder.create(
            {
                "customers": [
                    {"customer_id": "suspended_user", "status": "suspended"},
                ],
                "products": [
                    {"product_id": "any-product", "in_stock": True},
                ],
                "orders": [
                    {
                        "id": "blocked_order",
                        "customer_id": "suspended_user",
                        "items": [{"product_id": "any-product", "quantity": 1}],
                    }
                ],
            }
        )

        # Act
        checkout = Checkout(db)
        result = checkout.process(order_id="blocked_order")

        # Assert
        assert result.success is False
        assert "not active" in result.error
        assert "suspended" in result.error

        # Order status should remain unchanged
        order = db["orders"].find_one({"id": "blocked_order"})
        assert order["status"] == "pending"

    def test_checkout_rejects_out_of_stock_item(
        self, scenario_builder: ScenarioBuilder, db: Database
    ):
        """
        Scenario: Product is out of stock.

        Checkout should fail gracefully when any item in the order
        is not available in inventory.
        """
        # Arrange
        scenario_builder.create(
            {
                "customers": [
                    {"customer_id": "eager_buyer", "status": "active"},
                ],
                "products": [
                    {"product_id": "sold-out-item", "in_stock": False},
                ],
                "orders": [
                    {
                        "id": "unavailable_order",
                        "customer_id": "eager_buyer",
                        "items": [{"product_id": "sold-out-item", "quantity": 1}],
                    }
                ],
            }
        )

        # Act
        checkout = Checkout(db)
        result = checkout.process(order_id="unavailable_order")

        # Assert
        assert result.success is False
        assert "out of stock" in result.error.lower()
        assert "sold-out-item" in result.error

    def test_checkout_rejects_nonexistent_order(
        self, scenario_builder: ScenarioBuilder, db: Database
    ):
        """
        Scenario: Order ID doesn't exist.

        Demonstrates that tests start with a clean database,
        so non-existent orders are properly rejected.
        """
        # Arrange: Empty scenario (clean database)
        # No need to create any data

        # Act
        checkout = Checkout(db)
        result = checkout.process(order_id="ghost_order")

        # Assert
        assert result.success is False
        assert result.error == "Order not found"


class TestScenarioIsolation:
    """Tests demonstrating that scenarios are isolated between tests."""

    def test_first_scenario_creates_data(self, scenario_builder: ScenarioBuilder, db: Database):
        """First test creates some data."""
        scenario_builder.create(
            {
                "customers": [{"customer_id": "test_isolation_customer"}],
            }
        )

        assert db["customers"].count_documents({}) == 1

    def test_second_scenario_has_clean_slate(self, scenario_builder: ScenarioBuilder, db: Database):
        """
        Second test starts fresh.

        This proves that pytest-scenarios cleans up between tests,
        ensuring true isolation.
        """
        # The customer from the previous test should not exist
        assert db["customers"].count_documents({}) == 0
        assert db["customers"].find_one({"customer_id": "test_isolation_customer"}) is None
