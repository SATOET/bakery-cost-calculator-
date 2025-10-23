from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    material_cost = Column(Float, default=0)  # 材料費合計 (自動計算)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recipes")
    recipe_materials = relationship("RecipeMaterial", back_populates="recipe", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="recipe")

    def calculate_material_cost(self):
        """材料費を計算"""
        total = 0
        for rm in self.recipe_materials:
            if rm.material:
                total += rm.material.unit_price * rm.quantity
        self.material_cost = total
        return total


class RecipeMaterial(Base):
    """レシピと材料の中間テーブル"""
    __tablename__ = "recipe_materials"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)  # 使用量

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_materials")
    material = relationship("Material", back_populates="recipe_materials")
