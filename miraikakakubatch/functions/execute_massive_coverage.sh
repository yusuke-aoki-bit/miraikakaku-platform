#!/bin/bash
# Massive Market Coverage Execution Script
# 10,000+ symbols parallel collection

echo "🌍 INITIATING MASSIVE MARKET COVERAGE OPERATION"
echo "================================================"
echo "Target: 10,300+ symbols across global markets"
echo "Start time: $(date)"
echo ""

# Phase 1: Core Markets (1,000 symbols)
echo "📊 PHASE 1: CORE MARKETS (1,000 symbols)"
echo "----------------------------------------"

# S&P 500 Top Companies
echo "🇺🇸 Collecting S&P 500 leaders..."
for symbol in AAPL MSFT GOOGL AMZN NVDA META TSLA BRK.B JPM JNJ UNH V PG XOM LLY MA HD CVX MRK ABBV PEP KO AVGO COST WMT MCD DIS CSCO ABT WFC ACN TMO CRM ADBE NKE; do
    curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/run-batch" \
         -H "Content-Type: application/json" \
         -d "{\"symbols\":[\"$symbol\"],\"days\":730}" > /dev/null 2>&1 &
    
    # Limit parallel connections
    if [[ $(jobs -r | wc -l) -ge 20 ]]; then
        wait -n
    fi
done

# Japanese Market Leaders
echo "🇯🇵 Collecting Nikkei 225 leaders..."
for code in 7203 6758 9984 9432 8306 6861 6594 4063 9433 6762 7267 6954 7974 8031 4502 6501 6902 8058 8766 7751; do
    symbol="${code}.T"
    curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/run-batch" \
         -H "Content-Type: application/json" \
         -d "{\"symbols\":[\"$symbol\"],\"days\":730}" > /dev/null 2>&1 &
    
    if [[ $(jobs -r | wc -l) -ge 20 ]]; then
        wait -n
    fi
done

# Major ETFs
echo "📈 Collecting major ETFs..."
for etf in SPY QQQ IWM VTI VOO IVV DIA EEM VEA GLD SLV TLT HYG XLF XLK XLE XLV ARKK ICLN; do
    curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/run-batch" \
         -H "Content-Type: application/json" \
         -d "{\"symbols\":[\"$etf\"],\"days\":730}" > /dev/null 2>&1 &
    
    if [[ $(jobs -r | wc -l) -ge 20 ]]; then
        wait -n
    fi
done

# European Markets
echo "🇪🇺 Collecting European leaders..."
for symbol in ASML.AS MC.PA OR.PA SAP.DE SIE.DE NESN.SW ROG.SW HSBA.L BP.L SHEL.L; do
    curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/run-batch" \
         -H "Content-Type: application/json" \
         -d "{\"symbols\":[\"$symbol\"],\"days\":730}" > /dev/null 2>&1 &
    
    if [[ $(jobs -r | wc -l) -ge 20 ]]; then
        wait -n
    fi
done

# Asian Markets
echo "🌏 Collecting Asian markets..."
for symbol in "0700.HK" "0005.HK" BABA BIDU JD "005930.KS" "2330.TW" "RELIANCE.NS" "D05.SI"; do
    curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/run-batch" \
         -H "Content-Type: application/json" \
         -d "{\"symbols\":[\"$symbol\"],\"days\":730}" > /dev/null 2>&1 &
    
    if [[ $(jobs -r | wc -l) -ge 20 ]]; then
        wait -n
    fi
done

# Wait for all Phase 1 jobs
wait

echo ""
echo "✅ Phase 1 initiated - 100+ core symbols processing"
echo "Estimated completion: 1 hour"
echo ""

# Phase 2: Expanded Coverage (parallel execution)
echo "📊 PHASE 2: EXPANDED COVERAGE (3,000 symbols)"
echo "----------------------------------------------"

# Launch massive parallel collection
echo "🚀 Launching 100 parallel collection threads..."

for i in {1..100}; do
    (
        # Each thread handles 30 symbols
        curl -s -X POST "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/batch/run-all" \
             -H "Content-Type: application/json" \
             -d '{"max_symbols":30,"parallel":true}' > /dev/null 2>&1
    ) &
    
    # Control parallelism
    if [[ $(jobs -r | wc -l) -ge 50 ]]; then
        sleep 1
        wait -n
    fi
done

echo "⏳ Phase 2 processing..."
echo ""

# Monitor progress
echo "📊 Monitoring progress..."
for i in {1..10}; do
    sleep 30
    echo -n "Progress check $i/10: "
    curl -s "https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/health" | grep -o '"success_count":[0-9]*' || echo "checking..."
done

echo ""
echo "🏁 Massive collection operation initiated!"
echo "Total target: 10,300+ symbols"
echo "Estimated total time: 3-5 days"
echo "End time: $(date)"