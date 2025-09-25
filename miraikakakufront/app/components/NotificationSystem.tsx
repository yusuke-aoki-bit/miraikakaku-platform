'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Bell
  X
  AlertTriangle
  Info
  CheckCircle
  XCircle
  Settings
  Volume2
  VolumeX
} from 'lucide-react';

interface Notification {
  id: string;
  type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  data?: any;
  expires_at?: string;
}

interface NotificationToast extends Notification {
  isVisible: boolean;
  timeoutId?: NodeJS.Timeout;
}

export const NotificationSystem: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false
  const [notifications, setNotifications] = useState<Notification[]>([]
  const [toasts, setToasts] = useState<NotificationToast[]>([]
  const [isDropdownOpen, setIsDropdownOpen] = useState(false
  const [soundEnabled, setSoundEnabled] = useState(true
  const [unreadCount, setUnreadCount] = useState(0
  const wsRef = useRef<WebSocket | null>(null
  const audioRef = useRef<HTMLAudioElement | null>(null
  useEffect(() => {
    // Create audio element for notification sounds
    audioRef.current = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBTuR1/LNeSsFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaBQ=='
    audioRef.current.volume = 0.3;

    connectWebSocket(
    return () => {
      if (wsRef.current) {
        wsRef.current.close(
      }
    };
  }, []
  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8080/ws/notifications`;
    const ws = new WebSocket(wsUrl
    ws.onopen = () => {
      setIsConnected(true
      };

    ws.onclose = () => {
      setIsConnected(false
      // Attempt to reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000
    };

    ws.onerror = (error) => {
      setIsConnected(false
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data
        if (data.type === 'notification') {
          handleNewNotification(data.notification
        } else if (data.type === 'notification_history') {
          setNotifications(data.notifications
        }
      } catch (error) {
        }
    };

    wsRef.current = ws;
  };

  const handleNewNotification = (notification: Notification) => {
    // Add to notifications list
    setNotifications(prev => [notification, ...prev].slice(0, 100)); // Keep last 100

    // Create toast
    const toast: NotificationToast = {
      ...notification
      isVisible: true
    };

    // Play sound if enabled
    if (soundEnabled && audioRef.current) {
      audioRef.current.play().catch(console.error
    }

    // Add toast
    setToasts(prev => [toast, ...prev]
    // Auto-remove toast after delay
    const delay = getSeverityDelay(notification.severity
    toast.timeoutId = setTimeout(() => {
      removeToast(toast.id
    }, delay
    // Update unread count
    setUnreadCount(prev => prev + 1
  };

  const getSeverityDelay = (severity: string): number => {
    switch (severity) {
      case 'critical': return 10000; // 10 seconds
      case 'error': return 8000;     // 8 seconds
      case 'warning': return 6000;   // 6 seconds
      case 'info': return 4000;      // 4 seconds
      default: return 5000;
    }
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => {
      if (toast.id === id) {
        if (toast.timeoutId) {
          clearTimeout(toast.timeoutId
        }
        return false;
      }
      return true;
    })
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical'
      case 'error'
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning'
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info'
        return <Info className="w-5 h-5 text-blue-500" />;
      default
        return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical'
      case 'error'
        return 'border-red-200 bg-red-50';
      case 'warning'
        return 'border-yellow-200 bg-yellow-50';
      case 'info'
        return 'border-blue-200 bg-blue-50';
      default
        return 'border-green-200 bg-green-50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ja-JP'
  };

  const clearAllNotifications = () => {
    setNotifications([]
    setUnreadCount(0
  };

  const markAsRead = () => {
    setUnreadCount(0
  };

  return (
    <>
      {/* Notification Bell Icon */}
      <div className="relative">
        <button
          onClick={() => {
            setIsDropdownOpen(!isDropdownOpen
            markAsRead(
          }}
          className="p-2 rounded-full hover:bg-gray-100 transition-colors relative"
          title="通知"
        >
          <Bell className={`w-6 h-6 ${isConnected ? 'text-gray-700' : 'text-gray-400'}`} />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
          {!isConnected && (
            <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          )}
        </button>

        {/* Notification Dropdown */}
        {isDropdownOpen && (
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border z-50 max-h-96 overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">通知</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className="p-1 rounded hover:bg-gray-100"
                  title={soundEnabled ? '音を無効にする' : '音を有効にする'}
                >
                  {soundEnabled ? (
                    <Volume2 className="w-4 h-4 text-gray-600" />
                  ) : (
                    <VolumeX className="w-4 h-4 text-gray-600" />
                  )}
                </button>
                <button
                  onClick={clearAllNotifications}
                  className="text-sm text-blue-600 hover:underline"
                >
                  すべて削除
                </button>
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  通知はありません
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b hover:bg-gray-50 ${getSeverityColor(notification.severity)}`}
                  >
                    <div className="flex items-start space-x-3">
                      {getSeverityIcon(notification.severity)}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {notification.title}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          {formatTimestamp(notification.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {!isConnected && (
              <div className="p-4 bg-yellow-50 border-t border-yellow-200">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm text-yellow-700">
                    通知サーバーに接続していません
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`
              max-w-sm p-4 rounded-lg shadow-lg border transform transition-all duration-300
              ${toast.isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
              ${getSeverityColor(toast.severity)}
            `}
          >
            <div className="flex items-start space-x-3">
              {getSeverityIcon(toast.severity)}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900">
                  {toast.title}
                </h4>
                <p className="text-sm text-gray-600 mt-1">
                  {toast.message}
                </p>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Click outside to close dropdown */}
      {isDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </>
};