from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MaterialBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    purchase_price: float = Field(..., gt=0)
    purchase_quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    purchase_price: Optional[float] = Field(None, gt=0)
    purchase_quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)


class MaterialResponse(MaterialBase):
    id: int
    user_id: int
    unit_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
