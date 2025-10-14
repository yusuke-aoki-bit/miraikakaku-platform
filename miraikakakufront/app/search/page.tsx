'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient, SearchResult } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';

  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState(query);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await apiClient.searchStocks(query);
        setResults(data.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : '検索に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  const handleStockClick = (symbol: string) => {
    router.push(`/stock/${symbol}`);
  };

  const retryFetch = () => {
    setLoading(true);
    setError(null);
    window.location.reload();
  };

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
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
            検索結果
          </h1>
        </div>

        {/* Search Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <form onSubmit={handleSearch}>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="銘柄コード、企業名で検索..."
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
              >
                検索
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {loading ? (
            <div className="text-center py-12">
              <LoadingSpinner size="lg" className="mb-4" />
              <p className="text-xl text-gray-600 dark:text-gray-400">「{query}」を検索中...</p>
            </div>
          ) : error ? (
            <div className="py-12">
              <ErrorMessage message={error} onRetry={retryFetch} />
            </div>
          ) : !query ? (
            <div className="text-center py-12">
              <div className="text-xl text-gray-600 dark:text-gray-400">
                検索キーワードを入力してください
              </div>
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-xl text-gray-600 dark:text-gray-400 mb-2">
                「{query}」の検索結果が見つかりませんでした
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                別のキーワードで検索してみてください
              </p>
            </div>
          ) : (
            <>
              <div className="mb-4">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
                  「{query}」の検索結果: {results.length}件
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.map((result) => (
                  <div
                    key={result.symbol}
                    onClick={() => handleStockClick(result.symbol)}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-lg font-mono font-bold text-blue-600 dark:text-blue-400">
                        {result.symbol}
                      </span>
                      <span className="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded">
                        {result.exchange}
                      </span>
                    </div>
                    <div className="text-gray-900 dark:text-white font-medium">
                      {result.company_name || '---'}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
