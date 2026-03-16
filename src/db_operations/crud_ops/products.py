"""Product CRUD operations"""

import time
from typing import List, Optional

from sqlalchemy.orm import Session

from src.db_operations.db_models import Product
from src.utils.constants import SEED_PRODUCTS


def get_all_products(db: Session) -> List[Product]:
    return db.query(Product).order_by(Product.name).all()


def get_product_by_code(db: Session, product_code: str) -> Optional[Product]:
    return db.query(Product).filter(Product.product_code == product_code).first()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, data: dict) -> Product:
    now = int(time.time())
    product = Product(
        name=data["name"],
        product_code=data["product_code"],
        available_stocks=data["available_stocks"],
        price_per_unit=data["price_per_unit"],
        tax_percentage=data["tax_percentage"],
        created_at=now,
        updated_at=now,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: dict) -> Optional[Product]:
    product = get_product_by_id(db, product_id)
    if not product:
        return None
    for key, value in data.items():
        setattr(product, key, value)
    product.updated_at = int(time.time())
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = get_product_by_id(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


def decrement_stock(db: Session, product_id: int, quantity: int) -> bool:
    product = get_product_by_id(db, product_id)
    if not product or product.available_stocks < quantity:
        return False
    product.available_stocks -= quantity
    product.updated_at = int(time.time())
    db.commit()
    return True


def seed_default_products(db: Session) -> int:
    inserted = 0
    for item in SEED_PRODUCTS:
        if not get_product_by_code(db, item["product_code"]):
            create_product(db, item)
            inserted += 1
    return inserted
