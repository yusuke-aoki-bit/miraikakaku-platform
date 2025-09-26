# System Architecture

## Overview
MiraiKakaku is a distributed AI-powered stock prediction system with the following architecture:

```
Frontend (Next.js) ← API (FastAPI) ← Database (PostgreSQL)
                         ↓
                   Batch System (GCP Batch)
                         ↓
                   AI/ML Services (Vertex AI)
```

## Components

### 1. Frontend (`miraikakakufront/`)
- **Technology**: Next.js, React, TypeScript, Tailwind CSS
- **Purpose**: User interface and data visualization
- **Key Features**: Real-time charts, stock search, prediction display

### 2. API Server (`miraikakakuapi/`)
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL
- **Purpose**: REST API and real-time data services
- **Key Features**: Stock data API, dual prediction system, authentication

### 3. Batch Processing (`miraikakakubatch/`)
- **Technology**: Python, GCP Batch, Cloud Functions
- **Purpose**: Data collection and AI model processing
- **Key Features**: Scheduled data updates, ML model training, bulk processing

### 4. Shared Components (`shared/`)
- **Purpose**: Common utilities and database models
- **Contents**: Unified database models, utility functions, configuration helpers

### 5. Configuration (`config/`)
- **Purpose**: Centralized configuration management
- **Contents**: Environment templates, deployment configurations

## Data Flow

1. **Data Collection**: Batch system collects stock data from external APIs
2. **Data Storage**: Raw data stored in PostgreSQL database
3. **AI Processing**: ML models generate predictions using collected data
4. **API Serving**: FastAPI serves data and predictions to frontend
5. **User Interface**: Next.js frontend displays data and predictions

## Security Architecture

- Environment variables for all sensitive data
- JWT-based authentication
- Database connection pooling
- Rate limiting and input validation
- HTTPS encryption in production

## Deployment Architecture

- **Frontend**: Vercel/Netlify static deployment
- **API**: Google Cloud Run containerized deployment
- **Batch**: GCP Batch jobs for processing
- **Database**: Google Cloud SQL PostgreSQL instance
- **Monitoring**: Cloud Logging and monitoring integration