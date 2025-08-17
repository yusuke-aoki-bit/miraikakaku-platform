'use client';

import React, { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Maximize2, Download, Settings } from 'lucide-react';

// Plotlyを動的インポート（SSRを避けるため）
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface InteractiveChartProps {
  symbol: string;
  height?: number;
}

interface CandlestickData {
  x: string[];
  open: number[];
  high: number[];
  low: number[];
  close: number[];
  volume: number[];
}

export default function InteractiveChart({ symbol, height = 600 }: InteractiveChartProps) {
  const [candlestickData, setCandlestickData] = useState<CandlestickData>({
    x: [], open: [], high: [], low: [], close: [], volume: []
  });
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    if (symbol) {
      fetchAdvancedData();
    }
  }, [symbol]);

  const fetchAdvancedData = async () => {
    setLoading(true);
    try {
      const [priceResponse, predictionResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/price?days=90`),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/predictions?days=14`)
      ]);

      let priceData = [];
      let predictionData = [];

      if (priceResponse.ok) {
        priceData = await priceResponse.json();
      }
      
      if (predictionResponse.ok) {
        predictionData = await predictionResponse.json();
      }

      // Candlestickデータを準備
      const sortedPrices = priceData.sort((a: any, b: any) => 
        new Date(a.date).getTime() - new Date(b.date).getTime()
      );

      const candleData: CandlestickData = {
        x: sortedPrices.map((p: any) => p.date),
        open: sortedPrices.map((p: any) => p.open_price || p.close_price),
        high: sortedPrices.map((p: any) => p.high_price || p.close_price),
        low: sortedPrices.map((p: any) => p.low_price || p.close_price),
        close: sortedPrices.map((p: any) => p.close_price),
        volume: sortedPrices.map((p: any) => p.volume || 0),
      };

      setCandlestickData(candleData);
      setPredictions(predictionData);
    } catch (error) {
      console.error('高度チャートデータ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const plotData = useMemo(() => {
    const traces: any[] = [];

    // Candlestickチャート
    if (candlestickData.x.length > 0) {
      traces.push({
        x: candlestickData.x,
        open: candlestickData.open,
        high: candlestickData.high,
        low: candlestickData.low,
        close: candlestickData.close,
        type: 'candlestick',
        name: symbol,
        increasing: { line: { color: '#10b981' } },
        decreasing: { line: { color: '#ef4444' } },
        yaxis: 'y1',
      });

      // 出来高バー
      traces.push({
        x: candlestickData.x,
        y: candlestickData.volume,
        type: 'bar',
        name: '出来高',
        opacity: 0.3,
        marker: { color: '#6366f1' },
        yaxis: 'y2',
      });

      // 移動平均線
      const sma20 = candlestickData.close.map((_, index) => {
        if (index < 19) return null;
        const slice = candlestickData.close.slice(index - 19, index + 1);
        return slice.reduce((sum, price) => sum + price, 0) / 20;
      });

      traces.push({
        x: candlestickData.x,
        y: sma20,
        type: 'scatter',
        mode: 'lines',
        name: 'SMA(20)',
        line: { color: '#f59e0b', width: 2 },
        yaxis: 'y1',
      });
    }

    // AI予測
    if (predictions.length > 0) {
      traces.push({
        x: predictions.map(p => p.target_date),
        y: predictions.map(p => p.predicted_price),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'AI予測',
        line: { color: '#8b5cf6', width: 3, dash: 'dash' },
        marker: { size: 8, symbol: 'diamond' },
        yaxis: 'y1',
      });
    }

    return traces;
  }, [candlestickData, predictions, symbol]);

  const layout = {
    title: {
      text: `${symbol} - 高度分析チャート`,
      font: { size: 18, family: 'Arial, sans-serif' },
    },
    xaxis: {
      title: '日付',
      rangeslider: { visible: false },
      type: 'date',
    },
    yaxis: {
      title: '価格 ($)',
      domain: [0.3, 1],
      side: 'left',
    },
    yaxis2: {
      title: '出来高',
      domain: [0, 0.25],
      side: 'right',
    },
    plot_bgcolor: theme === 'dark' ? '#1f2937' : '#ffffff',
    paper_bgcolor: theme === 'dark' ? '#111827' : '#ffffff',
    font: {
      color: theme === 'dark' ? '#ffffff' : '#000000',
    },
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      bgcolor: 'rgba(255, 255, 255, 0.8)',
    },
    margin: { l: 50, r: 50, t: 50, b: 50 },
    height: height,
  };

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: `${symbol}_chart`,
      height: 800,
      width: 1200,
      scale: 1
    },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-48 mb-4"></div>
            <div className="h-32 bg-gray-300 rounded"></div>
          </div>
          <div className="text-gray-600 mt-4">インタラクティブチャートを読み込み中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* チャート設定 */}
      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold">インタラクティブチャート</h3>
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="flex items-center space-x-2 px-3 py-1 rounded bg-white hover:bg-gray-100"
          >
            <Settings className="w-4 h-4" />
            <span>{theme === 'light' ? 'ダーク' : 'ライト'}モード</span>
          </button>
        </div>
        
        <div className="flex space-x-2">
          <button className="flex items-center space-x-2 px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700">
            <Download className="w-4 h-4" />
            <span>エクスポート</span>
          </button>
          <button className="flex items-center space-x-2 px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700">
            <Maximize2 className="w-4 h-4" />
            <span>全画面</span>
          </button>
        </div>
      </div>

      {/* Plotlyチャート */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: `${height}px` }}
        />
      </div>

      {/* チャート説明 */}
      <div className="text-sm text-gray-600 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold mb-2">チャート機能:</h4>
        <ul className="space-y-1">
          <li>• ズーム・パン操作でデータを詳細表示</li>
          <li>• 下部のブラシでデータ範囲を選択</li>
          <li>• レジェンドクリックで表示/非表示切り替え</li>
          <li>• ホバーで詳細データを表示</li>
          <li>• 右クリックメニューで画像エクスポート</li>
        </ul>
      </div>
    </div>
  );
}