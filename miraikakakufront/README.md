# Miraikakaku - AI株価予測プラットフォーム

<p align="center">
  <img src="public/icon-192x192.png" alt="Miraikakaku Logo" width="120" height="120">
</p>

<p align="center">
  <strong>先進的なAI技術による株価予測プラットフォーム</strong><br>
  深層学習モデル（LSTM）とVertex AIを活用した高精度な市場分析ツール
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js" alt="Next.js 15">
  <img src="https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript" alt="TypeScript 5">
  <img src="https://img.shields.io/badge/PWA-Enabled-green?style=for-the-badge" alt="PWA">
  <img src="https://img.shields.io/badge/Docker-Supported-blue?style=for-the-badge&logo=docker" alt="Docker">
</p>

**Miraikakaku**（未来価格）は、最先端のAI技術を駆使した株価予測プラットフォームです。機械学習モデル（LSTM、Vertex AI）を用いて株価、出来高、通貨（外国為替）の将来予測を行い、投資家の意思決定をサポートします。

---

## 📋 目次

- [概要](#概要)
- [主な機能](#主な機能)
- [技術スタック](#技術スタック)
- [プロジェクト構成](#プロジェクト構成)
- [セットアップ](#セットアップ)
- [使用方法](#使用方法)
- [API仕様](#api仕様)
- [PWA機能](#pwa機能)
- [デプロイメント](#デプロイメント)
- [開発者向け情報](#開発者向け情報)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

---

## 🎯 概要

**Miraikakaku**は、最先端のAI技術を駆使した株価予測プラットフォームです。機械学習モデル（LSTM、Vertex AI）を用いて株価の将来予測を行い、投資家の意思決定をサポートします。

### 🌟 特徴

- **高精度AI予測**: LSTM（Long Short-Term Memory）とVertex AIによる多角的予測
- **リアルタイム分析**: WebSocketを活用したライブ市場データ
- **包括的分析**: 株価、出来高、通貨（外国為替）の統合分析
- **プログレッシブウェブアプリ（PWA）**: オフライン対応とネイティブアプリ体験
- **レスポンシブデザイン**: モバイル・タブレット・デスクトップ完全対応

---

## 🚀 主な機能

### 📊 株価予測・分析
- **リアルタイムダッシュボード**: 市場動向のライブ監視
- **AI予測チャート**: LSTM・Vertex AIによる将来価格予測
- **トリプルチャート**: 複数時間軸での比較分析
- **推奨レーティング**: AI分析による投資推奨度

### 📈 出来高分析
- **出来高予測**: 過去データと未来予測の可視化
- **価格-出来高相関**: 統計的相関関係の分析
- **トレンド分析**: 出来高パターンによる市場動向予測

### 💱 通貨予測
- **8通貨ペア対応**: 主要外国為替レートの予測
- **経済カレンダー**: 重要経済指標との連動分析
- **テクニカル指標**: RSI、MACD、ボリンジャーバンド
- **トレーディングシグナル**: 売買タイミングの提案

### 🔍 検索・ランキング
- **インテリジェント検索**: 銘柄・企業名での高速検索
- **パフォーマンスランキング**: 予測精度・収益性ランキング
- **セクター分析**: 業界別パフォーマンス比較

### 👤 ユーザー機能
- **ウォッチリスト**: お気に入り銘柄の管理
- **アラート機能**: 価格変動・予測更新通知
- **履歴管理**: 過去の予測精度追跡

## 🛠 Technology Stack

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) with React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Chart.js, Recharts, Plotly.js
- **State Management**: React Hooks with Context API
- **Real-time**: WebSocket connections
- **Testing**: Jest, React Testing Library, Playwright

### Backend
- **Runtime**: Python with FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI/ML**: TensorFlow, scikit-learn, pandas
- **Real-time**: WebSocket with uvicorn
- **API**: RESTful API with automatic documentation

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Cloud Platform**: Google Cloud Platform (GCP)
- **CI/CD**: GitHub Actions
- **Monitoring**: Custom monitoring with alerts
- **Deployment**: Cloud Run (serverless)

## 🚦 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose (optional)
- Git

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/miraikakaku.git
   cd miraikakaku
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Development Setup

#### Frontend Setup
```bash
cd miraikakakufront

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

#### Backend Setup
```bash
cd miraikakakuapi/functions

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Configuration

#### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

#### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./miraikakaku.db

# External APIs
ALPHA_VANTAGE_API_KEY=your_api_key_here
POLYGON_API_KEY=your_api_key_here

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000

# AI/ML Configuration
MODEL_UPDATE_INTERVAL=3600
PREDICTION_CONFIDENCE_THRESHOLD=0.6
```

## 📁 Project Structure

```
miraikakaku/
├── miraikakakufront/           # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   │   ├── (pages)/        # Route groups
│   │   │   ├── globals.css     # Global styles
│   │   │   └── layout.tsx      # Root layout
│   │   ├── components/         # Reusable components
│   │   │   ├── charts/         # Chart components
│   │   │   ├── common/         # Common UI components
│   │   │   ├── home/           # Homepage components
│   │   │   ├── layout/         # Layout components
│   │   │   └── search/         # Search components
│   │   ├── config/             # Configuration files
│   │   │   ├── constants.ts    # Application constants
│   │   │   └── design-tokens.ts # Design system tokens
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utility libraries
│   │   │   └── api-client.ts   # API client
│   │   └── types/              # TypeScript type definitions
│   ├── public/                 # Static assets
│   ├── tailwind.config.js      # Tailwind configuration
│   ├── package.json            # Dependencies
│   └── next.config.js          # Next.js configuration
│
├── miraikakakuapi/             # FastAPI Backend Application
│   └── functions/
│       ├── api/                # API routes
│       │   ├── admin/          # Admin endpoints
│       │   ├── auth/           # Authentication
│       │   ├── finance/        # Stock market APIs
│       │   └── websocket/      # WebSocket handlers
│       ├── database/           # Database models and setup
│       ├── services/           # Business logic
│       ├── repositories/       # Data access layer
│       ├── utils/              # Utility functions
│       └── main.py             # FastAPI application entry
│
├── miraikakakubatch/           # Batch Processing Services
│   └── functions/
│       ├── data_pipeline/      # Data processing
│       ├── ml_models/          # Machine learning models
│       └── schedulers/         # Cron jobs
│
├── monitoring/                 # Monitoring and alerting
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml          # Docker services
└── README.md                   # This file
```

## 🎨 Design System

Our design system is built around a cohesive set of tokens and components:

### Color Palette
- **Primary**: Blue (#2196f3) - Interactive elements, CTAs
- **Success**: Green (#10b981) - Positive metrics, gains
- **Danger**: Red (#ef4444) - Negative metrics, losses, alerts
- **Surface**: Black/Gray scale - Backgrounds and cards
- **Text**: White/Gray scale - Typography hierarchy

### Typography
- **Font Family**: System font stack for optimal performance
- **Font Sizes**: Modular scale (0.75rem to 8rem)
- **Font Weights**: Normal (400), Medium (500), Semibold (600), Bold (700)

### Spacing & Layout
- **Base Unit**: 4px (0.25rem)
- **Scale**: 1x, 2x, 3x, 4x, 5x, 6x, 8x, 10x, 12x, 16x, 20x
- **Layout**: CSS Grid and Flexbox-based responsive system

## 🧪 Testing

### Frontend Testing
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Test coverage
npm run test:coverage
```

### Backend Testing
```bash
# Run tests
python -m pytest

# Test with coverage
python -m pytest --cov=.

# Integration tests
python -m pytest tests/integration/
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Google Cloud Platform
```bash
# Deploy frontend
gcloud run deploy miraikakaku-frontend \
  --source ./miraikakakufront \
  --platform managed \
  --region asia-northeast1

# Deploy API
gcloud run deploy miraikakaku-api \
  --source ./miraikakakuapi \
  --platform managed \
  --region asia-northeast1
```

### CI/CD Pipeline
Our GitHub Actions pipeline automatically:
1. Runs tests on all pull requests
2. Builds Docker images
3. Deploys to staging on merge to `develop`
4. Deploys to production on release tags

## 📊 Performance

### Lighthouse Scores
- **Performance**: 95+
- **Accessibility**: 100
- **Best Practices**: 100
- **SEO**: 95+

### Key Metrics
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **Time to Interactive**: < 3.5s

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style
- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + flake8 formatting
- **Commits**: Conventional Commits format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [https://miraikakaku.example.com](https://miraikakaku.example.com)
- **API Documentation**: [https://api.miraikakaku.example.com/docs](https://api.miraikakaku.example.com/docs)
- **Design System**: [https://storybook.miraikakaku.example.com](https://storybook.miraikakaku.example.com)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/miraikakaku/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/miraikakaku/discussions)
- **Email**: support@miraikakaku.example.com

## 🙏 Acknowledgments

- Market data provided by [Alpha Vantage](https://www.alphavantage.co/)
- Icons by [Lucide](https://lucide.dev/)
- Charts powered by [Chart.js](https://www.chartjs.org/) and [Plotly.js](https://plotly.com/javascript/)
- UI inspiration from modern financial platforms

---

**Built with ❤️ by the Miraikakaku team**