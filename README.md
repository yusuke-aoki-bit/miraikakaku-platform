# Miraikakaku - AI株価予測システム

## 📁 プロジェクト構造

### 🔧 miraikakakubatch - バッチ処理システム
データ収集、予測生成、バックグラウンド処理を担当
- **技術**: Python、GCP Batch、PostgreSQL
- **主要機能**: 株価データ取得、AI予測の大量生成、スケジュール実行
- **ディレクトリ**: `./miraikakakubatch/`

### 🌐 miraikakakuapi - API サーバー
REST API、LSTM + VertexAI 予測エンジンを提供
- **技術**: FastAPI、TensorFlow、Google Cloud
- **主要機能**: デュアル予測システム、リアルタイム株価API
- **ディレクトリ**: `./miraikakakuapi/`

### 💻 miraikakakufront - フロントエンド
ユーザーインターフェース、データビジュアライゼーション
- **技術**: Next.js、React、TypeScript、Tailwind CSS
- **主要機能**: 株価チャート、予測表示、検索機能
- **ディレクトリ**: `./miraikakakufront/`

### 🗄️ shared - 共有ユーティリティ
各モジュール間で共有される共通機能
- **場所**: `./shared/utils/`
- **機能**: データベース管理、制約修正、シンボル管理

### 📄 docs - ドキュメント
プロジェクトドキュメント、レポート
- **場所**: `./docs/`

## 🔗 システム連携

```
batch → database ← api ← frontend
  ↓        ↓        ↓       ↓
 GCP    PostgreSQL FastAPI Next.js
```

## 🚀 特徴

- **デュアル予測システム**: LSTM + VertexAI による独立した予測
- **リアルタイム処理**: 株価データの即座な取得と分析
- **スケーラブル**: 各モジュールが独立してデプロイ・スケール可能
- **堅牢性**: 包括的なエラーハンドリングとログ機能

## 📊 実績

- **パフォーマンス向上**: プログレッシブローディングにより86%の性能改善
- **環境整備**: GCP Batch jobsの最適化とエラー対策
- **UI/UX**: デュアル予測システムの比較分析機能

## 🛠️ 開発・デプロイ

各モジュールは独立して開発・デプロイが可能です。詳細な設定については各ディレクトリ内のREADMEを参照してください。