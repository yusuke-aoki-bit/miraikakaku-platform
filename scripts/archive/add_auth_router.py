#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add auth router import to api_predictions.py
"""

# Read api_predictions.py
with open('api_predictions.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with 'if __name__ == "__main__":'
insert_index = None
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        insert_index = i
        break

if insert_index is not None:
    # Insert auth router import before if __name__ block
    new_lines = (
        lines[:insert_index] +
        ['\n', '# ============================================\n',
         '# Include Authentication Router\n',
         '# ============================================\n',
         'from auth_endpoints import router as auth_router\n',
         'app.include_router(auth_router)\n', '\n'] +
        lines[insert_index:]
    )

    # Write back to file
    with open('api_predictions.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✅ Auth router added at line {insert_index}")
    print("✅ api_predictions.py updated successfully")
else:
    print("❌ Could not find 'if __name__' block")
    exit(1)
