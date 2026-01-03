"""
Checkout module - demonstrates business logic for testing with pytest-scenarios.

This is a simplified e-commerce checkout system that validates orders,
checks product availability, and processes payments.
"""

from dataclasses import dataclass
from typing import Literal

from pymongo.database import Database


@dataclass
class CheckoutResult:
    """Result of a checkout operation."""

    success: bool
    order_id: str | None = None
    error: str | None = None


class Checkout:
    """
    Handles the checkout process for an e-commerce order.

    This class demonstrates how business logic interacts with a database,
    making it ideal for integration testing with pytest-scenarios.

    Example usage:
        checkout = Checkout(db)
        result = checkout.process(order_id="order_123")
    """

    def __init__(self, db: Database):
        """
        Initialize Checkout with a MongoDB database connection.

        Args:
            db: MongoDB database instance (injected from tests)
        """
        self.db = db

    def process(self, order_id: str) -> CheckoutResult:
        """
        Process a checkout for the given order.

        This method orchestrates the entire checkout flow:
        1. Validates the order exists
        2. Validates the customer is active
        3. Checks all items are in stock
        4. Calculates the total
        5. Marks the order as completed

        Args:
            order_id: The unique identifier of the order to process

        Returns:
            CheckoutResult with success status and any error message
        """
        # Step 1: Find the order
        order = self.db["orders"].find_one({"id": order_id})
        if not order:
            return CheckoutResult(success=False, error="Order not found")

        # Step 2: Validate customer
        customer = self.db["customers"].find_one({"customer_id": order["customer_id"]})
        if not customer:
            return CheckoutResult(success=False, error="Customer not found")

        if customer.get("status") != "active":
            return CheckoutResult(
                success=False, error=f"Customer is not active: {customer.get('status')}"
            )

        # Step 3: Check stock for all items
        for item in order.get("items", []):
            product = self.db["products"].find_one({"product_id": item["product_id"]})
            if not product:
                return CheckoutResult(
                    success=False, error=f"Product not found: {item['product_id']}"
                )
            if not product.get("in_stock", False):
                return CheckoutResult(
                    success=False, error=f"Product out of stock: {item['product_id']}"
                )

        # Step 4: Calculate total (if not pre-calculated)
        total = self._calculate_total(order)

        # Step 5: Mark order as completed
        self.db["orders"].update_one(
            {"id": order_id}, {"$set": {"status": "completed", "total": total}}
        )

        return CheckoutResult(success=True, order_id=order_id)

    def _calculate_total(self, order: dict) -> float:
        """
        Calculate the order total from item prices.

        Args:
            order: The order document

        Returns:
            The calculated total price
        """
        # If total is already set, use it
        if order.get("total", 0) > 0:
            return order["total"]

        # Otherwise, calculate from items
        total = 0.0
        for item in order.get("items", []):
            product = self.db["products"].find_one({"product_id": item["product_id"]})
            if product:
                quantity = item.get("quantity", 1)
                total += product.get("price", 0) * quantity
        return total

    def get_order_status(self, order_id: str) -> Literal["pending", "completed", "failed"] | None:
        """
        Get the current status of an order.

        Args:
            order_id: The order identifier

        Returns:
            The order status or None if not found
        """
        order = self.db["orders"].find_one({"id": order_id})
        return order.get("status") if order else None

