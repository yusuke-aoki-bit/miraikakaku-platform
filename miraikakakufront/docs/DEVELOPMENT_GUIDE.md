# 👨‍💻 Miraikakaku Development Guide

Complete guide for developers working on the Miraikakaku platform. This document covers everything from local setup to production deployment, coding standards, and contribution workflows.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Architecture](#code-architecture)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Performance Guidelines](#performance-guidelines)
- [Deployment Process](#deployment-process)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js** 18+ with npm
- **Python** 3.9+
- **Docker** & Docker Compose (recommended)
- **Git** for version control
- **PostgreSQL** (for production) or SQLite (for development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/miraikakaku.git
   cd miraikakaku
   ```

2. **Setup with Docker (Recommended)**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f miraikakaku-frontend
   docker-compose logs -f miraikakaku-api
   ```

3. **Manual setup (Alternative)**
   ```bash
   # Frontend setup
   cd miraikakakufront
   npm install
   cp .env.example .env.local
   npm run dev
   
   # Backend setup (new terminal)
   cd miraikakakuapi/functions
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python init_db.py
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Batch services (new terminal)
   cd miraikakakubatch/functions
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 🛠 Development Environment

### Environment Configuration

#### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_DEBUG_MODE=true

# Development Tools
NEXT_PUBLIC_STORYBOOK=true
ANALYZE=false
```

#### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./miraikakaku_dev.db
# DATABASE_URL=postgresql://user:password@localhost:5432/miraikakaku_dev

# External APIs
ALPHA_VANTAGE_API_KEY=your_api_key_here
POLYGON_API_KEY=your_api_key_here
FINNHUB_API_KEY=your_api_key_here

# Security
SECRET_KEY=your-development-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# AI/ML Configuration
MODEL_UPDATE_INTERVAL=3600
PREDICTION_CONFIDENCE_THRESHOLD=0.6
ENABLE_MODEL_TRAINING=true

# Development
DEBUG=true
LOG_LEVEL=debug
ENABLE_CORS=true
```

### Development Tools

#### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "files.exclude": {
    "**/node_modules": true,
    "**/.next": true,
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "python.defaultInterpreterPath": "./miraikakakuapi/functions/venv/bin/python"
}
```

#### Recommended Extensions
```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "ms-python.python",
    "ms-python.flake8",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "ms-playwright.playwright"
  ]
}
```

### Git Configuration

#### Git Hooks Setup
```bash
# Install husky for git hooks
npm install --save-dev husky
npx husky install

# Pre-commit hook
npx husky add .husky/pre-commit "npm run lint && npm run type-check"

# Commit message hook
npx husky add .husky/commit-msg 'npx commitlint --edit "$1"'
```

#### Conventional Commits
Follow conventional commits format:
```
feat: add stock prediction confidence scoring
fix: resolve WebSocket connection timeout
docs: update API documentation
style: improve chart loading animations
refactor: optimize data fetching logic
test: add integration tests for search functionality
chore: update dependencies
```

---

## 🏗 Code Architecture

### Frontend Architecture

```
src/
├── app/                 # Next.js App Router
│   ├── (pages)/         # Route groups
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Homepage
├── components/          # React components
│   ├── common/          # Shared components
│   ├── charts/          # Chart components
│   ├── layout/          # Layout components
│   └── [feature]/       # Feature-specific components
├── hooks/               # Custom React hooks
├── lib/                 # Utility libraries
├── types/               # TypeScript definitions
├── config/              # Configuration files
│   ├── constants.ts     # Application constants
│   └── design-tokens.ts # Design system tokens
└── styles/              # Additional styles
```

### Backend Architecture

```
functions/
├── api/                 # API routes
│   ├── auth/            # Authentication
│   ├── finance/         # Finance endpoints
│   ├── admin/           # Admin endpoints
│   └── websocket/       # WebSocket handlers
├── database/            # Database layer
│   ├── models/          # SQLAlchemy models
│   └── database.py      # Database configuration
├── services/            # Business logic
├── repositories/        # Data access layer
├── utils/               # Utility functions
├── middleware/          # Custom middleware
└── main.py              # FastAPI application
```

### Design Patterns

1. **Component Composition**: Build complex UI from simple components
2. **Custom Hooks**: Encapsulate stateful logic
3. **Repository Pattern**: Abstract data access layer
4. **Service Layer**: Business logic separation
5. **Factory Pattern**: Create chart instances
6. **Observer Pattern**: Real-time data updates

---

## 🔄 Development Workflow

### Branch Strategy

```bash
main          # Production branch
├── develop   # Development integration
├── feature/* # Feature branches
├── hotfix/*  # Hot fixes
└── release/* # Release preparation
```

### Feature Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/stock-predictions-ui
   ```

2. **Development Process**
   ```bash
   # Make changes
   npm run dev  # Start development server
   
   # Run tests frequently
   npm run test
   npm run test:e2e
   
   # Check code quality
   npm run lint
   npm run type-check
   ```

3. **Pre-commit Checklist**
   - [ ] All tests pass
   - [ ] TypeScript compilation successful
   - [ ] ESLint and Prettier formatting applied
   - [ ] No console.log statements in production code
   - [ ] Updated documentation if needed

4. **Create Pull Request**
   ```bash
   git add .
   git commit -m "feat: add enhanced stock prediction visualization"
   git push origin feature/stock-predictions-ui
   ```

### Code Review Process

#### Pull Request Template
```markdown
## 📝 Description
Brief description of changes

## 🎯 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## 🧪 Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## 📷 Screenshots
Include screenshots for UI changes

## 📋 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
```

#### Review Criteria
- Code quality and readability
- Performance implications
- Security considerations
- Accessibility compliance
- Test coverage
- Documentation completeness

---

## 🧪 Testing Strategy

### Testing Pyramid

1. **Unit Tests** (70%): Individual component/function testing
2. **Integration Tests** (20%): Component interaction testing
3. **End-to-End Tests** (10%): Full user journey testing

### Frontend Testing

#### Unit Tests with Jest + React Testing Library
```typescript
// src/components/__tests__/StockSearch.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import StockSearch from '../StockSearch';

// Mock API calls
jest.mock('@/lib/api-client');

describe('StockSearch Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should display search results', async () => {
    const mockOnSelect = jest.fn();
    
    render(<StockSearch onSymbolSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText(/検索/);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    await waitFor(() => {
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    });
  });

  it('should handle empty search results', async () => {
    render(<StockSearch onSymbolSelect={jest.fn()} />);
    
    const input = screen.getByPlaceholderText(/検索/);
    fireEvent.change(input, { target: { value: 'NONEXISTENT' } });
    
    await waitFor(() => {
      expect(screen.getByText(/結果が見つかりません/)).toBeInTheDocument();
    });
  });
});
```

#### Integration Tests
```typescript
// src/__tests__/integration/stock-analysis.test.tsx
import { render, screen } from '@testing-library/react';
import { server } from '../../mocks/server';
import StockAnalysisPage from '@/app/analysis/page';

describe('Stock Analysis Integration', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('should load stock data and display chart', async () => {
    render(<StockAnalysisPage />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('stock-chart')).toBeInTheDocument();
    });

    // Verify chart renders with correct data
    expect(screen.getByText('AAPL - 株価チャート')).toBeInTheDocument();
  });
});
```

#### E2E Tests with Playwright
```typescript
// tests/e2e/stock-search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Stock Search Flow', () => {
  test('should search and select stock', async ({ page }) => {
    await page.goto('/');
    
    // Search for stock
    await page.fill('[data-testid="stock-search-input"]', 'AAPL');
    
    // Wait for suggestions
    await page.waitForSelector('[data-testid="search-suggestions"]');
    
    // Click on Apple Inc.
    await page.click('text=Apple Inc.');
    
    // Verify navigation to stock page
    await expect(page).toHaveURL('/stock/AAPL');
    
    // Verify chart loads
    await expect(page.locator('[data-testid="stock-chart"]')).toBeVisible();
  });

  test('should handle search errors gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/finance/stocks/search*', route => {
      route.fulfill({ status: 500 });
    });
    
    await page.goto('/');
    await page.fill('[data-testid="stock-search-input"]', 'TEST');
    
    // Should show error message
    await expect(page.locator('text=検索エラーが発生しました')).toBeVisible();
  });
});
```

### Backend Testing

#### Unit Tests with pytest
```python
# tests/test_finance_routes.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestFinanceRoutes:
    def test_search_stocks_success(self):
        response = client.get("/api/finance/stocks/search?query=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["symbol"] == "AAPL"
    
    def test_search_stocks_empty_query(self):
        response = client.get("/api/finance/stocks/search?query=")
        assert response.status_code == 422  # Validation error
    
    def test_get_stock_price_not_found(self):
        response = client.get("/api/finance/stocks/INVALID/price")
        assert response.status_code == 404
```

#### Performance Tests
```python
# tests/test_performance.py
import pytest
import asyncio
from locust import HttpUser, task

class StockSearchLoadTest(HttpUser):
    @task
    def search_stocks(self):
        self.client.get("/api/finance/stocks/search?query=AAPL")
    
    @task
    def get_stock_price(self):
        self.client.get("/api/finance/stocks/AAPL/price?days=30")
```

### Running Tests

```bash
# Frontend tests
npm run test              # Unit tests
npm run test:coverage     # With coverage
npm run test:e2e          # E2E tests
npm run test:watch        # Watch mode

# Backend tests
python -m pytest                    # All tests
python -m pytest --cov=.            # With coverage
python -m pytest tests/integration/ # Integration only
python -m pytest -v -s             # Verbose output

# Load testing
locust -f tests/load/api_test.py --host=http://localhost:8000
```

---

## ⚡ Performance Guidelines

### Frontend Optimization

#### Code Splitting
```typescript
// Lazy load heavy components
const InteractiveChart = React.lazy(() => 
  import('@/components/charts/InteractiveChart')
);

// Route-based splitting (automatic with Next.js App Router)
export default function StockAnalysisPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <InteractiveChart symbol="AAPL" />
    </Suspense>
  );
}
```

#### Memoization
```typescript
// Memoize expensive calculations
const chartData = useMemo(() => {
  return processStockData(rawData);
}, [rawData]);

// Memoize components
const OptimizedChart = React.memo(StockChart, (prev, next) => {
  return prev.symbol === next.symbol && prev.timeframe === next.timeframe;
});
```

#### Image Optimization
```typescript
import Image from 'next/image';

// Optimized images with Next.js
<Image
  src="/charts/stock-preview.jpg"
  alt="Stock Chart Preview"
  width={400}
  height={300}
  loading="lazy"
  placeholder="blur"
/>
```

### Backend Optimization

#### Database Optimization
```python
# Use indexes for frequent queries
class StockMaster(Base):
    __tablename__ = "stock_master"
    
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)  # For search queries
    sector = Column(String, index=True)  # For filtering

# Optimize queries with select_related
def get_stock_with_prices(symbol: str):
    return db.query(StockMaster).filter(
        StockMaster.symbol == symbol
    ).options(
        selectinload(StockMaster.prices)
    ).first()
```

#### Caching Strategy
```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=1000)
def get_stock_info(symbol: str):
    return db.query(StockMaster).filter(
        StockMaster.symbol == symbol
    ).first()

# Redis caching
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_predictions(symbol: str):
    cache_key = f"predictions:{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    data = fetch_predictions(symbol)
    cache.set(cache_key, json.dumps(data), ex=3600)  # 1 hour TTL
    return data
```

### Monitoring Performance

#### Web Vitals Monitoring
```typescript
// pages/_app.tsx
export function reportWebVitals(metric: NextWebVitalsMetric) {
  if (process.env.NODE_ENV === 'production') {
    // Send to analytics
    analytics.track('web-vital', {
      name: metric.name,
      value: metric.value,
      id: metric.id,
    });
  }
}
```

#### API Performance Monitoring
```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow queries
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.url} took {process_time:.2f}s")
    
    return response
```

---

## 🚀 Deployment Process

### Development Deployment

#### Local Development
```bash
# Frontend development
npm run dev

# Backend development
uvicorn main:app --reload --port 8000

# Full stack with Docker
docker-compose up -d
```

### Staging Deployment

#### Docker Build Process
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

#### CI/CD Pipeline (.github/workflows/deploy-staging.yml)
```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test:ci
      
      - name: Run E2E tests
        run: npm run test:e2e:ci

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Google Cloud Run
        run: |
          gcloud run deploy miraikakaku-staging \
            --source . \
            --region asia-northeast1 \
            --platform managed
```

### Production Deployment

#### Environment Setup
```bash
# Production environment variables
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://api.miraikakaku.com
DATABASE_URL=postgresql://user:pass@prod-db:5432/miraikakaku
REDIS_URL=redis://prod-redis:6379
```

#### Deployment Steps
```bash
# 1. Build and test
npm run build
npm run test:prod

# 2. Create production build
docker build -t miraikakaku-frontend:latest .
docker build -t miraikakaku-api:latest ./miraikakakuapi

# 3. Deploy to production
kubectl apply -f k8s/production/
# or
gcloud run deploy --source . --platform managed
```

#### Health Checks
```yaml
# kubernetes/health-check.yaml
apiVersion: v1
kind: Service
metadata:
  name: health-check
spec:
  selector:
    app: miraikakaku-frontend
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: miraikakaku-frontend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: frontend
        image: miraikakaku-frontend:latest
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 🐛 Troubleshooting

### Common Issues

#### WebSocket Connection Failures
```typescript
// Debug WebSocket connection
const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Fallback to polling
  startPolling();
};
ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);
  if (event.code !== 1000) {
    // Unexpected close, try to reconnect
    setTimeout(() => reconnectWebSocket(), 5000);
  }
};
```

#### API Connection Issues
```typescript
// API client with retry logic
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    
    if (error.response?.status === 503 && !original._retry) {
      original._retry = true;
      await new Promise(resolve => setTimeout(resolve, 1000));
      return apiClient(original);
    }
    
    return Promise.reject(error);
  }
);
```

#### Database Connection Issues
```python
# Database connection with retry
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def create_db_engine(database_url: str, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            # Test connection
            engine.execute("SELECT 1")
            return engine
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Development Environment Issues

#### Port Conflicts
```bash
# Find processes using ports
lsof -i :3000
lsof -i :8000

# Kill processes
kill -9 $(lsof -t -i :3000)
kill -9 $(lsof -t -i :8000)

# Or use our helper script
npm run kill-ports
```

#### Node Modules Issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Clear Next.js cache
rm -rf .next
npm run build
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Performance Issues

#### Frontend Performance Debugging
```typescript
// Performance monitoring
if (typeof window !== 'undefined' && 'performance' in window) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      console.log('Load time:', perfData.loadEventEnd - perfData.fetchStart);
      
      // Send to monitoring service
      analytics.track('page-load-time', {
        duration: perfData.loadEventEnd - perfData.fetchStart,
        page: window.location.pathname,
      });
    }, 0);
  });
}
```

#### Backend Performance Debugging
```python
import cProfile
import pstats

def profile_endpoint():
    pr = cProfile.Profile()
    pr.enable()
    
    # Your endpoint logic here
    result = expensive_operation()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return result
```

### Debugging Tools

#### Frontend Debugging
- React DevTools
- Redux DevTools
- Chrome DevTools Performance tab
- Lighthouse for performance audits
- Bundle analyzer: `npm run analyze`

#### Backend Debugging
- FastAPI automatic docs: `/docs`
- Database query logging
- APM tools (New Relic, Datadog)
- Custom logging with structured output

---

## 📚 Additional Resources

### Development Tools
- [VS Code Extensions](https://marketplace.visualstudio.com/search?term=react%20typescript&target=VSCode)
- [Chrome DevTools Guide](https://developers.google.com/web/tools/chrome-devtools)
- [React DevTools](https://react.dev/learn/react-developer-tools)

### Learning Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)

### Community
- [GitHub Discussions](https://github.com/yourusername/miraikakaku/discussions)
- [Development Chat](https://discord.gg/miraikakaku-dev)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/miraikakaku)

---

**Happy coding! 🎉**

*This guide is continuously updated. Please contribute improvements and report issues.*