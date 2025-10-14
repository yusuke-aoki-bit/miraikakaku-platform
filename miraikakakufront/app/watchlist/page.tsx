'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getWatchlist, removeFromWatchlist, addToWatchlist, type WatchlistItem } from '@/app/lib/watchlist-api';
import Link from 'next/link';

export default function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const userId = 'demo_user'; // TODO: 実際の認証から取得

  useEffect(() => {
    loadWatchlist();
  }, []);

  async function loadWatchlist() {
    try {
      setLoading(true);
      setError(null);
      const data = await getWatchlist(userId);
      setItems(data);
    } catch (err) {
      console.error('Failed to load watchlist:', err);
      setError('ウォッチリストの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }

  async function handleRemove(id: number) {
    if (!confirm('この銘柄をウォッチリストから削除しますか？')) return;
    try {
      await removeFromWatchlist(id, userId);
      await loadWatchlist();
    } catch (err) {
      console.error('Failed to remove:', err);
      alert('削除に失敗しました');
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!newSymbol.trim()) {
      alert('銘柄コードを入力してください');
      return;
    }

    try {
      await addToWatchlist({
        user_id: userId,
        symbol: newSymbol.trim().toUpperCase(),
        notes: newNotes.trim() || undefined,
        alert_enabled: false,
      });
      setNewSymbol('');
      setNewNotes('');
      setShowAddForm(false);
      await loadWatchlist();
    } catch (err: any) {
      console.error('Failed to add:', err);
      alert(err.message || '追加に失敗しました');
    }
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 p-8">
        <div className="container mx-auto">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">読み込み中...</p>
          </div>
        </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4 md:p-8">
        {/* ヘッダー */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">ウォッチリスト</h1>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          >
            {showAddForm ? 'キャンセル' : '銘柄を追加'}
          </button>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* 追加フォーム */}
        {showAddForm && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">銘柄を追加</h2>
            <form onSubmit={handleAdd}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  銘柄コード *
                </label>
                <input
                  type="text"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value)}
                  placeholder="例: AAPL, 7203.T"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  メモ（任意）
                </label>
                <textarea
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  placeholder="この銘柄についてのメモ..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition"
              >
                追加
              </button>
            </form>
          </div>
        )}

        {/* ウォッチリスト */}
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg mb-4">
              ウォッチリストは空です
            </p>
            <p className="text-gray-400 text-sm">
              気になる銘柄を追加して、価格や予測をチェックしましょう
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {items.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
              >
                {/* ヘッダー */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <Link
                      href={`/stock/${encodeURIComponent(item.symbol)}`}
                      className="text-2xl font-bold text-blue-600 hover:text-blue-800 transition"
                    >
                      {item.symbol}
                    </Link>
                    <p className="text-gray-700 mt-1">{item.company_name}</p>
                    <p className="text-sm text-gray-500">
                      {item.exchange} {item.sector && `• ${item.sector}`}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-red-600 hover:text-red-800 font-medium transition"
                  >
                    削除
                  </button>
                </div>

                {/* 価格情報 */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-t border-b border-gray-200">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">現在価格</p>
                    <p className="text-xl font-bold text-gray-900">
                      ¥{item.current_price.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">変動</p>
                    <p
                      className={`text-xl font-bold ${
                        item.price_change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {item.price_change >= 0 ? '+' : ''}
                      {item.price_change_pct.toFixed(2)}%
                    </p>
                  </div>
                  {item.ensemble_prediction && (
                    <>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">予測価格</p>
                        <p className="text-xl font-bold text-purple-600">
                          ¥{item.ensemble_prediction.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">予測変動</p>
                        <p
                          className={`text-xl font-bold ${
                            item.predicted_change_pct && item.predicted_change_pct >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {item.predicted_change_pct
                            ? `${item.predicted_change_pct >= 0 ? '+' : ''}${item.predicted_change_pct.toFixed(2)}%`
                            : '-'}
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* アラートとメモ */}
                <div className="mt-4 flex flex-wrap gap-2 items-center">
                  {item.alert_triggered && (
                    <span className="inline-flex items-center bg-red-100 text-red-800 text-sm px-3 py-1 rounded-full">
                      🔔 アラート発生
                    </span>
                  )}
                  {item.alert_enabled && !item.alert_triggered && (
                    <span className="inline-flex items-center bg-yellow-100 text-yellow-800 text-sm px-3 py-1 rounded-full">
                      🔔 アラート有効
                    </span>
                  )}
                  {item.ensemble_confidence && (
                    <span className="inline-flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                      信頼度: {item.ensemble_confidence.toFixed(0)}%
                    </span>
                  )}
                </div>

                {item.notes && (
                  <p className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    📝 {item.notes}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
