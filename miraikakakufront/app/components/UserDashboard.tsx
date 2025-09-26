'use client';

import React, { useState, useEffect } from 'react';
import {
  User,
  Star,
  Bell,
  Settings,
  Plus,
  AlertTriangle,
  BarChart3,
  LogOut
} from 'lucide-react';

interface UserData {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  bio?: string;
  investment_experience?: string;
  risk_tolerance?: string;
  is_premium: boolean;
  created_at: string;
}

interface Watchlist {
  id: number;
  name: string;
  description?: string;
  symbols: string[];
  is_public: boolean;
  created_at: string;
}

interface PriceAlert {
  id: number;
  symbol: string;
  alert_type: string;
  target_price?: string;
  percentage_change?: string;
  is_active: boolean;
  created_at: string;
}

interface UserDashboardProps {
  user: UserData;
  onLogout: () => void;
}

export const UserDashboard: React.FC<UserDashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'watchlists' | 'alerts' | 'settings'>('overview');
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [newWatchlist, setNewWatchlist] = useState({ name: '', symbols: '', description: '' });
  const [newAlert, setNewAlert] = useState({ symbol: '', alertType: 'above', targetPrice: '', percentageChange: '' });
  useEffect(() => {
    fetchUserData();
  }, []);
  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const [watchlistsRes, alertsRes] = await Promise.all([
        fetch('http://localhost:8080/api/user/watchlists', { headers: getAuthHeaders() }),
        fetch('http://localhost:8080/api/user/alerts', { headers: getAuthHeaders() })
      ]);
      if (watchlistsRes.ok) {
        const watchlistsData = await watchlistsRes.json();
        setWatchlists(watchlistsData.watchlists || []);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWatchlist = async () => {
    if (!newWatchlist.name.trim()) return;

    try {
      const symbols = newWatchlist.symbols.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
      const response = await fetch('http://localhost:8080/api/user/watchlists', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          name: newWatchlist.name,
          description: newWatchlist.description,
          symbols: symbols,
          is_public: false
        })
      });
      if (response.ok) {
        setNewWatchlist({ name: '', symbols: '', description: '' });
        fetchUserData();
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const createAlert = async () => {
    if (!newAlert.symbol.trim()) return;

    try {
      const payload: any = {
        symbol: newAlert.symbol.toUpperCase(),
        alert_type: newAlert.alertType
      };

      if (newAlert.targetPrice) {
        payload.target_price = parseFloat(newAlert.targetPrice);
      }
      if (newAlert.percentageChange) {
        payload.percentage_change = parseFloat(newAlert.percentageChange);
      }

      const response = await fetch('http://localhost:8080/api/user/alerts', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        setNewAlert({ symbol: '', alertType: 'above', targetPrice: '', percentageChange: '' });
        fetchUserData();
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* User Profile Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {user.full_name || user.username}
            </h2>
            <p className="text-gray-600">{user.email}</p>
            {user.is_premium && (
              <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                Premium
              </span>
            )}
          </div>
        </div>

        {user.bio && (
          <p className="text-gray-700 mb-4">{user.bio}</p>
        )}

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">投資経験:</span>
            <span className="ml-2 font-medium">
              {user.investment_experience
                ? (user.investment_experience === 'beginner' ? '初心者'
                 : user.investment_experience === 'intermediate' ? '中級者' : '上級者')
                : '未設定'
              }
            </span>
          </div>
          <div>
            <span className="text-gray-500">リスク許容度:</span>
            <span className="ml-2 font-medium">
              {user.risk_tolerance
                ? (user.risk_tolerance === 'conservative' ? '保守的'
                 : user.risk_tolerance === 'moderate' ? '中程度' : '積極的')
                : '未設定'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Star className="w-8 h-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-gray-900">{watchlists.length}</p>
              <p className="text-gray-600">ウォッチリスト</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Bell className="w-8 h-8 text-blue-500 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-gray-900">{alerts.length}</p>
              <p className="text-gray-600">アクティブアラート</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-green-500 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-gray-900">
                {watchlists.reduce((total, wl) => total + wl.symbols.length, 0)}
              </p>
              <p className="text-gray-600">監視中銘柄</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderWatchlists = () => (
    <div className="space-y-6">
      {/* Create New Watchlist */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">新しいウォッチリストを作成</h3>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="ウォッチリスト名"
            value={newWatchlist.name}
            onChange={(e) => setNewWatchlist({ ...newWatchlist, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="銘柄コード (カンマ区切り: AAPL, GOOGL, MSFT)"
            value={newWatchlist.symbols}
            onChange={(e) => setNewWatchlist({ ...newWatchlist, symbols: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="説明（任意）"
            value={newWatchlist.description}
            onChange={(e) => setNewWatchlist({ ...newWatchlist, description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={createWatchlist}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            ウォッチリストを作成
          </button>
        </div>
      </div>

      {/* Existing Watchlists */}
      <div className="space-y-4">
        {watchlists.map((watchlist) => (
          <div key={watchlist.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold text-gray-900">{watchlist.name}</h4>
              <span className="text-sm text-gray-500">{formatDate(watchlist.created_at)}</span>
            </div>
            {watchlist.description && (
              <p className="text-gray-600 mb-3">{watchlist.description}</p>
            )}
            <div className="flex flex-wrap gap-2">
              {watchlist.symbols.map((symbol) => (
                <span key={symbol} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  {symbol}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-6">
      {/* Create New Alert */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">新しい価格アラートを作成</h3>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="銘柄コード (例: AAPL)"
            value={newAlert.symbol}
            onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={newAlert.alertType}
            onChange={(e) => setNewAlert({ ...newAlert, alertType: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="above">価格が上回った時</option>
            <option value="below">価格が下回った時</option>
            <option value="change_percent">変動率が一定以上の時</option>
          </select>
          {(newAlert.alertType === 'above' || newAlert.alertType === 'below') && (
            <input
              type="number"
              placeholder="目標価格"
              value={newAlert.targetPrice}
              onChange={(e) => setNewAlert({ ...newAlert, targetPrice: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          )}
          {newAlert.alertType === 'change_percent' && (
            <input
              type="number"
              placeholder="変動率 (%)"
              value={newAlert.percentageChange}
              onChange={(e) => setNewAlert({ ...newAlert, percentageChange: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          )}
          <button
            onClick={createAlert}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            アラートを作成
          </button>
        </div>
      </div>

      {/* Existing Alerts */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div key={alert.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <div>
                  <h4 className="font-semibold text-gray-900">{alert.symbol}</h4>
                  <p className="text-sm text-gray-600">
                    {alert.alert_type === 'above' && `${alert.target_price}円を上回った時`}
                    {alert.alert_type === 'below' && `${alert.target_price}円を下回った時`}
                    {alert.alert_type === 'change_percent' && `${alert.percentage_change}%以上変動した時`}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  alert.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {alert.is_active ? 'アクティブ' : '無効'}
                </span>
                <span className="text-sm text-gray-500">{formatDate(alert.created_at)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">ダッシュボード</h1>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <LogOut className="w-5 h-5" />
              <span>ログアウト</span>
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex space-x-8">
            {[
              { key: 'overview', label: '概要', icon: User },
              { key: 'watchlists', label: 'ウォッチリスト', icon: Star },
              { key: 'alerts', label: 'アラート', icon: Bell },
              { key: 'settings', label: '設定', icon: Settings }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                  activeTab === key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'watchlists' && renderWatchlists()}
            {activeTab === 'alerts' && renderAlerts()}
            {activeTab === 'settings' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">設定</h3>
                <p className="text-gray-600">設定機能は開発中です。</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};