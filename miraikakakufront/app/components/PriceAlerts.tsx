'use client';

import React, { useState } from 'react';
import { Bell, Plus, Trash2, TrendingUp, TrendingDown, Target } from 'lucide-react';

interface PriceAlert {
  id: string;
  symbol: string;
  targetPrice: number;
  type: 'above' | 'below';
  currentPrice: number;
  isActive: boolean;
  createdAt: Date;
}

interface PriceAlertsProps {
  symbol: string;
  currentPrice: number;
}

export default function PriceAlerts({ symbol, currentPrice }: PriceAlertsProps) {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]
  const [showAddForm, setShowAddForm] = useState(false
  const [newAlert, setNewAlert] = useState({
    targetPrice: ''
    type: 'above' as 'above' | 'below'
  }
  // Load alerts from localStorage on component mount
  React.useEffect(() => {
    const savedAlerts = localStorage.getItem(`alerts_${symbol}`
    if (savedAlerts) {
      try {
        const parsed = JSON.parse(savedAlerts
        setAlerts(parsed.map((alert: any) => ({
          ...alert
          createdAt: new Date(alert.createdAt)
        }))
      } catch (error) {
        }
    }
  }, [symbol]
  // Save alerts to localStorage whenever alerts change
  React.useEffect(() => {
    localStorage.setItem(`alerts_${symbol}`, JSON.stringify(alerts)
  }, [alerts, symbol]
  const addAlert = () => {
    const targetPrice = parseFloat(newAlert.targetPrice
    if (isNaN(targetPrice) || targetPrice <= 0) {
      window.alert('有効な価格を入力してください'
      return;
    }

    // Check if alert makes sense
    if (newAlert.type === 'above' && targetPrice <= currentPrice) {
      if (!window.confirm('現在価格より低い価格で「上昇アラート」を設定しますか？')) {
        return;
      }
    }
    if (newAlert.type === 'below' && targetPrice >= currentPrice) {
      if (!window.confirm('現在価格より高い価格で「下落アラート」を設定しますか？')) {
        return;
      }
    }

    const newPriceAlert: PriceAlert = {
      id: Date.now().toString()
      symbol
      targetPrice
      type: newAlert.type
      currentPrice
      isActive: true
      createdAt: new Date()
    };

    setAlerts(prev => [...prev, newPriceAlert]
    setNewAlert({ targetPrice: '', type: 'above' }
    setShowAddForm(false
  };

  const removeAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id)
  };

  const toggleAlert = (id: string) => {
    setAlerts(prev => prev.map(alert =>
      alert.id === id ? { ...alert, isActive: !alert.isActive } : alert
    )
  };

  const getAlertStatus = (alert: PriceAlert) => {
    if (!alert.isActive) return 'inactive';

    if (alert.type === 'above' && currentPrice >= alert.targetPrice) {
      return 'triggered';
    }
    if (alert.type === 'below' && currentPrice <= alert.targetPrice) {
      return 'triggered';
    }
    return 'active';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'triggered': return 'text-red-600 bg-red-50 border-red-200';
      case 'active': return 'text-green-600 bg-green-50 border-green-200';
      case 'inactive': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'triggered': return '発火';
      case 'active': return '監視中';
      case 'inactive': return '停止中';
      default: return '不明';
    }
  };

  const calculateDistance = (alert: PriceAlert) => {
    const distance = ((alert.targetPrice - currentPrice) / currentPrice * 100
    const absDistance = Math.abs(distance
    const direction = distance > 0 ? '上' : '下';
    return `${direction}${absDistance.toFixed(1)}%`;
  };

  return (
    <div className="rounded-lg shadow-md p-6" style={{
      backgroundColor: 'var(--yt-music-surface)'
      border: '1px solid var(--yt-music-border)'
    }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center" style={{ color: 'var(--yt-music-text-primary)' }}>
          <Bell className="w-5 h-5 mr-2" />
          価格アラート
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
          title="アラート追加"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Add Alert Form */}
      {showAddForm && (
        <div className="mb-4 p-4 border border-gray-200 rounded-lg" style={{
          backgroundColor: 'var(--yt-music-bg)'
        }}>
          <h4 className="font-medium mb-3" style={{ color: 'var(--yt-music-text-primary)' }}>
            新しいアラート
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--yt-music-text-secondary)' }}>
                目標価格
              </label>
              <input
                type="number"
                value={newAlert.targetPrice}
                onChange={(e) => setNewAlert(prev => ({ ...prev, targetPrice: e.target.value }))}
                placeholder={`現在価格: ¥${currentPrice.toFixed(2)}`}
                className="w-full p-2 border border-gray-300 rounded-lg"
                step="0.01"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--yt-music-text-secondary)' }}>
                アラートタイプ
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setNewAlert(prev => ({ ...prev, type: 'above' }))}
                  className={`flex-1 p-2 rounded-lg border flex items-center justify-center ${
                    newAlert.type === 'above'
                      ? 'bg-green-50 border-green-200 text-green-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600'
                  }`}
                >
                  <TrendingUp className="w-4 h-4 mr-1" />
                  上昇時
                </button>
                <button
                  onClick={() => setNewAlert(prev => ({ ...prev, type: 'below' }))}
                  className={`flex-1 p-2 rounded-lg border flex items-center justify-center ${
                    newAlert.type === 'below'
                      ? 'bg-red-50 border-red-200 text-red-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600'
                  }`}
                >
                  <TrendingDown className="w-4 h-4 mr-1" />
                  下落時
                </button>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={addAlert}
                className="flex-1 bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                アラート追加
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="px-4 bg-gray-300 text-gray-700 p-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alerts List */}
      {alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const status = getAlertStatus(alert
            return (
              <div key={alert.id} className="border border-gray-200 rounded-lg p-3" style={{
                backgroundColor: 'var(--yt-music-bg)'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    {alert.type === 'above' ? (
                      <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-2 text-red-600" />
                    )}
                    <span className="font-medium" style={{ color: 'var(--yt-music-text-primary)' }}>
                      ¥{alert.targetPrice.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(status)}`}>
                      {getStatusText(status)}
                    </div>
                    <button
                      onClick={() => toggleAlert(alert.id)}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title={alert.isActive ? "停止" : "開始"}
                    >
                      <Target className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => removeAlert(alert.id)}
                      className="p-1 text-red-500 hover:text-red-700"
                      title="削除"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="flex justify-between text-sm" style={{ color: 'var(--yt-music-text-secondary)' }}>
                  <span>
                    {alert.type === 'above' ? '上昇' : '下落'}アラート
                  </span>
                  <span>
                    距離: {calculateDistance(alert)}
                  </span>
                </div>
                {status === 'triggered' && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    🚨 アラート発火！目標価格に到達しました
                  </div>
                )}
              </div>
          })}
        </div>
      ) : (
        <div className="text-center py-8" style={{ color: 'var(--yt-music-text-secondary)' }}>
          <Bell className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>アラートが設定されていません</p>
          <p className="text-sm">価格変動を監視するアラートを追加してください</p>
        </div>
      )}

      {/* Quick Actions */}
      {currentPrice > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm font-medium mb-2" style={{ color: 'var(--yt-music-text-secondary)' }}>
            クイック設定
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                setNewAlert({
                  targetPrice: (currentPrice * 1.05).toFixed(2)
                  type: 'above'
                }
                setShowAddForm(true
              }}
              className="flex-1 text-xs p-2 bg-green-50 text-green-700 border border-green-200 rounded-lg hover:bg-green-100"
            >
              +5%
            </button>
            <button
              onClick={() => {
                setNewAlert({
                  targetPrice: (currentPrice * 1.1).toFixed(2)
                  type: 'above'
                }
                setShowAddForm(true
              }}
              className="flex-1 text-xs p-2 bg-green-50 text-green-700 border border-green-200 rounded-lg hover:bg-green-100"
            >
              +10%
            </button>
            <button
              onClick={() => {
                setNewAlert({
                  targetPrice: (currentPrice * 0.95).toFixed(2)
                  type: 'below'
                }
                setShowAddForm(true
              }}
              className="flex-1 text-xs p-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100"
            >
              -5%
            </button>
            <button
              onClick={() => {
                setNewAlert({
                  targetPrice: (currentPrice * 0.9).toFixed(2)
                  type: 'below'
                }
                setShowAddForm(true
              }}
              className="flex-1 text-xs p-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100"
            >
              -10%
            </button>
          </div>
        </div>
      )}
    </div>
}