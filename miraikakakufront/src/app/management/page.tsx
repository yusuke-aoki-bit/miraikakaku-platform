'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Users, Database, Brain, Activity, AlertTriangle } from 'lucide-react';

interface SystemStats {
  total_users: number;
  total_stocks: number;
  total_predictions: number;
  today_predictions: number;
  today_inferences: number;
  recent_active_users: number;
  system_uptime: string;
  last_updated: string;
}

interface ModelPerformance {
  model_name: string;
  total_predictions: number;
  avg_confidence: number;
  avg_accuracy: number;
  last_prediction: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export default function ManagementPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'models' | 'logs'>('overview');
  const [loading, setLoading] = useState(true);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSystemStats(),
        fetchModelPerformance(),
        fetchUsers()
      ]);
    } catch (error) {
      console.error('管理データ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const fetchSystemStats = async () => {
    try {
      const response = await fetch('/api/admin/system/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('システム統計取得エラー:', error);
    }
  };

  const fetchModelPerformance = async () => {
    try {
      const response = await fetch('/api/admin/models/performance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setModelPerformance(data);
      }
    } catch (error) {
      console.error('モデル性能取得エラー:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('ユーザー一覧取得エラー:', error);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* システム統計カード */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-blue-50 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">総ユーザー数</p>
                <p className="text-3xl font-bold text-blue-900">{stats.total_users}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-green-50 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">追跡銘柄数</p>
                <p className="text-3xl font-bold text-green-900">{stats.total_stocks}</p>
              </div>
              <Database className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-purple-50 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">総予測数</p>
                <p className="text-3xl font-bold text-purple-900">{stats.total_predictions}</p>
              </div>
              <Brain className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-orange-50 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">本日の推論</p>
                <p className="text-3xl font-bold text-orange-900">{stats.today_inferences}</p>
              </div>
              <Activity className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* モデル性能サマリー */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4">モデル性能概要</h3>
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">モデル名</th>
                <th className="text-right py-2">予測数</th>
                <th className="text-right py-2">平均信頼度</th>
                <th className="text-right py-2">平均精度</th>
                <th className="text-right py-2">最終予測</th>
              </tr>
            </thead>
            <tbody>
              {modelPerformance.map((model, index) => (
                <tr key={index} className="border-b hover:bg-gray-50">
                  <td className="py-3 font-semibold">{model.model_name}</td>
                  <td className="py-3 text-right">{model.total_predictions}</td>
                  <td className="py-3 text-right">{(model.avg_confidence * 100).toFixed(1)}%</td>
                  <td className="py-3 text-right">{(model.avg_accuracy * 100).toFixed(1)}%</td>
                  <td className="py-3 text-right text-sm text-gray-600">
                    {new Date(model.last_prediction).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">ユーザー管理</h3>
        <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          新規ユーザー
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full table-auto">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">メール</th>
              <th className="text-left py-2">名前</th>
              <th className="text-left py-2">ロール</th>
              <th className="text-left py-2">状態</th>
              <th className="text-left py-2">最終ログイン</th>
              <th className="text-right py-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b hover:bg-gray-50">
                <td className="py-3">{user.email}</td>
                <td className="py-3">{user.name}</td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    user.role === 'admin' ? 'bg-red-100 text-red-800' :
                    user.role === 'analyst' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {user.is_active ? 'アクティブ' : '無効'}
                  </span>
                </td>
                <td className="py-3 text-sm text-gray-600">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'なし'}
                </td>
                <td className="py-3 text-right">
                  <button className="text-blue-600 hover:text-blue-800 mr-2">編集</button>
                  <button className="text-red-600 hover:text-red-800">削除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <div className="text-gray-600">管理画面を読み込み中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* ヘッダー */}
      <div className="bg-white shadow">
        <div className="container mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">システム管理</h1>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="container mx-auto px-6 py-6">
        <div className="flex space-x-1 mb-6">
          {[
            { id: 'overview', label: '概要', icon: Activity },
            { id: 'users', label: 'ユーザー', icon: Users },
            { id: 'models', label: 'モデル', icon: Brain },
            { id: 'logs', label: 'ログ', icon: AlertTriangle },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'overview' | 'users' | 'models' | 'logs')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* タブコンテンツ */}
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'models' && (
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-bold mb-4">モデル管理</h3>
            <p className="text-gray-600">MLモデルの管理機能（実装予定）</p>
          </div>
        )}
        {activeTab === 'logs' && (
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-bold mb-4">システムログ</h3>
            <p className="text-gray-600">システムログの表示機能（実装予定）</p>
          </div>
        )}
      </div>
    </div>
  );
}