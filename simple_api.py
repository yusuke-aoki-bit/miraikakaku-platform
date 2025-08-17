from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Miraikakaku API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Miraikakaku API Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "miraikakaku-api"}

@app.get("/api/finance/stocks")
async def get_stocks():
    return {
        "stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "price": 150.25},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 2800.50},
            {"symbol": "MSFT", "name": "Microsoft Corp.", "price": 380.75}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)