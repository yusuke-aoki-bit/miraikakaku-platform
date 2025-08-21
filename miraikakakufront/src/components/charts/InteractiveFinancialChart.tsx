'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import { 
  ComposedChart, 
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Brush,
  ReferenceLine,
  ReferenceArea
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Volume, 
  Activity,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

interface PriceData {
  timestamp: number;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_5?: number;
  sma_20?: number;
  sma_50?: number;
  ema_12?: number;
  ema_26?: number;
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  bollinger_upper?: number;
  bollinger_lower?: number;
  bollinger_middle?: number;
}

interface InteractiveFinancialChartProps {
  symbol: string;
  data: PriceData[];
  height?: number;
  showVolume?: boolean;
  showIndicators?: boolean;
  className?: string;
}

interface VisibleIndicators {
  sma_5: boolean;
  sma_20: boolean;
  sma_50: boolean;
  ema_12: boolean;
  ema_26: boolean;
  bollinger: boolean;
  volume: boolean;
}

const INDICATOR_COLORS = {
  sma_5: '#ff6b6b',
  sma_20: '#4ecdc4',
  sma_50: '#45b7d1',
  ema_12: '#96ceb4',
  ema_26: '#ffeaa7',
  bollinger_upper: '#fd79a8',
  bollinger_lower: '#fd79a8',
  bollinger_middle: '#fdcb6e',
  volume: '#74b9ff'
};

const generateMockData = (symbol: string): PriceData[] => {
  const data: PriceData[] = [];
  const basePrice = 2500;
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;

  for (let i = 90; i >= 0; i--) {
    const timestamp = now - (i * oneDay);
    const trend = Math.sin((90 - i) * 0.1) * 0.1;
    const volatility = (Math.random() - 0.5) * 0.05;
    const price = basePrice * (1 + trend + volatility);
    
    const open = price * (1 + (Math.random() - 0.5) * 0.02);
    const close = price * (1 + (Math.random() - 0.5) * 0.02);
    const high = Math.max(open, close) * (1 + Math.random() * 0.02);
    const low = Math.min(open, close) * (1 - Math.random() * 0.02);
    const volume = Math.floor(Math.random() * 1000000 + 500000);

    data.push({
      timestamp,
      date: new Date(timestamp).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' }),
      open,
      high,
      low,
      close,
      volume
    });
  }

  // Calculate technical indicators
  return data.map((point, index) => {
    const window5 = data.slice(Math.max(0, index - 4), index + 1);
    const window20 = data.slice(Math.max(0, index - 19), index + 1);
    const window50 = data.slice(Math.max(0, index - 49), index + 1);

    return {
      ...point,
      sma_5: window5.length >= 5 ? window5.reduce((sum, p) => sum + p.close, 0) / window5.length : undefined,
      sma_20: window20.length >= 20 ? window20.reduce((sum, p) => sum + p.close, 0) / window20.length : undefined,
      sma_50: window50.length >= 50 ? window50.reduce((sum, p) => sum + p.close, 0) / window50.length : undefined,
      ema_12: index >= 12 ? calculateEMA(data.slice(0, index + 1), 12) : undefined,
      ema_26: index >= 26 ? calculateEMA(data.slice(0, index + 1), 26) : undefined,
      rsi: index >= 14 ? calculateRSI(data.slice(Math.max(0, index - 13), index + 1)) : undefined,
      bollinger_upper: window20.length >= 20 ? calculateBollingerBands(window20).upper : undefined,
      bollinger_lower: window20.length >= 20 ? calculateBollingerBands(window20).lower : undefined,
      bollinger_middle: window20.length >= 20 ? calculateBollingerBands(window20).middle : undefined,
    };
  });
};

const calculateEMA = (data: PriceData[], period: number): number => {
  const multiplier = 2 / (period + 1);
  let ema = data[0].close;
  
  for (let i = 1; i < data.length; i++) {
    ema = (data[i].close * multiplier) + (ema * (1 - multiplier));
  }
  
  return ema;
};

const calculateRSI = (data: PriceData[]): number => {
  const gains: number[] = [];
  const losses: number[] = [];
  
  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? Math.abs(change) : 0);
  }
  
  const avgGain = gains.reduce((sum, gain) => sum + gain, 0) / gains.length;
  const avgLoss = losses.reduce((sum, loss) => sum + loss, 0) / losses.length;
  
  const rs = avgGain / avgLoss;
  return 100 - (100 / (1 + rs));
};

const calculateBollingerBands = (data: PriceData[]) => {
  const closes = data.map(d => d.close);
  const avg = closes.reduce((sum, close) => sum + close, 0) / closes.length;
  const variance = closes.reduce((sum, close) => sum + Math.pow(close - avg, 2), 0) / closes.length;
  const stdDev = Math.sqrt(variance);
  
  return {
    upper: avg + (stdDev * 2),
    middle: avg,
    lower: avg - (stdDev * 2)
  };
};

export default function InteractiveFinancialChart({
  symbol,
  data: initialData,
  height = 500,
  showVolume = true,
  showIndicators = true,
  className = ''
}: InteractiveFinancialChartProps) {
  const [data, setData] = useState<PriceData[]>([]);
  const [visibleIndicators, setVisibleIndicators] = useState<VisibleIndicators>({
    sma_5: false,
    sma_20: true,
    sma_50: true,
    ema_12: false,
    ema_26: false,
    bollinger: false,
    volume: showVolume
  });
  const [zoomDomain, setZoomDomain] = useState<{ start?: number; end?: number }>({});
  const [selectedPoint, setSelectedPoint] = useState<PriceData | null>(null);
  const [showCrosshair, setShowCrosshair] = useState(true);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialData.length > 0) {
      setData(initialData);
    } else {
      // Generate mock data for demonstration
      const mockData = generateMockData(symbol);
      setData(mockData);
    }
  }, [initialData, symbol]);

  const processedData = useMemo(() => {
    return data.filter(d => {
      if (!zoomDomain.start || !zoomDomain.end) return true;
      return d.timestamp >= zoomDomain.start && d.timestamp <= zoomDomain.end;
    });
  }, [data, zoomDomain]);

  const latestPrice = data[data.length - 1];
  const previousPrice = data[data.length - 2];
  const priceChange = latestPrice && previousPrice ? latestPrice.close - previousPrice.close : 0;
  const priceChangePercent = previousPrice ? (priceChange / previousPrice.close) * 100 : 0;

  const toggleIndicator = (indicator: keyof VisibleIndicators) => {
    setVisibleIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }));
  };

  const resetZoom = () => {
    setZoomDomain({});
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0]?.payload;
    if (!data) return null;

    return (
      <div className="bg-surface-card border border-border-default rounded-lg p-4 shadow-lg">
        <div className="text-text-primary font-medium mb-2">{label}</div>
        
        <div className="space-y-1 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-text-secondary">始値: <span className="text-text-primary font-mono">¥{data.open?.toLocaleString()}</span></div>
              <div className="text-text-secondary">終値: <span className="text-text-primary font-mono">¥{data.close?.toLocaleString()}</span></div>
            </div>
            <div>
              <div className="text-text-secondary">高値: <span className="text-text-primary font-mono">¥{data.high?.toLocaleString()}</span></div>
              <div className="text-text-secondary">安値: <span className="text-text-primary font-mono">¥{data.low?.toLocaleString()}</span></div>
            </div>
          </div>
          
          {data.volume && (
            <div className="text-text-secondary">出来高: <span className="text-text-primary font-mono">{data.volume.toLocaleString()}</span></div>
          )}

          {visibleIndicators.sma_20 && data.sma_20 && (
            <div className="text-text-secondary">SMA(20): <span className="text-text-primary font-mono">¥{data.sma_20.toLocaleString()}</span></div>
          )}

          {data.rsi && (
            <div className="text-text-secondary">RSI: <span className="text-text-primary font-mono">{data.rsi.toFixed(2)}</span></div>
          )}
        </div>
      </div>
    );
  };

  const CandlestickShape = (props: any) => {
    const { payload, x, y, width, height } = props;
    const { open, high, low, close } = payload;
    
    const isPositive = close >= open;
    const color = isPositive ? '#10b981' : '#ef4444';
    const bodyHeight = Math.abs(close - open) / (high - low) * height;
    const bodyY = y + (Math.max(close, open) - high) / (high - low) * height;
    
    return (
      <g>
        {/* Wick */}
        <line
          x1={x + width / 2}
          y1={y}
          x2={x + width / 2}
          y2={y + height}
          stroke={color}
          strokeWidth={1}
        />
        
        {/* Body */}
        <rect
          x={x + width * 0.2}
          y={bodyY}
          width={width * 0.6}
          height={bodyHeight}
          fill={isPositive ? 'transparent' : color}
          stroke={color}
          strokeWidth={1}
        />
      </g>
    );
  };

  return (
    <div className={`bg-surface-card border border-border-default rounded-2xl overflow-hidden ${className}`}>
      {/* Chart Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default">
        <div className="flex items-center space-x-4">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">{symbol}</h3>
            {latestPrice && (
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold text-text-primary">
                  ¥{latestPrice.close.toLocaleString()}
                </span>
                <div className={`flex items-center space-x-1 text-sm font-medium ${
                  priceChange >= 0 ? 'text-status-success' : 'text-status-danger'
                }`}>
                  {priceChange >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  <span>{priceChange >= 0 ? '+' : ''}¥{priceChange.toFixed(2)}</span>
                  <span>({priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowCrosshair(!showCrosshair)}
            className={`p-2 rounded-lg transition-colors ${
              showCrosshair 
                ? 'bg-brand-primary text-white' 
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
            }`}
            title="クロスヘア"
          >
            {showCrosshair ? <Eye size={16} /> : <EyeOff size={16} />}
          </button>

          <button
            onClick={resetZoom}
            className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
            title="ズームリセット"
          >
            <RotateCcw size={16} />
          </button>

          <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors">
            <Download size={16} />
          </button>
        </div>
      </div>

      {/* Indicators Panel */}
      {showIndicators && (
        <div className="p-4 border-b border-border-default bg-surface-elevated/30">
          <div className="flex items-center space-x-2 mb-3">
            <Activity size={16} className="text-text-secondary" />
            <span className="text-sm font-medium text-text-primary">テクニカル指標</span>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {Object.entries(visibleIndicators).map(([key, enabled]) => {
              const labels: Record<string, string> = {
                sma_5: 'SMA(5)',
                sma_20: 'SMA(20)',
                sma_50: 'SMA(50)',
                ema_12: 'EMA(12)',
                ema_26: 'EMA(26)',
                bollinger: 'ボリンジャーバンド',
                volume: '出来高'
              };

              return (
                <button
                  key={key}
                  onClick={() => toggleIndicator(key as keyof VisibleIndicators)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    enabled
                      ? 'bg-brand-primary text-white'
                      : 'bg-surface-elevated text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {labels[key]}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Chart */}
      <div ref={chartRef} style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={processedData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            onMouseMove={(e) => {
              if (e?.activePayload?.[0]) {
                setSelectedPoint(e.activePayload[0].payload);
              }
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" opacity={0.5} />
            
            <XAxis 
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-tertiary)' }}
            />
            
            <YAxis 
              yAxisId="price"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-tertiary)' }}
              tickFormatter={(value) => `¥${value.toLocaleString()}`}
              domain={['dataMin - 100', 'dataMax + 100']}
            />

            {visibleIndicators.volume && (
              <YAxis 
                yAxisId="volume"
                orientation="right"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: 'var(--text-tertiary)' }}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
              />
            )}

            <Tooltip content={<CustomTooltip />} />

            {/* Volume Bars */}
            {visibleIndicators.volume && (
              <Bar
                yAxisId="volume"
                dataKey="volume"
                fill={INDICATOR_COLORS.volume}
                opacity={0.3}
                name="出来高"
              />
            )}

            {/* Bollinger Bands */}
            {visibleIndicators.bollinger && (
              <>
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="bollinger_upper"
                  stroke={INDICATOR_COLORS.bollinger_upper}
                  strokeWidth={1}
                  dot={false}
                  strokeDasharray="3 3"
                />
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="bollinger_middle"
                  stroke={INDICATOR_COLORS.bollinger_middle}
                  strokeWidth={1}
                  dot={false}
                />
                <Line
                  yAxisId="price"
                  type="monotone"
                  dataKey="bollinger_lower"
                  stroke={INDICATOR_COLORS.bollinger_lower}
                  strokeWidth={1}
                  dot={false}
                  strokeDasharray="3 3"
                />
              </>
            )}

            {/* Moving Averages */}
            {Object.entries(visibleIndicators).map(([key, enabled]) => {
              if (!enabled || !key.includes('sma') && !key.includes('ema')) return null;
              
              return (
                <Line
                  key={key}
                  yAxisId="price"
                  type="monotone"
                  dataKey={key}
                  stroke={INDICATOR_COLORS[key as keyof typeof INDICATOR_COLORS]}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              );
            })}

            {/* Price Line */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke="var(--brand-primary)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: 'var(--brand-primary)' }}
            />

            <Brush 
              dataKey="date" 
              height={30}
              stroke="var(--brand-primary)"
              fill="var(--surface-elevated)"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}