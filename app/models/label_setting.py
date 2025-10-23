from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LabelSetting(Base):
    __tablename__ = "label_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    preset_name = Column(String(255), nullable=False)  # プリセット名

    # ラベルサイズ (mm)
    label_width = Column(Float, nullable=False)
    label_height = Column(Float, nullable=False)

    # 余白 (mm)
    margin_top = Column(Float, default=10)
    margin_bottom = Column(Float, default=10)
    margin_left = Column(Float, default=10)
    margin_right = Column(Float, default=10)

    # 表示オプション
    show_price = Column(Boolean, default=True)
    show_ingredients = Column(Boolean, default=True)
    show_expiry_date = Column(Boolean, default=False)
    show_store_name = Column(Boolean, default=True)
    show_logo = Column(Boolean, default=False)

    # ロゴ画像パス (オプション)
    logo_path = Column(String(500), nullable=True)

    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="label_settings")

    def calculate_labels_per_sheet(self):
        """A4用紙に配置できるラベル数を計算"""
        # A4サイズ: 210mm x 297mm
        a4_width = 210
        a4_height = 297

        # 有効印刷エリア
        printable_width = a4_width - self.margin_left - self.margin_right
        printable_height = a4_height - self.margin_top - self.margin_bottom

        # ラベル数を計算
        labels_per_row = int(printable_width / self.label_width)
        labels_per_column = int(printable_height / self.label_height)

        return labels_per_row * labels_per_column, labels_per_row, labels_per_column
