'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface PerformanceHolding {
  id: number;
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
  current_price: number;
  cost_basis: number;
  current_value: number;
  unrealized_pl: number;
  return_pct: number;
  days_held: number;
  annualized_return_pct: number;
  predicted_price?: number;
  ensemble_confidence?: number;
  predicted_change_pct?: number;
}

interface PerformanceSummary {
  total_holdings: number;
  total_cost_basis: number;
  total_current_value: number;
  total_unrealized_pl: number;
  total_return_pct: number;
}

interface SectorAllocation {
  sector: string;
  holdings_count: number;
  total_cost_basis: number;
  total_current_value: number;
  total_unrealized_pl: number;
  sector_return_pct: number;
  allocation_pct: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default function PerformancePage() {
  const [holdings, setHoldings] = useState<PerformanceHolding[]>([]);
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [sectors, setSectors] = useState<SectorAllocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const userId = 'demo_user'; // TODO: 実際の認証から取得

  useEffect(() => {
    loadPerformanceData();
  }, []);

  async function loadPerformanceData() {
    try {
      setLoading(true);
      setError(null);

      // パフォーマンスデータ取得
      const perfResponse = await fetch(`${API_BASE}/api/portfolio/performance?user_id=${userId}`);
      if (!perfResponse.ok) throw new Error('Failed to fetch performance data');
      const perfData = await perfResponse.json();

      setHoldings(perfData.holdings || []);
      setSummary(perfData.summary || null);

      // セクター配分データ取得
      const sectorResponse = await fetch(`${API_BASE}/api/portfolio/sector-allocation?user_id=${userId}`);
      if (!sectorResponse.ok) throw new Error('Failed to fetch sector allocation');
      const sectorData = await sectorResponse.json();

      setSectors(sectorData.sectors || []);
    } catch (err) {
      console.error('Failed to load performance data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  function formatCurrency(value: number): string {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).replace('¥', '').replace('JPY', '') + '円';
  }

  function formatPercent(value: number): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-bold mb-2">エラー</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadPerformanceData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              再読み込み
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">ポートフォリオパフォーマンス</h1>
              <p className="text-gray-600 mt-1">投資成績と分析ダッシュボード</p>
            </div>
            <Link
              href="/portfolio"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              ポートフォリオへ戻る
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* サマリーカード */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">保有銘柄数</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total_holdings}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">投資額</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_cost_basis)}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">評価額</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_current_value)}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">評価損益</p>
              <p className={`text-2xl font-bold ${summary.total_unrealized_pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(summary.total_unrealized_pl)}
              </p>
              <p className={`text-sm ${summary.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercent(summary.total_return_pct)}
              </p>
            </div>
          </div>
        )}

        {/* セクター配分 */}
        {sectors.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">セクター別配分</h2>
            <div className="space-y-4">
              {sectors.map((sector) => (
                <div key={sector.sector} className="border-b border-gray-200 pb-4 last:border-0">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">{sector.sector}</p>
                      <p className="text-sm text-gray-600">{sector.holdings_count} 銘柄</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">{sector.allocation_pct.toFixed(1)}%</p>
                      <p className={`text-sm ${sector.sector_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercent(sector.sector_return_pct)}
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${sector.allocation_pct}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600 mt-2">
                    <span>評価額: {formatCurrency(sector.total_current_value)}</span>
                    <span className={sector.total_unrealized_pl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      損益: {formatCurrency(sector.total_unrealized_pl)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 保有銘柄パフォーマンス */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">保有銘柄別パフォーマンス</h2>
          </div>

          {holdings.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600 mb-4">保有銘柄がありません</p>
              <Link
                href="/portfolio"
                className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                ポートフォリオに銘柄を追加
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">銘柄</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">取得単価</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">現在価格</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">評価額</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">評価損益</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">リターン</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">保有日数</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {holdings.map((holding) => (
                    <tr key={holding.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{holding.symbol}</div>
                          <div className="text-sm text-gray-500">{holding.company_name}</div>
                          {holding.sector && (
                            <div className="text-xs text-gray-400">{holding.sector}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {holding.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {formatCurrency(holding.purchase_price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {formatCurrency(holding.current_price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                        {formatCurrency(holding.current_value)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <span className={holding.unrealized_pl >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {formatCurrency(holding.unrealized_pl)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <span className={holding.return_pct >= 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                          {formatPercent(holding.return_pct)}
                        </span>
                        <div className="text-xs text-gray-500">
                          年率: {holding.annualized_return_pct.toFixed(2)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                        {holding.days_held}日
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
