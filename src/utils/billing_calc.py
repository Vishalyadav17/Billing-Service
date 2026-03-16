"""Billing calculation helpers — item totals, tax and denomination change"""

import math
from typing import Dict, List

from src.db_operations.db_models import Product


def calculate_bill_items(
    products_with_qty: List[tuple[Product, int]],
) -> tuple[List[dict], float, float, float, float]:
    """Calculate per-item breakdown and overall totals. Returns (items, total_without_tax, total_tax, net_price, rounded_net_price)."""
    items = []
    total_without_tax = 0.0
    total_tax = 0.0

    for product, quantity in products_with_qty:
        purchase_price = round(product.price_per_unit * quantity, 2)
        tax_payable = round(purchase_price * (product.tax_percentage / 100), 2)
        total_price = round(purchase_price + tax_payable, 2)

        total_without_tax += purchase_price
        total_tax += tax_payable

        items.append(
            {
                "product_id": product.id,
                "product_code": product.product_code,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": product.price_per_unit,
                "tax_percentage": product.tax_percentage,
                "purchase_price": purchase_price,
                "tax_payable": tax_payable,
                "total_price": total_price,
            }
        )

    total_without_tax = round(total_without_tax, 2)
    total_tax = round(total_tax, 2)
    net_price = round(total_without_tax + total_tax, 2)
    rounded_net_price = float(math.floor(net_price))

    return items, total_without_tax, total_tax, net_price, rounded_net_price


def calculate_change_denominations(balance: float, available: Dict[int, int]) -> Dict[int, int]:
    """Return the denomination breakdown for giving change, using a greedy approach constrained by shop stock."""
    # greedy: largest denomination first, constrained by what the shop has
    remaining = round(balance)
    result: Dict[int, int] = {}

    for denom in sorted(available.keys(), reverse=True):
        if remaining <= 0:
            break
        count_available = available.get(denom, 0)
        if count_available <= 0:
            continue
        count_used = min(remaining // denom, count_available)
        if count_used > 0:
            result[denom] = count_used
            remaining -= count_used * denom

    return result
