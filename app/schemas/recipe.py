from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RecipeMaterialBase(BaseModel):
    material_id: int
    quantity: float = Field(..., gt=0)


class RecipeMaterialCreate(RecipeMaterialBase):
    pass


class RecipeMaterialResponse(RecipeMaterialBase):
    id: int
    material_name: Optional[str] = None
    material_unit: Optional[str] = None
    cost: Optional[float] = None

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class RecipeCreate(RecipeBase):
    materials: List[RecipeMaterialCreate] = []


class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    materials: Optional[List[RecipeMaterialCreate]] = None


class RecipeResponse(RecipeBase):
    id: int
    user_id: int
    material_cost: float
    materials: List[RecipeMaterialResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
