"""Bill and BillItem CRUD operations"""

import time
from typing import List, Optional

from sqlalchemy.orm import Session

from src.db_operations.db_models import Bill, BillItem


def create_bill(db: Session, data: dict) -> Bill:
    """Persist a new bill along with its line items in a single transaction."""
    now = int(time.time())
    bill = Bill(
        customer_email=data["customer_email"],
        total_without_tax=data["total_without_tax"],
        total_tax=data["total_tax"],
        net_price=data["net_price"],
        rounded_net_price=data["rounded_net_price"],
        cash_paid=data["cash_paid"],
        balance=data["balance"],
        denominations_available=data.get("denominations_available"),
        denominations_given=data.get("denominations_given"),
        created_at=now,
    )
    db.add(bill)
    db.flush()

    for item_data in data["items"]:
        item = BillItem(
            bill_id=bill.id,
            product_id=item_data["product_id"],
            product_code=item_data["product_code"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_percentage=item_data["tax_percentage"],
            purchase_price=item_data["purchase_price"],
            tax_payable=item_data["tax_payable"],
            total_price=item_data["total_price"],
        )
        db.add(item)

    db.commit()
    db.refresh(bill)
    return bill


def get_bill_by_id(db: Session, bill_id: int) -> Optional[Bill]:
    return db.query(Bill).filter(Bill.id == bill_id).first()


def get_bills_by_email(db: Session, email: str) -> List[Bill]:
    """Fetch all bills for a customer email, newest first."""
    return (
        db.query(Bill)
        .filter(Bill.customer_email == email.lower().strip())
        .order_by(Bill.created_at.desc())
        .all()
    )
