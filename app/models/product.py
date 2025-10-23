from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)

    # 原価計算関連
    include_fixed_cost = Column(Boolean, default=False)  # 固定費を含めるか
    fixed_cost_per_unit = Column(Float, default=0)  # 商品単位あたりの固定費
    material_cost = Column(Float, default=0)  # 材料費
    total_cost = Column(Float, default=0)  # 総原価

    # 価格設定
    profit_margin = Column(Float, default=30)  # 利益率 (%)
    suggested_price = Column(Float, default=0)  # 推奨販売価格
    selling_price = Column(Float, nullable=True)  # 実際の販売価格
    actual_profit_margin = Column(Float, default=0)  # 実際の利益率
    actual_profit_amount = Column(Float, default=0)  # 実際の利益額

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="products")
    recipe = relationship("Recipe", back_populates="products")

    def calculate_costs(self, total_monthly_fixed_cost=0, total_monthly_production=1):
        """原価を計算"""
        # レシピから材料費を取得
        if self.recipe:
            self.material_cost = self.recipe.material_cost

        # 固定費の計算
        if self.include_fixed_cost and total_monthly_production > 0:
            self.fixed_cost_per_unit = total_monthly_fixed_cost / total_monthly_production
        else:
            self.fixed_cost_per_unit = 0

        # 総原価
        self.total_cost = self.material_cost + self.fixed_cost_per_unit

        # 推奨販売価格の計算
        if self.profit_margin > 0:
            self.suggested_price = self.total_cost / (1 - self.profit_margin / 100)
        else:
            self.suggested_price = self.total_cost

        # 実際の価格が設定されている場合、実際の利益率と利益額を計算
        if self.selling_price:
            self.actual_profit_amount = self.selling_price - self.total_cost
            if self.selling_price > 0:
                self.actual_profit_margin = (self.actual_profit_amount / self.selling_price) * 100
            else:
                self.actual_profit_margin = 0
        else:
            self.actual_profit_amount = 0
            self.actual_profit_margin = 0
