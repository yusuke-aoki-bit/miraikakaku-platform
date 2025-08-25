'use client';

import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine
} from 'recharts';
import { 
  TrendingUp, 
  Eye, 
  EyeOff, 
  Settings, 
  Calendar,
  Activity,
  Zap
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
  current_price: number;
}

interface ChartDataPoint {
  date: string;
  actual_price?: number;
  lstm_prediction?: number;
  vertexai_prediction?: number;
  randomforest_prediction?: number;
  xgboost_prediction?: number;
  confidence_upper?: number;
  confidence_lower?: number;
  is_future?: boolean;
}

interface ModelToggle {
  name: string;
  key: string;
  color: string;
  enabled: boolean;
}

interface InteractivePredictionChartProps {
  stock: Stock | null;
}

export default function InteractivePredictionChart({ stock }: InteractivePredictionChartProps) {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [period, setPeriod] = useState<'1M' | '6M' | '1Y'>('6M');
  const [loading, setLoading] = useState(false);
  const [showConfidenceInterval, setShowConfidenceInterval] = useState(true);
  const [models, setModels] = useState<ModelToggle[]>([
    { name: 'LSTM', key: 'lstm_prediction', color: '#3b82f6', enabled: true },
    { name: 'VertexAI', key: 'vertexai_prediction', color: '#10b981', enabled: true },
    { name: 'RandomForest', key: 'randomforest_prediction', color: '#f59e0b', enabled: false },
    { name: 'XGBoost', key: 'xgboost_prediction', color: '#ef4444', enabled: false }
  ]);

  useEffect(() => {
    if (stock) {
      fetchChartData();
    }
  }, [stock, period]);

  const fetchChartData = async () => {
    if (!stock) return;

    setLoading(true);
    try {
      const periodDays = period === '1M' ? 30 : period === '6M' ? 180 : 365;
      const futureDays = 30;

      const [priceResponse, predictionResponse, historicalResponse] = await Promise.all([
        apiClient.getStockPrice(stock.symbol, periodDays),
        apiClient.getStockPredictions(stock.symbol, undefined, futureDays),
        apiClient.getHistoricalPredictions(stock.symbol, periodDays)
      ]);

      // 実際の価格データ（型安全）
      const priceData: any[] = (priceResponse.status === 'success' && Array.isArray(priceResponse.data)) ? priceResponse.data : [];
      const predictionData: any[] = (predictionResponse.status === 'success' && Array.isArray(predictionResponse.data)) ? predictionResponse.data : [];
      const historicalPredictions: any[] = (historicalResponse.status === 'success' && Array.isArray(historicalResponse.data)) ? historicalResponse.data : [];

      // チャートデータを構築
      const combinedData: ChartDataPoint[] = [];

      // 過去の実際の価格データ
      if (priceData.length > 0) {
        priceData.forEach((point: any, index: number) => {
          const historical = historicalPredictions.find((h: any) => h.date === point.date);
          combinedData.push({
            date: point.date,
            actual_price: point.close_price,
            lstm_prediction: historical?.lstm_prediction || undefined,
            vertexai_prediction: historical?.vertexai_prediction || undefined,
            randomforest_prediction: historical?.randomforest_prediction || undefined,
            xgboost_prediction: historical?.xgboost_prediction || undefined,
            is_future: false
          });
        });
      }

      // 未来の予測データ
      if (predictionData.length > 0) {
        const basePrice = stock.current_price;
        predictionData.forEach((point: any) => {
          combinedData.push({
            date: point.date,
            actual_price: undefined,
            lstm_prediction: point.lstm_prediction,
            vertexai_prediction: point.vertexai_prediction,
            randomforest_prediction: point.randomforest_prediction,
            xgboost_prediction: point.xgboost_prediction,
            confidence_upper: point.confidence_upper,
            confidence_lower: point.confidence_lower,
            is_future: true
          });
        });
      }

      setChartData(combinedData);
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      // モックデータでフォールバック
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    if (!stock) return;
    
    const data: ChartDataPoint[] = [];
    const periodDays = period === '1M' ? 30 : period === '6M' ? 180 : 365;
    const futureDays = 30;
    const basePrice = stock.current_price;
    
    // 過去データ
    for (let i = -periodDays; i <= 0; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      const trend = i / periodDays * 0.1;
      const noise = (Math.random() - 0.5) * 0.02;
      const actualPrice = basePrice * (1 + trend + noise);
      
      data.push({
        date: date.toISOString().split('T')[0],
        actual_price: actualPrice,
        lstm_prediction: actualPrice * (1 + (Math.random() - 0.5) * 0.01),
        vertexai_prediction: actualPrice * (1 + (Math.random() - 0.5) * 0.008),
        randomforest_prediction: actualPrice * (1 + (Math.random() - 0.5) * 0.012),
        xgboost_prediction: actualPrice * (1 + (Math.random() - 0.5) * 0.009),
        is_future: false
      });
    }
    
    // 未来データ
    for (let i = 1; i <= futureDays; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      const futurePrice = basePrice * (1 + (i / futureDays) * 0.05);
      const variation = (Math.random() - 0.5) * 0.02;
      
      data.push({
        date: date.toISOString().split('T')[0],
        actual_price: undefined,
        lstm_prediction: futurePrice * (1 + variation),
        vertexai_prediction: futurePrice * (1 + variation * 0.8),
        randomforest_prediction: futurePrice * (1 + variation * 1.2),
        xgboost_prediction: futurePrice * (1 + variation * 0.9),
        confidence_upper: futurePrice * (1 + variation + 0.03),
        confidence_lower: futurePrice * (1 + variation - 0.03),
        is_future: true
      });
    }
    
    setChartData(data);
  };

  const toggleModel = (modelKey: string) => {
    setModels(prev => prev.map(model =>
      model.key === modelKey
        ? { ...model, enabled: !model.enabled }
        : model
    ));
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const formatPrice = (value: number) => {
    if (stock?.symbol.match(/^[A-Z]+$/)) {
      return `$${value.toFixed(2)}`;
    }
    return `¥${Math.round(value).toLocaleString('ja-JP')}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const isFuture = data.is_future;

    return (
      <div className="bg-black/90 border border-gray-600 rounded-lg p-4 shadow-xl">
        <div className="text-gray-300 text-sm mb-2">
          {formatDate(label)} {isFuture && '(予測)'}
        </div>
        
        {data.actual_price && (
          <div className="text-white font-medium mb-1">
            実績価格: {formatPrice(data.actual_price)}
          </div>
        )}
        
        {models.filter(m => m.enabled).map(model => {
          const value = data[model.key];
          if (!value) return null;
          
          return (
            <div key={model.key} className="flex items-center justify-between text-sm">
              <span style={{ color: model.color }}>{model.name}:</span>
              <span className="text-white ml-2">{formatPrice(value)}</span>
            </div>
          );
        })}
        
        {isFuture && data.confidence_upper && data.confidence_lower && (
          <div className="mt-2 pt-2 border-t border-gray-700">
            <div className="text-xs text-gray-400">
              信頼区間: {formatPrice(data.confidence_lower)} - {formatPrice(data.confidence_upper)}
            </div>
          </div>
        )}
      </div>
    );
  };

  const todayDate = new Date().toISOString().split('T')[0];

  if (!stock) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            銘柄を選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            上の検索バーから分析したい銘柄を選択すると<br />
            AI予測チャートが表示されます
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center">
          <Activity className="w-6 h-6 mr-2 text-green-400" />
          AI予測チャート - {stock.symbol}
        </h2>

        {/* 期間選択 */}
        <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
          {(['1M', '6M', '1Y'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-md text-sm transition-all ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* コントロールパネル */}
      <div className="flex items-center justify-between mb-4">
        {/* モデル表示切替 */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">表示モデル:</span>
          </div>
          {models.map(model => (
            <button
              key={model.key}
              onClick={() => toggleModel(model.key)}
              className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm transition-all ${
                model.enabled
                  ? 'bg-gray-700/50 text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {model.enabled ? (
                <Eye className="w-3 h-3" />
              ) : (
                <EyeOff className="w-3 h-3" />
              )}
              <span style={{ color: model.enabled ? model.color : undefined }}>
                {model.name}
              </span>
            </button>
          ))}
        </div>

        {/* 信頼区間表示切替 */}
        <button
          onClick={() => setShowConfidenceInterval(!showConfidenceInterval)}
          className={`flex items-center space-x-2 px-3 py-1 rounded-md text-sm transition-all ${
            showConfidenceInterval
              ? 'bg-purple-600/20 text-purple-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Zap className="w-3 h-3" />
          <span>信頼区間</span>
        </button>
      </div>

      {/* チャート */}
      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
        </div>
      ) : (
        <div className="h-96 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatDate}
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                domain={['dataMin - 50', 'dataMax + 50']}
                tickFormatter={(value) => formatPrice(value)}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* 信頼区間 */}
              {showConfidenceInterval && (
                <>
                  <Area
                    type="monotone"
                    dataKey="confidence_upper"
                    stroke="none"
                    fill="rgba(168, 85, 247, 0.1)"
                    connectNulls={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="confidence_lower"
                    stroke="none"
                    fill="rgba(168, 85, 247, 0.1)"
                    connectNulls={false}
                  />
                </>
              )}
              
              {/* 今日の境界線 */}
              <ReferenceLine x={todayDate} stroke="#6b7280" strokeDasharray="2 2" />
              
              {/* 実績価格 */}
              <Line
                type="monotone"
                dataKey="actual_price"
                stroke="#ffffff"
                strokeWidth={3}
                dot={false}
                connectNulls={false}
              />
              
              {/* AIモデル予測線 */}
              {models.filter(m => m.enabled).map(model => (
                <Line
                  key={model.key}
                  type="monotone"
                  dataKey={model.key}
                  stroke={model.color}
                  strokeWidth={2}
                  strokeDasharray={model.key.includes('prediction') ? "5 5" : undefined}
                  dot={false}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* 凡例 */}
      <div className="flex items-center justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-1">
          <div className="w-4 h-0.5 bg-white"></div>
          <span className="text-gray-400">実績</span>
        </div>
        {models.filter(m => m.enabled).map(model => (
          <div key={model.key} className="flex items-center space-x-1">
            <div className="w-4 h-0.5 border-t-2 border-dashed" style={{ borderColor: model.color }}></div>
            <span className="text-gray-400">{model.name}予測</span>
          </div>
        ))}
        {showConfidenceInterval && (
          <div className="flex items-center space-x-1">
            <div className="w-4 h-2 bg-purple-400 opacity-20 rounded"></div>
            <span className="text-gray-400">信頼区間</span>
          </div>
        )}
      </div>
    </div>
  );
}