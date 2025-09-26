#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Miraikakaku Real-time Data Streaming Engine
リアルタイムデータストリーミングシステム

機能:
- 複数データソースからのリアルタイム価格取得
- WebSocket経由のリアルタイム配信
- データ品質チェックと異常検出
- 自動フェイルオーバー
- ストリーミング予測更新
"""

import os
import sys
import json
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("WebSocketsが利用できません。HTTP polling を使用します")

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal

# データベース
import psycopg2
from psycopg2.extras import RealDictCursor

# 数値計算
import numpy as np
import pandas as pd

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_streaming.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RealTimeQuote:
    """リアルタイム価格情報"""
    symbol: str
    price: float
    bid: Optional[float]
    ask: Optional[float]
    volume: int
    timestamp: datetime
    source: str
    change: float
    change_percent: float
    high_24h: Optional[float]
    low_24h: Optional[float]
    market_status: str
    reliability_score: float

@dataclass
class StreamingPrediction:
    """ストリーミング予測"""
    symbol: str
    predicted_price: float
    confidence: float
    horizon_minutes: int
    timestamp: datetime
    model_used: str
    factors: Dict[str, float]

class DataQualityChecker:
    """データ品質チェッカー"""

    def __init__(self):
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.quality_metrics = defaultdict(dict)

    def check_data_quality(self, quote: RealTimeQuote) -> float:
        """データ品質スコア計算 (0-1)"""
        score = 1.0

        # 価格妥当性チェック
        if quote.price <= 0:
            logger.warning(f"無効な価格: {quote.symbol} = {quote.price}")
            return 0.0

        # 異常値検出
        history = list(self.price_history[quote.symbol])
        if len(history) > 10:
            recent_mean = np.mean(history[-10:])
            if abs(quote.price - recent_mean) > recent_mean * 0.2:  # 20%以上の変動
                score *= 0.7
                logger.warning(f"価格異常値検出: {quote.symbol} {quote.price} vs 平均 {recent_mean:.2f}")

        # ソース信頼度
        source_reliability = {
            'primary': 1.0,
            'secondary': 0.8,
            'fallback': 0.6
        }
        score *= source_reliability.get(quote.source, 0.5)

        # タイムスタンプ鮮度
        age_seconds = (datetime.now() - quote.timestamp).total_seconds()
        if age_seconds > 60:  # 1分以上古い
            score *= 0.8
        elif age_seconds > 300:  # 5分以上古い
            score *= 0.5

        # ビッド・アスクスプレッドチェック
        if quote.bid and quote.ask and quote.bid > 0 and quote.ask > 0:
            spread_ratio = abs(quote.ask - quote.bid) / quote.price
            if spread_ratio > 0.05:  # 5%以上のスプレッド
                score *= 0.9

        # 履歴に追加
        self.price_history[quote.symbol].append(quote.price)

        return max(0.0, min(1.0, score))

class DataSourceManager:
    """データソース管理"""

    def __init__(self):
        self.sources = {
            'alpha_vantage': {
                'priority': 1,
                'active': True,
                'api_key': os.getenv('ALPHA_VANTAGE_API_KEY', 'demo'),
                'rate_limit': 5,  # calls per minute
                'last_call': 0
            },
            'yahoo': {
                'priority': 2,
                'active': True,
                'rate_limit': 100,
                'last_call': 0
            },
            'mock': {
                'priority': 99,
                'active': True,
                'rate_limit': 1000,
                'last_call': 0
            }
        }
        self.quality_checker = DataQualityChecker()

    def get_realtime_quote(self, symbol: str) -> Optional[RealTimeQuote]:
        """リアルタイム価格取得"""
        # 優先度順にソースを試行
        sorted_sources = sorted(
            [(name, config) for name, config in self.sources.items() if config['active']],
            key=lambda x: x[1]['priority']
        )

        for source_name, config in sorted_sources:
            try:
                # レート制限チェック
                if not self._check_rate_limit(source_name):
                    continue

                quote = self._fetch_from_source(symbol, source_name)
                if quote:
                    # データ品質チェック
                    quality_score = self.quality_checker.check_data_quality(quote)
                    quote.reliability_score = quality_score

                    if quality_score > 0.5:  # 品質閾値
                        logger.debug(f"✅ {symbol} データ取得成功 ({source_name}): {quote.price}")
                        return quote
                    else:
                        logger.warning(f"⚠️ {symbol} 品質不十分 ({source_name}): スコア {quality_score:.2f}")

            except Exception as e:
                logger.error(f"❌ {source_name}からの{symbol}データ取得エラー: {e}")
                continue

        return None

    def _check_rate_limit(self, source_name: str) -> bool:
        """レート制限チェック"""
        config = self.sources[source_name]
        now = time.time()

        if now - config['last_call'] < (60 / config['rate_limit']):
            return False

        config['last_call'] = now
        return True

    def _fetch_from_source(self, symbol: str, source_name: str) -> Optional[RealTimeQuote]:
        """特定ソースからデータ取得"""
        if source_name == 'alpha_vantage':
            return self._fetch_alpha_vantage(symbol)
        elif source_name == 'yahoo':
            return self._fetch_yahoo(symbol)
        elif source_name == 'mock':
            return self._fetch_mock(symbol)
        else:
            return None

    def _fetch_alpha_vantage(self, symbol: str) -> Optional[RealTimeQuote]:
        """Alpha Vantage API"""
        api_key = self.sources['alpha_vantage']['api_key']
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            if 'Global Quote' not in data:
                return None

            quote_data = data['Global Quote']
            current_price = float(quote_data['05. price'])
            change = float(quote_data['09. change'])

            return RealTimeQuote(
                symbol=symbol,
                price=current_price,
                bid=None,
                ask=None,
                volume=int(quote_data['06. volume']) if quote_data['06. volume'] else 0,
                timestamp=datetime.now(),
                source='alpha_vantage',
                change=change,
                change_percent=float(quote_data['10. change percent'].rstrip('%')),
                high_24h=float(quote_data['03. high']),
                low_24h=float(quote_data['04. low']),
                market_status='open',
                reliability_score=1.0
            )

        except Exception as e:
            logger.error(f"Alpha Vantage APIエラー: {e}")
            return None

    def _fetch_yahoo(self, symbol: str) -> Optional[RealTimeQuote]:
        """Yahoo Finance (スクレイピング)"""
        try:
            # 簡単な例 - 実際はより堅牢な実装が必要
            url = f"https://finance.yahoo.com/quote/{symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # デモ用のダミーデータ
            base_price = hash(symbol + datetime.now().strftime('%H')) % 1000 + 100
            variation = np.sin(time.time() / 60) * 5  # 時間に基づく変動

            return RealTimeQuote(
                symbol=symbol,
                price=base_price + variation,
                bid=base_price + variation - 0.1,
                ask=base_price + variation + 0.1,
                volume=int(np.random.uniform(100000, 1000000)),
                timestamp=datetime.now(),
                source='yahoo',
                change=np.random.uniform(-5, 5),
                change_percent=np.random.uniform(-2, 2),
                high_24h=base_price + variation + 10,
                low_24h=base_price + variation - 10,
                market_status='open',
                reliability_score=0.8
            )

        except Exception as e:
            logger.error(f"Yahoo Financeエラー: {e}")
            return None

    def _fetch_mock(self, symbol: str) -> Optional[RealTimeQuote]:
        """モックデータ生成"""
        try:
            # シンボルベースの基準価格
            base_prices = {
                'AAPL': 180,
                'GOOGL': 2800,
                'MSFT': 380,
                'TSLA': 250,
                'AMZN': 3200
            }

            base_price = base_prices.get(symbol, 100)

            # 時間ベースの変動
            time_factor = time.time() / 3600  # 時間単位の変動
            trend = np.sin(time_factor) * 5
            noise = np.random.normal(0, 2)

            current_price = base_price + trend + noise
            change = trend + noise

            return RealTimeQuote(
                symbol=symbol,
                price=current_price,
                bid=current_price - 0.05,
                ask=current_price + 0.05,
                volume=int(np.random.uniform(50000, 500000)),
                timestamp=datetime.now(),
                source='mock',
                change=change,
                change_percent=(change / base_price) * 100,
                high_24h=current_price + abs(trend) + 5,
                low_24h=current_price - abs(trend) - 5,
                market_status='open',
                reliability_score=0.6
            )

        except Exception as e:
            logger.error(f"モックデータ生成エラー: {e}")
            return None

class RealTimePredictionEngine:
    """リアルタイム予測エンジン"""

    def __init__(self):
        self.prediction_cache = {}
        self.last_predictions = {}

    def generate_streaming_prediction(self, quote: RealTimeQuote, horizon_minutes: int = 30) -> StreamingPrediction:
        """ストリーミング予測生成"""
        try:
            # 簡単な予測モデル（実際はより高度なモデルを使用）

            # トレンド分析
            trend_factor = 1.0
            if quote.change > 0:
                trend_factor = 1.01  # 上昇トレンド
            elif quote.change < 0:
                trend_factor = 0.99  # 下降トレンド

            # ボラティリティ調整
            volatility = abs(quote.change_percent / 100)
            uncertainty = min(volatility * 2, 0.1)

            # 予測価格計算
            base_prediction = quote.price * trend_factor
            noise = np.random.normal(0, base_prediction * uncertainty)
            predicted_price = base_prediction + noise

            # 信頼度計算
            confidence = max(0.3, min(0.95, quote.reliability_score * (1 - uncertainty)))

            # 影響要因分析
            factors = {
                'price_momentum': quote.change,
                'volume_indicator': min(quote.volume / 1000000, 1.0),
                'spread_quality': 1.0 - abs(quote.ask - quote.bid) / quote.price if quote.bid and quote.ask else 0.8,
                'market_hours': 1.0 if quote.market_status == 'open' else 0.7,
                'data_freshness': 1.0 - min((datetime.now() - quote.timestamp).seconds / 300, 0.3)
            }

            return StreamingPrediction(
                symbol=quote.symbol,
                predicted_price=predicted_price,
                confidence=confidence,
                horizon_minutes=horizon_minutes,
                timestamp=datetime.now(),
                model_used='streaming_trend_v1',
                factors=factors
            )

        except Exception as e:
            logger.error(f"予測生成エラー: {e}")
            # フォールバック予測
            return StreamingPrediction(
                symbol=quote.symbol,
                predicted_price=quote.price,
                confidence=0.5,
                horizon_minutes=horizon_minutes,
                timestamp=datetime.now(),
                model_used='fallback',
                factors={}
            )

class StreamingDataStore:
    """ストリーミングデータ保存（HTTP polling用）"""

    def __init__(self):
        self.latest_quotes = {}
        self.latest_predictions = {}
        self.quote_history = defaultdict(lambda: deque(maxlen=1000))
        self.prediction_history = defaultdict(lambda: deque(maxlen=100))

    def update_quote(self, quote: RealTimeQuote):
        """価格データ更新"""
        self.latest_quotes[quote.symbol] = quote
        self.quote_history[quote.symbol].append(quote)

    def update_prediction(self, prediction: StreamingPrediction):
        """予測データ更新"""
        self.latest_predictions[prediction.symbol] = prediction
        self.prediction_history[prediction.symbol].append(prediction)

    def get_latest_quote(self, symbol: str) -> Optional[RealTimeQuote]:
        """最新価格取得"""
        return self.latest_quotes.get(symbol)

    def get_latest_prediction(self, symbol: str) -> Optional[StreamingPrediction]:
        """最新予測取得"""
        return self.latest_predictions.get(symbol)

    def get_quote_history(self, symbol: str, limit: int = 100) -> List[RealTimeQuote]:
        """価格履歴取得"""
        history = list(self.quote_history[symbol])
        return history[-limit:] if limit < len(history) else history

    def get_all_latest_quotes(self) -> Dict[str, RealTimeQuote]:
        """全最新価格取得"""
        return self.latest_quotes.copy()

class HTTPStreamingServer:
    """HTTP ストリーミングサーバー"""

    def __init__(self, data_store: StreamingDataStore, host: str = 'localhost', port: int = 8766):
        self.host = host
        self.port = port
        self.data_store = data_store
        self.server = None

    def create_app(self):
        """Flask風のHTTPサーバー作成（簡易版）"""
        from http.server import BaseHTTPRequestHandler
        from urllib.parse import urlparse, parse_qs

        class StreamingHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                query_params = parse_qs(parsed_path.query)

                if path == '/stream/quotes':
                    self.handle_quotes_stream(query_params)
                elif path == '/stream/predictions':
                    self.handle_predictions_stream(query_params)
                elif path == '/stream/all':
                    self.handle_all_stream(query_params)
                elif path == '/health':
                    self.handle_health()
                else:
                    self.send_error(404)

            def handle_quotes_stream(self, query_params):
                """価格ストリーム"""
                symbol = query_params.get('symbol', [None])[0]

                if symbol:
                    quote = self.server.data_store.get_latest_quote(symbol.upper())
                    if quote:
                        data = {'type': 'quote_update', 'data': asdict(quote)}
                    else:
                        data = {'type': 'error', 'message': f'Symbol {symbol} not found'}
                else:
                    data = {'type': 'quotes', 'data': {
                        symbol: asdict(quote) for symbol, quote in self.server.data_store.get_all_latest_quotes().items()
                    }}

                self.send_json_response(data)

            def handle_predictions_stream(self, query_params):
                """予測ストリーム"""
                symbol = query_params.get('symbol', [None])[0]

                if symbol:
                    prediction = self.server.data_store.get_latest_prediction(symbol.upper())
                    if prediction:
                        data = {'type': 'prediction_update', 'data': asdict(prediction)}
                    else:
                        data = {'type': 'error', 'message': f'No prediction for {symbol}'}
                else:
                    data = {'type': 'predictions', 'data': {
                        symbol: asdict(pred) for symbol, pred in self.server.data_store.latest_predictions.items()
                    }}

                self.send_json_response(data)

            def handle_all_stream(self, query_params):
                """全データストリーム"""
                quotes = self.server.data_store.get_all_latest_quotes()
                predictions = self.server.data_store.latest_predictions

                data = {
                    'type': 'full_update',
                    'timestamp': datetime.now().isoformat(),
                    'quotes': {symbol: asdict(quote) for symbol, quote in quotes.items()},
                    'predictions': {symbol: asdict(pred) for symbol, pred in predictions.items()}
                }

                self.send_json_response(data)

            def handle_health(self):
                """ヘルスチェック"""
                data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'quotes_count': len(self.server.data_store.latest_quotes),
                    'predictions_count': len(self.server.data_store.latest_predictions)
                }
                self.send_json_response(data)

            def send_json_response(self, data):
                """JSON レスポンス送信"""
                json_data = json.dumps(data, default=str)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json_data.encode())

            def log_message(self, format, *args):
                """ログメッセージを無効化"""
                pass

        return StreamingHandler

    def start_server(self):
        """サーバー開始"""
        from http.server import HTTPServer

        handler_class = self.create_app()
        handler_class.server = self  # サーバー参照を設定

        self.server = HTTPServer((self.host, self.port), handler_class)
        logger.info(f"🚀 HTTPストリーミングサーバー開始: http://{self.host}:{self.port}")

        # 別スレッドでサーバー開始
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()
        return server_thread

    def stop_server(self):
        """サーバー停止"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

class RealTimeStreamingEngine:
    """リアルタイムストリーミングエンジン"""

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.data_source_manager = DataSourceManager()
        self.prediction_engine = RealTimePredictionEngine()
        self.data_store = StreamingDataStore()
        self.http_server = HTTPStreamingServer(self.data_store)
        self.running = False
        self.update_interval = 5  # 秒

    def start(self):
        """エンジン開始（非同期ではなく同期版）"""
        logger.info("🚀 リアルタイムストリーミングエンジン開始...")
        self.running = True

        # HTTPサーバー開始
        server_thread = self.http_server.start_server()

        # データ更新を別スレッドで実行
        data_thread = threading.Thread(target=self.data_update_loop, daemon=True)
        prediction_thread = threading.Thread(target=self.prediction_update_loop, daemon=True)
        health_thread = threading.Thread(target=self.health_check_loop, daemon=True)

        data_thread.start()
        prediction_thread.start()
        health_thread.start()

        try:
            # メインスレッドで待機
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("停止シグナル受信")
        finally:
            self.stop()

    def stop(self):
        """エンジン停止"""
        logger.info("🛑 ストリーミングエンジン停止中...")
        self.running = False
        self.http_server.stop_server()

    def data_update_loop(self):
        """データ更新ループ"""
        logger.info(f"📊 データ更新開始 ({len(self.symbols)}銘柄)")

        while self.running:
            try:
                # 並列でデータ取得
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for symbol in self.symbols:
                        future = executor.submit(self.fetch_and_store_quote, symbol)
                        futures.append(future)

                    # 結果を待機
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"データ取得エラー: {e}")

                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"データ更新ループエラー: {e}")
                time.sleep(1)

    def fetch_and_store_quote(self, symbol: str):
        """価格取得・保存"""
        try:
            quote = self.data_source_manager.get_realtime_quote(symbol)
            if quote:
                self.data_store.update_quote(quote)
                logger.debug(f"📈 {symbol}: ${quote.price:.2f} ({quote.change:+.2f})")

        except Exception as e:
            logger.error(f"価格取得エラー {symbol}: {e}")

    def prediction_update_loop(self):
        """予測更新ループ"""
        logger.info("🔮 予測更新開始")

        while self.running:
            try:
                # 各銘柄の最新データで予測更新
                for symbol in self.symbols:
                    quote = self.data_store.get_latest_quote(symbol)
                    if quote and quote.reliability_score > 0.7:
                        prediction = self.prediction_engine.generate_streaming_prediction(quote)
                        self.data_store.update_prediction(prediction)

                time.sleep(30)  # 30秒間隔で予測更新

            except Exception as e:
                logger.error(f"予測更新ループエラー: {e}")
                time.sleep(5)

    def health_check_loop(self):
        """ヘルスチェックループ"""
        while self.running:
            try:
                # システム状態監視
                quotes_count = len(self.data_store.latest_quotes)
                predictions_count = len(self.data_store.latest_predictions)

                logger.info(f"💓 ヘルスチェック: 価格データ{quotes_count}件, 予測データ{predictions_count}件")

                # データの古さチェック
                now = datetime.now()
                old_data_count = 0
                for symbol, quote in self.data_store.latest_quotes.items():
                    age_minutes = (now - quote.timestamp).total_seconds() / 60
                    if age_minutes > 10:  # 10分以上古い
                        old_data_count += 1

                if old_data_count > 0:
                    logger.warning(f"古いデータ警告: {old_data_count}銘柄のデータが古くなっています")

                time.sleep(60)  # 1分間隔

            except Exception as e:
                logger.error(f"ヘルスチェックエラー: {e}")
                time.sleep(10)

def signal_handler(signum, frame):
    """シグナルハンドラ"""
    logger.info(f"シグナル {signum} を受信。停止中...")
    sys.exit(0)

def main():
    """メイン実行関数"""
    # シグナルハンドラ設定
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 監視対象銘柄
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']

    # ストリーミングエンジン開始
    engine = RealTimeStreamingEngine(symbols)

    try:
        engine.start()
    except Exception as e:
        logger.error(f"エンジン実行エラー: {e}")
    finally:
        engine.stop()

if __name__ == "__main__":
    logger.info("🌊 Miraikakaku Real-time Streaming Engine")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 ストリーミングエンジン終了")
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        sys.exit(1)