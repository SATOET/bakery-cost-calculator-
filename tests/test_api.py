"""
API テストサンプル

使用方法:
pytest tests/test_api.py
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """ヘルスチェックのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_user_registration():
    """ユーザー登録のテスト"""
    response = client.post(
        "/api/auth/register",
        json={
            "store_id": "test_store_001",
            "store_name": "テストベーカリー",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["store_id"] == "test_store_001"
    assert data["email"] == "test@example.com"


def test_user_login():
    """ログインのテスト"""
    # まずユーザーを登録
    client.post(
        "/api/auth/register",
        json={
            "store_id": "test_store_002",
            "store_name": "テストベーカリー2",
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )

    # ログイン
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_material_crud():
    """材料のCRUDテスト"""
    # ユーザー登録とログイン
    client.post(
        "/api/auth/register",
        json={
            "store_id": "test_store_003",
            "store_name": "テストベーカリー3",
            "email": "test3@example.com",
            "password": "testpassword123"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test3@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 材料の作成
    create_response = client.post(
        "/api/materials/",
        json={
            "name": "強力粉",
            "purchase_price": 500,
            "purchase_quantity": 1000,
            "unit": "g"
        },
        headers=headers
    )
    assert create_response.status_code == 201
    material = create_response.json()
    assert material["name"] == "強力粉"
    assert material["unit_price"] == 0.5

    # 材料の取得
    get_response = client.get(f"/api/materials/{material['id']}", headers=headers)
    assert get_response.status_code == 200

    # 材料の更新
    update_response = client.put(
        f"/api/materials/{material['id']}",
        json={"purchase_price": 600},
        headers=headers
    )
    assert update_response.status_code == 200
    updated_material = update_response.json()
    assert updated_material["purchase_price"] == 600
    assert updated_material["unit_price"] == 0.6

    # 材料の削除
    delete_response = client.delete(f"/api/materials/{material['id']}", headers=headers)
    assert delete_response.status_code == 204


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
