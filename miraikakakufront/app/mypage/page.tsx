'use client';

import { useEffect, useState } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { useToast } from '@/components/Toast';
import LoadingSpinner from '@/components/LoadingSpinner';
import EnhancedPortfolio from '@/components/EnhancedPortfolio';
import PriceAlertManager from '@/components/PriceAlertManager';

interface WatchlistItem {
  id: number;
  symbol: string;
  company_name: string;
  exchange: string;
  added_at: string;
  notes?: string;
  current_price?: number;
  prediction_change?: number;
}

export default function MyPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { showToast } = useToast();
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'watchlist' | 'portfolio' | 'alerts'>('watchlist');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  useEffect(() => {
    if (status === 'authenticated' && session) {
      loadWatchlist();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, session]);

  const loadWatchlist = async () => {
    try {
      setLoading(true);
      setError('');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const token = (session as any)?.accessToken;
      if (!token) {
        throw new Error('No access token');
      }
      const data = await apiClient.getWatchlist(token);
      setWatchlist(data);
    } catch (err) {
      console.error('Failed to load watchlist:', err);
      setError('ウォッチリストの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (symbol: string) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const token = (session as any)?.accessToken;
      if (!token) return;

      await apiClient.removeFromWatchlist(token, symbol);
      setWatchlist(watchlist.filter(item => item.symbol !== symbol));
      showToast('ウォッチリストから削除しました', 'success');
    } catch (err) {
      console.error('Failed to remove from watchlist:', err);
      showToast('削除に失敗しました', 'error');
    }
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const handleSignOut = async () => {
    await signOut({ callbackUrl: '/' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            マイページ
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            アカウント情報とお気に入り銘柄の管理
          </p>
        </div>

        {/* User Info Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
            アカウント情報
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">ユーザー名</p>
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                {session.user?.name || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">メールアドレス</p>
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                {session.user?.email || 'N/A'}
              </p>
            </div>
          </div>
          <div className="mt-6">
            <button
              onClick={handleSignOut}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
            >
              ログアウト
            </button>
          </div>
        </div>

        {/* タブナビゲーション */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg mb-6">
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('watchlist')}
              className={`flex-1 px-6 py-4 text-center font-semibold transition-colors ${
                activeTab === 'watchlist'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              ウォッチリスト
            </button>
            <button
              onClick={() => setActiveTab('portfolio')}
              className={`flex-1 px-6 py-4 text-center font-semibold transition-colors ${
                activeTab === 'portfolio'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              ポートフォリオ
            </button>
            <button
              onClick={() => setActiveTab('alerts')}
              className={`flex-1 px-6 py-4 text-center font-semibold transition-colors ${
                activeTab === 'alerts'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              価格アラート
            </button>
          </div>
        </div>

        {/* ウォッチリストタブ */}
        {activeTab === 'watchlist' && (
          <>
            {/* Watchlist Statistics */}
            {watchlist.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
                <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                  ウォッチリスト統計
                </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">登録銘柄数</p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {watchlist.length}
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均予測変動率</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {(() => {
                    const validPredictions = watchlist.filter(item => item.prediction_change !== null && item.prediction_change !== undefined);
                    if (validPredictions.length === 0) return 'N/A';
                    const avg = validPredictions.reduce((sum, item) => sum + (item.prediction_change || 0), 0) / validPredictions.length;
                    return `${avg >= 0 ? '+' : ''}${avg.toFixed(2)}%`;
                  })()}
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">最高予測変動率</p>
                <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {(() => {
                    const validPredictions = watchlist.filter(item => item.prediction_change !== null && item.prediction_change !== undefined);
                    if (validPredictions.length === 0) return 'N/A';
                    const max = Math.max(...validPredictions.map(item => item.prediction_change || 0));
                    return `+${max.toFixed(2)}%`;
                  })()}
                </p>
              </div>
              <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">価格データあり</p>
                <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                  {watchlist.filter(item => item.current_price).length}/{watchlist.length}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Watchlist Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
              ウォッチリスト ({watchlist.length}銘柄)
            </h2>
            {watchlist.length > 0 && (
              <button
                onClick={() => router.push('/search')}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
              >
                + 銘柄を追加
              </button>
            )}
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="text-gray-600 dark:text-gray-400">読み込み中...</div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          ) : watchlist.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                ウォッチリストが空です
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                お気に入りの銘柄を追加して、簡単に追跡しましょう
              </p>
              <button
                onClick={() => router.push('/search')}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
              >
                銘柄を検索
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {watchlist.map((item) => (
                <div
                  key={item.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 cursor-pointer" onClick={() => router.push(`/stock/${item.symbol}`)}>
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {item.symbol}
                        </h3>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {item.company_name}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300">
                          {item.exchange}
                        </span>
                        {item.current_price && (
                          <span className="text-gray-700 dark:text-gray-300">
                            現在価格: ¥{item.current_price.toFixed(2)}
                          </span>
                        )}
                        {item.prediction_change !== null && item.prediction_change !== undefined && (
                          <span className={`font-medium ${
                            item.prediction_change >= 0
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-red-600 dark:text-red-400'
                          }`}>
                            予測変動: {item.prediction_change >= 0 ? '+' : ''}{item.prediction_change.toFixed(2)}%
                          </span>
                        )}
                      </div>
                      {item.notes && (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                          メモ: {item.notes}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemove(item.symbol);
                      }}
                      className="ml-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                    >
                      削除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
          </>
        )}

        {/* ポートフォリオタブ */}
        {activeTab === 'portfolio' && (
          <EnhancedPortfolio />
        )}

        {/* 価格アラートタブ */}
        {activeTab === 'alerts' && (
          <PriceAlertManager />
        )}

        {/* Quick Links */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => router.push('/rankings')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 dark:text-white">ランキング</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">予測・精度ランキング</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => router.push('/search')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 dark:text-white">銘柄検索</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">銘柄を検索</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => router.push('/')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 dark:text-white">ホーム</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">トップページ</p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
