from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from typing import List, Optional
import os


class LabelPDFGenerator:
    def __init__(self, label_setting, store_name: str):
        self.label_setting = label_setting
        self.store_name = store_name
        self.buffer = BytesIO()

        # A4サイズの設定
        self.page_width, self.page_height = A4

        # ラベルサイズ (mmをポイントに変換)
        self.label_width = label_setting.label_width * mm
        self.label_height = label_setting.label_height * mm

        # 余白
        self.margin_left = label_setting.margin_left * mm
        self.margin_top = label_setting.margin_top * mm
        self.margin_right = label_setting.margin_right * mm
        self.margin_bottom = label_setting.margin_bottom * mm

        # 印刷可能エリア
        self.printable_width = self.page_width - self.margin_left - self.margin_right
        self.printable_height = self.page_height - self.margin_top - self.margin_bottom

        # 1シートあたりのラベル数
        self.labels_per_row = int(self.printable_width / self.label_width)
        self.labels_per_column = int(self.printable_height / self.label_height)

    def generate_labels(self, products: List, expiry_date: Optional[str] = None) -> BytesIO:
        """ラベルPDFを生成"""
        c = canvas.Canvas(self.buffer, pagesize=A4)

        label_index = 0
        for product in products:
            # ラベルの位置を計算
            row = label_index // self.labels_per_row
            col = label_index % self.labels_per_row

            # 新しいページが必要な場合
            if row >= self.labels_per_column:
                c.showPage()
                label_index = 0
                row = 0
                col = 0

            # ラベルの左下座標
            x = self.margin_left + (col * self.label_width)
            y = self.page_height - self.margin_top - ((row + 1) * self.label_height)

            # ラベルを描画
            self._draw_label(c, x, y, product, expiry_date)

            label_index += 1

        c.save()
        self.buffer.seek(0)
        return self.buffer

    def _draw_label(self, c, x, y, product, expiry_date):
        """個別のラベルを描画"""
        # ラベルの枠線 (デバッグ用 - 本番では削除可能)
        c.rect(x, y, self.label_width, self.label_height)

        # 内側の余白
        padding = 5
        content_x = x + padding
        content_y = y + self.label_height - padding
        content_width = self.label_width - (2 * padding)

        current_y = content_y

        # 商品名 (大きく表示)
        c.setFont("Helvetica-Bold", 14)
        product_name = product.name[:30]  # 長い場合は切り詰め
        c.drawString(content_x, current_y, product_name)
        current_y -= 20

        # 価格 (オプション)
        if self.label_setting.show_price and product.selling_price:
            c.setFont("Helvetica-Bold", 12)
            price_text = f"¥{int(product.selling_price):,}"
            c.drawString(content_x, current_y, price_text)
            current_y -= 18

        # 材料リスト (オプション)
        if self.label_setting.show_ingredients and product.recipe:
            c.setFont("Helvetica", 8)
            c.drawString(content_x, current_y, "原材料:")
            current_y -= 12

            # 材料を列挙
            materials = []
            for rm in product.recipe.recipe_materials:
                if rm.material:
                    materials.append(rm.material.name)

            # 材料を3つずつ表示
            material_text = ", ".join(materials[:5])
            if len(materials) > 5:
                material_text += "..."

            c.setFont("Helvetica", 7)
            # テキストが長い場合は折り返し
            if len(material_text) > 35:
                c.drawString(content_x, current_y, material_text[:35])
                current_y -= 10
                if len(material_text) > 35:
                    c.drawString(content_x, current_y, material_text[35:70])
                    current_y -= 10
            else:
                c.drawString(content_x, current_y, material_text)
                current_y -= 10

        # 賞味期限 (オプション)
        if self.label_setting.show_expiry_date and expiry_date:
            c.setFont("Helvetica", 8)
            c.drawString(content_x, current_y, f"賞味期限: {expiry_date}")
            current_y -= 12

        # 店舗名 (オプション)
        if self.label_setting.show_store_name:
            c.setFont("Helvetica", 7)
            c.drawString(content_x, y + 5, self.store_name)
