from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LabelSettingBase(BaseModel):
    preset_name: str = Field(..., min_length=1, max_length=255)
    label_width: float = Field(..., gt=0)
    label_height: float = Field(..., gt=0)
    margin_top: float = Field(default=10, ge=0)
    margin_bottom: float = Field(default=10, ge=0)
    margin_left: float = Field(default=10, ge=0)
    margin_right: float = Field(default=10, ge=0)
    show_price: bool = True
    show_ingredients: bool = True
    show_expiry_date: bool = False
    show_store_name: bool = True
    show_logo: bool = False
    logo_path: Optional[str] = None
    is_default: bool = False


class LabelSettingCreate(LabelSettingBase):
    pass


class LabelSettingUpdate(BaseModel):
    preset_name: Optional[str] = Field(None, min_length=1, max_length=255)
    label_width: Optional[float] = Field(None, gt=0)
    label_height: Optional[float] = Field(None, gt=0)
    margin_top: Optional[float] = Field(None, ge=0)
    margin_bottom: Optional[float] = Field(None, ge=0)
    margin_left: Optional[float] = Field(None, ge=0)
    margin_right: Optional[float] = Field(None, ge=0)
    show_price: Optional[bool] = None
    show_ingredients: Optional[bool] = None
    show_expiry_date: Optional[bool] = None
    show_store_name: Optional[bool] = None
    show_logo: Optional[bool] = None
    logo_path: Optional[str] = None
    is_default: Optional[bool] = None


class LabelSettingResponse(LabelSettingBase):
    id: int
    user_id: int
    labels_per_sheet: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LabelPrintRequest(BaseModel):
    product_ids: List[int] = Field(..., min_items=1)
    label_setting_id: Optional[int] = None
    expiry_date: Optional[str] = None  # YYYY-MM-DD形式
