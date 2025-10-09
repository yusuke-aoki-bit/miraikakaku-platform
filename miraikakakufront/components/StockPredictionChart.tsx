'use client';

import { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Brush } from 'recharts';
import { StockPrice, StockPrediction } from '@/lib/api';

interface StockPredictionChartProps {
  priceHistory: StockPrice[];
  predictions: StockPrediction[];
  symbol: string;
}

interface ChartDataPoint {
  date: string;
  dateObj: Date;
  actual_price?: number;
  past_predicted_price?: number;
  future_predicted_price?: number;
  displayDate?: string;
}

export default function StockPredictionChart({ priceHistory, predictions }: StockPredictionChartProps) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Chart controls state
  const [dateRange, setDateRange] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('6M');
  const [yAxisScale, setYAxisScale] = useState<'auto' | 'dataMin' | 'dataMax'>('auto');
  const [showBrush, setShowBrush] = useState(false);

  // すべての予測データを使用（prediction_daysフィルタなし）
  const dailyPredictions = predictions;

  // デバッグログ
  console.log('=== StockPredictionChart Debug ===');
  console.log('Today:', today.toISOString().split('T')[0]);
  console.log('Total predictions:', predictions.length);
  console.log('Using all predictions');
  console.log('Price history:', priceHistory.length);

  // チャート用のデータポイントを作成
  const chartData = useMemo<ChartDataPoint[]>(() => {
    const data: ChartDataPoint[] = [];
    const dateSet = new Set<string>();
    let pastCount = 0;
    let futureCount = 0;

    // 1. 実際の価格データを追加
    priceHistory.forEach(p => {
      const dateObj = new Date(p.date);
      dateObj.setHours(0, 0, 0, 0);
      dateSet.add(p.date);
      data.push({
        date: p.date,
        dateObj: dateObj,
        actual_price: p.close_price,
      });
    });

    // 2. 予測データを追加
    dailyPredictions.forEach(pred => {
      const predDate = new Date(pred.prediction_date);
      predDate.setHours(0, 0, 0, 0);
      const isPast = predDate <= today; // 今日を過去に含める
      const predDateStr = pred.prediction_date;

      if (isPast) pastCount++;
      else futureCount++;

      // データポイントを探すか作成
      let dataPoint = data.find(d => d.date === predDateStr);

      if (!dataPoint) {
        // 新しいデータポイントを作成
        dataPoint = {
          date: predDateStr,
          dateObj: predDate,
        };
        dateSet.add(predDateStr);
        data.push(dataPoint);
      }

      // 予測値を追加
      if (isPast) {
        dataPoint.past_predicted_price = pred.predicted_price;
      } else {
        dataPoint.future_predicted_price = pred.predicted_price;
      }
    });

    // 日付でソート
    data.sort((a, b) => a.dateObj.getTime() - b.dateObj.getTime());

    console.log('Past predictions:', pastCount);
    console.log('Future predictions:', futureCount);
    console.log('Chart data points:', data.length);

    return data;
  }, [priceHistory, dailyPredictions, today]);

  // 日付範囲フィルタリング
  const filteredData = useMemo(() => {
    if (dateRange === 'ALL') return chartData;

    const todayForFilter = new Date();
    todayForFilter.setHours(0, 0, 0, 0);
    const startDate = new Date(todayForFilter);

    switch (dateRange) {
      case '1M':
        startDate.setMonth(todayForFilter.getMonth() - 1);
        break;
      case '3M':
        startDate.setMonth(todayForFilter.getMonth() - 3);
        break;
      case '6M':
        startDate.setMonth(todayForFilter.getMonth() - 6);
        break;
      case '1Y':
        startDate.setFullYear(todayForFilter.getFullYear() - 1);
        break;
    }

    return chartData.filter(d => d.dateObj >= startDate);
  }, [chartData, dateRange]);

  // データポイントのサンプルを確認
  const samplePoints = chartData.slice(0, 5).map(d => ({
    date: d.date,
    actual: d.actual_price,
    past_pred: d.past_predicted_price,
    future_pred: d.future_predicted_price
  }));
  console.log('Sample chart data (first 5):', samplePoints);

  // 9月25日〜30日のデータを確認（実際の価格と過去予測が両方あるはず）
  const sepData = chartData.filter(d => d.date >= '2025-09-25' && d.date <= '2025-09-30');
  console.log('Sep 25-30 data:', sepData.map(d => ({
    date: d.date,
    actual: d.actual_price,
    past_pred: d.past_predicted_price
  })));

  // 実際の価格データがある件数
  const actualPriceCount = chartData.filter(d => d.actual_price !== undefined).length;
  const pastPredCount = chartData.filter(d => d.past_predicted_price !== undefined).length;
  const futurePredCount = chartData.filter(d => d.future_predicted_price !== undefined).length;
  console.log(`Data with actual_price: ${actualPriceCount}`);
  console.log(`Data with past_predicted_price: ${pastPredCount}`);
  console.log(`Data with future_predicted_price: ${futurePredCount}`);

  // 日付をフォーマット
  const formattedData = useMemo(() => {
    return filteredData.map(item => ({
      ...item,
      displayDate: new Date(item.date).toLocaleDateString('ja-JP', {
        month: 'short',
        day: 'numeric'
      }),
    }));
  }, [filteredData]);

  // 今日の日付
  const todayStr = today.toISOString().split('T')[0];

  // X軸のラベル間隔を自動計算（データ量に応じて調整）
  const calculateXAxisInterval = (dataLength: number) => {
    if (dataLength <= 30) return 0; // 30日以下：全て表示
    if (dataLength <= 60) return 2; // 60日以下：2日おき
    if (dataLength <= 90) return 4; // 90日以下：4日おき
    if (dataLength <= 180) return 7; // 180日以下：1週間おき
    if (dataLength <= 365) return 14; // 1年以下：2週間おき
    return 30; // 1年超：1ヶ月おき
  };

  const xAxisInterval = calculateXAxisInterval(formattedData.length);

  // Y軸のドメイン設定
  const getYAxisDomain = () => {
    if (yAxisScale === 'auto') return ['auto', 'auto'];
    if (yAxisScale === 'dataMin') return ['dataMin', 'auto'];
    return ['auto', 'dataMax'];
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
            株価チャート
          </h3>

          {/* Chart Controls */}
          <div className="flex flex-col gap-3">
            {/* Date Range Selector */}
            <div className="flex gap-2">
              <span className="text-xs text-gray-600 dark:text-gray-400 self-center mr-2">期間:</span>
              {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map(range => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={`px-3 py-1 text-xs rounded ${
                    dateRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>

            {/* Y-axis Scale Selector */}
            <div className="flex gap-2">
              <span className="text-xs text-gray-600 dark:text-gray-400 self-center mr-2">Y軸:</span>
              {([
                { value: 'auto', label: '自動' },
                { value: 'dataMin', label: '最小から' },
                { value: 'dataMax', label: '最大まで' }
              ] as const).map(option => (
                <button
                  key={option.value}
                  onClick={() => setYAxisScale(option.value)}
                  className={`px-3 py-1 text-xs rounded ${
                    yAxisScale === option.value
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>

            {/* Brush Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setShowBrush(!showBrush)}
                className={`px-3 py-1 text-xs rounded ${
                  showBrush
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {showBrush ? 'ズーム表示中' : 'ズームバー表示'}
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-4 text-sm mb-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-blue-600"></div>
            <span className="text-gray-600 dark:text-gray-400">実際の価格</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-orange-500" style={{ borderTop: '2px dashed' }}></div>
            <span className="text-gray-600 dark:text-gray-400">過去予測</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-green-500" style={{ borderTop: '2px dashed' }}></div>
            <span className="text-gray-600 dark:text-gray-400">未来予測</span>
          </div>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400">
          表示期間: {formattedData.length}日分 | ※ 過去予測は実際の価格に重なって表示されます（精度比較用）
        </div>
      </div>

      <div className="w-full h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={formattedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis
              dataKey="displayDate"
              stroke="#6B7280"
              style={{ fontSize: '11px' }}
              angle={-45}
              textAnchor="end"
              height={80}
              interval={xAxisInterval}
            />
            <YAxis
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              domain={getYAxisDomain()}
              tickFormatter={(value) => `¥${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
              formatter={(value: number, name: string) => {
                if (typeof value === 'number') {
                  return [`¥${value.toLocaleString()}`, name];
                }
                return [value, name];
              }}
            />
            <Legend />

            {/* 今日の基準線 */}
            <ReferenceLine
              x={todayStr}
              stroke="#EF4444"
              strokeDasharray="3 3"
              label={{ value: '今日', position: 'top', fill: '#EF4444' }}
            />

            {/* 実際の価格（青・実線） */}
            <Line
              type="monotone"
              dataKey="actual_price"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
              name="実際の価格"
              activeDot={{ r: 6 }}
              connectNulls={true}
            />

            {/* 過去予測（オレンジ・破線） - 実際の価格に重なる */}
            <Line
              type="monotone"
              dataKey="past_predicted_price"
              stroke="#F97316"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3 }}
              name="過去予測"
              connectNulls={true}
            />

            {/* 未来予測（緑・破線） */}
            <Line
              type="monotone"
              dataKey="future_predicted_price"
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3 }}
              name="未来予測"
              connectNulls={true}
            />

            {/* Brush for zooming */}
            {showBrush && (
              <Brush
                dataKey="displayDate"
                height={30}
                stroke="#8884d8"
                fill="#374151"
                travellerWidth={10}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>
          <strong>青色実線</strong>: 実際の株価推移<br />
          <strong>オレンジ破線</strong>: 過去の予測（実際の価格に重ねて表示、ずれが精度を示す）<br />
          <strong>緑破線</strong>: 未来予測（今日以降）<br />
          赤い点線が「今日」を示します。過去予測と実際の価格が近いほど予測精度が高いことを意味します。
        </p>
      </div>
    </div>
  );
}
