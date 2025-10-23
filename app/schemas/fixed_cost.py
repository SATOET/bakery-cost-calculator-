from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FixedCostBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    monthly_amount: float = Field(..., ge=0)
    is_active: bool = True


class FixedCostCreate(FixedCostBase):
    pass


class FixedCostUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    monthly_amount: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class FixedCostResponse(FixedCostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
