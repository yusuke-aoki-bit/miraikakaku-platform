#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add auth schema admin endpoint to api_predictions.py
"""

# Read api_predictions.py
with open('api_predictions.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with '# Phase 5-1: Portfolio Management API Endpoints'
insert_index = None
for i, line in enumerate(lines):
    if '# Phase 5-1: Portfolio Management API Endpoints' in line:
        insert_index = i
        break

if insert_index is not None:
    # Auth schema endpoint code
    auth_endpoint_code = '''# ============================================
# Phase 6: Authentication API Admin Endpoints
# ============================================

@app.post("/admin/apply-auth-schema")
def apply_auth_schema():
    """Phase 6: Apply authentication database schema"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Read schema file
        import os
        schema_path = os.path.join(os.path.dirname(__file__), 'create_auth_schema.sql')

        if not os.path.exists(schema_path):
            return {"status": "error", "message": f"Schema file not found: {schema_path}"}

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        cur.execute(schema_sql)
        conn.commit()

        # Verify tables created
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'user_sessions')
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "Authentication schema applied successfully",
            "tables_created": tables
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

'''

    # Insert before Phase 5-1 section
    new_lines = (
        lines[:insert_index] +
        [auth_endpoint_code] +
        lines[insert_index:]
    )

    # Write back to file
    with open('api_predictions.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✅ Auth schema endpoint added at line {insert_index}")
    print("✅ api_predictions.py updated successfully")
else:
    print("❌ Could not find 'Phase 5-1: Portfolio Management' section")
    exit(1)
