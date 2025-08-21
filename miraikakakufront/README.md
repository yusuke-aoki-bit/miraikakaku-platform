# 🚀 Miraikakaku - AI-Driven Stock Prediction Platform

**Miraikakaku** (未来価格 - "Future Price" in Japanese) is a cutting-edge web application that leverages artificial intelligence to provide comprehensive stock market analysis and price predictions. Built with modern web technologies, it offers real-time market data, AI-powered insights, and intuitive user experiences.

## 🌟 Features

### 📈 Core Features
- **Real-time Stock Data** - Live market data and price updates
- **AI Price Predictions** - Machine learning-powered stock price forecasting
- **Interactive Charts** - Advanced charting with technical indicators
- **Market Rankings** - Growth potential and accuracy-based rankings
- **Portfolio Analysis** - Risk assessment and performance tracking
- **Smart Search** - Intelligent stock symbol and company name search
- **Responsive Design** - Optimized for desktop, tablet, and mobile devices

### 🤖 AI Capabilities
- **Multi-Model Predictions** - Various ML models for enhanced accuracy
- **Confidence Scoring** - Reliability metrics for each prediction
- **Historical Accuracy** - Track record of past predictions
- **Market Sentiment Analysis** - News and social media sentiment integration
- **Risk Assessment** - Volatility and risk factor analysis

### 🎨 User Experience
- **Dark Theme** - Modern, eye-friendly dark interface
- **Glass Morphism** - Beautiful translucent design elements
- **Smooth Animations** - Fluid transitions and micro-interactions
- **Intuitive Navigation** - Clear information architecture
- **Accessibility** - WCAG compliant design

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