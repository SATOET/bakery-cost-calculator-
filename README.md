# Bakery Cost Calculator

パン屋向け原価計算・ラベル印刷システム

## 概要

このアプリケーションは、複数のパン屋が利用できる原価計算とラベル印刷機能を持つWebアプリケーションです。材料管理、レシピ管理、固定費管理、商品の原価計算、そしてラベル印刷機能を提供します。

## 主要機能

### 1. ユーザー認証
- 店舗ごとのユーザー登録
- ログイン/ログアウト
- パスワードのハッシュ化 (bcrypt, cost factor 12)
- パスワードリセット機能 (メール認証)

### 2. 材料管理
- 材料の登録・編集・削除
- 購入金額と購入容量からの自動単価計算
- 材料一覧表示

### 3. レシピ管理
- レシピの登録・編集・削除
- 使用材料と使用量の管理
- 材料費の自動計算

### 4. 固定費管理
- 固定費項目の自由追加・編集・削除
- 固定費の有効/無効設定
- 月次固定費総額の計算

### 5. 商品・原価計算
- 商品ごとの原価計算
  - 材料費
  - 固定費 (オプション)
  - 総原価
- 利益率設定と推奨販売価格の自動計算
- 手動での販売価格設定
- 実際の利益率・利益額の表示

### 6. ラベル印刷
- A4用紙対応のラベル設定
- ラベルサイズと余白のカスタマイズ
- プリセット保存機能
- 複数商品の一括印刷
- PDF形式での出力

## 技術スタック

- **バックエンド**: FastAPI (Python)
- **データベース**: SQLite (開発用) / PostgreSQL (本番用対応)
- **認証**: JWT (JSON Web Token)
- **パスワードハッシュ化**: bcrypt
- **PDF生成**: ReportLab
- **フロントエンド**: HTML, CSS, JavaScript

## セットアップ

### 必要要件

- Python 3.8以上
- pip

### インストール手順

1. リポジトリをクローンまたはダウンロード

```bash
cd bakery_cost_calculator
```

2. 仮想環境の作成と有効化

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

4. 環境変数の設定

`.env.example`を`.env`にコピーして、必要な設定を行います:

```bash
cp .env.example .env
```

`.env`ファイルを編集:
```
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///./bakery.db
```

5. アプリケーションの起動

```bash
python -m uvicorn app.main:app --reload
```

または

```bash
python app/main.py
```

6. ブラウザでアクセス

```
http://localhost:8000
```

## API ドキュメント

FastAPIの自動生成ドキュメントが利用可能です:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## データベース構造

### テーブル一覧

1. **users** - ユーザー(店舗)情報
2. **password_reset_tokens** - パスワードリセットトークン
3. **materials** - 材料マスタ
4. **recipes** - レシピ
5. **recipe_materials** - レシピと材料の中間テーブル
6. **fixed_costs** - 固定費項目
7. **products** - 商品情報
8. **label_settings** - ラベル設定

## APIエンドポイント

### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `POST /api/auth/password-reset-request` - パスワードリセット要求
- `POST /api/auth/password-reset` - パスワードリセット

### 材料
- `GET /api/materials/` - 材料一覧取得
- `POST /api/materials/` - 材料追加
- `GET /api/materials/{id}` - 材料詳細取得
- `PUT /api/materials/{id}` - 材料更新
- `DELETE /api/materials/{id}` - 材料削除

### レシピ
- `GET /api/recipes/` - レシピ一覧取得
- `POST /api/recipes/` - レシピ追加
- `GET /api/recipes/{id}` - レシピ詳細取得
- `PUT /api/recipes/{id}` - レシピ更新
- `DELETE /api/recipes/{id}` - レシピ削除

### 固定費
- `GET /api/fixed-costs/` - 固定費一覧取得
- `POST /api/fixed-costs/` - 固定費追加
- `GET /api/fixed-costs/total` - 固定費合計取得
- `GET /api/fixed-costs/{id}` - 固定費詳細取得
- `PUT /api/fixed-costs/{id}` - 固定費更新
- `DELETE /api/fixed-costs/{id}` - 固定費削除

### 商品
- `GET /api/products/` - 商品一覧取得
- `POST /api/products/` - 商品追加
- `GET /api/products/{id}` - 商品詳細取得
- `PUT /api/products/{id}` - 商品更新
- `POST /api/products/{id}/calculate-cost` - 原価再計算
- `DELETE /api/products/{id}` - 商品削除

### ラベル
- `GET /api/labels/settings` - ラベル設定一覧
- `POST /api/labels/settings` - ラベル設定追加
- `GET /api/labels/settings/default` - デフォルト設定取得
- `GET /api/labels/settings/{id}` - 設定詳細取得
- `PUT /api/labels/settings/{id}` - 設定更新
- `DELETE /api/labels/settings/{id}` - 設定削除
- `POST /api/labels/print` - ラベル印刷 (PDF生成)

## セキュリティ

- パスワードは bcrypt でハッシュ化 (cost factor 12)
- JWT による認証
- 店舗ごとのデータ完全分離
- CSRF 対策
- SQLインジェクション対策 (SQLAlchemy ORM使用)

## 今後の拡張予定

- [ ] より詳細なフロントエンド UI の実装
- [ ] 商品・レシピの画像アップロード機能
- [ ] データのエクスポート/インポート機能
- [ ] 売上管理機能
- [ ] レポート機能
- [ ] モバイルアプリ対応

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題が発生した場合や機能要望がある場合は、Issueを作成してください。
