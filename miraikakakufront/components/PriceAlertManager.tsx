'use client';

import { useState, useEffect } from 'react';
import { PriceAlertManager, PriceAlert } from '@/lib/priceAlerts';

interface PriceAlertManagerProps {
  symbol?: string;
  companyName?: string;
  currentPrice?: number;
}

export default function PriceAlertManagerComponent({
  symbol,
  companyName,
  currentPrice,
}: PriceAlertManagerProps) {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [targetPrice, setTargetPrice] = useState('');
  const [condition, setCondition] = useState<'above' | 'below'>('above');
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermission>('default');

  useEffect(() => {
    loadAlerts();
    checkNotificationPermission();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  const loadAlerts = () => {
    if (symbol) {
      setAlerts(PriceAlertManager.getAlertsForSymbol(symbol));
    } else {
      setAlerts(PriceAlertManager.getAlerts());
    }
  };

  const checkNotificationPermission = () => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setNotificationPermission(Notification.permission);
    }
  };

  const requestNotificationPermission = async () => {
    const permission = await PriceAlertManager.requestNotificationPermission();
    setNotificationPermission(permission);
  };

  const handleAddAlert = () => {
    if (!symbol || !companyName || !targetPrice) return;

    const price = parseFloat(targetPrice);
    if (isNaN(price) || price <= 0) return;

    PriceAlertManager.addAlert(symbol, companyName, price, condition);
    setTargetPrice('');
    setShowAddForm(false);
    loadAlerts();

    // 通知権限がない場合はリクエスト
    if (notificationPermission !== 'granted') {
      requestNotificationPermission();
    }
  };

  const handleRemoveAlert = (alertId: string) => {
    PriceAlertManager.removeAlert(alertId);
    loadAlerts();
  };

  const handleClearTriggered = () => {
    PriceAlertManager.clearTriggeredAlerts();
    loadAlerts();
  };

  const activeAlerts = alerts.filter(a => !a.triggered);
  const triggeredAlerts = alerts.filter(a => a.triggered);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          価格アラート
        </h2>
        {symbol && (
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            {showAddForm ? 'キャンセル' : '+ アラート追加'}
          </button>
        )}
      </div>

      {/* 通知権限の案内 */}
      {notificationPermission !== 'granted' && (
        <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 mb-2">
            ブラウザ通知を有効にして、価格アラートを受け取りませんか？
          </p>
          <button
            onClick={requestNotificationPermission}
            className="text-sm text-yellow-900 dark:text-yellow-100 font-semibold hover:underline"
          >
            通知を許可する
          </button>
        </div>
      )}

      {/* アラート追加フォーム */}
      {showAddForm && symbol && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                目標価格
              </label>
              <input
                type="number"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                placeholder="例: 1000"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
              {currentPrice && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  現在価格: ¥{currentPrice.toLocaleString()}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                条件
              </label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value as 'above' | 'below')}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="above">以上になったら</option>
                <option value="below">以下になったら</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={handleAddAlert}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                追加
              </button>
            </div>
          </div>
        </div>
      )}

      {/* アクティブなアラート */}
      {activeAlerts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            アクティブなアラート ({activeAlerts.length})
          </h3>
          <div className="space-y-2">
            {activeAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {alert.company_name} ({alert.symbol})
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {alert.condition === 'above' ? '≥' : '≤'} ¥{alert.target_price.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    作成: {new Date(alert.created_at).toLocaleString('ja-JP')}
                  </p>
                </div>
                <button
                  onClick={() => handleRemoveAlert(alert.id)}
                  className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
                >
                  削除
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* トリガー済みアラート */}
      {triggeredAlerts.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              トリガー済み ({triggeredAlerts.length})
            </h3>
            <button
              onClick={handleClearTriggered}
              className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              クリア
            </button>
          </div>
          <div className="space-y-2">
            {triggeredAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {alert.company_name} ({alert.symbol})
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {alert.condition === 'above' ? '≥' : '≤'} ¥{alert.target_price.toLocaleString()}
                  </p>
                  <p className="text-xs text-green-600 dark:text-green-400">
                    ✓ {alert.triggered_at && new Date(alert.triggered_at).toLocaleString('ja-JP')}
                  </p>
                </div>
                <button
                  onClick={() => handleRemoveAlert(alert.id)}
                  className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
                >
                  削除
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* アラートがない場合 */}
      {alerts.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            アラートが設定されていません
          </p>
          {symbol && (
            <button
              onClick={() => setShowAddForm(true)}
              className="mt-4 text-blue-600 dark:text-blue-400 hover:underline text-sm"
            >
              最初のアラートを追加する
            </button>
          )}
        </div>
      )}
    </div>
  );
}
