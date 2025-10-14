'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiClient, StockInfo } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

const EXCHANGE_NAMES: { [key: string]: string } = {
  'tse': '東京証券取引所',
  'jpx': '日本取引所グループ',
  'nasdaq': 'NASDAQ',
  'nyse': 'ニューヨーク証券取引所',
  'crypto': '暗号通貨',
  'tsx': 'トロント証券取引所',
  'lse': 'ロンドン証券取引所',
  'hkex': '香港証券取引所',
};

export default function ExchangePage() {
  const params = useParams();
  const router = useRouter();
  const exchangeKey = (params.name as string)?.toLowerCase();
  const exchangeName = EXCHANGE_NAMES[exchangeKey] || exchangeKey?.toUpperCase();

  const [stocks, setStocks] = useState<StockInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'symbol' | 'name'>('symbol');
  const [filterTerm, setFilterTerm] = useState('');

  useEffect(() => {
    const fetchStocks = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await apiClient.getAllStocks(1000, exchangeKey.toUpperCase());
        setStocks(data.stocks);
      } catch (err) {
        setError(err instanceof Error ? err.message : '銘柄一覧の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (exchangeKey) {
      fetchStocks();
    }
  }, [exchangeKey]);

  const filteredStocks = stocks
    .filter(stock =>
      stock.symbol.toLowerCase().includes(filterTerm.toLowerCase()) ||
      (stock.company_name?.toLowerCase().includes(filterTerm.toLowerCase()) || false)
    )
    .sort((a, b) => {
      if (sortBy === 'symbol') {
        return a.symbol.localeCompare(b.symbol);
      } else {
        return (a.company_name || '').localeCompare(b.company_name || '');
      }
    });

  const retryFetch = () => {
    setLoading(true);
    setError(null);
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-xl text-gray-700 dark:text-gray-300">{exchangeName}の銘柄を読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="max-w-md w-full">
          <ErrorMessage
            title="取引所データの取得エラー"
            message={error}
            onRetry={retryFetch}
          />
          <div className="mt-4 text-center">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              ホームに戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 dark:text-blue-400 hover:underline mb-4"
          >
            ← ホームに戻る
          </button>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            {exchangeName}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {filteredStocks.length}銘柄
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={filterTerm}
              onChange={(e) => setFilterTerm(e.target.value)}
              placeholder="銘柄コードまたは企業名で絞り込み..."
              className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'symbol' | 'name')}
              className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="symbol">シンボル順</option>
              <option value="name">企業名順</option>
            </select>
          </div>
        </div>

        {/* Stock List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {filteredStocks.length === 0 ? (
            <div className="text-center py-12 text-gray-600 dark:text-gray-400">
              {filterTerm ? '該当する銘柄が見つかりませんでした' : '銘柄データがありません'}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredStocks.map((stock) => (
                <div
                  key={stock.symbol}
                  onClick={() => router.push(`/stock/${stock.symbol}`)}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-lg font-mono font-bold text-blue-600 dark:text-blue-400">
                      {stock.symbol}
                    </span>
                    {stock.is_active && (
                      <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                        アクティブ
                      </span>
                    )}
                  </div>
                  <div className="text-gray-900 dark:text-white font-medium">
                    {stock.company_name || '---'}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {stock.exchange}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
