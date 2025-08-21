'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Settings, 
  Maximize, 
  Download,
  RefreshCw,
  Layers,
  MousePointer,
  Crosshair
} from 'lucide-react';

interface TradingViewChartProps {
  symbol: string;
  interval?: string;
  theme?: 'light' | 'dark';
  height?: number;
  showToolbar?: boolean;
  enableTrading?: boolean;
  studies?: string[];
  className?: string;
  onSymbolChange?: (symbol: string) => void;
}

interface ChartStudy {
  id: string;
  name: string;
  shortName: string;
  enabled: boolean;
  parameters?: { [key: string]: any };
}

const DEFAULT_STUDIES: ChartStudy[] = [
  { id: 'MA', name: '移動平均線', shortName: 'MA', enabled: true },
  { id: 'RSI', name: 'RSI', shortName: 'RSI', enabled: false },
  { id: 'MACD', name: 'MACD', shortName: 'MACD', enabled: false },
  { id: 'BB', name: 'ボリンジャーバンド', shortName: 'BB', enabled: false },
  { id: 'Volume', name: '出来高', shortName: 'Vol', enabled: true },
  { id: 'Stoch', name: 'ストキャスティクス', shortName: 'Stoch', enabled: false },
];

const CHART_INTERVALS = [
  { value: '1', label: '1分' },
  { value: '5', label: '5分' },
  { value: '15', label: '15分' },
  { value: '30', label: '30分' },
  { value: '60', label: '1時間' },
  { value: '240', label: '4時間' },
  { value: 'D', label: '1日' },
  { value: 'W', label: '1週間' },
  { value: 'M', label: '1月' },
];

export default function TradingViewChart({
  symbol,
  interval = 'D',
  theme = 'dark',
  height = 500,
  showToolbar = true,
  enableTrading = false,
  studies = [],
  className = '',
  onSymbolChange
}: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentInterval, setCurrentInterval] = useState(interval);
  const [activeStudies, setActiveStudies] = useState<ChartStudy[]>(DEFAULT_STUDIES);
  const [showStudiesPanel, setShowStudiesPanel] = useState(false);
  const [chartType, setChartType] = useState<'candlesticks' | 'line' | 'area'>('candlesticks');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Initialize TradingView widget
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.async = true;
    
    const config = {
      autosize: true,
      symbol: symbol,
      interval: currentInterval,
      timezone: 'Asia/Tokyo',
      theme: theme,
      style: chartType === 'candlesticks' ? '1' : chartType === 'line' ? '2' : '3',
      locale: 'ja',
      enable_publishing: false,
      backgroundColor: theme === 'dark' ? 'rgba(0, 0, 0, 1)' : 'rgba(255, 255, 255, 1)',
      gridColor: theme === 'dark' ? 'rgba(42, 46, 57, 0.5)' : 'rgba(233, 233, 234, 0.5)',
      hide_top_toolbar: !showToolbar,
      hide_legend: false,
      save_image: true,
      container_id: 'tradingview_chart',
      studies: activeStudies.filter(s => s.enabled).map(s => s.id),
      show_popup_button: true,
      popup_width: '1000',
      popup_height: '650',
      no_referral_id: true,
    };

    script.innerHTML = JSON.stringify(config);

    // Clear previous widget
    if (chartContainerRef.current) {
      chartContainerRef.current.innerHTML = '';
      chartContainerRef.current.appendChild(script);
    }

    // Set loading state
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, 3000);

    return () => {
      clearTimeout(loadingTimer);
      if (chartContainerRef.current) {
        chartContainerRef.current.innerHTML = '';
      }
    };
  }, [symbol, currentInterval, theme, chartType, activeStudies, showToolbar]);

  const toggleStudy = (studyId: string) => {
    setActiveStudies(prev =>
      prev.map(study =>
        study.id === studyId ? { ...study, enabled: !study.enabled } : study
      )
    );
  };

  const handleIntervalChange = (newInterval: string) => {
    setCurrentInterval(newInterval);
  };

  const exportChart = () => {
    try {
      // Use TradingView's built-in export functionality
      const widget = widgetRef.current;
      if (widget && widget.takeScreenshot) {
        widget.takeScreenshot().then((canvas: HTMLCanvasElement) => {
          // Create download link
          const link = document.createElement('a');
          link.download = `${symbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
          link.href = canvas.toDataURL();
          link.click();
        }).catch((error: Error) => {
          console.error('チャートエクスポートエラー:', error);
        });
      } else {
        // Fallback: Use html2canvas if TradingView method not available
        import('html2canvas').then(html2canvas => {
          if (chartContainerRef.current) {
            html2canvas.default(chartContainerRef.current).then(canvas => {
              const link = document.createElement('a');
              link.download = `${symbol}_chart_${new Date().toISOString().split('T')[0]}.png`;
              link.href = canvas.toDataURL();
              link.click();
            });
          }
        }).catch(() => {
          console.error('チャートエクスポート機能が利用できません');
        });
      }
    } catch (error) {
      console.error('チャートエクスポートエラー:', error);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      chartContainerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div className={`bg-surface-card border border-border-default rounded-2xl overflow-hidden ${className}`}>
      {/* Chart Header */}
      {showToolbar && (
        <div className="flex items-center justify-between p-4 border-b border-border-default bg-surface-elevated/50">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <BarChart3 size={20} className="text-brand-primary" />
              <h3 className="font-semibold text-text-primary">{symbol}</h3>
            </div>

            {/* Interval Selector */}
            <div className="flex items-center space-x-1 bg-surface-elevated rounded-lg p-1">
              {CHART_INTERVALS.map((int) => (
                <button
                  key={int.value}
                  onClick={() => handleIntervalChange(int.value)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    currentInterval === int.value
                      ? 'bg-brand-primary text-white'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {int.label}
                </button>
              ))}
            </div>

            {/* Chart Type Selector */}
            <div className="flex items-center space-x-1 bg-surface-elevated rounded-lg p-1">
              {[
                { type: 'candlesticks', label: 'ローソク足', icon: '📊' },
                { type: 'line', label: 'ライン', icon: '📈' },
                { type: 'area', label: 'エリア', icon: '🌊' }
              ].map((chart) => (
                <button
                  key={chart.type}
                  onClick={() => setChartType(chart.type as any)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    chartType === chart.type
                      ? 'bg-brand-primary text-white'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                  title={chart.label}
                >
                  {chart.icon}
                </button>
              ))}
            </div>
          </div>

          {/* Chart Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowStudiesPanel(!showStudiesPanel)}
              className={`p-2 rounded-lg transition-colors ${
                showStudiesPanel
                  ? 'bg-brand-primary text-white'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
              }`}
              title="インジケーター"
            >
              <Layers size={16} />
            </button>

            <button
              onClick={exportChart}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
              title="チャート保存"
            >
              <Download size={16} />
            </button>

            <button
              onClick={toggleFullscreen}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
              title="全画面表示"
            >
              <Maximize size={16} />
            </button>

            <button
              onClick={() => {
                // Open chart settings modal
                console.log('Open chart settings');
              }}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
              title="設定"
            >
              <Settings size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Studies Panel */}
      {showStudiesPanel && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="border-b border-border-default bg-surface-elevated/30 p-4"
        >
          <div className="flex items-center space-x-2 mb-3">
            <Layers size={16} className="text-text-secondary" />
            <span className="text-sm font-medium text-text-primary">テクニカル指標</span>
          </div>
          
          <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
            {activeStudies.map((study) => (
              <button
                key={study.id}
                onClick={() => toggleStudy(study.id)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  study.enabled
                    ? 'bg-brand-primary text-white'
                    : 'bg-surface-elevated text-text-secondary hover:text-text-primary'
                }`}
              >
                {study.shortName}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Chart Container */}
      <div className="relative" style={{ height: height }}>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface-card z-10">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin text-brand-primary mx-auto mb-3" />
              <p className="text-text-secondary text-sm">チャートを読み込み中...</p>
            </div>
          </div>
        )}

        <div
          ref={chartContainerRef}
          id="tradingview_chart"
          className="w-full h-full"
        />

        {/* Chart Overlay Controls */}
        <div className="absolute top-4 right-4 flex flex-col space-y-2 z-20">
          <button
            onClick={() => {
              // Toggle crosshair tool
              console.log('Toggle crosshair tool');
            }}
            className="p-2 bg-surface-card/80 hover:bg-surface-card border border-border-default rounded-lg text-text-secondary hover:text-text-primary transition-colors backdrop-blur-sm"
            title="クロスヘア"
          >
            <Crosshair size={16} />
          </button>
          
          <button
            onClick={() => {
              // Toggle drawing tools
              console.log('Toggle drawing tools');
            }}
            className="p-2 bg-surface-card/80 hover:bg-surface-card border border-border-default rounded-lg text-text-secondary hover:text-text-primary transition-colors backdrop-blur-sm"
            title="描画ツール"
          >
            <MousePointer size={16} />
          </button>
        </div>
      </div>

      {/* Chart Footer */}
      {showToolbar && (
        <div className="flex items-center justify-between p-2 border-t border-border-default bg-surface-elevated/30 text-xs text-text-tertiary">
          <div className="flex items-center space-x-4">
            <span>データ提供: TradingView</span>
            <span>•</span>
            <span>最終更新: {new Date().toLocaleTimeString('ja-JP')}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-status-success rounded-full"></div>
              <span>リアルタイム</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}