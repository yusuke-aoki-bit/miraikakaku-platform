'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
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
import { Calendar } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

interface AdvancedStockChartProps {
  symbol: string;
}

// Updated ChartData interface to include confidence interval
interface ChartData {
  date: string;
  close: number | null;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  sma_5?: number;
  sma_20?: number;
  prediction?: number;
  confidence_range?: [number, number]; // [lower_bound, upper_bound]
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
  const [showVolume, setShowVolume] = useState(true);
  const [showIndicators, setShowIndicators] = useState(true);
  const [loading, setLoading] = useState(false);

  const fetchChartData = useCallback(async () => {
    setLoading(true);
    try {
      const days = { '1M': 30, '3M': 90, '6M': 180, '1Y': 365 }[timeRange];
      
      const priceResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/price?days=${days}`
      );
      
      // Assuming the prediction endpoint now returns upper and lower bounds
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

      interface PricePoint {
        date: string;
        close_price: number;
        open_price: number;
        high_price: number;
        low_price: number;
        volume: number;
      }

      const chartPoints = priceData.map((price: PricePoint) => ({
        date: new Date(price.date).toLocaleDateString(),
        close: price.close_price,
        open: price.open_price,
        high: price.high_price,
        low: price.low_price,
        volume: price.volume,
      }));

      interface ChartPoint {
        date: string;
        close: number;
        open: number;
        high: number;
        low: number;
        volume: number;
      }

      const withMA = chartPoints.map((point: ChartPoint, index: number) => {
        const sma5Data = chartPoints.slice(Math.max(0, index - 4), index + 1);
        const sma20Data = chartPoints.slice(Math.max(0, index - 19), index + 1);
        
        return {
          ...point,
          sma_5: sma5Data.length >= 5 ? 
            sma5Data.reduce((sum: number, p: ChartPoint) => sum + p.close, 0) / sma5Data.length : undefined,
          sma_20: sma20Data.length >= 20 ? 
            sma20Data.reduce((sum: number, p: ChartPoint) => sum + p.close, 0) / sma20Data.length : undefined,
        };
      });

      // --- MODIFICATION START ---
      // Connect the last historical point to the first prediction point for a continuous line
      const lastHistoricalPoint = withMA.length > 0 ? withMA[withMA.length - 1] : null;

      interface PredictionPoint {
        predicted_price: number;
        confidence_score?: number;
        date: string;
        target_date: string;
      }

      predictionData.forEach((pred: PredictionPoint, index: number) => {
        const predictionValue = pred.predicted_price;
        const confidenceScore = pred.confidence_score || 0.8;
        const margin = predictionValue * (1 - confidenceScore) * 0.5;
        
        const point: ChartData = {
          date: new Date(pred.target_date).toLocaleDateString(),
          close: null, // Use null for historical price on future dates
          prediction: predictionValue,
          confidence_range: [predictionValue - margin, predictionValue + margin]
        };

        // Make the prediction line start from the last known price
        if (index === 0 && lastHistoricalPoint) {
            const firstPredictionPoint = { ...point, close: lastHistoricalPoint.close };
            withMA.push(firstPredictionPoint);
        } else {
            withMA.push(point);
        }
      });
      // --- MODIFICATION END ---

      setChartData(withMA);
    } catch (error) {
      console.error('チャートデータ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeRange]);

  const fetchTechnicalIndicators = useCallback(async () => {
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
  }, [symbol]);

  useEffect(() => {
    if (symbol) {
      fetchChartData();
      fetchTechnicalIndicators();
    }
  }, [symbol, timeRange, fetchChartData, fetchTechnicalIndicators]);

  interface TooltipProps {
    active?: boolean;
    payload?: Array<{ name: string; value: number; color: string; payload: Record<string, unknown> }>;
    label?: string;
  }

  const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as any;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          {payload.map((entry, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2)}
            </p>
          ))}
          {data.confidence_range && (
             <p style={{ color: '#82ca9d' }}>
                Confidence: ${data.confidence_range[0].toFixed(2)} - ${data.confidence_range[1].toFixed(2)}
             </p>
          )}
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
      {/* Chart settings panel... */}
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

      {/* Technical indicators summary... */}
      {indicators && Object.keys(indicators).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-blue-50 rounded-lg">
          {/* ... indicators ... */}
        </div>
      )}

      {/* Main Chart */}
      <div className="bg-white p-6 rounded-lg shadow-lg" data-testid="stock-chart">
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
              
              {/* --- MODIFICATION START --- */}
              {/* Confidence Interval Area */}
              <Area
                type="monotone"
                dataKey="confidence_range"
                stroke="none"
                fill="#82ca9d"
                fillOpacity={0.2}
                name="Confidence Interval"
              />
              {/* --- MODIFICATION END --- */}

              <Line
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="終値"
                connectNulls // Ensures line continues over prediction period
              />
              
              <Line
                type="monotone"
                dataKey="prediction"
                stroke="#dc2626"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#dc2626', r: 4 }}
                name="AI予測"
                connectNulls
              />
              
              {showIndicators && (
                <>
                  <Line type="monotone" dataKey="sma_5" stroke="#10b981" strokeWidth={1} dot={false} name="SMA(5)" />
                  <Line type="monotone" dataKey="sma_20" stroke="#f59e0b" strokeWidth={1} dot={false} name="SMA(20)" />
                </>
              )}
              
              {showVolume && (
                <Bar dataKey="volume" fill="#8884d8" opacity={0.3} yAxisId="volume" name="出来高" />
              )}
              
              {showIndicators && indicators.bollinger_bands && (
                <>
                  <ReferenceLine y={indicators.bollinger_bands.upper} stroke="#ef4444" strokeDasharray="3 3" label="BB上限" />
                  <ReferenceLine y={indicators.bollinger_bands.lower} stroke="#ef4444" strokeDasharray="3 3" label="BB下限" />
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

      {/* Price statistics... */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
          {/* ... stats ... */}
        </div>
      )}
    </div>
  );
}
