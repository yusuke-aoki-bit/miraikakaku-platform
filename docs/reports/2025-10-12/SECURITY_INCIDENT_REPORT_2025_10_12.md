# セキュリティインシデントレポート

## 🚨 インシデント概要

**発見日時**: 2025-10-12 15:50 JST
**重要度**: 🔴 HIGH
**ステータス**: 調査完了・対応推奨事項あり

---

## 📋 発見内容

### 問題: .envファイルがGit履歴に存在

**詳細**:
- `.env`ファイルが過去3つのコミットでGit履歴に記録されている
- 機密情報（データベースパスワード、APIキー等）が含まれる可能性

**影響を受けるコミット**:
```
adb90c8 - Comprehensive codebase cleanup and organization
eddedf3 - Initial commit: Miraikakaku project structure with proper .gitignore
6e76853 - Add initial project structure with Docker, environment configurations, and API setup
```

**現在の状態**:
- ✅ `.gitignore`に`.env`が含まれている（現在は追跡されない）
- ⚠️  Git履歴に`.env`が残存
- ⚠️  ルートディレクトリに`.env`ファイル存在（2,124 bytes）

---

## 🔍 リスク評価

### 潜在的な影響

| 項目 | リスクレベル | 詳細 |
|------|------------|------|
| データベース認証情報漏洩 | 🔴 HIGH | PostgreSQLパスワードが含まれる可能性 |
| APIキー漏洩 | 🟡 MEDIUM | Alpha Vantage, Finnhub等のキー |
| GCPプロジェクト情報 | 🟢 LOW | プロジェクトIDは公開情報 |
| リポジトリがPublic | ❓ UNKNOWN | 要確認 |

### リスクシナリオ

1. **リポジトリがPublicの場合**:
   - ✅ .gitignoreがあるため現在のファイルは非公開
   - ⚠️  Git履歴は公開されている
   - 🔴 誰でも過去の`.env`内容を閲覧可能

2. **リポジトリがPrivateの場合**:
   - ✅ 外部からのアクセス不可
   - ⚠️  内部メンバーは履歴閲覧可能
   - 🟡 将来Publicにする際に問題

---

## ✅ 現在の保護状態

### 良い点
1. ✅ `.gitignore`に`.env`が正しく設定されている
2. ✅ 現在のコミットでは`.env`は追跡されていない
3. ✅ `.env.example`が存在（テンプレート提供）

### 懸念点
1. ⚠️  過去のGit履歴に`.env`が残存
2. ⚠️  リポジトリのPublic/Private状態が不明
3. ⚠️  機密情報のローテーション未実施の可能性

---

## 🛡️ 推奨対応（優先度順）

### 🔴 Critical（即座に実施）

#### 1. リポジトリの公開状態確認
```bash
# GitHubの場合
gh repo view --json visibility

# または手動確認
# https://github.com/{username}/miraikakaku/settings
```

**判定**:
- Public → **即座に対応必須**
- Private → 中期対応で可

#### 2. 機密情報のローテーション（Publicの場合）
以下の認証情報を即座に変更:
- ✅ PostgreSQLパスワード
- ✅ Alpha Vantage APIキー
- ✅ Finnhub APIキー
- ✅ その他のAPIキー

**手順**:
```bash
# PostgreSQLパスワード変更
gcloud sql users set-password postgres \
  --instance=miraikakaku-postgres \
  --password=NEW_SECURE_PASSWORD

# APIキーの再発行
# → 各サービスのダッシュボードで実施
```

### 🟡 High（24時間以内）

#### 3. Git履歴から.envを完全削除
```bash
# BFG Repo-Cleanerを使用（推奨）
# https://rtyley.github.io/bfg-repo-cleaner/

# 1. リポジトリのバックアップ
git clone --mirror https://github.com/{username}/miraikakaku.git

# 2. .envファイルを履歴から削除
java -jar bfg.jar --delete-files .env miraikakaku.git

# 3. Git履歴を書き換え
cd miraikakaku.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 強制プッシュ（全メンバーに通知必要）
git push --force
```

**注意事項**:
- ⚠️  全ての開発者が`git clone`し直す必要あり
- ⚠️  既存のPull Requestが影響を受ける
- ⚠️  事前にチームへ通知必須

#### 4. Secret Managerへの移行
```bash
# GCP Secret Managerに機密情報を保存
echo -n "YOUR_POSTGRES_PASSWORD" | \
  gcloud secrets create postgres-password \
  --data-file=- \
  --replication-policy="automatic"

# Cloud Runからアクセス
gcloud run services update miraikakaku-api \
  --update-secrets=POSTGRES_PASSWORD=postgres-password:latest
```

### 🟢 Medium（1週間以内）

#### 5. セキュリティ監査の実施
- [ ] 全てのAPIキーの使用状況確認
- [ ] 不正アクセスログの確認
- [ ] データベースアクセスログの確認

#### 6. セキュリティポリシーの策定
- [ ] 機密情報管理ガイドライン作成
- [ ] Pre-commitフックの導入
- [ ] 定期的なセキュリティレビュー

---

## 📝 Git履歴クリーンアップ完全ガイド

### Option 1: BFG Repo-Cleaner（推奨）

**メリット**:
- 高速・安全
- 最新のコミットは保護される
- 簡単な操作

**手順**:
```bash
# 1. BFGをダウンロード
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# 2. リポジトリをミラークローン
git clone --mirror git@github.com:username/miraikakaku.git

# 3. .envを削除
java -jar bfg-1.14.0.jar --delete-files .env miraikakaku.git

# 4. クリーンアップ
cd miraikakaku.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. 強制プッシュ
git push
```

### Option 2: git filter-branch（古い方法）

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
git push origin --force --tags
```

### Option 3: 何もしない（Private限定）

**条件**:
- リポジトリがPrivateである
- 信頼できるメンバーのみがアクセス可能
- 将来Publicにする予定がない

**この場合の対応**:
- 現状維持（.gitignoreで保護済み）
- 定期的な監査実施
- 将来Public化する際に再評価

---

## 🔒 予防策

### Pre-commitフックの導入

`.git/hooks/pre-commit`を作成:
```bash
#!/bin/bash

# .envファイルのコミットを防ぐ
if git diff --cached --name-only | grep -q "^\.env$"; then
  echo "❌ ERROR: Attempting to commit .env file!"
  echo "Please remove .env from staged files:"
  echo "  git reset HEAD .env"
  exit 1
fi

# 機密情報のパターンチェック
if git diff --cached | grep -iE "(password|api_key|secret|token)\s*=\s*['\"]?[a-zA-Z0-9]{8,}"; then
  echo "⚠️  WARNING: Possible secret detected in commit!"
  echo "Please review your changes carefully."
  read -p "Continue? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi
```

### GitHub Actions監視

`.github/workflows/security-check.yml`:
```yaml
name: Security Check
on: [push, pull_request]
jobs:
  check-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for secrets
        run: |
          if git ls-files | grep -q "^\.env$"; then
            echo "❌ .env file detected!"
            exit 1
          fi
```

---

## 📊 対応状況トラッキング

| タスク | 優先度 | ステータス | 期限 |
|--------|--------|-----------|------|
| リポジトリ公開状態確認 | 🔴 Critical | ⏳ 未実施 | 即座 |
| 機密情報ローテーション | 🔴 Critical | ⏳ 未実施 | Public時のみ即座 |
| Git履歴クリーンアップ | 🟡 High | ⏳ 未実施 | 24時間以内 |
| Secret Manager移行 | 🟡 High | ⏳ 未実施 | 24時間以内 |
| セキュリティ監査 | 🟢 Medium | ⏳ 未実施 | 1週間以内 |
| Pre-commitフック導入 | 🟢 Medium | ⏳ 未実施 | 1週間以内 |

---

## 🎯 結論

### 現在のリスクレベル

**リポジトリがPrivateの場合**: 🟡 MEDIUM
- 即座の対応は不要
- 中期的な改善推奨

**リポジトリがPublicの場合**: 🔴 HIGH
- 即座の対応必須
- 機密情報のローテーション
- Git履歴のクリーンアップ

### 次のアクション

1. **即座**: リポジトリの公開状態確認
2. **条件付き**: Publicの場合は機密情報ローテーション
3. **24時間以内**: Git履歴クリーンアップまたはSecret Manager移行
4. **1週間以内**: 予防策の実装

---

**レポート作成者**: Claude (AI Assistant)
**作成日時**: 2025-10-12 15:50 JST
**次回レビュー**: 2025-10-19

**関連ドキュメント**:
- [ISSUES_AND_IMPROVEMENTS_2025_10_12.md](./ISSUES_AND_IMPROVEMENTS_2025_10_12.md)
- [GCP Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
