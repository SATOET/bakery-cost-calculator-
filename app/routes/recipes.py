from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe, RecipeMaterial
from app.models.material import Material
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeMaterialResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """レシピを新規登録"""
    # レシピの作成
    recipe = Recipe(
        user_id=current_user.id,
        name=recipe_data.name,
        description=recipe_data.description,
        material_cost=0
    )

    db.add(recipe)
    db.flush()  # IDを取得するためにflush

    # 材料の追加
    for material_data in recipe_data.materials:
        # 材料が存在し、かつ現在のユーザーのものであることを確認
        material = db.query(Material).filter(
            Material.id == material_data.material_id,
            Material.user_id == current_user.id
        ).first()

        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"材料ID {material_data.material_id} が見つかりません"
            )

        recipe_material = RecipeMaterial(
            recipe_id=recipe.id,
            material_id=material_data.material_id,
            quantity=material_data.quantity
        )
        db.add(recipe_material)

    # 材料費を計算
    db.flush()
    db.refresh(recipe)
    recipe.calculate_material_cost()

    db.commit()
    db.refresh(recipe)

    # レスポンスの構築
    return format_recipe_response(recipe)


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """レシピ一覧を取得"""
    recipes = db.query(Recipe).filter(
        Recipe.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return [format_recipe_response(recipe) for recipe in recipes]


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定のレシピを取得"""
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="レシピが見つかりません"
        )

    return format_recipe_response(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """レシピを更新"""
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="レシピが見つかりません"
        )

    # 基本情報の更新
    if recipe_data.name is not None:
        recipe.name = recipe_data.name
    if recipe_data.description is not None:
        recipe.description = recipe_data.description

    # 材料の更新
    if recipe_data.materials is not None:
        # 既存の材料を削除
        db.query(RecipeMaterial).filter(
            RecipeMaterial.recipe_id == recipe_id
        ).delete()

        # 新しい材料を追加
        for material_data in recipe_data.materials:
            # 材料が存在し、かつ現在のユーザーのものであることを確認
            material = db.query(Material).filter(
                Material.id == material_data.material_id,
                Material.user_id == current_user.id
            ).first()

            if not material:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"材料ID {material_data.material_id} が見つかりません"
                )

            recipe_material = RecipeMaterial(
                recipe_id=recipe.id,
                material_id=material_data.material_id,
                quantity=material_data.quantity
            )
            db.add(recipe_material)

        # 材料費を再計算
        db.flush()
        db.refresh(recipe)
        recipe.calculate_material_cost()

    db.commit()
    db.refresh(recipe)

    return format_recipe_response(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """レシピを削除"""
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="レシピが見つかりません"
        )

    db.delete(recipe)
    db.commit()

    return None


def format_recipe_response(recipe: Recipe) -> dict:
    """レシピレスポンスをフォーマット"""
    materials = []
    for rm in recipe.recipe_materials:
        if rm.material:
            materials.append({
                "id": rm.id,
                "material_id": rm.material_id,
                "quantity": rm.quantity,
                "material_name": rm.material.name,
                "material_unit": rm.material.unit,
                "cost": rm.material.unit_price * rm.quantity
            })

    return {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "name": recipe.name,
        "description": recipe.description,
        "material_cost": recipe.material_cost,
        "materials": materials,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at
    }
