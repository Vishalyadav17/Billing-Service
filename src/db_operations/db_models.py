from sqlalchemy import (
    BigInteger,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    product_code = Column(String(100), unique=True, nullable=False, index=True)
    available_stocks = Column(Integer, nullable=False, default=0)
    price_per_unit = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    total_without_tax = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    net_price = Column(Float, nullable=False)
    rounded_net_price = Column(Float, nullable=False)
    cash_paid = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    denominations_available = Column(MutableDict.as_mutable(JSONB), nullable=True)
    denominations_given = Column(MutableDict.as_mutable(JSONB), nullable=True)
    created_at = Column(BigInteger, nullable=False)

    items = relationship("BillItem", back_populates="bill", lazy="joined")


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # storing price snapshot so history stays accurate if product prices change later
    product_code = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_percentage = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    tax_payable = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    bill = relationship("Bill", back_populates="items")
    product = relationship("Product")
