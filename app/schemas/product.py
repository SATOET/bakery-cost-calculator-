from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    recipe_id: Optional[int] = None
    include_fixed_cost: bool = False
    profit_margin: float = Field(default=30, ge=0, le=100)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    recipe_id: Optional[int] = None
    include_fixed_cost: Optional[bool] = None
    profit_margin: Optional[float] = Field(None, ge=0, le=100)
    selling_price: Optional[float] = Field(None, ge=0)


class ProductCostCalculation(BaseModel):
    total_monthly_production: int = Field(default=1, gt=0)


class ProductResponse(ProductBase):
    id: int
    user_id: int
    fixed_cost_per_unit: float
    material_cost: float
    total_cost: float
    suggested_price: float
    selling_price: Optional[float]
    actual_profit_margin: float
    actual_profit_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
