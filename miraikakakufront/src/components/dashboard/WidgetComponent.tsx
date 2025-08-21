'use client';

import { useState, useEffect } from 'react';
import { Widget } from '@/types/dashboard';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  BarChart3, 
  Table, 
  Newspaper,
  PieChart,
  Briefcase,
  BookmarkCheck,
  Activity,
  Target,
  AlertTriangle,
  History,
  Bell,
  Maximize,
  Settings,
  RefreshCw
} from 'lucide-react';

// Widget Components
import PricePredictionChart from './widgets/PricePredictionChart';
import DataTable from './widgets/DataTable';
import KPIScorecard from './widgets/KPIScorecard';
import NewsSentiment from './widgets/NewsSentiment';
import MarketOverview from './widgets/MarketOverview';
import PortfolioSummary from './widgets/PortfolioSummary';
import Watchlist from './widgets/Watchlist';
import RealTimePrices from './widgets/RealTimePrices';
import TechnicalIndicators from './widgets/TechnicalIndicators';
import RiskAnalysis from './widgets/RiskAnalysis';
import TradingHistory from './widgets/TradingHistory';
import AlertsPanel from './widgets/AlertsPanel';

interface WidgetComponentProps {
  widget: Widget;
  isEditMode?: boolean;
  isSelected?: boolean;
}

const WIDGET_ICONS = {
  'price-prediction-chart': TrendingUp,
  'data-table': Table,
  'kpi-scorecard': BarChart3,
  'news-sentiment': Newspaper,
  'market-overview': PieChart,
  'portfolio-summary': Briefcase,
  'watchlist': BookmarkCheck,
  'real-time-prices': Activity,
  'technical-indicators': Target,
  'risk-analysis': AlertTriangle,
  'trading-history': History,
  'alerts-panel': Bell,
};

export default function WidgetComponent({ 
  widget, 
  isEditMode = false, 
  isSelected = false 
}: WidgetComponentProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const Icon = WIDGET_ICONS[widget.type];

  // Auto-refresh functionality
  useEffect(() => {
    if (!widget.config.refreshInterval || isEditMode) return;

    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, widget.config.refreshInterval);

    return () => clearInterval(interval);
  }, [widget.config.refreshInterval, isEditMode]);

  const handleRefresh = () => {
    setIsLoading(true);
    setLastUpdated(new Date());
    setTimeout(() => setIsLoading(false), 500); // Simulate loading
  };

  const renderWidgetContent = () => {
    if (isEditMode) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-text-secondary">
          <Icon size={48} className="mb-4 opacity-50" />
          <div className="text-center">
            <h3 className="font-medium text-text-primary mb-1">{widget.title}</h3>
            <p className="text-xs opacity-75">{widget.type}</p>
          </div>
        </div>
      );
    }

    // Render actual widget content based on type
    switch (widget.type) {
      case 'price-prediction-chart':
        return <PricePredictionChart widget={widget} />;
      case 'data-table':
        return <DataTable widget={widget} />;
      case 'kpi-scorecard':
        return <KPIScorecard widget={widget} />;
      case 'news-sentiment':
        return <NewsSentiment widget={widget} />;
      case 'market-overview':
        return <MarketOverview widget={widget} />;
      case 'portfolio-summary':
        return <PortfolioSummary widget={widget} />;
      case 'watchlist':
        return <Watchlist widget={widget} />;
      case 'real-time-prices':
        return <RealTimePrices widget={widget} />;
      case 'technical-indicators':
        return <TechnicalIndicators widget={widget} />;
      case 'risk-analysis':
        return <RiskAnalysis widget={widget} />;
      case 'trading-history':
        return <TradingHistory widget={widget} />;
      case 'alerts-panel':
        return <AlertsPanel widget={widget} />;
      default:
        return (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-text-secondary">
              <Icon size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">未実装のウィジェット</p>
            </div>
          </div>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`
        h-full bg-surface-card border border-border-default rounded-2xl overflow-hidden
        backdrop-blur-sm transition-all duration-200
        ${isSelected ? 'ring-2 ring-brand-primary' : ''}
        ${isEditMode ? 'cursor-move' : ''}
      `}
    >
      {/* Widget Header */}
      {(widget.config.showTitle !== false || !isEditMode) && (
        <div className="flex items-center justify-between p-4 border-b border-border-default bg-surface-elevated/50">
          <div className="flex items-center space-x-3">
            <Icon size={18} className="text-brand-primary" />
            <h3 className="font-medium text-text-primary truncate">
              {widget.title}
            </h3>
            {isLoading && (
              <RefreshCw size={14} className="text-text-secondary animate-spin" />
            )}
          </div>

          {!isEditMode && (
            <div className="flex items-center space-x-1">
              {widget.config.refreshInterval && (
                <button
                  onClick={handleRefresh}
                  className="p-1.5 text-text-secondary hover:text-text-primary rounded-md hover:bg-surface-elevated transition-colors"
                  title="更新"
                >
                  <RefreshCw size={14} />
                </button>
              )}

              {widget.config.allowFullscreen && (
                <button
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className="p-1.5 text-text-secondary hover:text-text-primary rounded-md hover:bg-surface-elevated transition-colors"
                  title="全画面表示"
                >
                  <Maximize size={14} />
                </button>
              )}

              <button
                className="p-1.5 text-text-secondary hover:text-text-primary rounded-md hover:bg-surface-elevated transition-colors"
                title="設定"
              >
                <Settings size={14} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Widget Content */}
      <div className="flex-1 p-4 overflow-hidden">
        {renderWidgetContent()}
      </div>

      {/* Widget Footer (for metadata) */}
      {!isEditMode && widget.config.refreshInterval && (
        <div className="px-4 pb-2">
          <div className="text-xs text-text-tertiary text-right">
            最終更新: {lastUpdated.toLocaleTimeString('ja-JP')}
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && !isEditMode && (
        <div className="absolute inset-0 bg-surface-overlay/50 backdrop-blur-sm flex items-center justify-center">
          <div className="flex items-center space-x-2 text-text-primary">
            <RefreshCw size={16} className="animate-spin" />
            <span className="text-sm">更新中...</span>
          </div>
        </div>
      )}

      {/* Edit Mode Overlay */}
      {isEditMode && (
        <div className="absolute inset-0 bg-surface-overlay/20 pointer-events-none" />
      )}
    </motion.div>
  );
}