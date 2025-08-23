'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { TrendingUp, TrendingDown, Activity, AlertCircle, RefreshCw, Globe } from 'lucide-react';
import { stockDataClient, IndexData } from '@/lib/stock-data-client';

// チャートコンポーネントを動的インポート（SSR無効化）
const IndexChart = dynamic(
  () => import('@/components/charts/IndexChart'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-surface-elevated rounded animate-pulse flex items-center justify-center">
        <span className="text-text-tertiary">Loading chart...</span>
      </div>
    )
  }
);

interface ChartDataPoint {
  date: string;
  value: number;
  type: 'actual' | 'historical_prediction' | 'future_prediction';
}

// 主要指数 - 日経、TOPIX、DOW、S&P500
const MAJOR_INDICES = [
  { symbol: 'NIKKEI', name: '日経平均株価', currency: 'JPY', market: 'TSE' },
  { symbol: 'TOPIX', name: '東証株価指数', currency: 'JPY', market: 'TSE' },
  { symbol: 'DOW', name: 'ダウ工業株30種', currency: 'USD', market: 'NYSE' },
  { symbol: 'SP500', name: 'S&P 500', currency: 'USD', market: 'NYSE' }
];

export default function RealTimeDashboard() {
  const [indexData, setIndexData] = useState<Record<string, IndexData>>({});
  const [alerts, setAlerts] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Real data fetching function
  const fetchRealData = async (symbol: string): Promise<IndexData | null> => {
    try {
      return await stockDataClient.getIndexData(symbol);
    } catch (error) {
      console.error(`Failed to fetch data for ${symbol}:`, error);
      addAlert(`${symbol}のデータ取得に失敗しました`);
      return null;
    }
  };

  const initializeIndexData = async () => {
    setIsLoading(true);
    const initialData: Record<string, IndexData> = {};
    
    try {
      // 並行してすべての指数データを取得
      const dataPromises = MAJOR_INDICES.map(index => 
        fetchRealData(index.symbol).then(data => ({ symbol: index.symbol, data }))
      );
      
      const results = await Promise.all(dataPromises);
      
      results.forEach(({ symbol, data }) => {
        if (data) {
          initialData[symbol] = data;
        }
      });
      
      setIndexData(initialData);
      addAlert('市場データを更新しました');
    } catch (error) {
      console.error('Failed to initialize data:', error);
      addAlert('データ初期化に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    await initializeIndexData();
    setLastUpdate(new Date().toLocaleTimeString());
  };

  const addAlert = (message: string) => {
    setAlerts(prev => [message, ...prev.slice(0, 4)]);
    setTimeout(() => {
      setAlerts(prev => prev.slice(0, -1));
    }, 5000);
  };

  useEffect(() => {
    setMounted(true);
    
    // クライアントサイドでのみ実行
    if (typeof window !== 'undefined') {
      // 初回データ取得
      initializeIndexData().then(() => {
        setLastUpdate(new Date().toLocaleTimeString());
      });
      
      const updateTime = () => {
        setCurrentTime(new Date().toLocaleTimeString());
      };
      
      updateTime();
      const interval = setInterval(updateTime, 1000);
      
      return () => {
        clearInterval(interval);
      };
    }
  }, []); // 依存配列を空にして、一度だけ実行

  // Individual index panel component - useMemoでメモ化
  const IndexPanel = useMemo(() => {
    return ({ data }: { data: IndexData }) => {
      const isPositive = data.change >= 0;
      const combinedData = useMemo(() => [...data.actualData, ...data.historicalPredictions, ...data.futurePredictions], [data.actualData, data.historicalPredictions, data.futurePredictions]);
      
      return (
      <div className="bg-surface-card border border-border-default rounded-xl p-6 backdrop-blur-sm">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Globe className="w-6 h-6 text-brand-primary" />
            <div>
              <h3 className="text-lg font-bold text-text-primary">{data.name}</h3>
              <p className="text-sm text-text-secondary">{data.symbol}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-text-primary">
              {data.price.toLocaleString('ja-JP', { maximumFractionDigits: 2 })}
            </div>
            <div className={`flex items-center space-x-1 ${isPositive ? 'text-status-success' : 'text-status-error'}`}>
              {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{isPositive ? '+' : ''}{data.change.toFixed(2)}</span>
              <span>({isPositive ? '+' : ''}{data.changePercent.toFixed(2)}%)</span>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-64 mb-4">
          <IndexChart data={combinedData} />
        </div>

        {/* Legend and Statistics */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#2196F3' }}></div>
              <span className="text-text-secondary">実測値</span>
            </div>
            <div className="flex items-center space-x-2 mb-1">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#10B981' }}></div>
              <span className="text-text-secondary">過去予測</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: '#8B5CF6' }}></div>
              <span className="text-text-secondary">未来予測</span>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-text-secondary">出来高:</span>
              <span className="text-text-primary">{(data.volume / 1000000).toFixed(1)}M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">更新:</span>
              <span className="text-text-primary">{data.lastUpdate}</span>
            </div>
          </div>
        </div>
      </div>
      );
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-background to-surface-elevated p-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">株価予測ダッシュボード</h1>
          <p className="text-text-secondary">AI予測による実際の市場データ分析</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={refreshData}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-primary text-white hover:bg-brand-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? '更新中...' : '更新'}</span>
          </button>
          {mounted && (
            <div className="text-sm text-text-secondary">
              最終更新: {lastUpdate}
            </div>
          )}
        </div>
      </div>

      {/* アラート */}
      {alerts.length > 0 && (
        <div className="mb-6">
          {alerts.map((alert, index) => (
            <div key={index} className="flex items-center space-x-2 p-3 mb-2 bg-brand-primary/20 border border-brand-primary/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-brand-primary" />
              <span className="text-brand-primary">{alert}</span>
            </div>
          ))}
        </div>
      )}

      {/* 4面パネル - 主要指数 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {mounted ? (
          MAJOR_INDICES.map((index) => {
            const data = indexData[index.symbol];
            return data ? (
              <IndexPanel key={index.symbol} data={data} />
            ) : (
              <div key={index.symbol} className="bg-surface-card border border-border-default rounded-xl p-6 backdrop-blur-sm animate-pulse">
                <div className="h-8 bg-surface-elevated rounded mb-4"></div>
                <div className="h-64 bg-surface-elevated rounded mb-4"></div>
                <div className="h-16 bg-surface-elevated rounded"></div>
              </div>
            );
          })
        ) : (
          MAJOR_INDICES.map((index) => (
            <div key={index.symbol} className="bg-surface-card border border-border-default rounded-xl p-6 backdrop-blur-sm animate-pulse">
              <div className="h-8 bg-surface-elevated rounded mb-4"></div>
              <div className="h-64 bg-surface-elevated rounded mb-4"></div>
              <div className="h-16 bg-surface-elevated rounded"></div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}