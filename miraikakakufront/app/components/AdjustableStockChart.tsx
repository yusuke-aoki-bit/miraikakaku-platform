'use client';

import React, { useMemo, useState, useRef, useCallback } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
  Brush
} from 'recharts';
import { format, parseISO, subDays, isAfter } from 'date-fns';
import {
  Settings,
  TrendingUp,
  Calendar,
  BarChart3,
  LineChart as LineChartIcon,
  Activity,
  Maximize2,
  Minimize2,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCcw
} from 'lucide-react';
import { StockPrice, StockPrediction, HistoricalPrediction } from '../types';
import { ChartLoader } from './LoadingSpinner';
import { useTranslation } from 'react-i18next';

interface StockChartProps {
  priceHistory: StockPrice[];
  predictions: StockPrediction[];
  historicalPredictions: HistoricalPrediction[];
}

type ChartType = 'line' | 'area' | 'bar' | 'candlestick' | 'mixed';
type Period = '1W' | '1M' | '3M' | '6M' | '1Y' | '2Y' | 'ALL';

export default function AdjustableStockChart({
  priceHistory,
  predictions,
  historicalPredictions
}: StockChartProps) {
  const { t } = useTranslation('common');
  // Chart control states
  const [chartType, setChartType] = useState<ChartType>('line');
  const [selectedPeriod, setSelectedPeriod] = useState<Period>('1M');
  const [showVolume, setShowVolume] = useState(false);
  const [showPredictions, setShowPredictions] = useState(true);
  const [showHistoricalPredictions, setShowHistoricalPredictions] = useState(true);
  const [showMovingAverage, setShowMovingAverage] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null);
  const [brushStartIndex, setBrushStartIndex] = useState<number | null>(null);
  const [brushEndIndex, setBrushEndIndex] = useState<number | null>(null);
  const chartRef = useRef<any>(null);
  // Calculate moving average
  const calculateMovingAverage = (data: any[], period: number = 20) => {
    return data.map((item, index) => {
      if (index < period - 1) return { ...item, ma20: null };

      const sum = data
        .slice(index - period + 1, index + 1)
        .reduce((acc, curr) => acc + (curr.actual || 0), 0);
      return { ...item, ma20: sum / period };
    });
  };

  // Filter data based on selected period
  const filterDataByPeriod = useCallback((data: any[]) => {
    const now = new Date();
    let startDate: Date;

    switch (selectedPeriod) {
      case '1W':
        startDate = subDays(now, 7);
        break;
      case '1M':
        startDate = subDays(now, 30);
        break;
      case '3M':
        startDate = subDays(now, 90);
        break;
      case '6M':
        startDate = subDays(now, 180);
        break;
      case '1Y':
        startDate = subDays(now, 365);
        break;
      case '2Y':
        startDate = subDays(now, 730);
        break;
      case 'ALL':
      default:
        return data;
    }

    return data.filter(item => {
      const itemDate = parseISO(item.date);
      return isAfter(itemDate, startDate);
    });
  }, [selectedPeriod]);
  // Zoom and pan handlers
  const handleZoomIn = useCallback(() => {
    setZoomLevel(prev => Math.min(prev * 1.5, 10));
  }, []);
  const handleZoomOut = useCallback(() => {
    setZoomLevel(prev => Math.max(prev / 1.5, 1));
  }, []);
  const handleResetZoom = useCallback(() => {
    setZoomLevel(1);
    setZoomDomain(null);
    setBrushStartIndex(null);
    setBrushEndIndex(null);
  }, []);
  const handleBrushChange = useCallback((brushData: any) => {
    if (brushData) {
      setBrushStartIndex(brushData.startIndex);
      setBrushEndIndex(brushData.endIndex);
    }
  }, []);
  const chartData = useMemo(() => {
    if (!priceHistory || priceHistory.length === 0) {
      return [];
    }
    const dataMap = new Map();
    // Add price history
    if (Array.isArray(priceHistory)) {
      priceHistory.forEach(price => {
        if (price && price.date && price.close_price !== null) {
          // For candlestick charts, ensure we have OHLC data
          // If not available, simulate them from close price
          const closePrice = price.close_price;
          const open = price.open_price || closePrice;
          const high = price.high_price || closePrice * 1.02; // Simulate 2% variation
          const low = price.low_price || closePrice * 0.98;

          dataMap.set(price.date, {
            date: price.date,
            actual: closePrice,
            close: closePrice,
            open: open,
            high: Math.max(high, open, closePrice),
            low: Math.min(low, open, closePrice),
            volume: price.volume || 0
          });
        }
      });
    }

    // Add predictions
    if (showPredictions && Array.isArray(predictions)) {
      predictions.forEach(pred => {
        if (pred && pred.prediction_date) {
          const existing = dataMap.get(pred.prediction_date) || {};
          dataMap.set(pred.prediction_date, {
            ...existing,
            date: pred.prediction_date,
            predicted: pred.predicted_price
          });
        }
      });
    }

    // Add historical predictions
    if (showHistoricalPredictions && Array.isArray(historicalPredictions)) {
      historicalPredictions.forEach(pred => {
        // Use target_date instead of actual_date for compatibility
        const dateKey = pred?.target_date || pred?.actual_date;
        if (pred && dateKey) {
          const existing = dataMap.get(dateKey) || {};
          dataMap.set(dateKey, {
            ...existing,
            date: dateKey,
            pastPredicted: pred.predicted_price
          });
        }
      });
    }

    // Convert to array and sort
    let data = Array.from(dataMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    // Add moving average if enabled
    if (showMovingAverage) {
      data = calculateMovingAverage(data);
    }

    // Filter by period
    const filteredData = filterDataByPeriod(data);
    return filteredData;
  }, [priceHistory, predictions, historicalPredictions, showPredictions, showHistoricalPredictions, showMovingAverage, selectedPeriod, filterDataByPeriod]);
  // Export data functionality
  const exportToCSV = useCallback(() => {
    const csvData = chartData.map(item => ({
      Date: item.date,
      'Actual Price': item.actual || '',
      'Predicted Price': item.predicted || '',
      'Past Predicted': item.pastPredicted || '',
      'Moving Average': item.ma20 || '',
      Volume: item.volume || '',
      Open: item.open || '',
      High: item.high || '',
      Low: item.low || ''
    }));
    if (csvData.length === 0) return;

    const firstRow = csvData[0];
    if (!firstRow) return;

    const csvContent = [
      Object.keys(firstRow).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `stock-data-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [chartData]);
  const exportToJSON = useCallback(() => {
    const jsonData = {
      metadata: {
        exportDate: new Date().toISOString(),
        period: selectedPeriod,
        chartType: chartType,
        dataPoints: chartData.length
      },
      data: chartData
    };

    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `stock-data-${new Date().toISOString().split('T')[0]}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [chartData, selectedPeriod, chartType]);
  // Show loading if no price history data
  if (!priceHistory || priceHistory.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center">
        <div className="text-center">
          <ChartLoader />
          <p className="mt-4 text-gray-600">{t('loading.chart')}</p>
        </div>
      </div>
    );
  }

  const formatTooltipValue = (value: number, name: string) => {
    if (name === 'volume') return value.toLocaleString();
    return `¥${value.toFixed(2)}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="p-3 border rounded shadow-lg" style={{
          backgroundColor: '#0f0f0f',
          borderColor: '#333333',
          color: '#f1f1f1'
        }}>
          <p className="font-semibold" style={{ color: '#f1f1f1' }}>
            {format(parseISO(label), 'yyyy/MM/dd')}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {formatTooltipValue(entry.value, entry.dataKey)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Period selection buttons
  const periodButtons: Period[] = ['1W', '1M', '3M', '6M', '1Y', '2Y', 'ALL'];

  // Chart type buttons
  const chartTypes: { type: ChartType; icon: React.ReactNode; label: string }[] = [
    { type: 'line', icon: <LineChartIcon className="w-4 h-4" />, label: 'ライン' },
    { type: 'area', icon: <BarChart3 className="w-4 h-4" />, label: 'エリア' },
    { type: 'bar', icon: <Activity className="w-4 h-4" />, label: 'バー' },
    { type: 'candlestick', icon: <TrendingUp className="w-4 h-4" />, label: 'ローソク足' }
  ];

  const renderChart = () => {
    const priceChartProps = {
      data: chartData,
      margin: { top: 10, right: 40, left: 60, bottom: 10 }
    };

    const volumeChartProps = {
      data: chartData,
      margin: { top: 5, right: 40, left: 60, bottom: 30 }
    };

    // Stock chart layout with price and volume
    if (showVolume) {
      return (
        <div className="space-y-4 w-full">
          {/* Main Price Chart */}
          <div style={{ height: '380px', width: '100%' }} className="overflow-hidden">
            {renderPriceChart(priceChartProps)}
          </div>
          {/* Volume Chart */}
          <div style={{ height: '140px', width: '100%' }} className="overflow-hidden">
            {renderVolumeChart(volumeChartProps)}
          </div>
        </div>
      );
    }

    return (
      <div style={{ height: '500px', width: '100%' }} className="overflow-hidden">
        {renderPriceChart(priceChartProps)}
      </div>
    );
  };

  const renderPriceChart = (commonProps: any) => {
    switch (chartType) {
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <YAxis
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                color: '#f1f1f1',
                paddingTop: '20px'
              }}
            />
            <Area type="monotone" dataKey="actual" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} name="実際の価格" />
            {showMovingAverage && <Area type="monotone" dataKey="ma20" stroke="#ffc658" fill="#ffc658" fillOpacity={0.3} name="20日移動平均" />}
            {showPredictions && <Area type="monotone" dataKey="predicted" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} name="AI予測" />}
            {showHistoricalPredictions && <Area type="monotone" dataKey="pastPredicted" stroke="#ff7c7c" fill="#ff7c7c" fillOpacity={0.6} name="過去の予測" />}
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <YAxis
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                color: '#f1f1f1',
                paddingTop: '20px'
              }}
            />
            <Bar dataKey="actual" fill="#8884d8" name="実際の価格" />
            {showMovingAverage && <Line type="monotone" dataKey="ma20" stroke="#ffc658" strokeDasharray="5 5" dot={false} name="20日移動平均" />}
            {showPredictions && <Line type="monotone" dataKey="predicted" stroke="#82ca9d" strokeWidth={2} strokeDasharray="5 5" dot={false} name="AI予測" />}
            {showHistoricalPredictions && <Line type="monotone" dataKey="pastPredicted" stroke="#ff7c7c" strokeWidth={1} strokeDasharray="3 3" dot={false} name="過去の予測" />}
            </ComposedChart>
          </ResponsiveContainer>
        );
      case 'candlestick':
        // Custom candlestick shape component
        const Candlestick = (props: any) => {
          const { payload, x, y, width } = props;
          if (!payload || typeof payload.open !== 'number' || typeof payload.close !== 'number' ||
              typeof payload.high !== 'number' || typeof payload.low !== 'number') {
            return <g />;
          }

          const { open, close, high, low } = payload;
          const isRising = close >= open;
          const color = isRising ? '#10b981' : '#ef4444'; // Green for rising, red for falling

          // Find the scale from the chart
          const yScale = props.yScale || ((val: number) => y + (1 - (val - low) / (high - low)) * 100);
          // Calculate positions
          const centerX = x + width / 2;
          const openY = yScale(open);
          const closeY = yScale(close);
          const highY = yScale(high);
          const lowY = yScale(low);
          const bodyTop = Math.min(openY, closeY);
          const bodyBottom = Math.max(openY, closeY);
          const bodyHeight = Math.abs(bodyBottom - bodyTop) || 2; // Minimum height of 2px

          return (
            <g>
              {/* High-Low line (wick) */}
              <line
                x1={centerX}
                y1={highY}
                x2={centerX}
                y2={lowY}
                stroke={color}
                strokeWidth={1}
              />
              {/* Body rectangle */}
              <rect
                x={x + width * 0.25}
                y={bodyTop}
                width={width * 0.5}
                height={bodyHeight}
                fill={isRising ? 'transparent' : color}
                stroke={color}
                strokeWidth={1.5}
              />
            </g>
          );
        };

        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <YAxis
              domain={['dataMin - 1', 'dataMax + 1']}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                color: '#f1f1f1',
                paddingTop: '20px'
              }}
            />
            {/* Use scatter plot with custom candlestick shape */}
            <Bar
              dataKey="close"
              shape={Candlestick}
              fill="transparent"
              name="ローソク足"
            />
            {showMovingAverage && <Line type="monotone" dataKey="ma20" stroke="#ffc658" strokeDasharray="5 5" dot={false} name="20日移動平均" />}
            {showPredictions && <Line type="monotone" dataKey="predicted" stroke="#82ca9d" strokeWidth={2} strokeDasharray="5 5" dot={false} name="AI予測" />}
            </ComposedChart>
          </ResponsiveContainer>
        );
      case 'line':
      default:
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart {...commonProps} ref={chartRef}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
              domain={zoomDomain || ['dataMin', 'dataMax']}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <YAxis
              domain={['dataMin', 'dataMax']}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                color: '#f1f1f1',
                paddingTop: '20px'
              }}
            />
            <ReferenceLine y={0} stroke="#666" />
            <Line type="monotone" dataKey="actual" stroke="#8884d8" strokeWidth={2} dot={false} name="実際の価格" />
            {showMovingAverage && <Line type="monotone" dataKey="ma20" stroke="#ffc658" strokeWidth={1} strokeDasharray="5 5" dot={false} name="20日移動平均" />}
            {showPredictions && <Line type="monotone" dataKey="predicted" stroke="#82ca9d" strokeWidth={2} strokeDasharray="5 5" dot={false} name="AI予測" />}
            {showHistoricalPredictions && <Line type="monotone" dataKey="pastPredicted" stroke="#ff7c7c" strokeWidth={1} strokeDasharray="3 3" dot={false} name="過去の予測" />}
            <Brush
              dataKey="date"
              height={30}
              stroke="#8884d8"
              onChange={handleBrushChange}
              startIndex={brushStartIndex ?? 0}
              endIndex={brushEndIndex ?? chartData.length - 1}
            />
            </LineChart>
          </ResponsiveContainer>
        );
    }
  };

  const renderVolumeChart = (commonProps: any) => {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart {...commonProps}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333333" opacity={0.3} />
        <XAxis
          dataKey="date"
          tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
          tick={{ fill: '#aaaaaa', fontSize: 10 }}
          axisLine={{ stroke: '#333333' }}
          tickLine={{ stroke: '#333333' }}
          height={30}
        />
        <YAxis
          tick={{ fill: '#aaaaaa', fontSize: 10 }}
          axisLine={{ stroke: '#333333' }}
          tickLine={{ stroke: '#333333' }}
          width={50}
          tickFormatter={(value) => {
            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
            return value.toString();
          }}
        />
        <Tooltip
          formatter={(value: any) => [
            typeof value === 'number' ? value.toLocaleString() : value,
            '出来高'
          ]}
          labelFormatter={(label) => `日付: ${format(parseISO(label), 'yyyy/MM/dd')}`}
          contentStyle={{
            backgroundColor: '#0f0f0f',
            border: '1px solid #333333',
            borderRadius: '8px',
            color: '#f1f1f1'
          }}
        />
        <Bar
          dataKey="volume"
          fill="#ffc658"
          opacity={0.7}
          name="出来高"
        />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div
      className={`relative ${isFullscreen ? 'fixed inset-0 z-50 p-4' : ''}`}
      style={isFullscreen ? { backgroundColor: '#111111' } : {}}
    >
      {/* Controls Header */}
      <div className="mb-4 space-y-4">
        {/* Period Selection */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5" style={{ color: '#aaaaaa' }} />
            <div className="flex space-x-1">
              {periodButtons.map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className="px-3 py-1 text-sm rounded-lg transition-colors"
                  style={{
                    backgroundColor: selectedPeriod === period ? '#3b82f6' : '#333333',
                    color: selectedPeriod === period ? '#ffffff' : '#f1f1f1',
                    border: '1px solid #555555'
                  }}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 rounded-lg p-1" style={{ backgroundColor: '#333333' }}>
              <button
                onClick={handleZoomIn}
                className="p-1 rounded transition-colors"
                style={{ backgroundColor: 'transparent', color: '#f1f1f1' }}
                title="ズームイン"
                disabled={zoomLevel >= 10}
              >
                <ZoomIn className="w-3 h-3" />
              </button>
              <span className="text-xs px-2" style={{ color: '#f1f1f1' }}>{Math.round(zoomLevel * 100)}%</span>
              <button
                onClick={handleZoomOut}
                className="p-1 rounded transition-colors"
                style={{ backgroundColor: 'transparent', color: '#f1f1f1' }}
                title="ズームアウト"
                disabled={zoomLevel <= 1}
              >
                <ZoomOut className="w-3 h-3" />
              </button>
              <button
                onClick={handleResetZoom}
                className="p-1 rounded transition-colors"
                style={{ backgroundColor: 'transparent', color: '#f1f1f1' }}
                title="ズームリセット"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
            </div>

            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={exportToCSV}
                className="p-2 rounded-lg transition-colors"
                style={{ backgroundColor: '#333333', color: '#f1f1f1' }}
                title="CSVエクスポート"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>

            {/* Settings and Fullscreen Toggle */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-lg transition-colors"
              style={{ backgroundColor: '#333333', color: '#f1f1f1' }}
              title="設定"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg transition-colors"
              style={{ backgroundColor: '#333333', color: '#f1f1f1' }}
              title={isFullscreen ? '通常表示' : '全画面表示'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Advanced Settings Panel */}
        {showSettings && (
          <div className="p-4 rounded-lg space-y-3" style={{ backgroundColor: '#222222' }}>
            {/* Chart Type Selection */}
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium" style={{ color: '#f1f1f1' }}>チャートタイプ:</span>
              <div className="flex space-x-2">
                {chartTypes.map(({ type, icon, label }) => (
                  <button
                    key={type}
                    onClick={() => setChartType(type)}
                    className="flex items-center space-x-1 px-3 py-1 text-sm rounded-lg transition-colors"
                    style={{
                      backgroundColor: chartType === type ? '#3b82f6' : '#333333',
                      color: chartType === type ? '#ffffff' : '#f1f1f1',
                      border: '1px solid #555555'
                    }}
                    title={label}
                  >
                    {icon}
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Indicator Toggles */}
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium" style={{ color: '#f1f1f1' }}>表示設定:</span>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showPredictions}
                  onChange={(e) => setShowPredictions(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm" style={{ color: '#f1f1f1' }}>AI予測</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showHistoricalPredictions}
                  onChange={(e) => setShowHistoricalPredictions(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm" style={{ color: '#f1f1f1' }}>過去の予測</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showMovingAverage}
                  onChange={(e) => setShowMovingAverage(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm" style={{ color: '#f1f1f1' }}>移動平均線</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showVolume}
                  onChange={(e) => setShowVolume(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm" style={{ color: '#f1f1f1' }}>出来高</span>
              </label>
            </div>

            {/* Export Options */}
            <div className="flex items-center space-x-4 pt-2" style={{ borderTop: '1px solid #555555' }}>
              <span className="text-sm font-medium" style={{ color: '#f1f1f1' }}>エクスポート:</span>
              <div className="flex space-x-2">
                <button
                  onClick={exportToCSV}
                  className="px-3 py-1 text-sm rounded-lg transition-colors"
                  style={{ backgroundColor: '#16a34a', color: '#ffffff' }}
                >
                  CSV形式
                </button>
                <button
                  onClick={exportToJSON}
                  className="px-3 py-1 text-sm rounded-lg transition-colors"
                  style={{ backgroundColor: '#2563eb', color: '#ffffff' }}
                >
                  JSON形式
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex items-center space-x-6 pt-2" style={{ borderTop: '1px solid #555555' }}>
              <div className="text-sm">
                <span style={{ color: '#aaaaaa' }}>データ期間:</span>
                <span className="ml-2 font-medium" style={{ color: '#f1f1f1' }}>{chartData.length}日分</span>
              </div>
              <div className="text-sm">
                <span style={{ color: '#aaaaaa' }}>最高値:</span>
                <span className="ml-2 font-medium" style={{ color: '#10b981' }}>
                  ${Math.max(...chartData.map(d => d.actual || 0)).toFixed(2)}
                </span>
              </div>
              <div className="text-sm">
                <span style={{ color: '#aaaaaa' }}>最安値:</span>
                <span className="ml-2 font-medium" style={{ color: '#ef4444' }}>
                  ${Math.min(...chartData.filter(d => d.actual).map(d => d.actual)).toFixed(2)}
                </span>
              </div>
              <div className="text-sm">
                <span style={{ color: '#aaaaaa' }}>ズーム:</span>
                <span className="ml-2 font-medium" style={{ color: '#f1f1f1' }}>{Math.round(zoomLevel * 100)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Warning Messages */}
      {(showPredictions && predictions.length === 0) && (
        <div className="mb-4 p-3 rounded-lg border-l-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20">
          <div className="flex items-center">
            <div className="text-yellow-600 dark:text-yellow-400">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                {t('chart.warnings.noFuturePredictions', '未来の予測データがありません。AI予測機能を利用するには、最新の予測データが必要です。')}
              </p>
            </div>
          </div>
        </div>
      )}

      {(showHistoricalPredictions && historicalPredictions.length === 0) && (
        <div className="mb-4 p-3 rounded-lg border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20">
          <div className="flex items-center">
            <div className="text-blue-600 dark:text-blue-400">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {t('chart.warnings.noHistoricalPredictions', '過去の予測データがありません。予測精度の評価には、過去の予測履歴が必要です。')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className={isFullscreen ? 'h-[calc(100vh-200px)]' : 'h-auto'} style={{ minHeight: showVolume ? '520px' : '500px' }}>
        {renderChart()}
      </div>

      {/* Chart Legend for mobile */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm md:hidden">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-500"></div>
          <span>実際の価格</span>
        </div>
        {showPredictions && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500"></div>
            <span>AI予測</span>
          </div>
        )}
        {showHistoricalPredictions && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500"></div>
            <span>過去の予測</span>
          </div>
        )}
        {showMovingAverage && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-yellow-500"></div>
            <span>20日移動平均</span>
          </div>
        )}
      </div>
    </div>
  );
}
