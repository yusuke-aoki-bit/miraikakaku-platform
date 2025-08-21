'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Monitor, 
  Cpu, 
  HardDrive, 
  Wifi, 
  Gauge,
  X,
  Settings,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from 'lucide-react';
import { usePerformance } from '@/hooks/usePerformance';

interface PerformanceMonitorProps {
  isVisible: boolean;
  onToggle: () => void;
}

export default function PerformanceMonitor({ isVisible, onToggle }: PerformanceMonitorProps) {
  const { metrics, config, updateConfig } = usePerformance();
  const [showSettings, setShowSettings] = useState(false);

  // Performance status indicators
  const getPerformanceStatus = () => {
    const { loadTime, frameRate, memoryUsage } = metrics;
    
    if (loadTime > 3000 || frameRate < 30 || memoryUsage > 100) {
      return { status: 'poor', color: 'text-status-danger', bgColor: 'bg-status-danger/20' };
    } else if (loadTime > 1500 || frameRate < 50 || memoryUsage > 50) {
      return { status: 'fair', color: 'text-status-warning', bgColor: 'bg-status-warning/20' };
    } else {
      return { status: 'good', color: 'text-status-success', bgColor: 'bg-status-success/20' };
    }
  };

  const performanceStatus = getPerformanceStatus();

  if (!isVisible) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-20 right-4 w-12 h-12 bg-surface-card border border-border-default rounded-full shadow-lg hover:shadow-xl transition-all z-40 flex items-center justify-center"
        aria-label="パフォーマンスモニターを表示"
        title="パフォーマンスモニター"
      >
        <Monitor size={20} className="text-text-secondary" />
      </button>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 100 }}
        className="fixed bottom-4 right-4 w-80 bg-surface-card border border-border-default rounded-2xl shadow-2xl z-40"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border-default">
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${performanceStatus.bgColor}`}>
              <Monitor size={16} className={performanceStatus.color} />
            </div>
            <div>
              <h3 className="font-semibold text-text-primary">パフォーマンス</h3>
              <p className="text-xs text-text-secondary capitalize">
                {performanceStatus.status === 'good' ? '良好' : 
                 performanceStatus.status === 'fair' ? '普通' : '要改善'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors"
              aria-label="設定"
            >
              <Settings size={16} />
            </button>
            <button
              onClick={onToggle}
              className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors"
              aria-label="閉じる"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Metrics */}
        <div className="p-4 space-y-4">
          {/* Load Time */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Gauge size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary">読み込み時間</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-mono text-text-primary">
                {metrics.loadTime > 0 ? `${(metrics.loadTime / 1000).toFixed(2)}s` : '計測中...'}
              </span>
              {metrics.loadTime > 3000 && (
                <AlertTriangle size={14} className="text-status-danger" />
              )}
            </div>
          </div>

          {/* Frame Rate */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary">フレームレート</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-mono text-text-primary">
                {metrics.frameRate}fps
              </span>
              {metrics.frameRate < 30 ? (
                <TrendingDown size={14} className="text-status-danger" />
              ) : (
                <TrendingUp size={14} className="text-status-success" />
              )}
            </div>
          </div>

          {/* Memory Usage */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <HardDrive size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary">メモリ使用量</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-mono text-text-primary">
                {metrics.memoryUsage.toFixed(1)}MB
              </span>
              {metrics.memoryUsage > 100 && (
                <AlertTriangle size={14} className="text-status-warning" />
              )}
            </div>
          </div>

          {/* Cache Hit Ratio */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Cpu size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary">キャッシュ効率</span>
            </div>
            <span className="text-sm font-mono text-text-primary">
              {(metrics.cacheHitRatio * 100).toFixed(1)}%
            </span>
          </div>

          {/* Network Requests */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Wifi size={16} className="text-text-secondary" />
              <span className="text-sm text-text-primary">ネットワーク要求</span>
            </div>
            <span className="text-sm font-mono text-text-primary">
              {metrics.networkRequests}
            </span>
          </div>

          {/* Device Info */}
          {metrics.isLowEndDevice && (
            <div className="p-3 bg-status-warning/10 border border-status-warning/20 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle size={16} className="text-status-warning" />
                <span className="text-sm text-status-warning font-medium">
                  低スペックデバイス検出
                </span>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                パフォーマンス最適化が自動的に適用されています
              </p>
            </div>
          )}
        </div>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              className="border-t border-border-default overflow-hidden"
            >
              <div className="p-4 space-y-4">
                <h4 className="font-medium text-text-primary">最適化設定</h4>
                
                {/* Preloading */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-primary">プリロード</span>
                  <button
                    onClick={() => updateConfig({ enablePreloading: !config.enablePreloading })}
                    className={`w-10 h-5 rounded-full transition-colors ${
                      config.enablePreloading ? 'bg-brand-primary' : 'bg-surface-border'
                    }`}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      config.enablePreloading ? 'translate-x-5' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>

                {/* Lazy Loading */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-primary">遅延読み込み</span>
                  <button
                    onClick={() => updateConfig({ enableLazyLoading: !config.enableLazyLoading })}
                    className={`w-10 h-5 rounded-full transition-colors ${
                      config.enableLazyLoading ? 'bg-brand-primary' : 'bg-surface-border'
                    }`}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      config.enableLazyLoading ? 'translate-x-5' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>

                {/* Image Quality */}
                <div className="space-y-2">
                  <span className="text-sm text-text-primary">画像品質</span>
                  <select
                    value={config.imageQuality}
                    onChange={(e) => updateConfig({ imageQuality: e.target.value as any })}
                    className="w-full bg-surface-hover border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary"
                  >
                    <option value="high">高</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                  </select>
                </div>

                {/* Cache Strategy */}
                <div className="space-y-2">
                  <span className="text-sm text-text-primary">キャッシュ戦略</span>
                  <select
                    value={config.cacheStrategy}
                    onChange={(e) => updateConfig({ cacheStrategy: e.target.value as any })}
                    className="w-full bg-surface-hover border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary"
                  >
                    <option value="aggressive">積極的</option>
                    <option value="moderate">中程度</option>
                    <option value="minimal">最小限</option>
                  </select>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  );
}

// Performance status indicator component
export function PerformanceIndicator() {
  const { metrics, config, updateConfig } = usePerformance();
  const [showMonitor, setShowMonitor] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const getIndicatorColor = () => {
    const { loadTime, frameRate, memoryUsage } = metrics;
    
    if (loadTime > 3000 || frameRate < 30 || memoryUsage > 100) {
      return 'bg-status-danger';
    } else if (loadTime > 1500 || frameRate < 50 || memoryUsage > 50) {
      return 'bg-status-warning';
    } else {
      return 'bg-status-success';
    }
  };

  // Performance status indicators
  const getPerformanceStatus = () => {
    const { loadTime, frameRate, memoryUsage } = metrics;
    
    if (loadTime > 3000 || frameRate < 30 || memoryUsage > 100) {
      return { status: 'poor', color: 'text-status-danger', bgColor: 'bg-status-danger/20' };
    } else if (loadTime > 1500 || frameRate < 50 || memoryUsage > 50) {
      return { status: 'fair', color: 'text-status-warning', bgColor: 'bg-status-warning/20' };
    } else {
      return { status: 'good', color: 'text-status-success', bgColor: 'bg-status-success/20' };
    }
  };

  const performanceStatus = getPerformanceStatus();

  return (
    <>
      {!showMonitor && (
        <button
          onClick={() => setShowMonitor(true)}
          className="fixed bottom-32 right-4 w-3 h-3 rounded-full shadow-lg transition-all z-30"
          style={{ backgroundColor: 'var(--surface-card)' }}
          aria-label="パフォーマンス状態"
        >
          <div className={`w-full h-full rounded-full ${getIndicatorColor()}`} />
        </button>
      )}
      
      {showMonitor && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="fixed bottom-4 right-4 w-80 bg-surface-card border border-border-default rounded-2xl shadow-2xl z-40"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border-default">
              <div className="flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${performanceStatus.bgColor}`}>
                  <Monitor size={16} className={performanceStatus.color} />
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">パフォーマンス</h3>
                  <p className="text-xs text-text-secondary capitalize">
                    {performanceStatus.status === 'good' ? '良好' : 
                     performanceStatus.status === 'fair' ? '普通' : '要改善'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors"
                  aria-label="設定"
                >
                  <Settings size={16} />
                </button>
                <button
                  onClick={() => setShowMonitor(false)}
                  className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors"
                  aria-label="閉じる"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Metrics */}
            <div className="p-4 space-y-4">
              {/* Load Time */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Gauge size={16} className="text-text-secondary" />
                  <span className="text-sm text-text-primary">読み込み時間</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-text-primary">
                    {metrics.loadTime > 0 ? `${(metrics.loadTime / 1000).toFixed(2)}s` : '計測中...'}
                  </span>
                  {metrics.loadTime > 3000 && (
                    <AlertTriangle size={14} className="text-status-danger" />
                  )}
                </div>
              </div>

              {/* Frame Rate */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <TrendingUp size={16} className="text-text-secondary" />
                  <span className="text-sm text-text-primary">フレームレート</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-text-primary">
                    {metrics.frameRate}fps
                  </span>
                  {metrics.frameRate < 30 ? (
                    <TrendingDown size={14} className="text-status-danger" />
                  ) : (
                    <TrendingUp size={14} className="text-status-success" />
                  )}
                </div>
              </div>

              {/* Memory Usage */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <HardDrive size={16} className="text-text-secondary" />
                  <span className="text-sm text-text-primary">メモリ使用量</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-text-primary">
                    {metrics.memoryUsage.toFixed(1)}MB
                  </span>
                  {metrics.memoryUsage > 100 && (
                    <AlertTriangle size={14} className="text-status-warning" />
                  )}
                </div>
              </div>

              {/* Cache Hit Ratio */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cpu size={16} className="text-text-secondary" />
                  <span className="text-sm text-text-primary">キャッシュ効率</span>
                </div>
                <span className="text-sm font-mono text-text-primary">
                  {(metrics.cacheHitRatio * 100).toFixed(1)}%
                </span>
              </div>

              {/* Network Requests */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Wifi size={16} className="text-text-secondary" />
                  <span className="text-sm text-text-primary">ネットワーク要求</span>
                </div>
                <span className="text-sm font-mono text-text-primary">
                  {metrics.networkRequests}
                </span>
              </div>

              {/* Device Info */}
              {metrics.isLowEndDevice && (
                <div className="p-3 bg-status-warning/10 border border-status-warning/20 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle size={16} className="text-status-warning" />
                    <span className="text-sm text-status-warning font-medium">
                      低スペックデバイス検出
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary mt-1">
                    パフォーマンス最適化が自動的に適用されています
                  </p>
                </div>
              )}
            </div>

            {/* Settings Panel */}
            <AnimatePresence>
              {showSettings && (
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: 'auto' }}
                  exit={{ height: 0 }}
                  className="border-t border-border-default overflow-hidden"
                >
                  <div className="p-4 space-y-4">
                    <h4 className="font-medium text-text-primary">最適化設定</h4>
                    
                    {/* Preloading */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-text-primary">プリロード</span>
                      <button
                        onClick={() => updateConfig({ enablePreloading: !config.enablePreloading })}
                        className={`w-10 h-5 rounded-full transition-colors ${
                          config.enablePreloading ? 'bg-brand-primary' : 'bg-surface-border'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          config.enablePreloading ? 'translate-x-5' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>

                    {/* Lazy Loading */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-text-primary">遅延読み込み</span>
                      <button
                        onClick={() => updateConfig({ enableLazyLoading: !config.enableLazyLoading })}
                        className={`w-10 h-5 rounded-full transition-colors ${
                          config.enableLazyLoading ? 'bg-brand-primary' : 'bg-surface-border'
                        }`}
                      >
                        <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                          config.enableLazyLoading ? 'translate-x-5' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>

                    {/* Image Quality */}
                    <div className="space-y-2">
                      <span className="text-sm text-text-primary">画像品質</span>
                      <select
                        value={config.imageQuality}
                        onChange={(e) => updateConfig({ imageQuality: e.target.value as any })}
                        className="w-full bg-surface-hover border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary"
                      >
                        <option value="high">高</option>
                        <option value="medium">中</option>
                        <option value="low">低</option>
                      </select>
                    </div>

                    {/* Cache Strategy */}
                    <div className="space-y-2">
                      <span className="text-sm text-text-primary">キャッシュ戦略</span>
                      <select
                        value={config.cacheStrategy}
                        onChange={(e) => updateConfig({ cacheStrategy: e.target.value as any })}
                        className="w-full bg-surface-hover border border-border-default rounded-lg px-3 py-2 text-sm text-text-primary"
                      >
                        <option value="aggressive">積極的</option>
                        <option value="moderate">中程度</option>
                        <option value="minimal">最小限</option>
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </AnimatePresence>
      )}
    </>
  );
}