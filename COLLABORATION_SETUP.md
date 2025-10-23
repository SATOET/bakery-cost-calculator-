# GitHubでの共同開発セットアップガイド

このガイドでは、複数人でこのリポジトリを開発する方法を説明します。

## 1. コラボレーターの追加（リポジトリオーナーが実施）

### 方法A: GitHub Web UIから追加

1. リポジトリページにアクセス
   https://github.com/SATOET/bakery-cost-calculator-

2. 「Settings」タブをクリック

3. 左サイドバーの「Collaborators」をクリック

4. 「Add people」ボタンをクリック

5. 追加したい人のGitHubユーザー名またはメールアドレスを入力

6. 「Add [ユーザー名] to this repository」をクリック

7. 招待メールが送信されます

### 方法B: GitHub CLIから追加（コマンドライン）

```bash
# リポジトリディレクトリで実行
gh auth login  # 初回のみ必要

# コラボレーターを追加
gh repo add-collaborator SATOET/bakery-cost-calculator- <GitHubユーザー名>
```

## 2. 招待を受け取った人の手順

1. GitHubの通知またはメールから招待リンクをクリック

2. 「Accept invitation」をクリック

3. これでリポジトリへの書き込み権限が付与されます

## 3. 開発環境のセットアップ

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

### クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/SATOET/bakery-cost-calculator-.git
cd bakery-cost-calculator-

# 2. 仮想環境を作成
python -m venv venv

# 3. 仮想環境を有効化（Windows）
venv\Scripts\activate

# 4. 依存パッケージをインストール
pip install -r requirements.txt
pip install "pydantic[email]"

# 5. 環境変数を設定
cp .env.example .env
# .envファイルを編集

# 6. アプリケーションを起動
python -m uvicorn app.main:app --reload
```

## 4. 推奨される開発ツール

### Git設定

```bash
# ユーザー情報の設定
git config --global user.name "あなたの名前"
git config --global user.email "your.email@example.com"

# デフォルトブランチ名をmainに設定
git config --global init.defaultBranch main
```

### IDE / エディター

- **Visual Studio Code** (推奨)
  - 拡張機能: Python, GitLens, Pylance
- **PyCharm**
- **Sublime Text** + Anaconda plugin

### Python開発ツール

```bash
# コードフォーマット・リント
pip install black flake8 isort mypy

# 使用例
black app/
flake8 app/
isort app/
mypy app/
```

## 5. 開発ワークフロー

### 基本的な流れ

```bash
# 1. 最新のコードを取得
git checkout main
git pull origin main

# 2. 新しいブランチを作成
git checkout -b feature/your-feature-name

# 3. コードを編集
# ... 開発作業 ...

# 4. 変更をコミット
git add .
git commit -m "機能追加: ○○を実装"

# 5. GitHubにプッシュ
git push origin feature/your-feature-name

# 6. Pull Requestを作成
# GitHubのWebページで「Compare & pull request」をクリック
```

### Pull Request (PR) のベストプラクティス

1. **わかりやすいタイトル**
   - 良い例: `機能追加: ラベル印刷にQRコード機能を追加`
   - 悪い例: `update`

2. **詳細な説明**
   - 何を変更したか
   - なぜ変更したか
   - 影響範囲
   - テスト方法

3. **小さなPR**
   - 1つのPRで1つの機能/修正
   - レビューしやすいサイズ（目安: 300行以下）

4. **テストの追加**
   - 新機能には必ずテストを追加

## 6. コードレビューのガイドライン

### レビュワー向け

- [ ] コードが要件を満たしているか
- [ ] コードスタイルが統一されているか
- [ ] テストが追加されているか
- [ ] ドキュメントが更新されているか
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンスに問題がないか

### PR作成者向け

- レビューコメントには素早く対応
- 建設的な議論を心がける
- 必要に応じてコードを修正
- 承認後にマージ

## 7. ブランチ保護ルール（推奨設定）

リポジトリオーナーは以下の保護ルールを設定することを推奨:

1. Settings → Branches → Add rule

2. `main` ブランチに対して:
   - ☑ Require pull request reviews before merging
   - ☑ Require status checks to pass before merging
   - ☑ Require branches to be up to date before merging

## 8. Issue管理

### Issueの作成

1. 「Issues」タブ → 「New issue」

2. タイトルと説明を記入

3. ラベルを追加（bug, enhancement, documentationなど）

4. 担当者を指定（オプション）

### Issueテンプレート（推奨）

**バグ報告:**
```markdown
## 問題の説明
[バグの詳細]

## 再現手順
1. ...
2. ...
3. ...

## 期待される動作
[正しい動作]

## 実際の動作
[現在の動作]

## 環境
- OS: 
- Python: 
- ブラウザ: 
```

**機能要望:**
```markdown
## 機能の概要
[機能の説明]

## 理由
[なぜこの機能が必要か]

## 提案する実装方法
[実装のアイデア]
```

## 9. よくある質問

### Q: 他の人の変更とコンフリクトした場合は？

```bash
# mainブランチの最新を取得
git checkout main
git pull origin main

# 自分のブランチにマージ
git checkout your-branch
git merge main

# コンフリクトを解決
# ... ファイルを編集 ...

git add .
git commit -m "マージコンフリクトを解決"
git push origin your-branch
```

### Q: 間違ってmainブランチに直接コミットしてしまった

```bash
# コミットを取り消す（まだpushしていない場合）
git reset --soft HEAD~1

# 新しいブランチを作成
git checkout -b feature/correct-branch

# 再度コミット
git commit -m "正しいメッセージ"
git push origin feature/correct-branch
```

### Q: プライベートリポジトリにしたい

1. Settings → Danger Zone → Change visibility
2. 「Change to private」を選択

## 10. サポート

質問や問題がある場合:
1. まず [CONTRIBUTING.md](CONTRIBUTING.md) を確認
2. 既存のIssueを検索
3. 新しいIssueを作成

---

Happy Coding! 🎉
