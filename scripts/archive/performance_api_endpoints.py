# ============================================================
# Phase 5-3: Performance Analysis API Endpoints
# ============================================================

# Add these endpoints to api_predictions.py

@app.post("/admin/apply-performance-schema")
def apply_performance_schema():
    """Apply performance analysis schema to database"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        schema_file = "create_performance_schema.sql"
        if not os.path.exists(schema_file):
            return {"status": "error", "message": f"Schema file not found: {os.path.abspath(schema_file)}"}

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cur.execute(schema_sql)
        conn.commit()

        # Verify views created
        cur.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name IN ('v_portfolio_performance', 'v_portfolio_sector_allocation', 'v_daily_portfolio_value')
        """)
        views = [row[0] for row in cur.fetchall()]

        return {
            "status": "success",
            "message": "Performance analysis schema applied successfully",
            "views_created": views
        }
    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        cur.close()
        conn.close()

@app.get("/api/portfolio/performance")
def get_portfolio_performance(user_id: str):
    """Get current performance metrics for all portfolio holdings"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                id, symbol, company_name, exchange, sector,
                quantity, purchase_price, purchase_date,
                current_price, price_date,
                cost_basis, current_value, unrealized_pl, return_pct,
                days_held, annualized_return_pct,
                predicted_price, ensemble_confidence, predicted_change_pct,
                notes
            FROM v_portfolio_performance
            WHERE user_id = %s
            ORDER BY current_value DESC
        """, (user_id,))

        holdings = cur.fetchall()

        # Calculate summary statistics
        total_cost = sum(h['cost_basis'] or 0 for h in holdings)
        total_value = sum(h['current_value'] or 0 for h in holdings)
        total_pl = sum(h['unrealized_pl'] or 0 for h in holdings)
        total_return_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0

        return {
            "holdings": holdings,
            "summary": {
                "total_holdings": len(holdings),
                "total_cost_basis": float(total_cost),
                "total_current_value": float(total_value),
                "total_unrealized_pl": float(total_pl),
                "total_return_pct": float(total_return_pct)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/portfolio/sector-allocation")
def get_sector_allocation(user_id: str):
    """Get portfolio allocation by sector"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                sector,
                holdings_count,
                total_cost_basis,
                total_current_value,
                total_unrealized_pl,
                sector_return_pct,
                sector_value
            FROM v_portfolio_sector_allocation
            WHERE user_id = %s
            ORDER BY total_current_value DESC
        """, (user_id,))

        sectors = cur.fetchall()

        # Calculate allocation percentages
        total_value = sum(s['sector_value'] or 0 for s in sectors)
        for sector in sectors:
            sector['allocation_pct'] = (sector['sector_value'] / total_value * 100) if total_value > 0 else 0

        return {
            "sectors": sectors,
            "total_portfolio_value": float(total_value)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/portfolio/history")
def get_portfolio_history(user_id: str, days: int = 30):
    """Get historical portfolio value over time"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                date,
                total_value,
                total_cost_basis,
                unrealized_pl,
                total_return_pct
            FROM v_daily_portfolio_value
            WHERE user_id = %s
              AND date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date ASC
        """, (user_id, days))

        history = cur.fetchall()

        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/portfolio/analytics")
def get_portfolio_analytics(user_id: str, period_days: int = 30):
    """Get advanced portfolio analytics - returns, volatility, Sharpe ratio"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        start_date = datetime.now().date() - timedelta(days=period_days)
        end_date = datetime.now().date()

        # Calculate portfolio returns
        cur.execute("""
            SELECT * FROM calculate_portfolio_returns(%s, %s, %s)
        """, (user_id, start_date, end_date))

        returns_data = cur.fetchone()

        # Calculate Sharpe ratio
        cur.execute("""
            SELECT calculate_sharpe_ratio(%s, %s, %s) as sharpe_ratio
        """, (user_id, start_date, end_date))

        sharpe_data = cur.fetchone()

        # Get daily volatility
        cur.execute("""
            WITH daily_returns AS (
                SELECT
                    date,
                    total_value,
                    LAG(total_value) OVER (ORDER BY date) as prev_value,
                    CASE
                        WHEN LAG(total_value) OVER (ORDER BY date) > 0 THEN
                            (total_value - LAG(total_value) OVER (ORDER BY date)) / LAG(total_value) OVER (ORDER BY date)
                        ELSE 0
                    END as daily_return
                FROM v_daily_portfolio_value
                WHERE user_id = %s
                  AND date BETWEEN %s AND %s
            )
            SELECT
                STDDEV(daily_return) * SQRT(252) as annualized_volatility,
                AVG(daily_return) * 252 as annualized_return,
                MAX(daily_return) as best_day,
                MIN(daily_return) as worst_day
            FROM daily_returns
            WHERE prev_value IS NOT NULL
        """, (user_id, start_date, end_date))

        volatility_data = cur.fetchone()

        return {
            "period_days": period_days,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "returns": {
                "total_return": float(returns_data['total_return'] or 0) if returns_data else 0,
                "return_pct": float(returns_data['return_pct'] or 0) if returns_data else 0,
                "start_value": float(returns_data['start_value'] or 0) if returns_data else 0,
                "end_value": float(returns_data['end_value'] or 0) if returns_data else 0
            },
            "risk_metrics": {
                "sharpe_ratio": float(sharpe_data['sharpe_ratio'] or 0) if sharpe_data else 0,
                "annualized_volatility": float(volatility_data['annualized_volatility'] or 0) if volatility_data else 0,
                "annualized_return": float(volatility_data['annualized_return'] or 0) if volatility_data else 0,
                "best_day_return": float(volatility_data['best_day'] or 0) if volatility_data else 0,
                "worst_day_return": float(volatility_data['worst_day'] or 0) if volatility_data else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
