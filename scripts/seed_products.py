"""
Standalone seed script — run directly if needed:
    python scripts/seed_products.py

The app also supports seeding via the Admin UI at /admin/products.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv(".env")

from src.db_operations.db_connection import SessionLocal, engine
from src.db_operations.db_models import Base
from src.db_operations.crud_ops.products import seed_default_products

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_default_products(db)
        print(f"Seeded {count} product(s).")
    finally:
        db.close()
