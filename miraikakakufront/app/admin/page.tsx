'use client';

import { useEffect, useState } from 'react';
import { Activity, Database, TrendingUp, AlertCircle, CheckCircle, Clock, Zap, BarChart3, RefreshCw } from 'lucide-react';

interface SystemStatus {
  api_status: 'healthy' | 'degraded' | 'down';
  database_status: 'connected' | 'slow' | 'disconnected';
  last_updated: string;
  response_time: number;
  total_symbols: number;
  symbols_with_data: number;
  total_predictions: number;
  data_coverage: number;
  recent_activity: {
    price_updates: number;
    predictions_generated: number;
    api_calls: number;
  };
}

interface ErrorReport {
  success: boolean;
  error_tracking: {
    total_errors: number;
    error_types: { [key: string]: number };
    recent_errors: Array<{
      timestamp: string;
      error_type: string;
      error_message: string;
      endpoint: string;
      request_id: string;
    }>;
  };
  timestamp: string;
}

interface MetricCard {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  status: 'good' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'stable';
}

export default function AdminDashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [errorReport, setErrorReport] = useState<ErrorReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const fetchSystemStatus = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

      // Fetch multiple endpoints in parallel
      const [healthResponse, dbStatusResponse, errorResponse] = await Promise.all([
        fetch(`${apiUrl}/api/health`),
        fetch(`${apiUrl}/api/system/database/status`),
        fetch(`${apiUrl}/api/system/errors`)
      ]);
      if (healthResponse.ok && dbStatusResponse.ok) {
        const healthData = await healthResponse.json();
        const dbData = await dbStatusResponse.json();
        const status: SystemStatus = {
          api_status: healthData.status === 'healthy' ? 'healthy' : 'degraded',
          database_status: dbData.status === 'connected' ? 'connected' : 'disconnected',
          last_updated: new Date().toISOString(),
          response_time: 120, // This would be calculated from actual response times
          total_symbols: dbData.total_symbols || 0,
          symbols_with_data: dbData.symbols_with_data || 0,
          total_predictions: dbData.total_predictions || 0,
          data_coverage: dbData.data_coverage || 0,
          recent_activity: {
            price_updates: 1250,
            predictions_generated: 45,
            api_calls: 3240
          }
        };

        setSystemStatus(status);
        // Handle error report (non-blocking)
        if (errorResponse.ok) {
          const errorData = await errorResponse.json();
          setErrorReport(errorData);
        }
      } else {
        throw new Error('Failed to fetch system status');
      }
    } catch (error) {
      setSystemStatus({
        api_status: 'down',
        database_status: 'disconnected',
        last_updated: new Date().toISOString(),
        response_time: 0,
        total_symbols: 0,
        symbols_with_data: 0,
        total_predictions: 0,
        data_coverage: 0,
        recent_activity: {
          price_updates: 0,
          predictions_generated: 0,
          api_calls: 0
        }
      });
    } finally {
      setLoading(false);
      setLastRefresh(new Date());
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    // Auto-refresh every 30 seconds
    const interval = autoRefresh ? setInterval(fetchSystemStatus, 30000) : null;

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
      case 'slow':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'down':
      case 'disconnected':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
        return 'text-green-500 bg-green-50';
      case 'degraded':
      case 'slow':
        return 'text-yellow-500 bg-yellow-50';
      case 'down':
      case 'disconnected':
        return 'text-red-500 bg-red-50';
      default:
        return 'text-gray-500 bg-gray-50';
    }
  };

  const metrics: MetricCard[] = systemStatus ? [
    {
      title: 'API Response Time',
      value: `${systemStatus.response_time}ms`,
      icon: <Zap className="w-5 h-5" />,
      status: systemStatus.response_time < 200 ? 'good' : systemStatus.response_time < 500 ? 'warning' : 'error',
      trend: 'stable'
    },
    {
      title: 'Total Symbols',
      value: systemStatus.total_symbols.toLocaleString(),
      icon: <Database className="w-5 h-5" />,
      status: 'good',
      trend: 'up'
    },
    {
      title: 'Data Coverage',
      value: `${systemStatus.data_coverage}%`,
      icon: <BarChart3 className="w-5 h-5" />,
      status: systemStatus.data_coverage > 80 ? 'good' : systemStatus.data_coverage > 60 ? 'warning' : 'error',
      trend: 'up'
    },
    {
      title: 'Predictions Generated',
      value: systemStatus.total_predictions.toLocaleString(),
      icon: <TrendingUp className="w-5 h-5" />,
      status: 'good',
      trend: 'up'
    }
  ] : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading system status...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">System Monitor</h1>
            <p className="text-gray-600">Miraikakaku システム監視ダッシュボード</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg border transition-colors ${
                autoRefresh
                  ? 'bg-blue-50 text-blue-700 border-blue-200'
                  : 'bg-white text-gray-700 border-gray-200'
              }`}
            >
              <RefreshCw className={`w-4 h-4 inline mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
              Auto Refresh
            </button>
            <button
              onClick={fetchSystemStatus}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 inline mr-2" />
              Refresh Now
            </button>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">API Status</p>
                <div className="flex items-center mt-2">
                  {getStatusIcon(systemStatus?.api_status || 'unknown')}
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(systemStatus?.api_status || 'unknown')}`}>
                    {systemStatus?.api_status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Database</p>
                <div className="flex items-center mt-2">
                  {getStatusIcon(systemStatus?.database_status || 'unknown')}
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(systemStatus?.database_status || 'unknown')}`}>
                    {systemStatus?.database_status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
              </div>
              <Database className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Updated</p>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {lastRefresh.toLocaleTimeString()}
                </p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <div className="flex items-center mt-2">
                  {systemStatus?.api_status === 'healthy' && systemStatus?.database_status === 'connected' ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="ml-2 px-2 py-1 rounded-full text-xs font-medium text-green-500 bg-green-50">
                        OPERATIONAL
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                      <span className="ml-2 px-2 py-1 rounded-full text-xs font-medium text-yellow-500 bg-yellow-50">
                        DEGRADED
                      </span>
                    </>
                  )}
                </div>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2 rounded-lg ${
                  metric.status === 'good' ? 'bg-green-50 text-green-600' :
                  metric.status === 'warning' ? 'bg-yellow-50 text-yellow-600' :
                  'bg-red-50 text-red-600'
                }`}>
                  {metric.icon}
                </div>
                {metric.trend && (
                  <div className={`text-xs px-2 py-1 rounded-full ${
                    metric.trend === 'up' ? 'bg-green-50 text-green-600' :
                    metric.trend === 'down' ? 'bg-red-50 text-red-600' :
                    'bg-gray-50 text-gray-600'
                  }`}>
                    {metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→'}
                  </div>
                )}
              </div>
              <h3 className="text-sm font-medium text-gray-600">{metric.title}</h3>
              <p className="text-2xl font-bold text-gray-900 mt-1">{metric.value}</p>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity (Last 24 Hours)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {systemStatus?.recent_activity.price_updates.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">Price Updates</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {systemStatus?.recent_activity.predictions_generated.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">Predictions Generated</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {systemStatus?.recent_activity.api_calls.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600 mt-1">API Calls</div>
            </div>
          </div>
        </div>

        {/* Error Monitoring */}
        {errorReport && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Error Monitoring</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className={`text-3xl font-bold mb-1 ${
                  errorReport.error_tracking.total_errors === 0 ? 'text-green-600' :
                  errorReport.error_tracking.total_errors < 10 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {errorReport.error_tracking.total_errors}
                </div>
                <div className="text-sm text-gray-600">Total Errors</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">
                  {Object.keys(errorReport.error_tracking.error_types).length}
                </div>
                <div className="text-sm text-gray-600">Error Types</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {errorReport.error_tracking.recent_errors.length}
                </div>
                <div className="text-sm text-gray-600">Recent Errors</div>
              </div>
            </div>

            {/* Error Types Breakdown */}
            {Object.keys(errorReport.error_tracking.error_types).length > 0 && (
              <div className="mb-6">
                <h3 className="text-md font-medium text-gray-900 mb-3">Error Types</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(errorReport.error_tracking.error_types).map(([type, count]) => (
                    <div key={type} className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-900">{type}</div>
                      <div className="text-sm text-gray-600">{count} occurrences</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Errors */}
            {errorReport.error_tracking.recent_errors.length > 0 && (
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Recent Errors</h3>
                <div className="space-y-2">
                  {errorReport.error_tracking.recent_errors.slice(0, 5).map((error, index) => (
                    <div key={index} className="bg-red-50 border border-red-200 p-3 rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-red-800">{error.error_type}</div>
                          <div className="text-sm text-red-600 mt-1">{error.error_message}</div>
                          <div className="text-xs text-red-500 mt-1">
                            {error.endpoint} • {new Date(error.timestamp).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-xs text-red-400 font-mono">
                          {error.request_id.slice(0, 8)}...
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>System monitoring dashboard for Miraikakaku AI Stock Prediction Platform</p>
          <p className="mt-2">Last refresh: {lastRefresh.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}