# クイックスタートガイド

## 1. セットアップ

### 必要なもの
- Python 3.8以上

### インストール

1. プロジェクトディレクトリに移動:
```bash
cd bakery_cost_calculator
```

2. 仮想環境の作成:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

4. 環境設定:
```bash
# .env.exampleを.envにコピー
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

5. アプリケーションの起動:
```bash
python run.py
```

6. ブラウザでアクセス:
```
http://localhost:8000
```

## 2. 基本的な使い方

### ステップ1: ユーザー登録

1. トップページで「新規登録」タブをクリック
2. 以下の情報を入力:
   - 店舗ID: 任意の半角英数字 (例: bakery001)
   - 店舗名: あなたのパン屋の名前
   - メールアドレス: ログイン用
   - パスワード: 8文字以上
3. 「登録」ボタンをクリック

### ステップ2: ログイン

1. 「ログイン」タブに切り替え
2. メールアドレスとパスワードを入力
3. 「ログイン」ボタンをクリック

### ステップ3: 材料の登録

1. 「材料管理」タブをクリック
2. 「新規材料追加」ボタンをクリック
3. 以下の情報を入力:
   - 材料名: 例) 強力粉
   - 購入金額: 例) 500円
   - 購入容量: 例) 1000
   - 単位: 例) g
4. 単価が自動計算されます (例: 0.5円/g)

### ステップ4: レシピの作成

1. 「レシピ管理」タブをクリック
2. 「新規レシピ追加」ボタンをクリック
3. レシピ情報を入力:
   - レシピ名: 例) クロワッサン
   - 説明: 任意
   - 使用材料: 登録済みの材料から選択し、使用量を入力
4. 材料費が自動計算されます

### ステップ5: 固定費の設定 (オプション)

1. 「固定費管理」タブをクリック
2. 「固定費項目追加」ボタンをクリック
3. 固定費情報を入力:
   - 項目名: 例) 家賃
   - 月額: 例) 100000円
   - 有効/無効: 計算に含める場合はチェック
4. 他の固定費も同様に追加

### ステップ6: 商品の登録と原価計算

1. 「商品・原価計算」タブをクリック
2. 「新規商品追加」ボタンをクリック
3. 商品情報を入力:
   - 商品名: 例) クロワッサン
   - レシピ: 作成したレシピを選択
   - 固定費を含める: チェックすると固定費が原価に含まれます
   - 利益率: 例) 30% (推奨販売価格の計算に使用)
4. 原価と推奨販売価格が自動計算されます
5. 販売価格を手動で設定すると、実際の利益率が表示されます

### ステップ7: ラベルの印刷

1. 「ラベル印刷」タブをクリック
2. 「ラベル設定管理」で印刷設定を作成:
   - プリセット名: 例) 標準ラベル
   - ラベルサイズ: 幅と高さをmm単位で設定
   - 余白: 上下左右の余白をmm単位で設定
   - 表示オプション: 価格、材料リスト、賞味期限、店舗名など
3. ラベルを印刷したい商品を選択
4. 「選択した商品のラベルを印刷」ボタンをクリック
5. PDFファイルがダウンロードされます

## 3. API を直接使用する場合

### ログイン
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

レスポンス:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 材料の取得 (認証が必要)
```bash
curl -X GET "http://localhost:8000/api/materials/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 材料の追加
```bash
curl -X POST "http://localhost:8000/api/materials/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "強力粉",
    "purchase_price": 500,
    "purchase_quantity": 1000,
    "unit": "g"
  }'
```

## 4. トラブルシューティング

### ポート8000が既に使用されている
```bash
# 別のポートで起動
uvicorn app.main:app --port 8001
```

### データベースをリセットしたい
```bash
# bakery.db ファイルを削除して再起動
rm bakery.db  # Mac/Linux
del bakery.db # Windows
```

### パッケージのインストールエラー
```bash
# pipを最新版にアップグレード
pip install --upgrade pip

# 依存パッケージを再インストール
pip install -r requirements.txt --force-reinstall
```

## 5. 次のステップ

- API ドキュメントを確認: http://localhost:8000/docs
- テストを実行: `pytest tests/`
- より詳細なドキュメント: README.md を参照

## サポート

問題が発生した場合は、以下を確認してください:
1. Python のバージョンが 3.8 以上か
2. すべての依存パッケージがインストールされているか
3. .env ファイルが正しく設定されているか
4. ポート 8000 が他のアプリケーションで使用されていないか
