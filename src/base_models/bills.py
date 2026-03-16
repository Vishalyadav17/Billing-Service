from typing import Dict, List

from pydantic import BaseModel, EmailStr, Field, field_validator


class BillItemResponse(BaseModel):
    product_code: str
    product_name: str
    quantity: int
    unit_price: float
    purchase_price: float
    tax_percentage: float
    tax_payable: float
    total_price: float

    class Config:
        from_attributes = True


class BillSummaryResponse(BaseModel):
    id: int
    customer_email: str
    total_without_tax: float
    total_tax: float
    net_price: float
    rounded_net_price: float
    cash_paid: float
    balance: float
    denominations_given: Dict[str, int] | None
    created_at: int

    class Config:
        from_attributes = True


class BillDetailResponse(BillSummaryResponse):
    items: List[BillItemResponse]


class GenerateBillForm(BaseModel):
    """Validated form payload for bill generation."""

    customer_email: EmailStr
    product_codes: List[str]
    quantities: List[int]
    cash_paid: float = Field(..., gt=0)

    @field_validator("quantities", mode="before")
    @classmethod
    def quantities_must_be_positive(cls, v):
        for q in v:
            if int(q) <= 0:
                raise ValueError("All quantities must be greater than 0.")
        return [int(q) for q in v]

    @field_validator("product_codes")
    @classmethod
    def product_codes_not_empty(cls, v):
        if not v:
            raise ValueError("At least one product must be added.")
        return [code.strip().upper() for code in v]
