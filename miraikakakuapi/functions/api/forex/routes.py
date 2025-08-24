# 為替・通貨関連API

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 主要通貨ペアの定義
MAJOR_CURRENCY_PAIRS = {
    'USDJPY': {'base': 'USD', 'quote': 'JPY', 'name': '米ドル/円', 'yahoo_symbol': 'USDJPY=X'},
    'EURUSD': {'base': 'EUR', 'quote': 'USD', 'name': 'ユーロ/米ドル', 'yahoo_symbol': 'EURUSD=X'},
    'GBPUSD': {'base': 'GBP', 'quote': 'USD', 'name': '英ポンド/米ドル', 'yahoo_symbol': 'GBPUSD=X'},
    'EURJPY': {'base': 'EUR', 'quote': 'JPY', 'name': 'ユーロ/円', 'yahoo_symbol': 'EURJPY=X'},
    'AUDUSD': {'base': 'AUD', 'quote': 'USD', 'name': '豪ドル/米ドル', 'yahoo_symbol': 'AUDUSD=X'},
    'USDCHF': {'base': 'USD', 'quote': 'CHF', 'name': '米ドル/スイスフラン', 'yahoo_symbol': 'USDCHF=X'},
    'USDCAD': {'base': 'USD', 'quote': 'CAD', 'name': '米ドル/カナダドル', 'yahoo_symbol': 'USDCAD=X'},
    'NZDUSD': {'base': 'NZD', 'quote': 'USD', 'name': 'NZドル/米ドル', 'yahoo_symbol': 'NZDUSD=X'},
}

@router.get("/currency-pairs")
async def get_currency_pairs():
    """利用可能な通貨ペア一覧を取得"""
    try:
        pairs = []
        for pair_code, info in MAJOR_CURRENCY_PAIRS.items():
            pairs.append({
                "pair": f"{info['base']}/{info['quote']}",
                "code": pair_code,
                "base": info['base'],
                "quote": info['quote'],
                "name": info['name']
            })
        
        return {
            "status": "success",
            "data": pairs,
            "count": len(pairs)
        }
    except Exception as e:
        logger.error(f"Error getting currency pairs: {str(e)}")
        raise HTTPException(status_code=500, detail="通貨ペア取得エラー")

@router.get("/currency-rate/{pair}")
async def get_currency_rate(pair: str):
    """特定通貨ペアの現在レートを取得"""
    try:
        # ペア名を正規化（USD/JPY -> USDJPY）
        normalized_pair = pair.replace('/', '').upper()
        
        if normalized_pair not in MAJOR_CURRENCY_PAIRS:
            raise HTTPException(status_code=404, detail="指定された通貨ペアは対応していません")
        
        pair_info = MAJOR_CURRENCY_PAIRS[normalized_pair]
        yahoo_symbol = pair_info['yahoo_symbol']
        
        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(yahoo_symbol)
        hist = ticker.history(period="2d", interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="レートデータが取得できませんでした")
        
        # 最新と前日のレート
        latest_rate = float(hist['Close'].iloc[-1])
        previous_rate = float(hist['Close'].iloc[-2]) if len(hist) > 1 else latest_rate
        
        change = latest_rate - previous_rate
        change_percent = (change / previous_rate) * 100 if previous_rate != 0 else 0
        
        # Bid/Ask スプレッドの推定（実際のデータではないため推定値）
        spread = latest_rate * 0.0001  # 0.01%のスプレッドを想定
        bid = latest_rate - (spread / 2)
        ask = latest_rate + (spread / 2)
        
        return {
            "status": "success",
            "data": {
                "pair": f"{pair_info['base']}/{pair_info['quote']}",
                "name": pair_info['name'],
                "rate": latest_rate,
                "change": change,
                "change_percent": change_percent,
                "timestamp": datetime.now().isoformat(),
                "bid": bid,
                "ask": ask,
                "spread": spread,
                "source": "Yahoo Finance"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting currency rate for {pair}: {str(e)}")
        raise HTTPException(status_code=500, detail="為替レート取得エラー")

@router.get("/currency-history/{pair}")
async def get_currency_history(
    pair: str, 
    days: int = Query(30, ge=1, le=365, description="取得する日数")
):
    """通貨ペアの履歴データを取得"""
    try:
        normalized_pair = pair.replace('/', '').upper()
        
        if normalized_pair not in MAJOR_CURRENCY_PAIRS:
            raise HTTPException(status_code=404, detail="指定された通貨ペアは対応していません")
        
        pair_info = MAJOR_CURRENCY_PAIRS[normalized_pair]
        yahoo_symbol = pair_info['yahoo_symbol']
        
        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(yahoo_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="履歴データが取得できませんでした")
        
        # データを整形
        history_data = []
        for date, row in hist.iterrows():
            history_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        return {
            "status": "success",
            "data": {
                "pair": f"{pair_info['base']}/{pair_info['quote']}",
                "name": pair_info['name'],
                "history": history_data,
                "period_days": days,
                "count": len(history_data)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting currency history for {pair}: {str(e)}")
        raise HTTPException(status_code=500, detail="為替履歴取得エラー")

@router.get("/currency-predictions/{pair}")
async def get_currency_predictions(
    pair: str,
    timeframe: str = Query("1D", description="予測期間 (1H, 1D, 1W, 1M)"),
    limit: int = Query(7, ge=1, le=30, description="予測データ数")
):
    """通貨ペアの予測データを生成（簡易実装）"""
    try:
        normalized_pair = pair.replace('/', '').upper()
        
        if normalized_pair not in MAJOR_CURRENCY_PAIRS:
            raise HTTPException(status_code=404, detail="指定された通貨ペアは対応していません")
        
        # 現在レートを取得
        rate_response = await get_currency_rate(pair)
        current_rate = rate_response["data"]["rate"]
        
        # 時間枠に応じた増分を設定
        time_increments = {
            "1H": timedelta(hours=1),
            "1D": timedelta(days=1), 
            "1W": timedelta(weeks=1),
            "1M": timedelta(days=30)
        }
        
        if timeframe not in time_increments:
            timeframe = "1D"
        
        increment = time_increments[timeframe]
        
        # 簡易的な予測データ生成（移動平均とトレンドベース）
        predictions = []
        base_volatility = current_rate * 0.01  # 1%のボラティリティを想定
        
        for i in range(1, limit + 1):
            future_time = datetime.now() + (increment * i)
            
            # 簡易的なトレンド計算（実際にはより複雑な予測モデルを使用）
            trend_factor = 0.001 * (i % 3 - 1)  # 小さなトレンド
            volatility = base_volatility * (0.8 + (i * 0.1))  # 時間と共にボラティリティ増加
            
            predicted_rate = current_rate * (1 + trend_factor)
            upper_bound = predicted_rate + volatility
            lower_bound = predicted_rate - volatility
            
            confidence = max(50, 95 - (i * 2))  # 時間と共に信頼度低下
            
            predictions.append({
                "timestamp": future_time.isoformat(),
                "predicted_rate": predicted_rate,
                "confidence": confidence,
                "upper_bound": upper_bound,
                "lower_bound": lower_bound,
                "factors": ["technical_analysis", "market_sentiment", "economic_indicators"]
            })
        
        pair_info = MAJOR_CURRENCY_PAIRS[normalized_pair]
        return {
            "status": "success",
            "data": {
                "pair": f"{pair_info['base']}/{pair_info['quote']}",
                "name": pair_info['name'],
                "timeframe": timeframe,
                "current_rate": current_rate,
                "predictions": predictions,
                "note": "これは簡易的な予測モデルです。実際の取引には使用しないでください。"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating currency predictions for {pair}: {str(e)}")
        raise HTTPException(status_code=500, detail="通貨予測生成エラー")

@router.get("/economic-calendar")
async def get_economic_calendar(
    date: Optional[str] = Query(None, description="日付 (YYYY-MM-DD)"),
    country: Optional[str] = Query(None, description="国コード (US, EU, JP)")
):
    """経済指標カレンダーを取得（簡易実装）"""
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
        date_str = target_date.strftime("%Y-%m-%d")
        
        # 主要経済指標のテンプレート（実際のAPIではリアルタイムデータを使用）
        economic_events = [
            {
                "time": "08:30",
                "country": "US",
                "event": "米雇用統計 (非農業部門雇用者数)",
                "impact": "high",
                "actual": None,
                "forecast": "+195K",
                "previous": "+187K",
                "currency": "USD",
                "description": "月次雇用統計の発表"
            },
            {
                "time": "10:00", 
                "country": "EU",
                "event": "ECB政策金利発表",
                "impact": "high",
                "actual": None,
                "forecast": "4.25%",
                "previous": "4.25%", 
                "currency": "EUR",
                "description": "欧州中央銀行の金利政策決定"
            },
            {
                "time": "14:00",
                "country": "JP", 
                "event": "日銀短観 (大企業製造業)",
                "impact": "medium",
                "actual": None,
                "forecast": "+12",
                "previous": "+10",
                "currency": "JPY",
                "description": "企業の景況感調査"
            },
            {
                "time": "15:00",
                "country": "US",
                "event": "消費者物価指数 (CPI)",
                "impact": "high", 
                "actual": None,
                "forecast": "+3.2%",
                "previous": "+3.1%",
                "currency": "USD",
                "description": "月次インフレ率の指標"
            },
            {
                "time": "21:30",
                "country": "US",
                "event": "FOMC議事録公表",
                "impact": "medium",
                "actual": None,
                "forecast": None,
                "previous": None,
                "currency": "USD", 
                "description": "連邦公開市場委員会の議事録"
            }
        ]
        
        # 国でフィルタリング
        if country:
            economic_events = [event for event in economic_events if event["country"] == country.upper()]
        
        return {
            "status": "success",
            "data": {
                "date": date_str,
                "events": economic_events,
                "count": len(economic_events),
                "note": "これはサンプルデータです。実際の経済指標発表予定とは異なる場合があります。"
            }
        }
    except Exception as e:
        logger.error(f"Error getting economic calendar: {str(e)}")
        raise HTTPException(status_code=500, detail="経済指標カレンダー取得エラー")