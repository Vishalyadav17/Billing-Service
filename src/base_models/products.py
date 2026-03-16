from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    product_code: str = Field(..., min_length=1, max_length=100)
    available_stocks: int = Field(..., ge=0)
    price_per_unit: float = Field(..., gt=0)
    tax_percentage: float = Field(..., ge=0, le=100)

    @field_validator("product_code")
    @classmethod
    def uppercase_product_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    available_stocks: int | None = Field(None, ge=0)
    price_per_unit: float | None = Field(None, gt=0)
    tax_percentage: float | None = Field(None, ge=0, le=100)


class ProductResponse(BaseModel):
    id: int
    name: str
    product_code: str
    available_stocks: int
    price_per_unit: float
    tax_percentage: float

    class Config:
        from_attributes = True
