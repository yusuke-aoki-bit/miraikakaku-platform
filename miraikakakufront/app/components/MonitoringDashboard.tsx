'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Database,
  Server,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Clock,
  Users,
  Zap,
  HardDrive,
  Cpu,
  MemoryStick
} from 'lucide-react';
import { monitoringAPI, type SystemHealth, type PerformanceMetrics, type PerformanceAnalytics } from '../lib/monitoring-api';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  status?: 'good' | 'warning' | 'error';
  icon: React.ReactNode;
  trend?: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, status = 'good', icon, trend }) => {
  const statusColors = {
    good: 'border-green-200 bg-green-50',
    warning: 'border-yellow-200 bg-yellow-50',
    error: 'border-red-200 bg-red-50'
  };

  const valueColors = {
    good: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600'
  };

  return (
    <div className={`p-4 rounded-lg border ${statusColors[status]} transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className={`text-gray-600`}>{icon}</div>
          <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        </div>
        {trend !== undefined && (
          <div className={`text-xs ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {trend >= 0 ? '↗' : '↘'} {Math.abs(trend).toFixed(1)}%
          </div>
        )}
      </div>
      <div className="flex items-baseline space-x-1">
        <span className={`text-2xl font-bold ${valueColors[status]}`}>
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
        {unit && <span className="text-sm text-gray-500">{unit}</span>}
      </div>
    </div>
  );
};

interface StatusIndicatorProps {
  status: string;
  message?: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, message }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'critical':
      case 'error':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return <CheckCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'critical':
      case 'error':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={getStatusColor(status)}>
        {getStatusIcon(status)}
      </div>
      <span className={`font-medium ${getStatusColor(status)}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
      {message && (
        <span className="text-sm text-gray-500">- {message}</span>
      )}
    </div>
  );
};

export const MonitoringDashboard: React.FC = () => {
  const [dbHealth, setDbHealth] = useState<SystemHealth | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [analytics, setAnalytics] = useState<PerformanceAnalytics | null>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const fetchData = async () => {
    try {
      setError(null);
      const [dbHealthData, performanceData, analyticsData, systemData] = await Promise.all([
        monitoringAPI.getDatabaseHealth(),
        monitoringAPI.getCurrentPerformance(),
        monitoringAPI.getPerformanceAnalytics(24),
        monitoringAPI.getSystemStatus()
      ]);
      setDbHealth(dbHealthData);
      // Check if performance data has status field (indicating no monitoring data)
      if ('status' in performanceData && performanceData.status === 'no_data') {
        setPerformance(null);
      } else {
        setPerformance(performanceData as PerformanceMetrics);
      }

      setAnalytics(analyticsData);
      setSystemStatus(systemData);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch monitoring data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const getMetricStatus = (value: number, thresholds: { warning: number; error: number }): 'good' | 'warning' | 'error' => {
    if (value >= thresholds.error) return 'error';
    if (value >= thresholds.warning) return 'warning';
    return 'good';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">システム監視ダッシュボード</h1>
          <p className="text-gray-600 mt-1">
            最終更新: {lastUpdate.toLocaleString('ja-JP')}
          </p>
        </div>
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          更新
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">エラー</span>
          </div>
          <p className="text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold">データベース</h2>
          </div>
          {dbHealth ? (
            <div className="space-y-3">
              <StatusIndicator status={dbHealth.status} />
              {dbHealth.metrics && (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>接続数: {dbHealth.metrics.active_connections}/{dbHealth.metrics.total_connections}</div>
                  <div>CPU: {dbHealth.metrics.cpu_usage.toFixed(1)}%</div>
                  <div>メモリ: {dbHealth.metrics.memory_usage.toFixed(1)}%</div>
                  <div>クエリ時間: {dbHealth.metrics.avg_query_duration.toFixed(2)}ms</div>
                </div>
              )}
              {dbHealth.issues.length > 0 && (
                <div className="mt-3">
                  <h4 className="text-sm font-medium text-red-600 mb-1">問題:</h4>
                  <ul className="text-xs text-red-600 space-y-1">
                    {dbHealth.issues.map((issue, index) => (
                      <li key={index}>• {issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-500">データ取得中...</div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Server className="w-6 h-6 text-green-600" />
            <h2 className="text-xl font-semibold">API サーバー</h2>
          </div>
          {performance ? (
            <div className="space-y-3">
              <StatusIndicator
                status={performance.api.error_rate > 5 ? 'warning' : 'healthy'}
                message={`${performance.api.total_requests} リクエスト`}
              />
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>応答時間: {performance.api.response_time.toFixed(2)}s</div>
                <div>エラー率: {performance.api.error_rate.toFixed(1)}%</div>
                <div>アクティブ: {performance.api.active_requests}</div>
                <div>合計: {performance.api.total_requests}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">監視データなし</div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Activity className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-semibold">システム状態</h2>
          </div>
          {systemStatus ? (
            <div className="space-y-3">
              <StatusIndicator status={systemStatus.api_status} />
              <div className="grid grid-cols-1 gap-2 text-sm">
                <div>株式: {systemStatus.total_stocks?.toLocaleString() || 0}</div>
                <div>価格データ: {systemStatus.total_prices?.toLocaleString() || 0}</div>
                <div>予測: {systemStatus.total_predictions?.toLocaleString() || 0}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">データ取得中...</div>
          )}
        </div>
      </div>

      {/* Performance Metrics */}
      {performance && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <span>リアルタイム監視</span>
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <MetricCard
              title="CPU使用率"
              value={performance.system.cpu_usage}
              unit="%"
              status={getMetricStatus(performance.system.cpu_usage, { warning: 70, error: 85 })}
              icon={<Cpu className="w-5 h-5" />}
            />
            <MetricCard
              title="メモリ使用率"
              value={performance.system.memory_usage}
              unit="%"
              status={getMetricStatus(performance.system.memory_usage, { warning: 75, error: 90 })}
              icon={<MemoryStick className="w-5 h-5" />}
            />
            <MetricCard
              title="ディスク使用率"
              value={performance.system.disk_usage}
              unit="%"
              status={getMetricStatus(performance.system.disk_usage, { warning: 80, error: 95 })}
              icon={<HardDrive className="w-5 h-5" />}
            />
            <MetricCard
              title="API応答時間"
              value={performance.api.response_time}
              unit="s"
              status={getMetricStatus(performance.api.response_time, { warning: 1, error: 3 })}
              icon={<Clock className="w-5 h-5" />}
            />
            <MetricCard
              title="アクティブリクエスト"
              value={performance.api.active_requests}
              unit=""
              status={getMetricStatus(performance.api.active_requests, { warning: 10, error: 20 })}
              icon={<Users className="w-5 h-5" />}
            />
            <MetricCard
              title="キャッシュヒット率"
              value={performance.cache.hit_rate}
              unit="%"
              status={performance.cache.hit_rate < 70 ? 'warning' : 'good'}
              icon={<Zap className="w-5 h-5" />}
            />
          </div>
        </div>
      )}

      {/* Analytics Summary */}
      {analytics && analytics.data_points > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">過去24時間の統計</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">CPU使用率</h3>
              <div className="space-y-1 text-sm">
                <div>平均: {analytics.system.cpu.avg.toFixed(1)}%</div>
                <div>最大: {analytics.system.cpu.max.toFixed(1)}%</div>
                <div>最小: {analytics.system.cpu.min.toFixed(1)}%</div>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">メモリ使用率</h3>
              <div className="space-y-1 text-sm">
                <div>平均: {analytics.system.memory.avg.toFixed(1)}%</div>
                <div>最大: {analytics.system.memory.max.toFixed(1)}%</div>
                <div>最小: {analytics.system.memory.min.toFixed(1)}%</div>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">API統計</h3>
              <div className="space-y-1 text-sm">
                <div>総リクエスト: {analytics.api.total_requests.toLocaleString()}</div>
                <div>エラー率: {analytics.api.error_rate.toFixed(2)}%</div>
                <div>平均応答時間: {analytics.api.response_time.avg.toFixed(2)}s</div>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">データポイント</h3>
              <div className="space-y-1 text-sm">
                <div>収集数: {analytics.data_points}</div>
                <div>期間: {analytics.period_hours}時間</div>
                <div>開始: {new Date(analytics.period.start).toLocaleString('ja-JP')}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};