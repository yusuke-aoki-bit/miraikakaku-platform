"""
Watchlist API Endpoints for Miraikakaku
Allows users to save and manage favorite stocks
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from auth_utils import get_current_active_user
import os

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5433),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Miraikakaku2024!"),
        database=os.getenv("POSTGRES_DB", "miraikakaku"),
    )

# Models
class WatchlistAddRequest(BaseModel):
    symbol: str
    notes: Optional[str] = None

class WatchlistItem(BaseModel):
    id: int
    symbol: str
    added_at: datetime
    notes: Optional[str]

class WatchlistWithDetails(BaseModel):
    id: int
    symbol: str
    company_name: str
    exchange: str
    current_price: Optional[float]
    price_change_percent: Optional[float]
    prediction: Optional[float]
    added_at: datetime
    notes: Optional[str]

@router.get("", response_model=List[WatchlistItem])
def get_watchlist(current_user: dict = Depends(get_current_active_user)):
    """Get user's watchlist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, symbol, added_at, notes
            FROM user_watchlists
            WHERE user_id = %s
            ORDER BY added_at DESC
        """, (current_user["user_id"],))

        watchlist = cursor.fetchall()
        cursor.close()
        conn.close()

        return watchlist
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist: {str(e)}"
        )

@router.get("/details", response_model=List[WatchlistWithDetails])
def get_watchlist_with_details(current_user: dict = Depends(get_current_active_user)):
    """Get watchlist with stock details (prices, predictions)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                w.id,
                w.symbol,
                w.added_at,
                w.notes,
                sm.company_name,
                sm.exchange,
                sp.close_price as current_price,
                sp.price_change_percent,
                ep.ensemble_prediction as prediction
            FROM user_watchlists w
            JOIN stock_master sm ON w.symbol = sm.symbol
            LEFT JOIN LATERAL (
                SELECT close_price, price_change_percent
                FROM stock_prices
                WHERE symbol = w.symbol
                ORDER BY date DESC
                LIMIT 1
            ) sp ON true
            LEFT JOIN LATERAL (
                SELECT ensemble_prediction
                FROM ensemble_predictions
                WHERE symbol = w.symbol
                  AND prediction_date = CURRENT_DATE
                ORDER BY prediction_date DESC
                LIMIT 1
            ) ep ON true
            WHERE w.user_id = %s
            ORDER BY w.added_at DESC
        """, (current_user["user_id"],))

        watchlist = cursor.fetchall()
        cursor.close()
        conn.close()

        return watchlist
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist details: {str(e)}"
        )

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    request: WatchlistAddRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Add a stock to watchlist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if symbol exists in stock_master
        cursor.execute(
            "SELECT symbol FROM stock_master WHERE symbol = %s",
            (request.symbol,)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock symbol {request.symbol} not found"
            )

        # Add to watchlist
        cursor.execute("""
            INSERT INTO user_watchlists (user_id, symbol, notes)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, symbol) DO NOTHING
            RETURNING id
        """, (current_user["user_id"], request.symbol, request.notes))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Added to watchlist", "id": result[0]}
        else:
            return {"message": "Already in watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to watchlist: {str(e)}"
        )

@router.delete("/{symbol}")
def remove_from_watchlist(
    symbol: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove a stock from watchlist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM user_watchlists
            WHERE user_id = %s AND symbol = %s
            RETURNING id
        """, (current_user["user_id"], symbol))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Removed from watchlist"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found in watchlist"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove from watchlist: {str(e)}"
        )

@router.put("/{symbol}")
def update_watchlist_notes(
    symbol: str,
    notes: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Update notes for a watchlist item"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_watchlists
            SET notes = %s
            WHERE user_id = %s AND symbol = %s
            RETURNING id
        """, (notes, current_user["user_id"], symbol))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Notes updated"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock not found in watchlist"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notes: {str(e)}"
        )
