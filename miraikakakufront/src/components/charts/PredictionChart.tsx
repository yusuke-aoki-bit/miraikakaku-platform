'use client';

import { useState, useMemo, useRef } from 'react';
import { 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  ComposedChart,
  ReferenceLine,
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Info,
  Eye,
  EyeOff,
  Settings,
  Download,
  RotateCcw
} from 'lucide-react';

interface PredictionDataPoint {
  timestamp: number;
  date: string;
  actual_price?: number;
  predicted_price: number;
  confidence_90_lower: number;
  confidence_90_upper: number;
  confidence_95_lower: number;
  confidence_95_upper: number;
  confidence_99_lower: number;
  confidence_99_upper: number;
  model_confidence: number;
  volume?: number;
  prediction_type: 'historical' | 'forecast';
}

interface ModelMetadata {
  model_name: string;
  accuracy: number;
  r_squared: number;
  mae: number;
  last_trained: string;
  feature_importance: { [key: string]: number };
  data_freshness: number; // hours
}

interface PredictionChartProps {
  symbol: string;
  data: PredictionDataPoint[];
  metadata: ModelMetadata;
  className?: string;
  height?: number;
  showControls?: boolean;
  onTimeRangeChange?: (start: number, end: number) => void;
}

const CONFIDENCE_LEVELS = [
  { level: 90, color: '#10b981', opacity: 0.15, stroke: '#059669' },
  { level: 95, color: '#f59e0b', opacity: 0.1, stroke: '#d97706' },
  { level: 99, color: '#ef4444', opacity: 0.05, stroke: '#dc2626' }
];

const QUALITY_THRESHOLDS = {
  high: 0.8,
  medium: 0.6,
  low: 0.4
};

export default function PredictionChart({
  symbol,
  data,
  metadata,
  className = '',
  height = 400,
  showControls = true
}: PredictionChartProps) {
  const [visibleConfidenceLevels, setVisibleConfidenceLevels] = useState([90, 95]);
  const [showActualPrices, setShowActualPrices] = useState(true);
  const chartRef = useRef<HTMLDivElement>(null);

  const processedData = useMemo(() => {
    return data.map(point => ({
      ...point,
      formattedDate: new Date(point.timestamp).toLocaleDateString('ja-JP', {
        month: 'short',
        day: 'numeric'
      }),
      qualityLevel: getQualityLevel(point.model_confidence)
    }));
  }, [data]);

  const currentPrice = useMemo(() => {
    const latestActual = processedData
      .filter(d => d.actual_price !== undefined)
      .pop();
    return latestActual?.actual_price || 0;
  }, [processedData]);

  const prediction = useMemo(() => {
    const latestPrediction = processedData
      .filter(d => d.prediction_type === 'forecast')
      .shift();
    
    if (!latestPrediction) return null;

    const change = ((latestPrediction.predicted_price - currentPrice) / currentPrice) * 100;
    const direction = change >= 0 ? 'up' : 'down';
    
    return {
      price: latestPrediction.predicted_price,
      change,
      direction,
      confidence: latestPrediction.model_confidence,
      qualityLevel: getQualityLevel(latestPrediction.model_confidence)
    };
  }, [processedData, currentPrice]);

  function getQualityLevel(confidence: number): 'high' | 'medium' | 'low' {
    if (confidence >= QUALITY_THRESHOLDS.high) return 'high';
    if (confidence >= QUALITY_THRESHOLDS.medium) return 'medium';
    return 'low';
  }

  const getQualityColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-status-success';
      case 'medium': return 'text-status-warning';
      case 'low': return 'text-status-danger';
      default: return 'text-text-secondary';
    }
  };

  const toggleConfidenceLevel = (level: number) => {
    setVisibleConfidenceLevels(prev => 
      prev.includes(level) 
        ? prev.filter(l => l !== level)
        : [...prev, level].sort((a, b) => b - a)
    );
  };

  const resetZoom = () => {
    // Reset zoom functionality would go here
    console.log('Reset zoom');
  };

  interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{ name: string; value: number; color: string; payload: Record<string, unknown> }>;
    label?: string;
  }

  const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0]?.payload as any;
    if (!data) return null;

    return (
      <div className="bg-surface-card border border-border-default rounded-lg p-4 shadow-lg">
        <div className="text-text-primary font-medium mb-2">
          {new Date(data.timestamp).toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
        
        {data.actual_price && (
          <div className="text-sm text-text-secondary mb-1">
            実際の価格: <span className="text-text-primary font-mono">¥{data.actual_price.toLocaleString()}</span>
          </div>
        )}
        
        <div className="text-sm text-text-secondary mb-1">
          予測価格: <span className="text-text-primary font-mono">¥{data.predicted_price.toLocaleString()}</span>
        </div>
        
        <div className="text-sm text-text-secondary mb-2">
          信頼度: <span className={`font-medium ${getQualityColor(data.qualityLevel)}`}>
            {(data.model_confidence * 100).toFixed(1)}%
          </span>
        </div>

        <div className="border-t border-border-default pt-2 mt-2">
          <div className="text-xs text-text-tertiary mb-1">信頼区間:</div>
          {visibleConfidenceLevels.map(level => {
            const lowerKey = `confidence_${level}_lower` as keyof PredictionDataPoint;
            const upperKey = `confidence_${level}_upper` as keyof PredictionDataPoint;
            const lower = data[lowerKey] as number;
            const upper = data[upperKey] as number;
            const levelInfo = CONFIDENCE_LEVELS.find(l => l.level === level);
            
            return (
              <div key={level} className="text-xs flex justify-between">
                <span style={{ color: levelInfo?.stroke }}>{level}%:</span>
                <span className="font-mono">
                  ¥{lower.toLocaleString()} - ¥{upper.toLocaleString()}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderConfidenceBands = () => {
    return visibleConfidenceLevels.map(level => {
      const levelInfo = CONFIDENCE_LEVELS.find(l => l.level === level);
      if (!levelInfo) return null;

      return (
        <Area
          key={`confidence-${level}`}
          type="monotone"
          dataKey={`confidence_${level}_upper`}
          stackId="1"
          stroke="none"
          fill={levelInfo.color}
          fillOpacity={levelInfo.opacity}
          connectNulls
        />
      );
    });
  };

  return (
    <div className={`bg-surface-card border border-border-default rounded-2xl p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-xl font-semibold text-text-primary">
              {symbol} AI予測チャート
            </h3>
            <div className={`px-2 py-1 rounded-md text-xs font-medium ${
              prediction?.direction === 'up' 
                ? 'bg-status-success/20 text-status-success' 
                : 'bg-status-danger/20 text-status-danger'
            }`}>
              {prediction?.direction === 'up' ? (
                <TrendingUp size={12} className="inline mr-1" />
              ) : (
                <TrendingDown size={12} className="inline mr-1" />
              )}
              {prediction?.change ? `${prediction.change > 0 ? '+' : ''}${prediction.change.toFixed(2)}%` : 'N/A'}
            </div>
          </div>
          
          {prediction && (
            <div className="flex items-center space-x-6 text-sm text-text-secondary">
              <div>
                現在価格: <span className="text-text-primary font-mono">¥{currentPrice.toLocaleString()}</span>
              </div>
              <div>
                予測価格: <span className="text-text-primary font-mono">¥{prediction.price.toLocaleString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span>信頼度:</span>
                <span className={`font-medium ${getQualityColor(prediction.qualityLevel)}`}>
                  {(prediction.confidence * 100).toFixed(1)}%
                </span>
                {prediction.qualityLevel === 'low' && (
                  <AlertTriangle size={14} className="text-status-warning ml-1" />
                )}
              </div>
            </div>
          )}
        </div>

        {showControls && (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowActualPrices(!showActualPrices)}
              className={`p-2 rounded-lg transition-colors ${
                showActualPrices 
                  ? 'bg-brand-primary text-white' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
              }`}
              title={showActualPrices ? '実際の価格を非表示' : '実際の価格を表示'}
            >
              {showActualPrices ? <Eye size={16} /> : <EyeOff size={16} />}
            </button>

            <button
              onClick={resetZoom}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
              title="ズームをリセット"
            >
              <RotateCcw size={16} />
            </button>

            <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors">
              <Download size={16} />
            </button>

            <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors">
              <Settings size={16} />
            </button>
          </div>
        )}
      </div>

      {/* Confidence Level Controls */}
      <div className="flex items-center space-x-4 mb-4">
        <span className="text-sm text-text-secondary">信頼区間:</span>
        {CONFIDENCE_LEVELS.map(({ level, color }) => (
          <button
            key={level}
            onClick={() => toggleConfidenceLevel(level)}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              visibleConfidenceLevels.includes(level)
                ? 'text-white shadow-sm'
                : 'text-text-secondary hover:text-text-primary bg-surface-elevated'
            }`}
            style={{
              backgroundColor: visibleConfidenceLevels.includes(level) ? color : undefined
            }}
          >
            {level}%
          </button>
        ))}
      </div>

      {/* Chart */}
      <div ref={chartRef} style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={processedData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            onMouseMove={(e) => {
              // Chart interaction handling
              console.log('Chart interaction:', e?.activePayload?.[0]);
            }}
            onMouseLeave={() => console.log('Mouse left chart')}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" opacity={0.5} />
            
            <XAxis 
              dataKey="formattedDate"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-tertiary)' }}
              interval="preserveStartEnd"
            />
            
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-tertiary)' }}
              tickFormatter={(value) => `¥${value.toLocaleString()}`}
              domain={['dataMin - 100', 'dataMax + 100']}
            />

            <Tooltip content={<CustomTooltip />} />

            {/* Confidence Bands */}
            {renderConfidenceBands()}

            {/* Prediction Line */}
            <Line
              type="monotone"
              dataKey="predicted_price"
              stroke="var(--brand-primary)"
              strokeWidth={2}
              dot={false}
              activeDot={{ 
                r: 6, 
                fill: 'var(--brand-primary)',
                stroke: 'var(--surface-card)',
                strokeWidth: 2
              }}
              connectNulls
            />

            {/* Actual Price Line */}
            {showActualPrices && (
              <Line
                type="monotone"
                dataKey="actual_price"
                stroke="var(--text-primary)"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                activeDot={{ 
                  r: 6, 
                  fill: 'var(--text-primary)',
                  stroke: 'var(--surface-card)',
                  strokeWidth: 2
                }}
                connectNulls
              />
            )}

            {/* Reference line for current price */}
            <ReferenceLine 
              y={currentPrice} 
              stroke="var(--text-tertiary)" 
              strokeDasharray="2 2" 
              opacity={0.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Model Metadata */}
      <div className="mt-6 p-4 bg-surface-elevated/50 rounded-xl">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-text-primary flex items-center">
            <Info size={16} className="mr-2" />
            モデル情報
          </h4>
          <div className="text-xs text-text-tertiary">
            最終更新: {new Date(metadata.last_trained).toLocaleString('ja-JP')}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-text-primary">
              {(metadata.accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-text-secondary">精度</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-text-primary">
              {metadata.r_squared.toFixed(3)}
            </div>
            <div className="text-xs text-text-secondary">R²スコア</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-text-primary">
              ¥{metadata.mae.toFixed(0)}
            </div>
            <div className="text-xs text-text-secondary">平均絶対誤差</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${
              metadata.data_freshness <= 1 ? 'text-status-success' :
              metadata.data_freshness <= 6 ? 'text-status-warning' : 'text-status-danger'
            }`}>
              {metadata.data_freshness}h
            </div>
            <div className="text-xs text-text-secondary">データ鮮度</div>
          </div>
        </div>

        <div className="mt-4 text-xs text-text-tertiary">
          <strong>使用モデル:</strong> {metadata.model_name} | 
          <strong className="ml-2">主要特徴量:</strong> {
            Object.entries(metadata.feature_importance)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 3)
              .map(([feature]) => feature)
              .join(', ')
          }
        </div>
      </div>
    </div>
  );
}