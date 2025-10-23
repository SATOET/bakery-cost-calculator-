from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.fixed_cost import FixedCost
from app.schemas.fixed_cost import FixedCostCreate, FixedCostUpdate, FixedCostResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/fixed-costs", tags=["fixed-costs"])


@router.post("/", response_model=FixedCostResponse, status_code=status.HTTP_201_CREATED)
def create_fixed_cost(
    fixed_cost_data: FixedCostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """固定費を新規登録"""
    fixed_cost = FixedCost(
        user_id=current_user.id,
        name=fixed_cost_data.name,
        monthly_amount=fixed_cost_data.monthly_amount,
        is_active=fixed_cost_data.is_active
    )

    db.add(fixed_cost)
    db.commit()
    db.refresh(fixed_cost)

    return fixed_cost


@router.get("/", response_model=List[FixedCostResponse])
def get_fixed_costs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """固定費一覧を取得"""
    fixed_costs = db.query(FixedCost).filter(
        FixedCost.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return fixed_costs


@router.get("/total", response_model=dict)
def get_total_fixed_cost(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """有効な固定費の合計を取得"""
    total = db.query(FixedCost).filter(
        FixedCost.user_id == current_user.id,
        FixedCost.is_active == True
    ).with_entities(FixedCost.monthly_amount).all()

    total_amount = sum([fc[0] for fc in total]) if total else 0

    return {"total_monthly_fixed_cost": total_amount}


@router.get("/{fixed_cost_id}", response_model=FixedCostResponse)
def get_fixed_cost(
    fixed_cost_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定の固定費を取得"""
    fixed_cost = db.query(FixedCost).filter(
        FixedCost.id == fixed_cost_id,
        FixedCost.user_id == current_user.id
    ).first()

    if not fixed_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="固定費が見つかりません"
        )

    return fixed_cost


@router.put("/{fixed_cost_id}", response_model=FixedCostResponse)
def update_fixed_cost(
    fixed_cost_id: int,
    fixed_cost_data: FixedCostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """固定費を更新"""
    fixed_cost = db.query(FixedCost).filter(
        FixedCost.id == fixed_cost_id,
        FixedCost.user_id == current_user.id
    ).first()

    if not fixed_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="固定費が見つかりません"
        )

    # 更新するフィールドを設定
    update_data = fixed_cost_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fixed_cost, field, value)

    db.commit()
    db.refresh(fixed_cost)

    return fixed_cost


@router.delete("/{fixed_cost_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed_cost(
    fixed_cost_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """固定費を削除"""
    fixed_cost = db.query(FixedCost).filter(
        FixedCost.id == fixed_cost_id,
        FixedCost.user_id == current_user.id
    ).first()

    if not fixed_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="固定費が見つかりません"
        )

    db.delete(fixed_cost)
    db.commit()

    return None
