'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient, PredictionRanking } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { SectorBadge } from '@/components/SectorBadge';

type RankingType = 'prediction' | 'accuracy' | 'gainers' | 'losers' | 'volume';

export default function RankingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [rankings, setRankings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rankingType, setRankingType] = useState<RankingType>('prediction');
  const [limit, setLimit] = useState(50);

  // Phase 4-2: セクターフィルター用の状態
  const [sectors, setSectors] = useState<Array<{ name: string; count: number }>>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [sectorsLoading, setSectorsLoading] = useState(false);

  // Phase 4-2: URL からセクターパラメータを取得
  useEffect(() => {
    const sectorParam = searchParams.get('sector');
    if (sectorParam) {
      setSelectedSector(sectorParam);
    }
  }, [searchParams]);

  // Phase 4-2: セクター一覧の取得
  useEffect(() => {
    const fetchSectors = async () => {
      setSectorsLoading(true);
      try {
        const data = await apiClient.getSectors();
        setSectors(data.sectors || []);
      } catch (err) {
        console.error('Failed to fetch sectors:', err);
      } finally {
        setSectorsLoading(false);
      }
    };

    fetchSectors();
  }, []);

  useEffect(() => {
    const fetchRankings = async () => {
      setLoading(true);
      setError(null);

      try {
        // Phase 4-2: セクターフィルターが選択されている場合
        if (selectedSector) {
          const data = await apiClient.getSectorRankings(selectedSector, rankingType as any, limit);
          setRankings(data.rankings || []);
        } else {
          // 既存のランキング取得ロジック
          if (rankingType === 'prediction') {
            const data = await apiClient.getPredictionRankings(limit);
            setRankings(data.rankings || []);
          } else if (rankingType === 'accuracy') {
            const data = await apiClient.getAccuracyRankings(limit);
            setRankings(data.rankings || []);
          } else if (rankingType === 'gainers') {
            const data = await apiClient.getTopGainers(limit);
            setRankings(data.gainers || []);
          } else if (rankingType === 'losers') {
            const data = await apiClient.getTopLosers(limit);
            setRankings(data.losers || []);
          } else if (rankingType === 'volume') {
            const data = await apiClient.getTopVolume(limit);
            setRankings(data.volume_leaders || []);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'ランキングの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, [rankingType, limit, selectedSector]);

  const handleStockClick = (symbol: string) => {
    router.push(`/stock/${symbol}`);
  };

  // Phase 4-2: セクター選択ハンドラー
  const handleSectorChange = (sector: string) => {
    setSelectedSector(sector);
    // URLを更新
    if (sector) {
      router.push(`/rankings?sector=${encodeURIComponent(sector)}`);
    } else {
      router.push('/rankings');
    }
  };

  const retryFetch = () => {
    setLoading(true);
    setError(null);
    window.location.reload();
  };

  const getRankingTitle = () => {
    const sectorPrefix = selectedSector ? `${selectedSector} - ` : '';
    switch (rankingType) {
      case 'prediction': return `${sectorPrefix}予測変動率ランキング`;
      case 'accuracy': return `${sectorPrefix}予測精度ランキング`;
      case 'gainers': return `${sectorPrefix}値上がりランキング`;
      case 'losers': return `${sectorPrefix}値下がりランキング`;
      case 'volume': return `${sectorPrefix}出来高ランキング`;
      default: return `${sectorPrefix}ランキング`;
    }
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
            ランキング
          </h1>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-col gap-4">
            {/* Phase 4-2: セクターフィルター */}
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center pb-4 border-b border-gray-200 dark:border-gray-700">
              <label className="font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap">
                セクター:
              </label>
              <select
                value={selectedSector}
                onChange={(e) => handleSectorChange(e.target.value)}
                disabled={sectorsLoading}
                className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
              >
                <option value="">全セクター</option>
                {sectors.map((sector) => (
                  <option key={sector.name} value={sector.name}>
                    {sector.name} ({sector.count}銘柄)
                  </option>
                ))}
              </select>
              {selectedSector && (
                <button
                  onClick={() => handleSectorChange('')}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
                >
                  クリア
                </button>
              )}
            </div>

            {/* ランキングタイプと件数 */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setRankingType('prediction')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    rankingType === 'prediction'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  予測変動
                </button>
                <button
                  onClick={() => setRankingType('gainers')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    rankingType === 'gainers'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  値上がり
                </button>
                <button
                  onClick={() => setRankingType('losers')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    rankingType === 'losers'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  値下がり
                </button>
                <button
                  onClick={() => setRankingType('volume')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    rankingType === 'volume'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  出来高
                </button>
                <button
                  onClick={() => setRankingType('accuracy')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    rankingType === 'accuracy'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  予測精度
                </button>
              </div>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value={10}>TOP 10</option>
                <option value={25}>TOP 25</option>
                <option value={50}>TOP 50</option>
                <option value={100}>TOP 100</option>
              </select>
            </div>
          </div>
        </div>

        {/* Rankings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          {loading ? (
            <div className="text-center py-12">
              <LoadingSpinner size="lg" className="mb-4" />
              <p className="text-xl text-gray-600 dark:text-gray-400">ランキングデータを読み込み中...</p>
            </div>
          ) : error ? (
            <div className="py-12">
              <ErrorMessage message={error} onRetry={retryFetch} />
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                {getRankingTitle()} TOP {limit}
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">順位</th>
                      <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">銘柄</th>
                      <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">会社名</th>
                      {rankingType === 'prediction' && (
                        <>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">予測変動率</th>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">信頼度</th>
                        </>
                      )}
                      {(rankingType === 'gainers' || rankingType === 'losers') && (
                        <>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">現在価格</th>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">変動率</th>
                        </>
                      )}
                      {rankingType === 'volume' && (
                        <>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">現在価格</th>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">出来高</th>
                        </>
                      )}
                      {rankingType === 'accuracy' && (
                        <>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">方向精度</th>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">誤差率</th>
                          <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">評価数</th>
                          <th className="text-center py-3 px-4 text-gray-600 dark:text-gray-400">信頼性</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {rankings.map((ranking, idx) => (
                      <tr
                        key={ranking.symbol || idx}
                        onClick={() => handleStockClick(ranking.symbol)}
                        className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                      >
                        <td className="py-3 px-4 text-gray-900 dark:text-white font-semibold">
                          {ranking.rank || idx + 1}
                        </td>
                        <td className="py-3 px-4 font-mono text-blue-600 dark:text-blue-400 hover:underline">
                          {ranking.symbol}
                        </td>
                        <td className="py-3 px-4 text-gray-900 dark:text-white">
                          {ranking.company_name}
                        </td>
                        {rankingType === 'prediction' && (
                          <>
                            <td
                              className={`py-3 px-4 text-right font-semibold ${
                                (ranking.predicted_change_percent ?? 0) > 0
                                  ? 'text-green-600 dark:text-green-400'
                                  : 'text-red-600 dark:text-red-400'
                              }`}
                            >
                              {(ranking.predicted_change_percent ?? 0) > 0 ? '+' : ''}
                              {ranking.predicted_change_percent?.toFixed(2) ?? 'N/A'}%
                            </td>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {ranking.confidence_score ? (ranking.confidence_score * 100).toFixed(1) : 'N/A'}%
                            </td>
                          </>
                        )}
                        {(rankingType === 'gainers' || rankingType === 'losers') && (
                          <>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {ranking.current_price?.toFixed(2) ?? 'N/A'}
                            </td>
                            <td
                              className={`py-3 px-4 text-right font-semibold ${
                                (ranking.change_percent ?? 0) > 0
                                  ? 'text-green-600 dark:text-green-400'
                                  : 'text-red-600 dark:text-red-400'
                              }`}
                            >
                              {(ranking.change_percent ?? 0) > 0 ? '+' : ''}
                              {ranking.change_percent?.toFixed(2) ?? 'N/A'}%
                            </td>
                          </>
                        )}
                        {rankingType === 'volume' && (
                          <>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {ranking.current_price?.toFixed(2) ?? 'N/A'}
                            </td>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {ranking.volume?.toLocaleString() ?? 'N/A'}
                            </td>
                          </>
                        )}
                        {rankingType === 'accuracy' && (
                          <>
                            <td className="py-3 px-4 text-right text-green-600 dark:text-green-400 font-semibold">
                              {ranking.direction_accuracy?.toFixed(1) ?? 'N/A'}%
                            </td>
                            <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                              {ranking.mape?.toFixed(2) ?? 'N/A'}%
                            </td>
                            <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                              {ranking.sample_size ?? 'N/A'}
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span
                                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                  ranking.reliability === 'excellent'
                                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                                    : ranking.reliability === 'good'
                                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                                    : ranking.reliability === 'fair'
                                    ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                                }`}
                              >
                                {ranking.reliability === 'excellent'
                                  ? '優秀'
                                  : ranking.reliability === 'good'
                                  ? '良好'
                                  : ranking.reliability === 'fair'
                                  ? '普通'
                                  : '改善必要'}
                              </span>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {rankings.length === 0 && (
                <p className="text-center text-gray-600 dark:text-gray-400 py-8">
                  データがありません
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
