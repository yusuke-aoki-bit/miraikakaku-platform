'use client';

import { useState } from 'react';
import { EnvelopeIcon, DevicePhoneMobileIcon, BellIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

interface NotificationSettings {
  email: {
    enabled: boolean;
    news_updates: boolean;
    weekly_reports: boolean;
    watchlist_news: boolean;
    security_alerts: boolean;
  };
  push: {
    enabled: boolean;
    price_alerts: boolean;
    ai_signals: boolean;
    volume_alerts: boolean;
    market_hours: boolean;
  };
}

export default function NotificationsTab() {
  const [settings, setSettings] = useState<NotificationSettings>({
    email: {
      enabled: true,
      news_updates: true,
      weekly_reports: true,
      watchlist_news: true,
      security_alerts: true,
    },
    push: {
      enabled: false,
      price_alerts: false,
      ai_signals: false,
      volume_alerts: false,
      market_hours: false,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [pushPermission, setPushPermission] = useState<NotificationPermission>('default');

  const handleSettingChange = (category: 'email' | 'push', key: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const handlePushToggle = async (enabled: boolean) => {
    if (enabled && pushPermission !== 'granted') {
      try {
        const permission = await Notification.requestPermission();
        setPushPermission(permission);
        
        if (permission !== 'granted') {
          alert('プッシュ通知を有効にするには、ブラウザで通知を許可してください。');
          return;
        }
      } catch (error) {
        console.error('Notification permission error:', error);
        alert('プッシュ通知の設定に失敗しました。');
        return;
      }
    }

    handleSettingChange('push', 'enabled', enabled);
  };

  const saveSettings = async () => {
    setIsLoading(true);
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/notifications', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        alert('通知設定を保存しました');
      } else {
        throw new Error('通知設定の保存に失敗しました');
      }
    } catch (error) {
      console.error('Settings save error:', error);
      alert('通知設定の保存に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const testPushNotification = async () => {
    if (settings.push.enabled && 'Notification' in window) {
      new Notification('Miraikakaku', {
        body: 'プッシュ通知のテストです。正常に動作しています！',
        icon: '/favicon.ico',
      });
    } else {
      alert('プッシュ通知が有効でないか、ブラウザがサポートしていません。');
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-text-primary">通知設定</h2>
        <p className="text-sm text-text-secondary mt-1">
          受け取る通知の種類と頻度をカスタマイズできます
        </p>
      </div>

      <div className="space-y-8">
        {/* メール通知 */}
        <div className="border-b border-border-primary pb-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <EnvelopeIcon className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-text-primary">メール通知</h3>
              <p className="text-sm text-text-secondary">登録されたメールアドレスに通知を送信</p>
            </div>
          </div>

          <div className="ml-11 space-y-4">
            {/* メール通知総合設定 */}
            <div className="flex items-center justify-between p-3 bg-surface-background rounded-lg border border-border-primary">
              <div>
                <h4 className="font-medium text-text-primary">メール通知を受け取る</h4>
                <p className="text-sm text-text-secondary">すべてのメール通知の総合設定</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.email.enabled}
                  onChange={(e) => handleSettingChange('email', 'enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-primary"></div>
              </label>
            </div>

            {settings.email.enabled && (
              <div className="space-y-3 pl-4 border-l-2 border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">Miraikakakuからのお知らせ</h5>
                    <p className="text-xs text-text-secondary">新機能やメンテナンス情報</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.email.news_updates}
                      onChange={(e) => handleSettingChange('email', 'news_updates', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">週次パフォーマンスレポート</h5>
                    <p className="text-xs text-text-secondary">毎週のポートフォリオ状況</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.email.weekly_reports}
                      onChange={(e) => handleSettingChange('email', 'weekly_reports', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">ウォッチリスト銘柄の重要ニュース</h5>
                    <p className="text-xs text-text-secondary">注目銘柄の決算・業績発表</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.email.watchlist_news}
                      onChange={(e) => handleSettingChange('email', 'watchlist_news', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">セキュリティアラート</h5>
                    <p className="text-xs text-text-secondary">ログインや設定変更の通知</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.email.security_alerts}
                      onChange={(e) => handleSettingChange('email', 'security_alerts', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* プッシュ通知 */}
        <div className="border-b border-border-primary pb-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-500/10 rounded-lg">
              <DevicePhoneMobileIcon className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-text-primary">プッシュ通知</h3>
              <p className="text-sm text-text-secondary">ブラウザでリアルタイム通知を受信</p>
            </div>
          </div>

          <div className="ml-11 space-y-4">
            {/* プッシュ通知権限状態 */}
            {pushPermission === 'denied' && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  プッシュ通知が拒否されています。ブラウザの設定で通知を許可してください。
                </p>
              </div>
            )}

            {/* プッシュ通知総合設定 */}
            <div className="flex items-center justify-between p-3 bg-surface-background rounded-lg border border-border-primary">
              <div>
                <h4 className="font-medium text-text-primary">プッシュ通知を受け取る</h4>
                <p className="text-sm text-text-secondary">リアルタイム通知の総合設定</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.push.enabled}
                  onChange={(e) => handlePushToggle(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-primary"></div>
              </label>
            </div>

            {settings.push.enabled && (
              <div className="space-y-3 pl-4 border-l-2 border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">設定した株価への到達アラート</h5>
                    <p className="text-xs text-text-secondary">価格アラートの即座通知</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.push.price_alerts}
                      onChange={(e) => handleSettingChange('push', 'price_alerts', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">AIによる売買シグナル通知</h5>
                    <p className="text-xs text-text-secondary">AI分析による推奨アクション</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.push.ai_signals}
                      onChange={(e) => handleSettingChange('push', 'ai_signals', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">出来高の急増アラート</h5>
                    <p className="text-xs text-text-secondary">異常な出来高増加の検出</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.push.volume_alerts}
                      onChange={(e) => handleSettingChange('push', 'volume_alerts', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-text-primary">市場開始・終了通知</h5>
                    <p className="text-xs text-text-secondary">取引時間の開始・終了をお知らせ</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.push.market_hours}
                      onChange={(e) => handleSettingChange('push', 'market_hours', e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-accent-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-primary"></div>
                  </label>
                </div>

                <div className="mt-4 pt-3 border-t border-border-primary">
                  <button
                    onClick={testPushNotification}
                    className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium"
                  >
                    テスト通知を送信
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 通知頻度・タイミング設定 */}
        <div>
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <BellIcon className="w-6 h-6 text-purple-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-text-primary">通知タイミング</h3>
              <p className="text-sm text-text-secondary">通知を受け取る時間帯と頻度</p>
            </div>
          </div>

          <div className="ml-11 space-y-4">
            <div className="p-4 bg-surface-background rounded-lg border border-border-primary">
              <h4 className="font-medium text-text-primary mb-3">通知を受け取る時間帯</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-1">開始時刻</label>
                  <select className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary">
                    <option value="06:00">06:00</option>
                    <option value="07:00">07:00</option>
                    <option value="08:00">08:00</option>
                    <option value="09:00" selected>09:00</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-1">終了時刻</label>
                  <select className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary">
                    <option value="18:00">18:00</option>
                    <option value="19:00">19:00</option>
                    <option value="20:00">20:00</option>
                    <option value="21:00" selected>21:00</option>
                  </select>
                </div>
              </div>
              <p className="text-xs text-text-secondary mt-2">
                指定した時間帯外は緊急通知のみ送信されます
              </p>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <InformationCircleIcon className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h5 className="text-sm font-medium text-blue-800 mb-1">通知に関する注意</h5>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• セキュリティアラートは時間に関係なく常に送信されます</li>
                    <li>• プッシュ通知はブラウザの設定により制限される場合があります</li>
                    <li>• 通知が多すぎる場合は、設定を調整してください</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 保存ボタン */}
        <div className="pt-6 border-t border-border-primary">
          <button
            onClick={saveSettings}
            disabled={isLoading}
            className="bg-accent-primary hover:bg-accent-primary/90 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '保存中...' : '設定を保存'}
          </button>
        </div>
      </div>
    </div>
  );
}