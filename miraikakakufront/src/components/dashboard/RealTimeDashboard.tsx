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
      // WebSocket connected
    },
    onDisconnect: () => {
      // WebSocket disconnected
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
        // APIが利用できない場合のモックデータ生成
        if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
          const mockPrice = 150 + Math.random() * 50;
          updateMarketData({
            symbol,
            price: mockPrice,
            change: (Math.random() - 0.5) * 10,
            change_percent: (Math.random() - 0.5) * 5,
            volume: Math.floor(Math.random() * 10000000)
          });
          continue;
        }
        
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/price?days=1`,
          { 
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.length > 0) {
            const latest = data[0];
            updateMarketData({
              symbol,
              price: latest.close_price,
              volume: latest.volume,
              change: latest.change || 0,
              change_percent: latest.change_percent || 0
            });
          }
        } else {
          // API応答エラーの場合もモックデータを使用
          console.warn(`API応答エラー ${symbol}: ${response.status}`);
          const mockPrice = 150 + Math.random() * 50;
          updateMarketData({
            symbol,
            price: mockPrice,
            change: (Math.random() - 0.5) * 10,
            change_percent: (Math.random() - 0.5) * 5,
            volume: Math.floor(Math.random() * 10000000)
          });
        }
      } catch (error) {
        console.error(`初期データ取得エラー ${symbol}:`, error);
        // エラーの場合もモックデータで継続
        const mockPrice = 150 + Math.random() * 50;
        updateMarketData({
          symbol,
          price: mockPrice,
          change: (Math.random() - 0.5) * 10,
          change_percent: (Math.random() - 0.5) * 5,
          volume: Math.floor(Math.random() * 10000000)
        });
      }
    }
  };

  const fetchPredictions = async () => {
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
    
    for (const symbol of symbols) {
      try {
        // APIが利用できない場合のモック予測データ
        if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
          const currentPrice = marketData[symbol]?.price || 150 + Math.random() * 50;
          setPredictions(prev => [
            ...prev.filter(p => p.symbol !== symbol),
            {
              symbol,
              predicted_price: currentPrice * (1 + (Math.random() - 0.5) * 0.1),
              confidence: 0.7 + Math.random() * 0.25,
              model_name: 'Demo Model',
              target_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
            }
          ]);
          continue;
        }
        
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/predictions?days=1`,
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
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
        } else {
          // API応答エラーの場合もモックデータ使用
          console.warn(`予測API応答エラー ${symbol}: ${response.status}`);
          const currentPrice = marketData[symbol]?.price || 150 + Math.random() * 50;
          setPredictions(prev => [
            ...prev.filter(p => p.symbol !== symbol),
            {
              symbol,
              predicted_price: currentPrice * (1 + (Math.random() - 0.5) * 0.1),
              confidence: 0.7 + Math.random() * 0.25,
              model_name: 'Demo Model',
              target_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
            }
          ]);
        }
      } catch (error) {
        console.error(`予測データ取得エラー ${symbol}:`, error);
        // エラー時もモックデータで継続
        const currentPrice = marketData[symbol]?.price || 150 + Math.random() * 50;
        setPredictions(prev => [
          ...prev.filter(p => p.symbol !== symbol),
          {
            symbol,
            predicted_price: currentPrice * (1 + (Math.random() - 0.5) * 0.1),
            confidence: 0.7 + Math.random() * 0.25,
            model_name: 'Demo Model',
            target_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
          }
        ]);
      }
    }
  };

  return (
    <div className="min-h-screen bg-base-black p-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-text-white">リアルタイムダッシュボード</h1>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
            isConnected ? 'bg-icon-green/20 text-icon-green' : 'bg-icon-red/20 text-icon-red'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-icon-green' : 'bg-icon-red'}`}></div>
            <span className="text-sm font-medium">
              {isConnected ? 'ライブ' : '切断'}
            </span>
          </div>
          <button
            onClick={() => setIsLive(!isLive)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              isLive ? 'bg-base-blue-600 text-text-white' : 'bg-icon-green text-text-white'
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
            <div key={index} className="flex items-center space-x-2 p-3 bg-base-blue-500/20 border border-base-blue-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-base-blue-400" />
              <span className="text-base-blue-400">{alert}</span>
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
            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
              selectedSymbol === stock.symbol 
                ? 'bg-base-blue-600/20 text-text-white border-base-blue-600/30 transform scale-105' 
                : 'bg-base-gray-900/50 border-base-gray-800/50 hover:border-base-gray-700 text-text-white'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-bold text-lg">{stock.symbol}</h3>
              {stock.changePercent >= 0 ? (
                <TrendingUp className="w-5 h-5 text-icon-green" />
              ) : (
                <TrendingDown className="w-5 h-5 text-icon-red" />
              )}
            </div>
            <div className="text-2xl font-bold mb-1">
              ${stock.price.toFixed(2)}
            </div>
            <div className={`text-sm ${
              stock.changePercent >= 0 ? 'text-icon-green' : 'text-icon-red'
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
          <div className="bg-base-gray-900/50 border border-base-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-4 flex items-center text-text-white">
              <Activity className="w-5 h-5 mr-2 text-icon-red" />
              {selectedSymbol} - 高度分析
            </h2>
            <AdvancedStockChart symbol={selectedSymbol} />
          </div>
        </div>

        {/* サイド情報パネル */}
        <div className="space-y-6">
          {/* 予測サマリー */}
          <div className="bg-base-gray-900/50 border border-base-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-lg font-bold mb-4 text-text-white">AI予測サマリー</h3>
            <div className="space-y-3">
              {predictions.slice(0, 5).map((pred, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-base-black/30 rounded">
                  <div>
                    <div className="font-semibold text-text-white">{pred.symbol}</div>
                    <div className="text-sm text-base-gray-400">{pred.model_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-text-white">${pred.predicted_price.toFixed(2)}</div>
                    <div className="text-sm text-base-gray-400">
                      信頼度: {(pred.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* パフォーマンス指標 */}
          <div className="bg-base-gray-900/50 border border-base-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-lg font-bold mb-4 text-text-white">システム状態</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-300">WebSocket</span>
                <span className={`font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {isConnected ? '接続中' : '切断'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">追跡銘柄</span>
                <span className="font-semibold text-white">{Object.keys(marketData).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">アクティブ予測</span>
                <span className="font-semibold text-white">{predictions.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">最終更新</span>
                <span className="text-sm text-gray-400">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>

          {/* クイックアクション */}
          <div className="bg-gray-900/50 border border-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-lg font-bold mb-4 text-white">クイックアクション</h3>
            <div className="space-y-2">
              <button 
                onClick={() => fetchPredictions()}
                className="w-full px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded hover:bg-red-500/30 transition-colors"
              >
                予測を更新
              </button>
              <button 
                onClick={() => fetchInitialData()}
                className="w-full px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded hover:bg-green-500/30 transition-colors"
              >
                価格データ更新
              </button>
              <button className="w-full px-4 py-2 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded hover:bg-purple-500/30 transition-colors">
                アラート設定
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* インタラクティブチャート */}
      <div className="bg-gray-900/50 border border-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
        <h2 className="text-xl font-bold mb-4 text-white">インタラクティブ分析</h2>
        <InteractiveChart symbol={selectedSymbol} height={500} />
      </div>

      {/* 市場統計 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900/50 border border-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
          <h3 className="text-lg font-bold mb-4 text-green-400">本日の上昇銘柄</h3>
          <div className="space-y-2">
            {Object.values(marketData)
              .filter(stock => stock.changePercent > 0)
              .sort((a, b) => b.changePercent - a.changePercent)
              .slice(0, 5)
              .map((stock) => (
                <div key={stock.symbol} className="flex justify-between items-center">
                  <span className="font-semibold text-white">{stock.symbol}</span>
                  <span className="text-green-400">+{stock.changePercent.toFixed(2)}%</span>
                </div>
              ))
            }
          </div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
          <h3 className="text-lg font-bold mb-4 text-red-400">本日の下落銘柄</h3>
          <div className="space-y-2">
            {Object.values(marketData)
              .filter(stock => stock.changePercent < 0)
              .sort((a, b) => a.changePercent - b.changePercent)
              .slice(0, 5)
              .map((stock) => (
                <div key={stock.symbol} className="flex justify-between items-center">
                  <span className="font-semibold text-white">{stock.symbol}</span>
                  <span className="text-red-400">{stock.changePercent.toFixed(2)}%</span>
                </div>
              ))
            }
          </div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 p-6 rounded-lg backdrop-blur-sm">
          <h3 className="text-lg font-bold mb-4 text-purple-400">高信頼度予測</h3>
          <div className="space-y-2">
            {predictions
              .sort((a, b) => b.confidence - a.confidence)
              .slice(0, 5)
              .map((pred, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="font-semibold">{pred.symbol}</span>
                  <div className="text-right">
                    <div className="text-sm text-white">${pred.predicted_price.toFixed(2)}</div>
                    <div className="text-xs text-gray-400">
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