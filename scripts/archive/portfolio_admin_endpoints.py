"""
Portfolio Management Admin Endpoints
Phase 5-1: Database Schema Management and Diagnostics
"""

# これらのエンドポイントをapi_predictions.pyに追加してください

# ============================================================
# Debug/Admin Endpoints for Portfolio Schema Management
# ============================================================

@app.get("/admin/check-portfolio-schema")
def check_portfolio_schema():
    """Check current portfolio database schema structure"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if portfolio_holdings table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'portfolio_holdings'
            )
        """)
        table_exists = cur.fetchone()['exists']

        if not table_exists:
            return {
                "status": "info",
                "message": "portfolio_holdings table does not exist",
                "table_exists": False
            }

        # Get column information
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'portfolio_holdings'
            ORDER BY ordinal_position
        """)
        columns = [dict(row) for row in cur.fetchall()]

        # Get views
        cur.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name LIKE '%portfolio%'
            ORDER BY table_name
        """)
        views = [row['table_name'] for row in cur.fetchall()]

        # Get functions
        cur.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name LIKE '%portfolio%'
            ORDER BY routine_name
        """)
        functions = [row['routine_name'] for row in cur.fetchall()]

        # Check row count
        cur.execute("SELECT COUNT(*) as count FROM portfolio_holdings")
        row_count = cur.fetchone()['count']

        cur.close()
        conn.close()

        return {
            "status": "success",
            "table_exists": True,
            "columns": columns,
            "views": views,
            "functions": functions,
            "row_count": row_count,
            "user_id_exists": any(col['column_name'] == 'user_id' for col in columns)
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/fix-portfolio-schema")
def fix_portfolio_schema():
    """Fix portfolio schema by adding missing user_id column and creating views/functions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Step 1: Add user_id column if it doesn't exist
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'portfolio_holdings'
                    AND column_name = 'user_id'
                ) THEN
                    ALTER TABLE portfolio_holdings ADD COLUMN user_id VARCHAR(255);
                    UPDATE portfolio_holdings SET user_id = 'demo_user' WHERE user_id IS NULL;
                    ALTER TABLE portfolio_holdings ALTER COLUMN user_id SET NOT NULL;
                END IF;
            END $$;
        """)
        conn.commit()

        # Step 2: Read and apply views/functions schema
        import os
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_portfolio_views_only.sql')

        if not os.path.exists(schema_path):
            return {"status": "error", "message": f"Schema file not found: {schema_path}"}

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute views and functions creation
        cur.execute(schema_sql)
        conn.commit()

        # Verify
        cur.execute("""
            SELECT table_name FROM information_schema.views
            WHERE table_schema = 'public' AND table_name LIKE '%portfolio%'
        """)
        views = [row[0] for row in cur.fetchall()]

        cur.execute("""
            SELECT routine_name FROM information_schema.routines
            WHERE routine_schema = 'public' AND routine_name LIKE '%portfolio%'
        """)
        functions = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "Portfolio schema fixed successfully",
            "user_id_added": True,
            "views_created": views,
            "functions_created": functions
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
