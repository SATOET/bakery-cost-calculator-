# プロジェクト構造

```
bakery_cost_calculator/
│
├── app/                           # アプリケーションのメインパッケージ
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーションのエントリーポイント
│   ├── config.py                  # 設定管理
│   ├── database.py                # データベース接続設定
│   │
│   ├── models/                    # データベースモデル (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py                # ユーザー(店舗)モデル
│   │   ├── password_reset_token.py # パスワードリセットトークン
│   │   ├── material.py            # 材料モデル
│   │   ├── recipe.py              # レシピモデル
│   │   ├── fixed_cost.py          # 固定費モデル
│   │   ├── product.py             # 商品モデル
│   │   └── label_setting.py       # ラベル設定モデル
│   │
│   ├── schemas/                   # Pydanticスキーマ (バリデーション)
│   │   ├── __init__.py
│   │   ├── user.py                # ユーザー関連スキーマ
│   │   ├── material.py            # 材料関連スキーマ
│   │   ├── recipe.py              # レシピ関連スキーマ
│   │   ├── fixed_cost.py          # 固定費関連スキーマ
│   │   ├── product.py             # 商品関連スキーマ
│   │   └── label.py               # ラベル関連スキーマ
│   │
│   ├── routes/                    # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── auth.py                # 認証エンドポイント
│   │   ├── materials.py           # 材料管理エンドポイント
│   │   ├── recipes.py             # レシピ管理エンドポイント
│   │   ├── fixed_costs.py         # 固定費管理エンドポイント
│   │   ├── products.py            # 商品管理エンドポイント
│   │   └── labels.py              # ラベル印刷エンドポイント
│   │
│   ├── utils/                     # ユーティリティ関数
│   │   ├── __init__.py
│   │   ├── security.py            # セキュリティ関連 (認証、暗号化)
│   │   ├── email.py               # メール送信
│   │   ├── pdf_generator.py      # PDF生成 (ラベル印刷)
│   │   └── dependencies.py        # FastAPIの依存関係
│   │
│   ├── static/                    # 静的ファイル
│   │   ├── css/
│   │   │   └── style.css          # スタイルシート
│   │   └── js/
│   │       └── app.js             # JavaScriptファイル
│   │
│   └── templates/                 # HTMLテンプレート
│       └── index.html             # メインページ
│
├── tests/                         # テストコード
│   ├── __init__.py
│   └── test_api.py                # APIテスト
│
├── .env.example                   # 環境変数のサンプル
├── .gitignore                     # Gitで無視するファイル
├── requirements.txt               # 依存パッケージリスト
├── run.py                         # アプリケーション起動スクリプト
├── README.md                      # プロジェクトの詳細説明
├── QUICKSTART.md                  # クイックスタートガイド
└── PROJECT_STRUCTURE.md           # このファイル
```

## 各ディレクトリの役割

### app/
アプリケーションのメインコードが格納されています。

- **main.py**: FastAPIアプリケーションの設定とルーター登録
- **config.py**: 環境変数の管理
- **database.py**: データベース接続の設定

### app/models/
SQLAlchemyを使用したデータベースモデルの定義です。各モデルはデータベーステーブルに対応しています。

### app/schemas/
Pydanticを使用したデータのバリデーションと型定義です。APIのリクエスト/レスポンスの形式を定義しています。

### app/routes/
FastAPIのルーター定義です。各機能ごとにエンドポイントが分かれています。

### app/utils/
共通のユーティリティ関数です。
- セキュリティ機能 (パスワードハッシュ化、JWT生成)
- メール送信
- PDF生成
- 認証の依存関係

### app/static/
Webページで使用する静的ファイル (CSS, JavaScript)

### app/templates/
Jinja2テンプレートを使用したHTMLファイル

### tests/
pytestを使用したテストコード

## 主要な機能フロー

### 1. ユーザー登録とログイン
```
ユーザー入力 → routes/auth.py → schemas/user.py (バリデーション)
→ models/user.py (DB保存) → utils/security.py (パスワードハッシュ化)
```

### 2. 材料管理
```
ユーザー入力 → routes/materials.py → schemas/material.py
→ models/material.py (単価自動計算、DB保存)
```

### 3. レシピ管理
```
ユーザー入力 → routes/recipes.py → schemas/recipe.py
→ models/recipe.py (材料費自動計算、DB保存)
```

### 4. 商品・原価計算
```
ユーザー入力 → routes/products.py → schemas/product.py
→ models/product.py (原価計算、利益率計算、DB保存)
→ models/fixed_cost.py (固定費取得)
```

### 5. ラベル印刷
```
ユーザー入力 → routes/labels.py → schemas/label.py
→ models/label_setting.py (設定取得) → utils/pdf_generator.py (PDF生成)
```

## データの流れ

1. **フロントエンド** (templates/index.html + static/js/app.js)
   - ユーザー入力を受け取る
   - APIにリクエストを送信
   - レスポンスを画面に表示

2. **APIエンドポイント** (routes/)
   - リクエストを受け取る
   - スキーマでバリデーション
   - ビジネスロジックを実行
   - レスポンスを返す

3. **ビジネスロジック** (models/ + utils/)
   - データベース操作
   - 計算処理
   - PDF生成など

4. **データベース** (SQLite/PostgreSQL)
   - データの永続化

## セキュリティ

- パスワードは bcrypt でハッシュ化 (cost factor 12)
- JWT による認証
- 店舗ごとのデータ完全分離 (user_id で制御)
- SQLAlchemy ORM により SQLインジェクション対策
