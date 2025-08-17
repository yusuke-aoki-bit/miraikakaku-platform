'use client';

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { TrendingUp, TrendingDown, Activity, AlertCircle, RefreshCw } from 'lucide-react';
import AdvancedStockChart from '@/components/charts/AdvancedStockChart';
import InteractiveChart from '@/components/charts/InteractiveChart';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  lastUpdate: string;
}

interface PredictionData {
  symbol: string;
  predicted_price: number;
  confidence: number;
  model_name: string;
  target_date: string;
}

export default function RealTimeDashboard() {
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [alerts, setAlerts] = useState<string[]>([]);
  const [isLive, setIsLive] = useState(true);

  // WebSocket接続
  const { isConnected, lastMessage, error } = useWebSocket('/ws', {
    onMessage: (message) => {
      handleWebSocketMessage(message);
    },
    onConnect: () => {
      console.log('リアルタイムダッシュボード接続');
    },
    onDisconnect: () => {
      console.log('リアルタイムダッシュボード切断');
    }
  });

  useEffect(() => {
    // 初期データを取得
    fetchInitialData();
    fetchPredictions();
  }, []);

  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'price_update':
        updateMarketData(message.data);
        break;
      case 'prediction_update':
        updatePredictions(message.data);
        break;
      case 'system_alert':
        addAlert(message.data.message);
        break;
    }
  };

  const updateMarketData = (data: any) => {
    setMarketData(prev => ({
      ...prev,
      [data.symbol]: {
        symbol: data.symbol,
        price: data.price,
        change: data.change || 0,
        changePercent: data.change_percent || 0,
        volume: data.volume || 0,
        lastUpdate: new Date().toLocaleTimeString()
      }
    }));
  };

  const updatePredictions = (data: any) => {
    setPredictions(prev => {
      const filtered = prev.filter(p => p.symbol !== data.symbol);
      return [...filtered, data];
    });
  };

  const addAlert = (message: string) => {
    setAlerts(prev => [message, ...prev.slice(0, 4)]);
    setTimeout(() => {
      setAlerts(prev => prev.slice(0, -1));
    }, 5000);
  };

  const fetchInitialData = async () => {
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
    
    for (const symbol of symbols) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/price?days=1`
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.length > 0) {
            const latest = data[0];
            updateMarketData({
              symbol,
              price: latest.close_price,
              volume: latest.volume
            });
          }
        }
      } catch (error) {
        console.error(`初期データ取得エラー ${symbol}:`, error);
      }
    }
  };

  const fetchPredictions = async () => {
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
    
    for (const symbol of symbols) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/predictions?days=1`
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.length > 0) {
            setPredictions(prev => [
              ...prev.filter(p => p.symbol !== symbol),
              {
                symbol,
                predicted_price: data[0].predicted_price,
                confidence: data[0].confidence_score,
                model_name: data[0].model_name,
                target_date: data[0].target_date
              }
            ]);
          }
        }
      } catch (error) {
        console.error(`予測データ取得エラー ${symbol}:`, error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">リアルタイムダッシュボード</h1>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
            isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium">
              {isConnected ? 'ライブ' : '切断'}
            </span>
          </div>
          <button
            onClick={() => setIsLive(!isLive)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              isLive ? 'bg-red-600 text-white' : 'bg-green-600 text-white'
            }`}
          >
            <RefreshCw className="w-4 h-4" />
            <span>{isLive ? '一時停止' : '再開'}</span>
          </button>
        </div>
      </div>

      {/* アラート */}
      {alerts.length > 0 && (
        <div className="mb-6 space-y-2">
          {alerts.map((alert, index) => (
            <div key={index} className="flex items-center space-x-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <span className="text-yellow-800">{alert}</span>
            </div>
          ))}
        </div>
      )}

      {/* 市場概要 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {Object.values(marketData).map((stock) => (
          <div
            key={stock.symbol}
            onClick={() => setSelectedSymbol(stock.symbol)}
            className={`p-4 rounded-lg shadow cursor-pointer transition-all duration-200 ${
              selectedSymbol === stock.symbol 
                ? 'bg-blue-600 text-white transform scale-105' 
                : 'bg-white hover:shadow-lg'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-bold text-lg">{stock.symbol}</h3>
              {stock.changePercent >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-500" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-500" />
              )}
            </div>
            <div className="text-2xl font-bold mb-1">
              ${stock.price.toFixed(2)}
            </div>
            <div className={`text-sm ${
              stock.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
            </div>
            <div className="text-xs opacity-70 mt-2">
              {stock.lastUpdate}
            </div>
          </div>
        ))}
      </div>

      {/* メインチャートエリア */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
        {/* 高度チャート */}
        <div className="xl:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              {selectedSymbol} - 高度分析
            </h2>
            <AdvancedStockChart symbol={selectedSymbol} />
          </div>
        </div>

        {/* サイド情報パネル */}
        <div className="space-y-6">
          {/* 予測サマリー */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-lg font-bold mb-4">AI予測サマリー</h3>
            <div className="space-y-3">
              {predictions.slice(0, 5).map((pred, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div>
                    <div className="font-semibold">{pred.symbol}</div>
                    <div className="text-sm text-gray-600">{pred.model_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">${pred.predicted_price.toFixed(2)}</div>
                    <div className="text-sm text-gray-600">
                      信頼度: {(pred.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* パフォーマンス指標 */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-lg font-bold mb-4">システム状態</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>WebSocket</span>
                <span className={`font-semibold ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                  {isConnected ? '接続中' : '切断'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>追跡銘柄</span>
                <span className="font-semibold">{Object.keys(marketData).length}</span>
              </div>
              <div className="flex justify-between">
                <span>アクティブ予測</span>
                <span className="font-semibold">{predictions.length}</span>
              </div>
              <div className="flex justify-between">
                <span>最終更新</span>
                <span className="text-sm text-gray-600">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>

          {/* クイックアクション */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-lg font-bold mb-4">クイックアクション</h3>
            <div className="space-y-2">
              <button 
                onClick={() => fetchPredictions()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                予測を更新
              </button>
              <button 
                onClick={() => fetchInitialData()}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                価格データ更新
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                アラート設定
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* インタラクティブチャート */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-bold mb-4">インタラクティブ分析</h2>
        <InteractiveChart symbol={selectedSymbol} height={500} />
      </div>

      {/* 市場統計 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-green-600">本日の上昇銘柄</h3>
          <div className="space-y-2">
            {Object.values(marketData)
              .filter(stock => stock.changePercent > 0)
              .sort((a, b) => b.changePercent - a.changePercent)
              .slice(0, 5)
              .map((stock) => (
                <div key={stock.symbol} className="flex justify-between items-center">
                  <span className="font-semibold">{stock.symbol}</span>
                  <span className="text-green-600">+{stock.changePercent.toFixed(2)}%</span>
                </div>
              ))
            }
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-red-600">本日の下落銘柄</h3>
          <div className="space-y-2">
            {Object.values(marketData)
              .filter(stock => stock.changePercent < 0)
              .sort((a, b) => a.changePercent - b.changePercent)
              .slice(0, 5)
              .map((stock) => (
                <div key={stock.symbol} className="flex justify-between items-center">
                  <span className="font-semibold">{stock.symbol}</span>
                  <span className="text-red-600">{stock.changePercent.toFixed(2)}%</span>
                </div>
              ))
            }
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-purple-600">高信頼度予測</h3>
          <div className="space-y-2">
            {predictions
              .sort((a, b) => b.confidence - a.confidence)
              .slice(0, 5)
              .map((pred, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="font-semibold">{pred.symbol}</span>
                  <div className="text-right">
                    <div className="text-sm">${pred.predicted_price.toFixed(2)}</div>
                    <div className="text-xs text-gray-600">
                      {(pred.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      </div>
    </div>
  );
}