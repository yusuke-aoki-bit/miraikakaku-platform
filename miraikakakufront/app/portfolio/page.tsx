'use client';

/**
 * Portfolio Dashboard Page
 * Phase 5-2: Frontend Implementation
 *
 * Features:
 * - Display all portfolio holdings with real-time valuation
 * - Show portfolio summary (total value, gain/loss)
 * - Sector allocation visualization
 * - Add new holding button
 * - Delete holding functionality
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  getPortfolioHoldings,
  getPortfolioSummary,
  deletePortfolioHolding,
  formatCurrency,
  formatPercentage,
  getGainLossColor,
} from '@/app/lib/portfolio-api';
import type { PortfolioHolding, PortfolioSummary } from '@/app/types/portfolio';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function PortfolioPage() {
  const router = useRouter();
  const [holdings, setHoldings] = useState<PortfolioHolding[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  // For demo, we'll use a hardcoded user ID
  // In production, this should come from authentication context
  const userId = 'demo_user';

  // Fetch portfolio data
  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [holdingsData, summaryData] = await Promise.all([
        getPortfolioHoldings(userId),
        getPortfolioSummary(userId),
      ]);

      setHoldings(holdingsData);
      setSummary(summaryData);
    } catch (err) {
      console.error('Error fetching portfolio:', err);
      setError(err instanceof Error ? err.message : 'Failed to load portfolio');
    } finally {
      setLoading(false);
    }
  };

  // Handle delete holding
  const handleDelete = async (holdingId: number) => {
    try {
      await deletePortfolioHolding(holdingId, userId);
      setDeleteConfirm(null);
      // Refresh portfolio data
      await fetchPortfolioData();
    } catch (err) {
      console.error('Error deleting holding:', err);
      alert('Failed to delete holding: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  // Initial load
  useEffect(() => {
    fetchPortfolioData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-lg text-gray-600">読み込み中...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-800 mb-2">エラー</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={fetchPortfolioData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              再読み込み
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (holdings.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">ポートフォリオ</h1>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              保有銘柄がありません
            </h2>
            <p className="text-gray-600 mb-6">
              銘柄を追加してポートフォリオを作成しましょう
            </p>
            <Link
              href="/portfolio/add"
              className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
            >
              + 銘柄を追加
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">ポートフォリオ</h1>
          <Link
            href="/portfolio/add"
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
          >
            + 銘柄を追加
          </Link>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">総投資額</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_cost)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">現在価値</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_value)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">評価損益</div>
              <div className={`text-2xl font-bold ${getGainLossColor(summary.unrealized_gain)}`}>
                {formatCurrency(summary.unrealized_gain)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">損益率</div>
              <div className={`text-2xl font-bold ${getGainLossColor(summary.unrealized_gain_pct)}`}>
                {formatPercentage(summary.unrealized_gain_pct)}
              </div>
            </div>
          </div>
        )}

        {/* Holdings Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    銘柄
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    数量
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    購入単価
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    現在価格
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    評価額
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    損益
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    損益率
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-600 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {holdings.map((holding) => (
                  <tr key={holding.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <Link
                          href={`/stock/${holding.symbol}`}
                          className="text-blue-600 font-medium hover:underline"
                        >
                          {holding.symbol}
                        </Link>
                        <span className="text-sm text-gray-600">{holding.company_name}</span>
                        <span className="text-xs text-gray-500">{holding.sector}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right text-gray-900">
                      {holding.quantity.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right text-gray-900">
                      {formatCurrency(holding.purchase_price)}
                    </td>
                    <td className="px-6 py-4 text-right text-gray-900">
                      {formatCurrency(holding.current_price)}
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-gray-900">
                      {formatCurrency(holding.current_value)}
                    </td>
                    <td className={`px-6 py-4 text-right font-medium ${getGainLossColor(holding.unrealized_gain)}`}>
                      {formatCurrency(holding.unrealized_gain)}
                    </td>
                    <td className={`px-6 py-4 text-right font-medium ${getGainLossColor(holding.unrealized_gain_pct)}`}>
                      {formatPercentage(holding.unrealized_gain_pct)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {deleteConfirm === holding.id ? (
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => handleDelete(holding.id)}
                            className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            削除
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="px-3 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                          >
                            キャンセル
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(holding.id)}
                          className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          削除
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Notes Section */}
        {holdings.some(h => h.notes) && (
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">メモ</h3>
            <div className="space-y-3">
              {holdings
                .filter(h => h.notes)
                .map(h => (
                  <div key={h.id} className="flex items-start gap-3">
                    <span className="font-medium text-gray-700">{h.symbol}:</span>
                    <span className="text-gray-600">{h.notes}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
    </ProtectedRoute>
  );
}
