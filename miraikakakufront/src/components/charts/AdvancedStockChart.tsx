'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  Area,
  ComposedChart,
  Bar
} from 'recharts';
import { Calendar, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

interface AdvancedStockChartProps {
  symbol: string;
}

interface ChartData {
  date: string;
  close: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  sma_5?: number;
  sma_20?: number;
  prediction?: number;
}

interface TechnicalIndicators {
  sma_5?: number;
  sma_20?: number;
  rsi?: number;
  macd?: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollinger_bands?: {
    upper: number;
    middle: number;
    lower: number;
  };
  volatility_1m?: number;
}

export default function AdvancedStockChart({ symbol }: AdvancedStockChartProps) {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [indicators, setIndicators] = useState<TechnicalIndicators>({});
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y'>('1M');
  const [chartType, setChartType] = useState<'line' | 'candlestick' | 'area'>('line');
  const [showVolume, setShowVolume] = useState(true);
  const [showIndicators, setShowIndicators] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (symbol) {
      fetchChartData();
      fetchTechnicalIndicators();
    }
  }, [symbol, timeRange]);

  const fetchChartData = async () => {
    setLoading(true);
    try {
      const days = { '1M': 30, '3M': 90, '6M': 180, '1Y': 365 }[timeRange];
      
      // 価格データを取得
      const priceResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/price?days=${days}`
      );
      
      // 予測データを取得
      const predictionResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/predictions?days=7`
      );

      let priceData = [];
      let predictionData = [];

      if (priceResponse.ok) {
        priceData = await priceResponse.json();
      }
      
      if (predictionResponse.ok) {
        predictionData = await predictionResponse.json();
      }

      // チャートデータを統合
      const chartPoints = priceData.map((price: any) => ({
        date: new Date(price.date).toLocaleDateString(),
        close: price.close_price,
        open: price.open_price,
        high: price.high_price,
        low: price.low_price,
        volume: price.volume,
      }));

      // 移動平均を計算
      const withMA = chartPoints.map((point: any, index: number) => {
        const sma5Data = chartPoints.slice(Math.max(0, index - 4), index + 1);
        const sma20Data = chartPoints.slice(Math.max(0, index - 19), index + 1);
        
        return {
          ...point,
          sma_5: sma5Data.length >= 5 ? 
            sma5Data.reduce((sum: number, p: any) => sum + p.close, 0) / sma5Data.length : undefined,
          sma_20: sma20Data.length >= 20 ? 
            sma20Data.reduce((sum: number, p: any) => sum + p.close, 0) / sma20Data.length : undefined,
        };
      });

      // 予測データを追加
      predictionData.forEach((pred: any) => {
        withMA.push({
          date: new Date(pred.target_date).toLocaleDateString(),
          close: pred.predicted_price,
          prediction: pred.predicted_price,
        });
      });

      setChartData(withMA);
    } catch (error) {
      console.error('チャートデータ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTechnicalIndicators = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/indicators`
      );
      
      if (response.ok) {
        const data = await response.json();
        setIndicators(data);
      }
    } catch (error) {
      console.error('テクニカル指標取得エラー:', error);
    }
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 youtube-card">
        <LoadingSpinner 
          type="ai" 
          size="lg" 
          message="高度チャートとAI分析を読み込み中..."
        />
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* チャート設定パネル */}
      <div className="flex flex-wrap gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium">期間:</span>
          {(['1M', '3M', '6M', '1Y'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded text-sm ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {range}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium">表示:</span>
          <label className="flex items-center space-x-1">
            <input
              type="checkbox"
              checked={showVolume}
              onChange={(e) => setShowVolume(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">出来高</span>
          </label>
          <label className="flex items-center space-x-1">
            <input
              type="checkbox"
              checked={showIndicators}
              onChange={(e) => setShowIndicators(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">テクニカル指標</span>
          </label>
        </div>
      </div>

      {/* テクニカル指標サマリー */}
      {indicators && Object.keys(indicators).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-blue-50 rounded-lg">
          {indicators.rsi && (
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{indicators.rsi.toFixed(1)}</div>
              <div className="text-sm text-gray-600">RSI</div>
            </div>
          )}
          {indicators.sma_20 && (
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">${indicators.sma_20.toFixed(2)}</div>
              <div className="text-sm text-gray-600">SMA(20)</div>
            </div>
          )}
          {indicators.macd && (
            <div className="text-center">
              <div className={`text-2xl font-bold ${indicators.macd.macd > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {indicators.macd.macd.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">MACD</div>
            </div>
          )}
          {indicators.volatility_1m && (
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{(indicators.volatility_1m * 100).toFixed(1)}%</div>
              <div className="text-sm text-gray-600">ボラティリティ</div>
            </div>
          )}
        </div>
      )}

      {/* メインチャート */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                domain={['dataMin - 5', 'dataMax + 5']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* 価格ライン */}
              <Line
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="終値"
              />
              
              {/* 予測ライン */}
              <Line
                type="monotone"
                dataKey="prediction"
                stroke="#dc2626"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#dc2626', r: 4 }}
                name="AI予測"
              />
              
              {/* 移動平均線 */}
              {showIndicators && (
                <>
                  <Line
                    type="monotone"
                    dataKey="sma_5"
                    stroke="#10b981"
                    strokeWidth={1}
                    dot={false}
                    name="SMA(5)"
                  />
                  <Line
                    type="monotone"
                    dataKey="sma_20"
                    stroke="#f59e0b"
                    strokeWidth={1}
                    dot={false}
                    name="SMA(20)"
                  />
                </>
              )}
              
              {/* 出来高バー */}
              {showVolume && (
                <Bar
                  dataKey="volume"
                  fill="#8884d8"
                  opacity={0.3}
                  yAxisId="volume"
                  name="出来高"
                />
              )}
              
              {/* ボリンジャーバンド */}
              {showIndicators && indicators.bollinger_bands && (
                <>
                  <ReferenceLine 
                    y={indicators.bollinger_bands.upper} 
                    stroke="#ef4444" 
                    strokeDasharray="3 3"
                    label="BB上限"
                  />
                  <ReferenceLine 
                    y={indicators.bollinger_bands.lower} 
                    stroke="#ef4444" 
                    strokeDasharray="3 3"
                    label="BB下限"
                  />
                </>
              )}
              
              {showVolume && (
                <YAxis yAxisId="volume" orientation="right" tick={{ fontSize: 10 }} />
              )}
              
              <Brush dataKey="date" height={30} stroke="#8884d8" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 価格統計 */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-lg font-bold">${chartData[chartData.length - 1]?.close.toFixed(2)}</div>
            <div className="text-sm text-gray-600">現在価格</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">
              ${Math.max(...chartData.map(d => d.high || d.close)).toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">期間高値</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">
              ${Math.min(...chartData.map(d => d.low || d.close)).toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">期間安値</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold">
              {((chartData[chartData.length - 1]?.close - chartData[0]?.close) / chartData[0]?.close * 100).toFixed(2)}%
            </div>
            <div className="text-sm text-gray-600">期間変化率</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold">
              {(chartData.reduce((sum, d) => sum + (d.volume || 0), 0) / chartData.length / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">平均出来高</div>
          </div>
        </div>
      )}
    </div>
  );
}