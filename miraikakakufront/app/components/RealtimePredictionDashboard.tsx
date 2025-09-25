'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  AlertCircle,
  CheckCircle,
  Clock,
  Wifi,
  WifiOff,
  BarChart3,
  Brain,
  Target
} from 'lucide-react';
import { useRealtimeAI, RealtimePrediction, RealtimeAlert, MarketData, SystemHealth } from '../lib/websocket-client';

interface PredictionDisplayProps {
  prediction: RealtimePrediction;
  marketData?: MarketData;
}

const PredictionDisplay: React.FC<PredictionDisplayProps> = ({ prediction, marketData }) => {
  const isPositive = prediction.prediction > 0;
  const confidenceColor = prediction.confidence > 0.8 ? 'text-green-600' :
                          prediction.confidence > 0.6 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mr-4">
            <span className="text-white font-bold text-lg">{prediction.symbol}</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{prediction.symbol}</h3>
            <p className="text-sm text-gray-500">
              {new Date(prediction.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center">
            {isPositive ? (
              <TrendingUp className="w-5 h-5 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-500 mr-1" />
            )}
            <span className={`text-2xl font-bold ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}>
              {isPositive ? '+' : ''}{prediction.prediction.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-center mt-1">
            <Target className={`w-4 h-4 mr-1 ${confidenceColor}`} />
            <span className={`text-sm ${confidenceColor}`}>
              {(prediction.confidence * 100).toFixed(1)}% 信頼度
            </span>
          </div>
        </div>
      </div>

      {/* AI Factors */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <Brain className="w-4 h-4 mr-2" />
          AI判断要因
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {prediction.factors.map((factor, index) => (
            <div key={index} className="bg-gray-50 rounded p-3">
              <div className="text-sm font-medium text-gray-900">{factor.name}</div>
              <div className="flex justify-between items-center mt-1">
                <span className={`text-sm ${
                  factor.impact > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {factor.impact > 0 ? '+' : ''}{(factor.impact * 100).toFixed(1)}%
                </span>
                <span className="text-xs text-gray-500">
                  {(factor.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="flex justify-between items-center text-sm text-gray-500 border-t pt-3">
        <div className="flex items-center">
          <Zap className="w-4 h-4 mr-1" />
          レスポンス: {prediction.latency_ms}ms
        </div>
        <div>
          Model: {prediction.model_version}
        </div>
      </div>
    </div>
  );
};

interface SystemStatusProps {
  health?: SystemHealth;
  connected: boolean;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ health, connected }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      case 'down': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Activity className="w-5 h-5 mr-2" />
        システムステータス
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Connection Status */}
        <div className="text-center">
          <div className={`text-2xl mb-1 ${connected ? 'text-green-500' : 'text-red-500'}`}>
            {connected ? <Wifi className="w-6 h-6 mx-auto" /> : <WifiOff className="w-6 h-6 mx-auto" />}
          </div>
          <div className="text-sm text-gray-600">
            {connected ? '接続中' : '切断中'}
          </div>
        </div>

        {/* System Health */}
        {health && (
          <>
            <div className="text-center">
              <div className={`text-2xl font-bold mb-1 ${getStatusColor(health.status)}`}>
                {health.status.toUpperCase()}
              </div>
              <div className="text-sm text-gray-600">システム</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {health.latency_ms.toFixed(0)}ms
              </div>
              <div className="text-sm text-gray-600">平均レスポンス</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 mb-1">
                {health.active_connections}
              </div>
              <div className="text-sm text-gray-600">接続数</div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default function RealtimePredictionDashboard() {
  const [watchedSymbols, setWatchedSymbols] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL']);
  const [predictions, setPredictions] = useState<Map<string, RealtimePrediction>>(new Map());
  const [marketData, setMarketData] = useState<Map<string, MarketData>>(new Map());
  const [alerts, setAlerts] = useState<RealtimeAlert[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | undefined>();
  const [newSymbol, setNewSymbol] = useState('');

  const {
    client,
    connected,
    connectionInfo,
    subscribeToSymbol,
    unsubscribeFromSymbol,
    subscribeToMarketData,
    subscribeToSystemHealth,
    requestPrediction
  } = useRealtimeAI();

  // イベントハンドラー設定
  useEffect(() => {
    if (!client) return;

    const handlePrediction = (prediction: RealtimePrediction) => {
      setPredictions(prev => new Map(prev.set(prediction.symbol, prediction)));
    };

    const handleMarketData = (data: MarketData) => {
      setMarketData(prev => new Map(prev.set(data.symbol, data)));
    };

    const handleAlert = (alert: RealtimeAlert) => {
      setAlerts(prev => [alert, ...prev.slice(0, 9)]); // 最新10件保持
    };

    const handleSystemHealth = (health: SystemHealth) => {
      setSystemHealth(health);
    };

    client.on('prediction', handlePrediction);
    client.on('market_data', handleMarketData);
    client.on('alert', handleAlert);
    client.on('system_health', handleSystemHealth);

    return () => {
      client.off('prediction', handlePrediction);
      client.off('market_data', handleMarketData);
      client.off('alert', handleAlert);
      client.off('system_health', handleSystemHealth);
    };
  }, [client]);

  // 接続確立時の初期サブスクリプション
  useEffect(() => {
    if (!connected || !client) return;

    // ウォッチ銘柄の予測にサブスクライブ
    watchedSymbols.forEach(symbol => {
      subscribeToSymbol?.(symbol);
    });

    // 市場データにサブスクライブ
    subscribeToMarketData?.(watchedSymbols);

    // システムヘルスにサブスクライブ
    subscribeToSystemHealth?.();

  }, [connected, client, watchedSymbols, subscribeToSymbol, subscribeToMarketData, subscribeToSystemHealth]);

  const addSymbol = useCallback(() => {
    if (!newSymbol.trim() || watchedSymbols.includes(newSymbol.toUpperCase())) {
      return;
    }

    const symbol = newSymbol.toUpperCase();
    setWatchedSymbols(prev => [...prev, symbol]);
    setNewSymbol('');

    if (connected) {
      subscribeToSymbol?.(symbol);
      // 即座に予測をリクエスト
      requestPrediction?.(symbol, { model: 'ensemble', confidence: 0.95 });
    }
  }, [newSymbol, watchedSymbols, connected, subscribeToSymbol, requestPrediction]);

  const removeSymbol = useCallback((symbol: string) => {
    setWatchedSymbols(prev => prev.filter(s => s !== symbol));
    setPredictions(prev => {
      const newMap = new Map(prev);
      newMap.delete(symbol);
      return newMap;
    });

    if (connected) {
      unsubscribeFromSymbol?.(symbol);
    }
  }, [connected, unsubscribeFromSymbol]);

  const requestNewPrediction = useCallback((symbol: string) => {
    if (connected && requestPrediction) {
      requestPrediction(symbol, {
        model: 'ensemble',
        confidence: 0.95,
        horizon: '1d'
      });
    }
  }, [connected, requestPrediction]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            リアルタイムAI予測ダッシュボード
          </h1>
          <p className="text-gray-600">
            Phase 3.1 - 次世代リアルタイム株価予測システム
          </p>
        </div>

        {/* System Status */}
        <SystemStatus health={systemHealth} connected={connected} />

        {/* Symbol Management */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            監視銘柄管理
          </h3>

          <div className="flex items-center mb-4">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="銘柄コード (例: TSLA)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
            />
            <button
              onClick={addSymbol}
              disabled={!connected}
              className={`ml-3 px-6 py-2 rounded-lg font-medium ${
                connected
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              追加
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {watchedSymbols.map(symbol => (
              <div key={symbol} className="flex items-center bg-blue-50 rounded-lg px-3 py-1">
                <span className="text-blue-700 font-medium">{symbol}</span>
                <button
                  onClick={() => requestNewPrediction(symbol)}
                  disabled={!connected}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                  title="予測更新"
                >
                  <BarChart3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="ml-2 text-red-500 hover:text-red-700"
                  title="削除"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Predictions Display */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
          {watchedSymbols.map(symbol => {
            const prediction = predictions.get(symbol);
            const market = marketData.get(symbol);

            if (!prediction) {
              return (
                <div key={symbol} className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-center h-32">
                    <div className="text-center">
                      <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">
                        {connected ? `${symbol} 予測待機中...` : '接続待機中...'}
                      </p>
                    </div>
                  </div>
                </div>
              );
            }

            return (
              <PredictionDisplay
                key={symbol}
                prediction={prediction}
                marketData={market}
              />
            );
          })}
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              アラート履歴
            </h3>
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert, index) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border-l-4 ${
                    alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                    alert.severity === 'high' ? 'border-orange-500 bg-orange-50' :
                    alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                    'border-blue-500 bg-blue-50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900">
                        {alert.symbol} - {alert.alert_type.replace('_', ' ')}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        {alert.message}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connection Info */}
        {connectionInfo && (
          <div className="mt-6 bg-gray-100 rounded-lg p-4">
            <details>
              <summary className="cursor-pointer text-sm font-medium text-gray-700">
                接続詳細情報
              </summary>
              <div className="mt-2 text-xs text-gray-600">
                <div>Connection ID: {connectionInfo.connectionId}</div>
                <div>Subscriptions: {connectionInfo.subscriptions.length}</div>
                <div>Reconnect Attempts: {connectionInfo.reconnectAttempts}</div>
              </div>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}