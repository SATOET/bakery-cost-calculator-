from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.recipe import Recipe
from app.models.fixed_cost import FixedCost
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductCostCalculation
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商品を新規登録"""
    # レシピが指定されている場合、存在確認
    if product_data.recipe_id:
        recipe = db.query(Recipe).filter(
            Recipe.id == product_data.recipe_id,
            Recipe.user_id == current_user.id
        ).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="レシピが見つかりません"
            )

    product = Product(
        user_id=current_user.id,
        recipe_id=product_data.recipe_id,
        name=product_data.name,
        include_fixed_cost=product_data.include_fixed_cost,
        profit_margin=product_data.profit_margin
    )

    db.add(product)
    db.flush()

    # 原価計算
    calculate_product_costs(product, current_user.id, db)

    db.commit()
    db.refresh(product)

    return product


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商品一覧を取得"""
    products = db.query(Product).filter(
        Product.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定の商品を取得"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません"
        )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商品を更新"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません"
        )

    # レシピが指定されている場合、存在確認
    if product_data.recipe_id is not None:
        recipe = db.query(Recipe).filter(
            Recipe.id == product_data.recipe_id,
            Recipe.user_id == current_user.id
        ).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="レシピが見つかりません"
            )

    # 更新するフィールドを設定
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    # 原価を再計算
    calculate_product_costs(product, current_user.id, db)

    db.commit()
    db.refresh(product)

    return product


@router.post("/{product_id}/calculate-cost", response_model=ProductResponse)
def calculate_product_cost(
    product_id: int,
    calc_data: ProductCostCalculation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商品の原価を再計算"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません"
        )

    # 原価を計算
    calculate_product_costs(product, current_user.id, db, calc_data.total_monthly_production)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商品を削除"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品が見つかりません"
        )

    db.delete(product)
    db.commit()

    return None


def calculate_product_costs(
    product: Product,
    user_id: int,
    db: Session,
    total_monthly_production: int = 1
):
    """商品の原価を計算"""
    # 固定費の合計を取得
    total_fixed_cost = 0
    if product.include_fixed_cost:
        fixed_costs = db.query(FixedCost).filter(
            FixedCost.user_id == user_id,
            FixedCost.is_active == True
        ).all()
        total_fixed_cost = sum([fc.monthly_amount for fc in fixed_costs])

    # 商品の原価を計算
    product.calculate_costs(total_fixed_cost, total_monthly_production)
