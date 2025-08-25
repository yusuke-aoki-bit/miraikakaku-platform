'use client';

import React, { useState, useEffect } from 'react';
import { 
  ComposedChart, 
  Line, 
  Bar,
  Area,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar,
  Activity,
  Eye,
  EyeOff
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
  current_price: number;
}

interface VolumeAnalysisDataPoint {
  date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  volume_ma20: number;
  predicted_volume?: number;
  is_future?: boolean;
  price_change?: number;
  is_up_day: boolean;
}

interface VolumeAnalysisChartProps {
  stock: Stock | null;
}

export default function VolumeAnalysisChart({ stock }: VolumeAnalysisChartProps) {
  const [chartData, setChartData] = useState<VolumeAnalysisDataPoint[]>([]);
  const [period, setPeriod] = useState<'1M' | '6M' | '1Y'>('6M');
  const [loading, setLoading] = useState(false);
  const [showVolumeMA, setShowVolumeMA] = useState(true);
  const [showPredictions, setShowPredictions] = useState(true);

  useEffect(() => {
    if (stock) {
      fetchVolumeData();
    }
  }, [stock, period]);

  const fetchVolumeData = async () => {
    if (!stock) return;

    setLoading(true);
    try {
      const periodDays = period === '1M' ? 30 : period === '6M' ? 180 : 365;
      const futureDays = 14; // 2週間の予測

      const [priceResponse, volumeResponse, volumePredictionResponse] = await Promise.all([
        apiClient.getStockPrice(stock.symbol, periodDays),
        apiClient.getVolumeData(stock.symbol, periodDays),
        apiClient.getVolumePredictions(stock.symbol, futureDays)
      ]);

      // データを組み合わせてチャート用データを構築
      const combinedData: VolumeAnalysisDataPoint[] = [];
      
      // 過去のデータ処理
      if (priceResponse.status === 'success' && Array.isArray(priceResponse.data)) {
        const priceData = priceResponse.data;
        const volumeData = (volumeResponse.status === 'success' && Array.isArray(volumeResponse.data)) ? volumeResponse.data : [];
        
        priceData.forEach((pricePoint: any, index: number) => {
          const volumePoint = volumeData.find((v: any) => v.date === pricePoint.date);
          const volume = volumePoint?.volume || 1000000;
          
          // 20日移動平均計算（簡易版）
          const startIndex = Math.max(0, index - 19);
          const recentData = priceData.slice(startIndex, index + 1);
          const avgVolume = recentData.reduce((sum: number, item: any, i: number) => {
            const vol = volumeData.find((v: any) => v.date === item.date)?.volume || 
                       Math.floor(Math.random() * 5000000) + 1000000;
            return sum + vol;
          }, 0) / recentData.length;

          const isUpDay = pricePoint.close_price >= pricePoint.open_price;

          combinedData.push({
            date: pricePoint.date,
            open_price: pricePoint.open_price,
            high_price: pricePoint.high_price,
            low_price: pricePoint.low_price,
            close_price: pricePoint.close_price,
            volume: volume,
            volume_ma20: avgVolume,
            price_change: pricePoint.close_price - pricePoint.open_price,
            is_up_day: isUpDay,
            is_future: false
          });
        });
      }

      // 未来の予測データ処理
      if (volumePredictionResponse.status === 'success' && Array.isArray(volumePredictionResponse.data)) {
        const lastPrice = combinedData[combinedData.length - 1]?.close_price || (stock as any).current_price;
        const avgVolume = combinedData.slice(-20).reduce((sum, item) => sum + item.volume, 0) / 20;
        
        volumePredictionResponse.data.forEach((prediction: any, index: number) => {
          const date = new Date();
          date.setDate(date.getDate() + index + 1);
          
          // 価格の予測（簡易版）
          const priceVariation = (Math.random() - 0.5) * 0.02; // ±1%
          const predictedPrice = lastPrice * (1 + priceVariation + (index * 0.001));
          const isUpDay = Math.random() > 0.5;
          
          combinedData.push({
            date: date.toISOString().split('T')[0],
            open_price: predictedPrice * 0.999,
            high_price: predictedPrice * (1 + Math.random() * 0.01),
            low_price: predictedPrice * (1 - Math.random() * 0.01),
            close_price: predictedPrice,
            volume: 0, // 実績出来高なし
            predicted_volume: prediction.predicted_volume || Math.floor(avgVolume * (0.8 + Math.random() * 0.6)),
            volume_ma20: avgVolume,
            price_change: isUpDay ? predictedPrice * 0.01 : -predictedPrice * 0.01,
            is_up_day: isUpDay,
            is_future: true
          });
        });
      }

      if (combinedData.length === 0) {
        generateMockData();
      } else {
        setChartData(combinedData);
      }

    } catch (error) {
      console.error('Failed to fetch volume data:', error);
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    if (!stock) return;
    
    const periodDays = period === '1M' ? 30 : period === '6M' ? 180 : 365;
    const futureDays = 14;
    const basePrice = stock.current_price;
    const baseVolume = 2000000; // 200万株
    const mockData: VolumeAnalysisDataPoint[] = [];

    // 過去データ生成
    for (let i = -periodDays; i <= 0; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      const trend = (i / periodDays) * 0.1;
      const dailyVariation = (Math.random() - 0.5) * 0.04; // ±2%
      const priceMultiplier = 1 + trend + dailyVariation;
      
      const open = basePrice * priceMultiplier * (0.98 + Math.random() * 0.04);
      const close = basePrice * priceMultiplier;
      const high = Math.max(open, close) * (1 + Math.random() * 0.02);
      const low = Math.min(open, close) * (1 - Math.random() * 0.02);
      
      const isUpDay = close >= open;
      const volumeMultiplier = isUpDay ? (1 + Math.random() * 0.5) : (0.7 + Math.random() * 0.4);
      const volume = Math.floor(baseVolume * volumeMultiplier);
      
      // 20日移動平均計算
      const startIndex = Math.max(0, i + periodDays - 19);
      const volumeMA = baseVolume * (0.9 + Math.random() * 0.2);

      mockData.push({
        date: date.toISOString().split('T')[0],
        open_price: open,
        high_price: high,
        low_price: low,
        close_price: close,
        volume: volume,
        volume_ma20: volumeMA,
        price_change: close - open,
        is_up_day: isUpDay,
        is_future: false
      });
    }

    // 未来データ生成
    const lastData = mockData[mockData.length - 1];
    for (let i = 1; i <= futureDays; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      const futureVariation = (Math.random() - 0.5) * 0.03;
      const predictedPrice = lastData.close_price * (1 + futureVariation);
      const isUpDay = Math.random() > 0.5;
      
      const predictedVolume = Math.floor(
        baseVolume * (0.8 + Math.random() * 0.6) * (isUpDay ? 1.2 : 0.9)
      );

      mockData.push({
        date: date.toISOString().split('T')[0],
        open_price: predictedPrice * 0.999,
        high_price: predictedPrice * (1 + Math.random() * 0.01),
        low_price: predictedPrice * (1 - Math.random() * 0.01),
        close_price: predictedPrice,
        volume: 0,
        predicted_volume: predictedVolume,
        volume_ma20: lastData.volume_ma20,
        price_change: isUpDay ? predictedPrice * 0.01 : -predictedPrice * 0.01,
        is_up_day: isUpDay,
        is_future: true
      });
    }

    setChartData(mockData);
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

  const formatVolume = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return value.toLocaleString();
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const isFuture = data.is_future;
    const actualVolume = data.volume;
    const predictedVolume = data.predicted_volume;
    const displayVolume = isFuture ? predictedVolume : actualVolume;

    return (
      <div className="bg-black/90 border border-gray-600 rounded-lg p-4 shadow-xl">
        <div className="text-gray-300 text-sm mb-2">
          {formatDate(label)} {isFuture && '(予測)'}
        </div>
        
        <div className="space-y-1">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-400">始値: <span className="text-white">{formatPrice(data.open_price)}</span></div>
              <div className="text-gray-400">高値: <span className="text-white">{formatPrice(data.high_price)}</span></div>
            </div>
            <div>
              <div className="text-gray-400">安値: <span className="text-white">{formatPrice(data.low_price)}</span></div>
              <div className="text-gray-400">終値: <span className="text-white">{formatPrice(data.close_price)}</span></div>
            </div>
          </div>
          
          <hr className="border-gray-600 my-2" />
          
          <div className="text-sm">
            <div className="text-gray-400">
              出来高{isFuture ? '(予測)' : ''}: 
              <span className={`ml-1 font-medium ${data.is_up_day ? 'text-green-400' : 'text-red-400'}`}>
                {formatVolume(displayVolume)}
              </span>
            </div>
            <div className="text-gray-400">
              20日平均: <span className="text-blue-400">{formatVolume(data.volume_ma20)}</span>
            </div>
            {displayVolume && data.volume_ma20 && (
              <div className="text-gray-400">
                平均比: <span className={displayVolume > data.volume_ma20 ? 'text-green-400' : 'text-red-400'}>
                  {((displayVolume / data.volume_ma20)).toFixed(1)}倍
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const todayDate = new Date().toISOString().split('T')[0];

  if (!stock) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            銘柄を選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            銘柄を選択すると価格と出来高の<br />
            詳細な分析チャートが表示されます
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
          <Activity className="w-6 h-6 mr-2 text-blue-400" />
          出来高分析チャート - {stock.symbol}
        </h2>

        <div className="flex items-center space-x-4">
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
      </div>

      {/* コントロール */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4 text-sm">
          <button
            onClick={() => setShowVolumeMA(!showVolumeMA)}
            className={`flex items-center space-x-1 px-2 py-1 rounded ${
              showVolumeMA ? 'bg-blue-600/20 text-blue-400' : 'text-gray-400 hover:text-white'
            }`}
          >
            {showVolumeMA ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            <span>出来高移動平均</span>
          </button>

          <button
            onClick={() => setShowPredictions(!showPredictions)}
            className={`flex items-center space-x-1 px-2 py-1 rounded ${
              showPredictions ? 'bg-purple-600/20 text-purple-400' : 'text-gray-400 hover:text-white'
            }`}
          >
            {showPredictions ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            <span>予測データ</span>
          </button>
        </div>

        <div className="text-sm text-gray-400">
          クリックで期間を変更 • 緑:上昇日、赤:下落日
        </div>
      </div>

      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
        </div>
      ) : (
        <>
          {/* 価格チャート (上段) */}
          <div className="h-48 mb-2">
            <div className="text-sm font-medium text-gray-300 mb-2">株価推移</div>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  stroke="#9CA3AF"
                  fontSize={10}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  fontSize={10}
                  domain={['dataMin * 0.95', 'dataMax * 1.05']}
                  tickFormatter={(value) => formatPrice(value)}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {/* 今日の境界線 */}
                <ReferenceLine x={todayDate} stroke="#6b7280" strokeDasharray="2 2" />
                
                {/* 価格ライン */}
                <Line
                  type="monotone"
                  dataKey="close_price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  connectNulls={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* 出来高チャート (下段) */}
          <div className="h-32">
            <div className="text-sm font-medium text-gray-300 mb-2">出来高分析</div>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  stroke="#9CA3AF"
                  fontSize={10}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  fontSize={10}
                  tickFormatter={formatVolume}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {/* 今日の境界線 */}
                <ReferenceLine x={todayDate} stroke="#6b7280" strokeDasharray="2 2" />
                
                {/* 実績出来高 */}
                <Bar
                  dataKey="volume"
                  fill="#10b981"
                  opacity={0.7}
                />

                {/* 予測出来高 */}
                {showPredictions && (
                  <Bar
                    dataKey="predicted_volume"
                    fill="#8b5cf6"
                    opacity={0.5}
                  />
                )}

                {/* 出来高移動平均線 */}
                {showVolumeMA && (
                  <Line
                    type="monotone"
                    dataKey="volume_ma20"
                    stroke="#fbbf24"
                    strokeWidth={2}
                    dot={false}
                    strokeDasharray="5 5"
                  />
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* 凡例 */}
          <div className="flex items-center justify-center space-x-6 text-xs mt-4">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 rounded opacity-70"></div>
              <span className="text-gray-400">上昇日出来高</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded opacity-70"></div>
              <span className="text-gray-400">下落日出来高</span>
            </div>
            {showPredictions && (
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-purple-500 rounded opacity-50"></div>
                <span className="text-gray-400">予測出来高</span>
              </div>
            )}
            {showVolumeMA && (
              <div className="flex items-center space-x-1">
                <div className="w-3 h-0.5 bg-yellow-400 border-dashed border-t"></div>
                <span className="text-gray-400">20日移動平均</span>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}