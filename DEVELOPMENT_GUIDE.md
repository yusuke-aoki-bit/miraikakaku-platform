# 🛠️ Miraikakaku 開発ガイド

**最終更新**: 2025-08-27  
**対象システム**: v4.0統合版

## 🎯 概要

このガイドでは、Miraikakaku AI株価予測プラットフォームの開発環境セットアップから、実際の開発・デプロイまでの手順を説明します。

## 🏗️ システム構成

```
miraikakaku/
├── miraikakakufront/     # Next.js フロントエンド
├── miraikakakuapi/       # FastAPI バックエンド
├── miraikakakubatch/     # LSTM + Vertex AI バッチシステム
└── docs/                 # ドキュメント
```

## 🚀 開発環境セットアップ

### 📋 前提条件

```bash
# 必要なソフトウェア
- Node.js 18+ (フロントエンド)
- Python 3.11+ (バックエンド・バッチ)
- Google Cloud SDK (デプロイ用)
- Docker (オプション)
```

### 🔧 初期セットアップ

#### 1. フロントエンド (Next.js)

```bash
cd miraikakakufront

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
# → http://localhost:3000

# ビルド・型チェック
npm run build
npm run type-check
```

#### 2. バックエンド API (FastAPI)

```bash
cd miraikakakuapi/functions

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt

# 統合版API起動
python integrated_main.py
# → http://localhost:8080
```

#### 3. バッチシステム (LSTM + Vertex AI)

```bash
cd miraikakakubatch/functions

# 仮想環境作成・有効化
python -m venv venv_batch
source venv_batch/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# バッチシステム起動
python simple_batch_main.py
# → http://localhost:8080
```

### 🔑 環境変数設定

#### `.env.local` (フロントエンド)
```env
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

#### `.env` (バックエンド)
```env
# Cloud SQL
CLOUD_SQL_PASSWORD=your_password
CLOUD_SQL_USER=root
CLOUD_SQL_DATABASE=miraikakaku_prod
CLOUD_SQL_INSTANCE=miraikakaku
CLOUD_SQL_REGION=us-central1

# Google Cloud
GOOGLE_CLOUD_PROJECT=pricewise-huqkr
VERTEX_AI_LOCATION=us-central1
```

## 🔍 開発フロー

### 🎯 機能開発手順

1. **ブランチ作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **開発・テスト**
   ```bash
   # フロントエンド
   npm run dev
   npm run test
   npm run type-check
   
   # バックエンド
   python integrated_main.py
   pytest  # テスト実行
   ```

3. **コミット**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. **プッシュ・PR作成**
   ```bash
   git push origin feature/your-feature-name
   ```

### 📊 API開発

#### エンドポイント追加例

```python
# miraikakakuapi/functions/integrated_main.py

@app.get("/api/finance/stocks/{symbol}/analysis")
async def get_stock_analysis(symbol: str):
    """新しい分析エンドポイント"""
    try:
        # Yahoo Finance からデータ取得
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # 分析処理
        analysis = {
            "symbol": symbol.upper(),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "analysis_date": datetime.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### フロントエンドでの API呼び出し

```typescript
// miraikakakufront/src/lib/api-client.ts

async getStockAnalysis(symbol: string): Promise<APIResponse<StockAnalysis>> {
  return this.request(`/api/finance/stocks/${symbol}/analysis`, {
    method: 'GET'
  });
}
```

### 🧠 AI/ML モデル開発

#### LSTM予測モデル修正

```python
# miraikakakubatch/functions/models/lstm_predictor.py

class LSTMStockPredictor:
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.model = self.build_model()
    
    def build_model(self):
        """LSTMモデル構築"""
        model = Sequential([
            LSTM(100, return_sequences=True, 
                 input_shape=(self.sequence_length, 9)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(7)  # 7日間予測
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
```

### 🎨 フロントエンド開発

#### 新しいページ作成

```typescript
// miraikakakufront/src/app/analysis/page.tsx

'use client';

import React from 'react';
import { useApiClient } from '@/lib/api-client';

export default function AnalysisPage() {
  const [data, setData] = useState(null);
  const apiClient = useApiClient();
  
  useEffect(() => {
    async function fetchData() {
      const result = await apiClient.getStockAnalysis('AAPL');
      setData(result.data);
    }
    
    fetchData();
  }, []);
  
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">株式分析</h1>
      {data && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold">{data.symbol}</h2>
          <p>時価総額: {data.market_cap}</p>
          <p>PER: {data.pe_ratio}</p>
        </div>
      )}
    </div>
  );
}
```

## 🧪 テスト

### フロントエンドテスト

```bash
# 単体テスト
npm run test

# E2Eテスト
npm run test:e2e

# 型チェック
npm run type-check
```

#### テスト例

```typescript
// miraikakakufront/src/components/__tests__/StockChart.test.tsx

import { render, screen } from '@testing-library/react';
import { StockChart } from '../StockChart';

describe('StockChart', () => {
  it('renders stock data correctly', () => {
    const mockData = {
      symbol: 'AAPL',
      prices: [150, 155, 152, 160]
    };
    
    render(<StockChart data={mockData} />);
    
    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });
});
```

### バックエンドテスト

```bash
# APIテスト
cd miraikakakuapi/functions
pytest tests/

# 特定テスト
pytest tests/test_finance_api.py -v
```

#### テスト例

```python
# miraikakakuapi/functions/tests/test_finance_api.py

import pytest
from fastapi.testclient import TestClient
from integrated_main import app

client = TestClient(app)

def test_health_check():
    """ヘルスチェックAPI テスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stock_predictions():
    """株価予測API テスト"""
    response = client.get("/api/finance/stocks/AAPL/predictions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "predicted_price" in data[0]
```

## 🚀 デプロイ

### 🏗️ ビルド・デプロイ手順

#### 1. フロントエンド

```bash
cd miraikakakufront

# プロダクションビルド
npm run build

# Cloud Run デプロイ
gcloud run deploy miraikakaku-front \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

#### 2. バックエンド API

```bash
cd miraikakakuapi

# Cloud Build経由でデプロイ
gcloud builds submit --config=cloudbuild.yaml

# または直接デプロイ
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api \
  --region us-central1 \
  --set-env-vars="CLOUD_SQL_PASSWORD=xxx,GOOGLE_CLOUD_PROJECT=pricewise-huqkr"
```

#### 3. バッチシステム

```bash
cd miraikakakubatch

# Cloud Build経由でデプロイ
gcloud builds submit --config=cloudbuild.yaml
```

### 🔍 デプロイ後確認

```bash
# ヘルスチェック
curl https://miraikakaku-api-465603676610.us-central1.run.app/health

# 機能テスト
curl "https://miraikakaku-api-465603676610.us-central1.run.app/api/finance/stocks/AAPL/predictions?days=3"
```

## 🐛 トラブルシューティング

### よくある問題

#### 1. **データベース接続エラー**

```bash
# 問題: "database": "disconnected"
# 解決: 環境変数確認
echo $CLOUD_SQL_PASSWORD

# Cloud SQL 接続テスト
gcloud sql connect miraikakaku --user=root
```

#### 2. **CORS エラー**

```python
# integrated_main.py で CORS設定確認
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発時のみ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. **依存関係エラー**

```bash
# Python依存関係更新
pip install --upgrade -r requirements.txt

# Node.js依存関係更新
npm update
```

#### 4. **メモリ不足エラー**

```dockerfile
# Cloud Run メモリ制限増加
gcloud run services update miraikakaku-api \
  --memory 2Gi \
  --region us-central1
```

### 🔍 ログ確認

```bash
# Cloud Run ログ
gcloud run services logs read miraikakaku-api --limit=50

# Cloud Build ログ
gcloud builds log [BUILD_ID]
```

## 📊 監視・メトリクス

### パフォーマンス監視

```bash
# レスポンス時間測定
curl -w "@curl-format.txt" -o /dev/null -s \
  "https://miraikakaku-api-465603676610.us-central1.run.app/health"

# 同時接続テスト
ab -n 1000 -c 10 https://miraikakaku-api-465603676610.us-central1.run.app/health
```

### エラー監視

```python
# integrated_main.py にログ追加
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    
    return response
```

## 🔐 セキュリティ

### 機密情報管理

```bash
# Google Secret Manager使用
gcloud secrets create cloud-sql-password --data-file=password.txt

# Cloud Run で使用
gcloud run services update miraikakaku-api \
  --update-secrets="CLOUD_SQL_PASSWORD=cloud-sql-password:latest"
```

### API セキュリティ

```python
# レート制限
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/finance/stocks/{symbol}/predictions")
@limiter.limit("100/hour")
async def get_predictions(request: Request, symbol: str):
    # 予測処理
    pass
```

## 📚 参考資料

### 公式ドキュメント
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)

### プロジェクト固有
- [システム構成詳細](/docs/SYSTEM_ARCHITECTURE.md)
- [API実装詳細](/docs/API_IMPLEMENTATION_FINAL_COMPLETE.md)
- [デプロイメント状況](/docs/DEPLOYMENT_STATUS.md)

---

## 🤝 開発チームへの貢献

### コーディング規約
- **Python**: PEP 8準拠、型ヒント必須
- **TypeScript**: ESLint + Prettier設定
- **コミット**: Conventional Commits形式

### PR作成時のチェックリスト
- [ ] テスト追加・更新
- [ ] 型チェック通過
- [ ] リント・フォーマット適用
- [ ] ドキュメント更新
- [ ] ヘルスチェック確認

---

**🛠️ Miraikakaku Development Guide**  
*Complete Development Workflow for AI-Driven Stock Prediction Platform*

*最終更新: 2025-08-27 - 全システム稼働中*