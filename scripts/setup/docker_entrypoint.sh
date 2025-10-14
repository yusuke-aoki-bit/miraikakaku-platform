#!/bin/bash
set -e

echo "=========================================="
echo "Miraikakaku Sector/Industry Data Setup"
echo "=========================================="

# Step 1: Add columns
echo ""
echo "Step 1: Adding sector and industry columns..."
python add_sector_columns.py

if [ $? -eq 0 ]; then
    echo "✓ Columns added successfully"
else
    echo "❌ Failed to add columns"
    exit 1
fi

# Step 2: Fetch sector/industry data
echo ""
echo "Step 2: Fetching sector and industry data for all stocks..."
echo "This will take 30-60 minutes for ~3,756 stocks..."
python fetch_sector_industry_data.py

if [ $? -eq 0 ]; then
    echo "✓ Data collection complete"
else
    echo "❌ Data collection failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
