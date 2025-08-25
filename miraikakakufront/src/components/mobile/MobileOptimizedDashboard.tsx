'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { useDashboardStore } from '@/store/dashboardStore';
// import { useUserModeStore } from '@/store/userModeStore'; // Removed
import { useResponsive } from '@/hooks/useResponsive';
import { Widget } from '@/types/dashboard';
import { 
  Maximize2, 
  Minimize2, 
  MoreVertical, 
  RefreshCw, 
  Settings,
  Plus,
  Grid3X3,
  Layers
} from 'lucide-react';
import WidgetComponent from '@/components/dashboard/WidgetComponent';

interface MobileOptimizedDashboardProps {
  className?: string;
}

interface WidgetCardProps {
  widget: Widget;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onRefresh: () => void;
}

function MobileWidgetCard({ widget, isExpanded, onToggleExpand, onRefresh }: WidgetCardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    onRefresh();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <motion.div
      layout
      className={`
        bg-surface-card border border-border-default rounded-2xl overflow-hidden
        ${isExpanded ? 'col-span-full' : ''}
      `}
      animate={{
        height: isExpanded ? 'auto' : undefined
      }}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default bg-surface-elevated/50">
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 bg-brand-primary rounded-full" />
          <h3 className="font-semibold text-text-primary text-sm">{widget.title}</h3>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
          </button>

          <button
            onClick={onToggleExpand}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>

          <button 
            onClick={() => {
              // Widget options menu - show context menu
              console.log('Widget options:', widget.id);
            }}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <MoreVertical size={16} />
          </button>
        </div>
      </div>

      {/* Widget Content */}
      <div className={`${isExpanded ? 'h-80' : 'h-48'} overflow-hidden`}>
        <WidgetComponent widget={widget} isEditMode={false} />
      </div>

      {/* Widget Actions (only when expanded) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-border-default bg-surface-elevated/30 p-3"
          >
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => {
                  // Navigate to detailed widget view
                  window.location.href = `/widget/${widget.id}`;
                }}
                className="flex-1 py-2 px-3 bg-brand-primary text-white rounded-lg text-sm font-medium"
              >
                詳細を見る
              </button>
              <button 
                onClick={() => {
                  // Open widget settings
                  console.log('Widget settings:', widget.id);
                }}
                className="py-2 px-3 border border-border-default text-text-secondary rounded-lg text-sm font-medium"
              >
                設定
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function MobileOptimizedDashboard({ className = '' }: MobileOptimizedDashboardProps) {
  const { getActiveLayout, updateWidget } = useDashboardStore();
  // const { config } = useUserModeStore(); // Removed - using default config
  const config = { mode: 'light' as const };
  const { isMobile } = useResponsive();
  const [expandedWidgetId, setExpandedWidgetId] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'grid' | 'list'>('grid');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const activeLayout = getActiveLayout();

  // Show regular dashboard on larger screens
  if (!isMobile) return null;

  const handleWidgetRefresh = (widgetId: string) => {
    // Find and update the widget
    const widget = activeLayout?.widgets.find(w => w.id === widgetId);
    if (widget && activeLayout) {
      // Trigger a re-render by updating widget's lastUpdated timestamp
      updateWidget(activeLayout.id, widgetId, {
        ...widget,
        config: {
          ...widget.config,
          lastUpdated: new Date().toISOString()
        }
      });
    }
  };

  const handleGlobalRefresh = async () => {
    setIsRefreshing(true);
    // Refresh all widgets
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  if (!activeLayout) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center">
          <Grid3X3 size={48} className="mx-auto mb-4 text-text-tertiary opacity-50" />
          <h3 className="text-lg font-medium text-text-primary mb-2">
            ダッシュボードが見つかりません
          </h3>
          <p className="text-text-secondary text-sm mb-4">
            新しいダッシュボードを作成してください
          </p>
          <button className="px-6 py-3 bg-brand-primary text-white rounded-lg font-medium">
            <Plus size={16} className="inline mr-2" />
            ダッシュボード作成
          </button>
        </div>
      </div>
    );
  }

  const visibleWidgets = activeLayout.widgets.filter(w => w.isVisible);

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Mobile Dashboard Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default bg-surface-elevated/50">
        <div>
          <h1 className="text-lg font-semibold text-text-primary">{activeLayout.name}</h1>
          <p className="text-xs text-text-secondary">
            {visibleWidgets.length} ウィジェット • {config.mode}モード
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* View Toggle */}
          <div className="flex bg-surface-elevated rounded-lg p-1">
            <button
              onClick={() => setCurrentView('grid')}
              className={`p-2 rounded-md transition-colors ${
                currentView === 'grid' 
                  ? 'bg-brand-primary text-white' 
                  : 'text-text-secondary'
              }`}
            >
              <Grid3X3 size={16} />
            </button>
            <button
              onClick={() => setCurrentView('list')}
              className={`p-2 rounded-md transition-colors ${
                currentView === 'list' 
                  ? 'bg-brand-primary text-white' 
                  : 'text-text-secondary'
              }`}
            >
              <Layers size={16} />
            </button>
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleGlobalRefresh}
            disabled={isRefreshing}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />
          </button>

          {/* Settings */}
          <button 
            onClick={() => {
              // Open dashboard settings
              window.location.href = '/settings';
            }}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <Settings size={18} />
          </button>
        </div>
      </div>

      {/* Widgets Container */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          {currentView === 'grid' ? (
            <motion.div
              key="grid"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="p-4"
            >
              <div className="grid grid-cols-1 gap-4">
                {visibleWidgets.map((widget) => (
                  <MobileWidgetCard
                    key={widget.id}
                    widget={widget}
                    isExpanded={expandedWidgetId === widget.id}
                    onToggleExpand={() => {
                      setExpandedWidgetId(
                        expandedWidgetId === widget.id ? null : widget.id
                      );
                    }}
                    onRefresh={() => handleWidgetRefresh(widget.id)}
                  />
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="list"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="p-4"
            >
              {/* List View - Compact Cards */}
              <div className="space-y-3">
                {visibleWidgets.map((widget, index) => (
                  <motion.div
                    key={widget.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-surface-card border border-border-default rounded-xl p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-text-primary">{widget.title}</h3>
                      <button
                        onClick={() => setExpandedWidgetId(widget.id)}
                        className="p-1 text-text-secondary hover:text-text-primary"
                      >
                        <Maximize2 size={14} />
                      </button>
                    </div>
                    
                    {/* Compact Widget Preview */}
                    <div className="h-20 overflow-hidden bg-surface-elevated rounded-lg flex items-center justify-center">
                      <span className="text-text-tertiary text-sm">プレビュー</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Quick Actions Bar */}
      <div className="border-t border-border-default bg-surface-elevated/50 p-4">
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => {
              // Open widget selector
              console.log('Add widget to dashboard');
            }}
            className="flex-1 py-3 bg-brand-primary text-white rounded-lg font-medium"
          >
            <Plus size={16} className="inline mr-2" />
            ウィジェット追加
          </button>
          <button 
            onClick={() => {
              // Toggle edit mode
              console.log('Toggle dashboard edit mode');
            }}
            className="px-4 py-3 border border-border-default text-text-secondary rounded-lg font-medium"
          >
            編集
          </button>
        </div>
      </div>

      {/* Expanded Widget Modal */}
      <AnimatePresence>
        {expandedWidgetId && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-surface-overlay backdrop-blur-sm"
            onClick={() => setExpandedWidgetId(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="absolute inset-4 bg-surface-card border border-border-default rounded-2xl overflow-hidden"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between p-4 border-b border-border-default bg-surface-elevated/50">
                <h2 className="font-semibold text-text-primary">
                  {visibleWidgets.find(w => w.id === expandedWidgetId)?.title}
                </h2>
                <button
                  onClick={() => setExpandedWidgetId(null)}
                  className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
                >
                  <Minimize2 size={18} />
                </button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-hidden">
                {visibleWidgets
                  .filter(w => w.id === expandedWidgetId)
                  .map(widget => (
                    <WidgetComponent
                      key={widget.id}
                      widget={widget}
                      isEditMode={false}
                    />
                  ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}