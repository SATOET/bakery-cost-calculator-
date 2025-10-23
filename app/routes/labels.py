from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.label_setting import LabelSetting
from app.models.product import Product
from app.schemas.label import (
    LabelSettingCreate, LabelSettingUpdate, LabelSettingResponse,
    LabelPrintRequest
)
from app.utils.dependencies import get_current_user
from app.utils.pdf_generator import LabelPDFGenerator

router = APIRouter(prefix="/api/labels", tags=["labels"])


@router.post("/settings", response_model=LabelSettingResponse, status_code=status.HTTP_201_CREATED)
def create_label_setting(
    setting_data: LabelSettingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ラベル設定を新規登録"""
    # デフォルト設定として登録する場合、既存のデフォルトを解除
    if setting_data.is_default:
        db.query(LabelSetting).filter(
            LabelSetting.user_id == current_user.id,
            LabelSetting.is_default == True
        ).update({"is_default": False})

    setting = LabelSetting(
        user_id=current_user.id,
        preset_name=setting_data.preset_name,
        label_width=setting_data.label_width,
        label_height=setting_data.label_height,
        margin_top=setting_data.margin_top,
        margin_bottom=setting_data.margin_bottom,
        margin_left=setting_data.margin_left,
        margin_right=setting_data.margin_right,
        show_price=setting_data.show_price,
        show_ingredients=setting_data.show_ingredients,
        show_expiry_date=setting_data.show_expiry_date,
        show_store_name=setting_data.show_store_name,
        show_logo=setting_data.show_logo,
        logo_path=setting_data.logo_path,
        is_default=setting_data.is_default
    )

    db.add(setting)
    db.commit()
    db.refresh(setting)

    # ラベル数を計算して返す
    labels_per_sheet, _, _ = setting.calculate_labels_per_sheet()
    response = LabelSettingResponse.from_orm(setting)
    response.labels_per_sheet = labels_per_sheet

    return response


@router.get("/settings", response_model=List[LabelSettingResponse])
def get_label_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ラベル設定一覧を取得"""
    settings = db.query(LabelSetting).filter(
        LabelSetting.user_id == current_user.id
    ).all()

    response_list = []
    for setting in settings:
        labels_per_sheet, _, _ = setting.calculate_labels_per_sheet()
        resp = LabelSettingResponse.from_orm(setting)
        resp.labels_per_sheet = labels_per_sheet
        response_list.append(resp)

    return response_list


@router.get("/settings/default", response_model=LabelSettingResponse)
def get_default_label_setting(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """デフォルトのラベル設定を取得"""
    setting = db.query(LabelSetting).filter(
        LabelSetting.user_id == current_user.id,
        LabelSetting.is_default == True
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="デフォルトのラベル設定が見つかりません"
        )

    labels_per_sheet, _, _ = setting.calculate_labels_per_sheet()
    response = LabelSettingResponse.from_orm(setting)
    response.labels_per_sheet = labels_per_sheet

    return response


@router.get("/settings/{setting_id}", response_model=LabelSettingResponse)
def get_label_setting(
    setting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定のラベル設定を取得"""
    setting = db.query(LabelSetting).filter(
        LabelSetting.id == setting_id,
        LabelSetting.user_id == current_user.id
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ラベル設定が見つかりません"
        )

    labels_per_sheet, _, _ = setting.calculate_labels_per_sheet()
    response = LabelSettingResponse.from_orm(setting)
    response.labels_per_sheet = labels_per_sheet

    return response


@router.put("/settings/{setting_id}", response_model=LabelSettingResponse)
def update_label_setting(
    setting_id: int,
    setting_data: LabelSettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ラベル設定を更新"""
    setting = db.query(LabelSetting).filter(
        LabelSetting.id == setting_id,
        LabelSetting.user_id == current_user.id
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ラベル設定が見つかりません"
        )

    # デフォルト設定として更新する場合、既存のデフォルトを解除
    if setting_data.is_default:
        db.query(LabelSetting).filter(
            LabelSetting.user_id == current_user.id,
            LabelSetting.is_default == True,
            LabelSetting.id != setting_id
        ).update({"is_default": False})

    # 更新するフィールドを設定
    update_data = setting_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)

    db.commit()
    db.refresh(setting)

    labels_per_sheet, _, _ = setting.calculate_labels_per_sheet()
    response = LabelSettingResponse.from_orm(setting)
    response.labels_per_sheet = labels_per_sheet

    return response


@router.delete("/settings/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label_setting(
    setting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ラベル設定を削除"""
    setting = db.query(LabelSetting).filter(
        LabelSetting.id == setting_id,
        LabelSetting.user_id == current_user.id
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ラベル設定が見つかりません"
        )

    db.delete(setting)
    db.commit()

    return None


@router.post("/print")
def print_labels(
    print_request: LabelPrintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ラベルを印刷 (PDFを生成)"""
    # ラベル設定を取得
    if print_request.label_setting_id:
        label_setting = db.query(LabelSetting).filter(
            LabelSetting.id == print_request.label_setting_id,
            LabelSetting.user_id == current_user.id
        ).first()
    else:
        # デフォルト設定を使用
        label_setting = db.query(LabelSetting).filter(
            LabelSetting.user_id == current_user.id,
            LabelSetting.is_default == True
        ).first()

    if not label_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ラベル設定が見つかりません"
        )

    # 商品を取得
    products = db.query(Product).filter(
        Product.id.in_(print_request.product_ids),
        Product.user_id == current_user.id
    ).all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません"
        )

    # PDFを生成
    generator = LabelPDFGenerator(label_setting, current_user.store_name)
    pdf_buffer = generator.generate_labels(products, print_request.expiry_date)

    # PDFを返す
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=labels.pdf"
        }
    )
