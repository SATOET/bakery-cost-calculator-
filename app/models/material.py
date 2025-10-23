from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    purchase_price = Column(Float, nullable=False)  # 購入金額
    purchase_quantity = Column(Float, nullable=False)  # 購入容量
    unit = Column(String(50), nullable=False)  # 単位 (g, ml, 個など)
    unit_price = Column(Float, nullable=False)  # 単価 (自動計算)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="materials")
    recipe_materials = relationship("RecipeMaterial", back_populates="material", cascade="all, delete-orphan")

    def calculate_unit_price(self):
        """単価を計算"""
        if self.purchase_quantity > 0:
            self.unit_price = self.purchase_price / self.purchase_quantity
        else:
            self.unit_price = 0
