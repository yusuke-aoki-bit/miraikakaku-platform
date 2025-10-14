"""
Portfolio Management API Endpoints
Allows users to track stock holdings and performance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from auth_utils import get_current_active_user
import os

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5433),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Miraikakaku2024!"),
        database=os.getenv("POSTGRES_DB", "miraikakaku"),
    )

# Models
class PortfolioAddRequest(BaseModel):
    symbol: str
    quantity: float
    average_buy_price: float
    buy_date: date
    notes: Optional[str] = None

class PortfolioUpdateRequest(BaseModel):
    quantity: Optional[float] = None
    average_buy_price: Optional[float] = None
    notes: Optional[str] = None

class PortfolioItem(BaseModel):
    id: int
    symbol: str
    quantity: float
    average_buy_price: float
    buy_date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class PortfolioWithPerformance(BaseModel):
    id: int
    symbol: str
    company_name: str
    quantity: float
    average_buy_price: float
    current_price: Optional[float]
    market_value: Optional[float]
    cost_basis: float
    unrealized_gain_loss: Optional[float]
    unrealized_gain_loss_percent: Optional[float]
    buy_date: date
    notes: Optional[str]

class PortfolioSummary(BaseModel):
    total_cost_basis: float
    total_market_value: float
    total_unrealized_gain_loss: float
    total_unrealized_gain_loss_percent: float
    holdings_count: int
    best_performer: Optional[dict]
    worst_performer: Optional[dict]

@router.get("", response_model=List[PortfolioItem])
def get_portfolio(current_user: dict = Depends(get_current_active_user)):
    """Get user's portfolio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, symbol, quantity, average_buy_price, buy_date,
                   notes, created_at, updated_at
            FROM user_portfolios
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (current_user["user_id"],))

        portfolio = cursor.fetchall()
        cursor.close()
        conn.close()

        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")

@router.get("/performance", response_model=List[PortfolioWithPerformance])
def get_portfolio_performance(current_user: dict = Depends(get_current_active_user)):
    """Get portfolio with performance metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                p.id, p.symbol, p.quantity, p.average_buy_price, p.buy_date, p.notes,
                sm.company_name,
                sp.close_price as current_price,
                (p.quantity * sp.close_price) as market_value,
                (p.quantity * p.average_buy_price) as cost_basis,
                ((sp.close_price - p.average_buy_price) * p.quantity) as unrealized_gain_loss,
                (((sp.close_price - p.average_buy_price) / p.average_buy_price) * 100) as unrealized_gain_loss_percent
            FROM user_portfolios p
            JOIN stock_master sm ON p.symbol = sm.symbol
            LEFT JOIN LATERAL (
                SELECT close_price
                FROM stock_prices
                WHERE symbol = p.symbol
                ORDER BY date DESC
                LIMIT 1
            ) sp ON true
            WHERE p.user_id = %s
            ORDER BY unrealized_gain_loss_percent DESC NULLS LAST
        """, (current_user["user_id"],))

        portfolio = cursor.fetchall()
        cursor.close()
        conn.close()

        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio performance: {str(e)}")

@router.get("/summary", response_model=PortfolioSummary)
def get_portfolio_summary(current_user: dict = Depends(get_current_active_user)):
    """Get portfolio summary with aggregated metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            WITH portfolio_data AS (
                SELECT
                    p.symbol,
                    p.quantity,
                    p.average_buy_price,
                    sp.close_price as current_price,
                    (p.quantity * p.average_buy_price) as cost_basis,
                    (p.quantity * sp.close_price) as market_value,
                    ((sp.close_price - p.average_buy_price) * p.quantity) as gain_loss,
                    (((sp.close_price - p.average_buy_price) / p.average_buy_price) * 100) as gain_loss_percent
                FROM user_portfolios p
                LEFT JOIN LATERAL (
                    SELECT close_price
                    FROM stock_prices
                    WHERE symbol = p.symbol
                    ORDER BY date DESC
                    LIMIT 1
                ) sp ON true
                WHERE p.user_id = %s
            )
            SELECT
                COALESCE(SUM(cost_basis), 0) as total_cost_basis,
                COALESCE(SUM(market_value), 0) as total_market_value,
                COALESCE(SUM(gain_loss), 0) as total_unrealized_gain_loss,
                CASE
                    WHEN SUM(cost_basis) > 0
                    THEN ((SUM(market_value) - SUM(cost_basis)) / SUM(cost_basis) * 100)
                    ELSE 0
                END as total_unrealized_gain_loss_percent,
                COUNT(*) as holdings_count
            FROM portfolio_data
        """, (current_user["user_id"],))

        summary = cursor.fetchone()

        # Get best and worst performers
        cursor.execute("""
            SELECT symbol,
                   (((sp.close_price - p.average_buy_price) / p.average_buy_price) * 100) as gain_loss_percent
            FROM user_portfolios p
            LEFT JOIN LATERAL (
                SELECT close_price FROM stock_prices
                WHERE symbol = p.symbol ORDER BY date DESC LIMIT 1
            ) sp ON true
            WHERE p.user_id = %s AND sp.close_price IS NOT NULL
            ORDER BY gain_loss_percent DESC
            LIMIT 1
        """, (current_user["user_id"],))
        best = cursor.fetchone()

        cursor.execute("""
            SELECT symbol,
                   (((sp.close_price - p.average_buy_price) / p.average_buy_price) * 100) as gain_loss_percent
            FROM user_portfolios p
            LEFT JOIN LATERAL (
                SELECT close_price FROM stock_prices
                WHERE symbol = p.symbol ORDER BY date DESC LIMIT 1
            ) sp ON true
            WHERE p.user_id = %s AND sp.close_price IS NOT NULL
            ORDER BY gain_loss_percent ASC
            LIMIT 1
        """, (current_user["user_id"],))
        worst = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            **summary,
            "best_performer": dict(best) if best else None,
            "worst_performer": dict(worst) if worst else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio summary: {str(e)}")

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_portfolio(request: PortfolioAddRequest, current_user: dict = Depends(get_current_active_user)):
    """Add a holding to portfolio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if symbol exists
        cursor.execute("SELECT symbol FROM stock_master WHERE symbol = %s", (request.symbol,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Stock symbol {request.symbol} not found")

        cursor.execute("""
            INSERT INTO user_portfolios (user_id, symbol, quantity, average_buy_price, buy_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (current_user["user_id"], request.symbol, request.quantity,
              request.average_buy_price, request.buy_date, request.notes))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Added to portfolio", "id": result[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to portfolio: {str(e)}")

@router.put("/{portfolio_id}")
def update_portfolio_item(portfolio_id: int, request: PortfolioUpdateRequest,
                          current_user: dict = Depends(get_current_active_user)):
    """Update a portfolio item"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        updates = []
        params = []
        if request.quantity is not None:
            updates.append("quantity = %s")
            params.append(request.quantity)
        if request.average_buy_price is not None:
            updates.append("average_buy_price = %s")
            params.append(request.average_buy_price)
        if request.notes is not None:
            updates.append("notes = %s")
            params.append(request.notes)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([current_user["user_id"], portfolio_id])

        query = f"""
            UPDATE user_portfolios
            SET {', '.join(updates)}
            WHERE user_id = %s AND id = %s
            RETURNING id
        """

        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Portfolio updated"}
        else:
            raise HTTPException(status_code=404, detail="Portfolio item not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update portfolio: {str(e)}")

@router.delete("/{portfolio_id}")
def delete_from_portfolio(portfolio_id: int, current_user: dict = Depends(get_current_active_user)):
    """Remove a holding from portfolio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM user_portfolios
            WHERE user_id = %s AND id = %s
            RETURNING id
        """, (current_user["user_id"], portfolio_id))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Removed from portfolio"}
        else:
            raise HTTPException(status_code=404, detail="Portfolio item not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from portfolio: {str(e)}")
