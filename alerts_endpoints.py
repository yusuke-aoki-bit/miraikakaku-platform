"""
Price Alerts API Endpoints
Allows users to set price alerts for stocks
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
from auth_utils import get_current_active_user
import os

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5433),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Miraikakaku2024!"),
        database=os.getenv("POSTGRES_DB", "miraikakaku"),
    )

# Enums
class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PERCENT_UP = "price_change_percent_up"
    PRICE_CHANGE_PERCENT_DOWN = "price_change_percent_down"
    PREDICTION_UP = "prediction_up"
    PREDICTION_DOWN = "prediction_down"

# Models
class AlertCreateRequest(BaseModel):
    symbol: str
    alert_type: AlertType
    threshold: float
    notes: Optional[str] = None

class AlertUpdateRequest(BaseModel):
    threshold: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class Alert(BaseModel):
    id: int
    symbol: str
    alert_type: AlertType
    threshold: float
    is_active: bool
    triggered_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

class AlertWithDetails(BaseModel):
    id: int
    symbol: str
    company_name: str
    alert_type: AlertType
    threshold: float
    current_price: Optional[float]
    is_triggered: bool
    is_active: bool
    triggered_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

@router.get("", response_model=List[Alert])
def get_alerts(
    active_only: bool = True,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's price alerts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, symbol, alert_type, threshold, is_active,
                   triggered_at, notes, created_at
            FROM price_alerts
            WHERE user_id = %s
        """

        if active_only:
            query += " AND is_active = true"

        query += " ORDER BY created_at DESC"

        cursor.execute(query, (current_user["user_id"],))
        alerts = cursor.fetchall()
        cursor.close()
        conn.close()

        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.get("/details", response_model=List[AlertWithDetails])
def get_alerts_with_details(
    active_only: bool = True,
    current_user: dict = Depends(get_current_active_user)
):
    """Get alerts with stock details and trigger status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                a.id, a.symbol, a.alert_type, a.threshold, a.is_active,
                a.triggered_at, a.notes, a.created_at,
                sm.company_name,
                sp.close_price as current_price,
                CASE
                    WHEN a.triggered_at IS NOT NULL THEN true
                    ELSE false
                END as is_triggered
            FROM price_alerts a
            JOIN stock_master sm ON a.symbol = sm.symbol
            LEFT JOIN LATERAL (
                SELECT close_price
                FROM stock_prices
                WHERE symbol = a.symbol
                ORDER BY date DESC
                LIMIT 1
            ) sp ON true
            WHERE a.user_id = %s
        """

        if active_only:
            query += " AND a.is_active = true"

        query += " ORDER BY a.created_at DESC"

        cursor.execute(query, (current_user["user_id"],))
        alerts = cursor.fetchall()
        cursor.close()
        conn.close()

        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alert details: {str(e)}")

@router.post("", status_code=status.HTTP_201_CREATED)
def create_alert(
    request: AlertCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new price alert"""
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
            INSERT INTO price_alerts (user_id, symbol, alert_type, threshold, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (current_user["user_id"], request.symbol, request.alert_type,
              request.threshold, request.notes))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Alert created", "id": result[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.put("/{alert_id}")
def update_alert(
    alert_id: int,
    request: AlertUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Update an existing alert"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        updates = []
        params = []

        if request.threshold is not None:
            updates.append("threshold = %s")
            params.append(request.threshold)
        if request.is_active is not None:
            updates.append("is_active = %s")
            params.append(request.is_active)
        if request.notes is not None:
            updates.append("notes = %s")
            params.append(request.notes)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Reset triggered_at if reactivating
        if request.is_active is True:
            updates.append("triggered_at = NULL")

        params.extend([current_user["user_id"], alert_id])

        query = f"""
            UPDATE price_alerts
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
            return {"message": "Alert updated"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")

@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete an alert"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM price_alerts
            WHERE user_id = %s AND id = %s
            RETURNING id
        """, (current_user["user_id"], alert_id))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return {"message": "Alert deleted"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

@router.get("/triggered", response_model=List[AlertWithDetails])
def get_triggered_alerts(current_user: dict = Depends(get_current_active_user)):
    """Get alerts that have been triggered"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                a.id, a.symbol, a.alert_type, a.threshold, a.is_active,
                a.triggered_at, a.notes, a.created_at,
                sm.company_name,
                sp.close_price as current_price,
                true as is_triggered
            FROM price_alerts a
            JOIN stock_master sm ON a.symbol = sm.symbol
            LEFT JOIN LATERAL (
                SELECT close_price
                FROM stock_prices
                WHERE symbol = a.symbol
                ORDER BY date DESC
                LIMIT 1
            ) sp ON true
            WHERE a.user_id = %s AND a.triggered_at IS NOT NULL
            ORDER BY a.triggered_at DESC
        """, (current_user["user_id"],))

        alerts = cursor.fetchall()
        cursor.close()
        conn.close()

        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch triggered alerts: {str(e)}")

@router.post("/check")
def check_alerts_manual(current_user: dict = Depends(get_current_active_user)):
    """Manually trigger alert checking (for testing)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get all active alerts for this user
        cursor.execute("""
            SELECT a.id, a.symbol, a.alert_type, a.threshold,
                   sp.close_price as current_price,
                   sp.price_change_percent
            FROM price_alerts a
            LEFT JOIN LATERAL (
                SELECT close_price, price_change_percent
                FROM stock_prices
                WHERE symbol = a.symbol
                ORDER BY date DESC
                LIMIT 1
            ) sp ON true
            WHERE a.user_id = %s AND a.is_active = true AND a.triggered_at IS NULL
        """, (current_user["user_id"],))

        alerts = cursor.fetchall()
        triggered_count = 0

        for alert in alerts:
            should_trigger = False

            if alert['current_price'] is None:
                continue

            # Check trigger conditions
            if alert['alert_type'] == 'price_above' and alert['current_price'] >= alert['threshold']:
                should_trigger = True
            elif alert['alert_type'] == 'price_below' and alert['current_price'] <= alert['threshold']:
                should_trigger = True
            elif alert['alert_type'] == 'price_change_percent_up' and alert['price_change_percent'] and alert['price_change_percent'] >= alert['threshold']:
                should_trigger = True
            elif alert['alert_type'] == 'price_change_percent_down' and alert['price_change_percent'] and alert['price_change_percent'] <= -alert['threshold']:
                should_trigger = True

            if should_trigger:
                cursor.execute("""
                    UPDATE price_alerts
                    SET triggered_at = CURRENT_TIMESTAMP, is_active = false
                    WHERE id = %s
                """, (alert['id'],))
                triggered_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": f"Checked alerts", "triggered_count": triggered_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check alerts: {str(e)}")
