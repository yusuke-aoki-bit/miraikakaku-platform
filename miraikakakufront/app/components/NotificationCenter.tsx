'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { NotificationWebSocket, AlertNotification } from '@/lib/websocket-client';

/**
 * Notification Center Component
 * リアルタイムアラート通知を表示するコンポーネント
 */
export default function NotificationCenter() {
  const { user, accessToken } = useAuth();
  const [notifications, setNotifications] = useState<AlertNotification[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const wsRef = useRef<NotificationWebSocket | null>(null);

  useEffect(() => {
    // ログイン済みの場合のみWebSocket接続
    if (user && accessToken) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const ws = new NotificationWebSocket(apiUrl, accessToken);

      ws.connect()
        .then(() => {
          setIsConnected(true);
          console.log('✅ Notification WebSocket connected');
        })
        .catch((err) => {
          console.error('❌ Failed to connect WebSocket:', err);
          setIsConnected(false);
        });

      // アラート通知を受信
      const unsubscribe = ws.onAlertTriggered((alert) => {
        console.log('🔔 Alert triggered:', alert);

        // 新しい通知を追加
        setNotifications(prev => [alert, ...prev]);

        // ブラウザ通知（許可されている場合）
        if (Notification.permission === 'granted') {
          new Notification('価格アラート', {
            body: alert.message,
            icon: '/icon-192x192.png',
            badge: '/icon-192x192.png',
          });
        }

        // 音を鳴らす（オプション）
        try {
          const audio = new Audio('/notification.mp3');
          audio.play().catch(err => console.log('Audio playback failed:', err));
        } catch (err) {
          // 音声再生失敗は無視
        }
      });

      wsRef.current = ws;

      return () => {
        unsubscribe();
        ws.disconnect();
        wsRef.current = null;
      };
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [user, accessToken]);

  // ブラウザ通知の許可をリクエスト
  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
    }
  };

  useEffect(() => {
    requestNotificationPermission();
  }, []);

  // 通知をクリア
  const clearNotification = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // ログインしていない場合は表示しない
  if (!user) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 z-50">
      {/* 通知アイコンとバッジ */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow"
      >
        {/* ベルアイコン */}
        <svg
          className="w-6 h-6 text-gray-700"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* 接続状態インジケーター */}
        <div
          className={`absolute top-1 right-1 w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}
          title={isConnected ? '接続済み' : '未接続'}
        />

        {/* 未読バッジ */}
        {notifications.length > 0 && (
          <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
            {notifications.length > 99 ? '99+' : notifications.length}
          </div>
        )}
      </button>

      {/* 通知パネル */}
      {showNotifications && (
        <div className="mt-2 w-96 max-h-[600px] bg-white rounded-lg shadow-2xl overflow-hidden">
          {/* ヘッダー */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 flex justify-between items-center">
            <h3 className="font-bold text-lg">通知</h3>
            <div className="flex gap-2">
              {notifications.length > 0 && (
                <button
                  onClick={clearAllNotifications}
                  className="text-sm bg-white/20 hover:bg-white/30 px-3 py-1 rounded transition-colors"
                >
                  全てクリア
                </button>
              )}
              <button
                onClick={() => setShowNotifications(false)}
                className="text-white hover:bg-white/20 rounded p-1 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* 通知リスト */}
          <div className="max-h-[500px] overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <p className="font-medium">通知はありません</p>
                <p className="text-sm mt-1">アラートがトリガーされると、ここに表示されます</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <div
                    key={`${notification.id}-${notification.timestamp}`}
                    className="p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        {/* 銘柄情報 */}
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-bold text-gray-900">
                            {notification.company_name}
                          </span>
                          <span className="text-sm text-gray-500">
                            ({notification.symbol})
                          </span>
                        </div>

                        {/* アラートメッセージ */}
                        <p className="text-sm text-gray-700 mb-2">
                          {notification.message}
                        </p>

                        {/* 現在価格 */}
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-600">現在価格:</span>
                          <span className="font-bold text-blue-600">
                            ¥{notification.current_price.toLocaleString()}
                          </span>
                        </div>

                        {/* タイムスタンプ */}
                        <p className="text-xs text-gray-400 mt-2">
                          {new Date(notification.timestamp).toLocaleString('ja-JP')}
                        </p>
                      </div>

                      {/* 削除ボタン */}
                      <button
                        onClick={() => clearNotification(notification.id)}
                        className="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* フッター */}
          <div className="bg-gray-50 p-3 text-center border-t border-gray-200">
            <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>{isConnected ? 'リアルタイム接続中' : '接続が切断されました'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
