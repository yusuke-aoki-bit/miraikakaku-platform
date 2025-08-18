# Miraikakaku (未来価格) - Financial Analysis & Stock Price Prediction Platform

Miraikakaku is a comprehensive, full-stack platform for financial analysis and stock price prediction. It leverages a modern technology stack, including Next.js, FastAPI, and Google Cloud Vertex AI, to deliver real-time data, AI-powered insights, and a rich user experience.

The entire application is containerized with Docker, providing a consistent and reproducible development environment.

## 🏛️ System Architecture

The project is structured as a monorepo containing several distinct services:

-   **`miraikakakufront`**: A **Next.js 15** frontend with React 19, TypeScript, and Tailwind CSS. It provides the user interface, data visualizations, and interactive charts.
-   **`miraikakakuapi`**: A **FastAPI** backend that serves as the core API. It handles business logic, user authentication, data retrieval, and serves machine learning model predictions.
-   **`miraikakakubatch`**: A dedicated Python service for offline batch processing. It handles periodic data ingestion from financial APIs (like yfinance) and triggers ML model training pipelines.
-   **`nginx`**: An Nginx reverse proxy that routes traffic to the frontend and API services.
-   **`monitoring`**: A **Prometheus** and **Grafana** stack for collecting metrics and visualizing system health.

### Core Technologies

-   **Frontend**: Next.js, React, TypeScript, Tailwind CSS, Chart.js, Zustand
-   **Backend**: FastAPI, Python, SQLAlchemy
-   **Database**: MySQL 8.0
-   **Caching**: Redis
-   **Machine Learning**: Google Cloud Vertex AI, TensorFlow, scikit-learn
-   **Infrastructure**: Docker, Docker Compose, Google Cloud Platform (GCP)

## 🚀 Getting Started

Follow these steps to set up and run the development environment locally.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
-   [Node.js](https://nodejs.org/en/) (v18 or later)
-   [Python](https://www.python.org/downloads/) (v3.9 or later)
-   A code editor (e.g., VS Code)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd miraikakaku
```

### 2. Set Up Environment Variables

The project uses `.env` files for configuration. Start by copying the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and customize the variables as needed. You will need to provide credentials for:

-   `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`
-   `JWT_SECRET_KEY` (generate a long, random string)
-   Google Cloud credentials (`VERTEX_AI_PROJECT_ID`, etc.) if you intend to connect to GCP services.

### 3. Build and Start the Containers

The simplest way to get started is to use Docker Compose, which will build the images and start all the services defined in `docker-compose.yml`.

```bash
docker-compose up --build -d
```

-   `--build`: Forces a rebuild of the Docker images. Use this the first time you start the application or if you make changes to the Dockerfiles.
-   `-d`: Runs the containers in detached mode (in the background).

### 4. Accessing the Services

Once the containers are running, you can access the different parts of the application:

-   **Frontend Application**: [http://localhost:3000](http://localhost:3000)
-   **FastAPI Backend (Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Grafana Dashboard**: [http://localhost:3001](http://localhost:3001)
-   **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)

The database (MySQL) will be running on port `3306` and Redis on port `6379`.

### 5. Running Batch Processes

To run a batch process manually (e.g., to ingest the latest stock data), you can execute a command inside the running `batch` container:

```bash
docker-compose exec miraikakaku-batch python functions/main.py --task data_pipeline
```
*(Note: The exact command might differ based on the implementation in `main.py`)*

### 6. Stopping the Environment

To stop all running containers, use:

```bash
docker-compose down
```

## 🧪 Testing

The project includes a testing suite. Refer to the `REPRODUCIBLE_SYSTEM_DESIGN.md` document for detailed information on running the Jest, Playwright, and Pytest tests for each service.

## 📄 Documentation

For a complete and in-depth overview of the system architecture, data models, API endpoints, and deployment strategy, please refer to the **[Reproducible System Design Document](docs/REPRODUCIBLE_SYSTEM_DESIGN.md)**.
