'use client';

/**
 * Alerts Dashboard Page
 * Phase 10: Frontend Implementation
 *
 * Features:
 * - Display all user price alerts
 * - Create new alerts with target price and condition
 * - Update existing alerts
 * - Delete alerts
 * - Real-time alert status display
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { alertsAPI } from '@/lib/api-client';
import ProtectedRoute from '@/components/ProtectedRoute';

interface Alert {
  id: number;
  symbol: string;
  company_name?: string;
  alert_type: 'price_above' | 'price_below' | 'price_change' | 'volume_spike';
  target_price?: number;
  threshold_pct?: number;
  is_active: boolean;
  triggered_at?: string;
  created_at: string;
}

export default function AlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  // Create form state
  const [newAlert, setNewAlert] = useState({
    symbol: '',
    alert_type: 'price_above' as Alert['alert_type'],
    target_price: '',
    threshold_pct: '',
  });

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await alertsAPI.getAll();
      setAlerts(data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  // Create alert
  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const alertData: any = {
        symbol: newAlert.symbol.toUpperCase(),
        alert_type: newAlert.alert_type,
      };

      if (newAlert.alert_type === 'price_above' || newAlert.alert_type === 'price_below') {
        alertData.target_price = parseFloat(newAlert.target_price);
      } else if (newAlert.alert_type === 'price_change' || newAlert.alert_type === 'volume_spike') {
        alertData.threshold_pct = parseFloat(newAlert.threshold_pct);
      }

      await alertsAPI.create(alertData);

      // Reset form
      setNewAlert({
        symbol: '',
        alert_type: 'price_above',
        target_price: '',
        threshold_pct: '',
      });
      setShowCreateForm(false);

      // Refresh alerts
      await fetchAlerts();
    } catch (err) {
      alert('Failed to create alert: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  // Delete alert
  const handleDelete = async (alertId: number) => {
    try {
      await alertsAPI.delete(alertId);
      setDeleteConfirm(null);
      await fetchAlerts();
    } catch (err) {
      alert('Failed to delete alert: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  // Toggle alert active status
  const handleToggleActive = async (alertId: number, currentStatus: boolean) => {
    try {
      await alertsAPI.update(alertId, { is_active: !currentStatus });
      await fetchAlerts();
    } catch (err) {
      alert('Failed to update alert: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  // Alert type labels
  const getAlertTypeLabel = (type: Alert['alert_type']) => {
    switch (type) {
      case 'price_above': return '目標価格以上';
      case 'price_below': return '目標価格以下';
      case 'price_change': return '価格変動';
      case 'volume_spike': return '出来高急増';
      default: return type;
    }
  };

  // Alert condition display
  const getAlertCondition = (alert: Alert) => {
    if (alert.alert_type === 'price_above' || alert.alert_type === 'price_below') {
      return `¥${alert.target_price?.toLocaleString()}`;
    } else if (alert.threshold_pct) {
      return `${alert.threshold_pct}%`;
    }
    return '-';
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-center h-64">
              <div className="text-lg text-gray-600">読み込み中...</div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-red-800 mb-2">エラー</h2>
              <p className="text-red-600">{error}</p>
              <button
                onClick={fetchAlerts}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                再読み込み
              </button>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">価格アラート</h1>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
            >
              {showCreateForm ? 'キャンセル' : '+ アラート追加'}
            </button>
          </div>

          {/* Create Form */}
          {showCreateForm && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">新規アラート作成</h2>
              <form onSubmit={handleCreateAlert} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      銘柄コード
                    </label>
                    <input
                      type="text"
                      value={newAlert.symbol}
                      onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
                      placeholder="例: 7203.T, AAPL"
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      アラート種類
                    </label>
                    <select
                      value={newAlert.alert_type}
                      onChange={(e) => setNewAlert({ ...newAlert, alert_type: e.target.value as Alert['alert_type'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="price_above">目標価格以上</option>
                      <option value="price_below">目標価格以下</option>
                      <option value="price_change">価格変動（%）</option>
                      <option value="volume_spike">出来高急増（%）</option>
                    </select>
                  </div>

                  {(newAlert.alert_type === 'price_above' || newAlert.alert_type === 'price_below') && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        目標価格（円/ドル）
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={newAlert.target_price}
                        onChange={(e) => setNewAlert({ ...newAlert, target_price: e.target.value })}
                        placeholder="例: 1500"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  )}

                  {(newAlert.alert_type === 'price_change' || newAlert.alert_type === 'volume_spike') && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        変動率（%）
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={newAlert.threshold_pct}
                        onChange={(e) => setNewAlert({ ...newAlert, threshold_pct: e.target.value })}
                        placeholder="例: 5.0"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  )}
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
                  >
                    作成
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Empty State */}
          {alerts.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <div className="text-6xl mb-4">🔔</div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                アラートが設定されていません
              </h2>
              <p className="text-gray-600 mb-6">
                銘柄の価格変動をリアルタイムで通知するアラートを設定しましょう
              </p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
              >
                + アラート追加
              </button>
            </div>
          ) : (
            /* Alerts Table */
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                        銘柄
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                        アラート種類
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase">
                        条件
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-600 uppercase">
                        ステータス
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-600 uppercase">
                        作成日時
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-600 uppercase">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {alerts.map((alert) => (
                      <tr key={alert.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <button
                            onClick={() => router.push(`/stock/${alert.symbol}`)}
                            className="text-blue-600 font-medium hover:underline"
                          >
                            {alert.symbol}
                          </button>
                          {alert.company_name && (
                            <div className="text-sm text-gray-600">{alert.company_name}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-gray-900">
                          {getAlertTypeLabel(alert.alert_type)}
                        </td>
                        <td className="px-6 py-4 text-right font-medium text-gray-900">
                          {getAlertCondition(alert)}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleToggleActive(alert.id, alert.is_active)}
                              className={`px-3 py-1 text-xs rounded-full font-medium ${
                                alert.is_active
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {alert.is_active ? '有効' : '無効'}
                            </button>
                            {alert.triggered_at && (
                              <span className="px-3 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-full font-medium">
                                発火済み
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center text-sm text-gray-600">
                          {new Date(alert.created_at).toLocaleDateString('ja-JP')}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {deleteConfirm === alert.id ? (
                            <div className="flex items-center justify-center gap-2">
                              <button
                                onClick={() => handleDelete(alert.id)}
                                className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                              >
                                削除
                              </button>
                              <button
                                onClick={() => setDeleteConfirm(null)}
                                className="px-3 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                              >
                                キャンセル
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => setDeleteConfirm(alert.id)}
                              className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              削除
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
