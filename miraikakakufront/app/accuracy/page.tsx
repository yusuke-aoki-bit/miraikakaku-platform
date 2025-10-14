'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

interface ModelSummary {
  evaluated_symbols: number;
  total_predictions: number;
  overall_mae: number;
  overall_mape: number;
  overall_direction_accuracy: number;
  evaluation_period: string;
}

interface AccuracyRanking {
  symbol: string;
  company_name: string;
  sample_size: number;
  mae: number;
  mape: number;
  direction_accuracy: number;
  reliability: string;
  reliability_score: number;
}

export default function AccuracyDashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<ModelSummary | null>(null);
  const [topAccuracy, setTopAccuracy] = useState<AccuracyRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError('');

    try {
      const [summaryData, rankingsData] = await Promise.all([
        apiClient.getModelAccuracySummary(),
        apiClient.getAccuracyRankings(10),
      ]);

      setSummary(summaryData);
      setTopAccuracy(rankingsData.rankings);
    } catch (err) {
      setError('予測精度データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const retryFetch = () => {
    setError('');
    fetchData();
  };

  const getReliabilityColor = (reliability: string) => {
    switch (reliability) {
      case 'excellent':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-700';
      case 'good':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border border-blue-200 dark:border-blue-700';
      case 'fair':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 border border-yellow-200 dark:border-yellow-700';
      default:
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-700';
    }
  };

  const getReliabilityText = (reliability: string) => {
    switch (reliability) {
      case 'excellent':
        return '優秀';
      case 'good':
        return '良好';
      case 'fair':
        return '普通';
      default:
        return '改善必要';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-xl text-gray-700 dark:text-gray-300">予測精度データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="max-w-md w-full">
          <ErrorMessage message={error} onRetry={retryFetch} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="animate-fadeIn">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline mb-4 transition-colors"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            ホームに戻る
          </button>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            AI予測精度ダッシュボード
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
            LSTMモデルの予測性能と信頼性の分析
          </p>
        </div>

        {/* Overall Summary */}
        {summary && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 animate-slideUp">
            <h2 className="text-xl sm:text-2xl font-semibold mb-6 text-gray-800 dark:text-white flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              全体サマリー
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
              <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg hover:shadow-md transition-shadow border border-blue-200 dark:border-blue-800">
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">評価銘柄数</p>
                <p className="text-2xl sm:text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {summary.evaluated_symbols.toLocaleString()}
                </p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg hover:shadow-md transition-shadow border border-green-200 dark:border-green-800">
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">総予測数</p>
                <p className="text-2xl sm:text-3xl font-bold text-green-600 dark:text-green-400">
                  {summary.total_predictions?.toLocaleString() ?? 'N/A'}
                </p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg hover:shadow-md transition-shadow border border-purple-200 dark:border-purple-800">
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">平均誤差率</p>
                <p className="text-2xl sm:text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {summary.overall_mape?.toFixed(2) ?? 'N/A'}%
                </p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg hover:shadow-md transition-shadow border border-orange-200 dark:border-orange-800">
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">方向精度</p>
                <p className="text-2xl sm:text-3xl font-bold text-orange-600 dark:text-orange-400">
                  {summary.overall_direction_accuracy?.toFixed(1) ?? 'N/A'}%
                </p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/20 dark:to-pink-800/20 rounded-lg hover:shadow-md transition-shadow border border-pink-200 dark:border-pink-800">
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">平均絶対誤差</p>
                <p className="text-2xl sm:text-3xl font-bold text-pink-600 dark:text-pink-400">
                  {summary.overall_mae?.toFixed(2) ?? 'N/A'}
                </p>
              </div>
            </div>
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong className="text-gray-800 dark:text-gray-200">評価期間:</strong> {summary.evaluation_period}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                ※ MAPEは平均絶対パーセンテージ誤差、MAEは平均絶対誤差を示します。数値が低いほど予測精度が高いことを示します。
              </p>
            </div>
          </div>
        )}

        {/* Accuracy Metrics Explanation */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 animate-slideUp" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-xl sm:text-2xl font-semibold mb-6 text-gray-800 dark:text-white flex items-center">
            <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            評価指標について
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-all hover:border-purple-300 dark:hover:border-purple-600">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-base sm:text-lg">MAPE (平均誤差率)</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                予測値と実際の価格との誤差をパーセンテージで表します。値が小さいほど精度が高いです。
              </p>
              <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <div><strong className="text-green-600 dark:text-green-400">良好:</strong> &lt;5%</div>
                <div><strong className="text-yellow-600 dark:text-yellow-400">普通:</strong> 5-10%</div>
                <div><strong className="text-red-600 dark:text-red-400">改善必要:</strong> &gt;10%</div>
              </div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-all hover:border-orange-300 dark:hover:border-orange-600">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-base sm:text-lg">方向精度</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                価格の上昇・下降の方向を正しく予測できた割合。トレードの意思決定に重要な指標です。
              </p>
              <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <div><strong className="text-green-600 dark:text-green-400">優秀:</strong> &gt;70%</div>
                <div><strong className="text-blue-600 dark:text-blue-400">良好:</strong> 60-70%</div>
                <div><strong className="text-yellow-600 dark:text-yellow-400">普通:</strong> 50-60%</div>
              </div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-all hover:border-blue-300 dark:hover:border-blue-600">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3 text-base sm:text-lg">信頼性スコア</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                複数の指標を総合的に評価したスコア。予測の全体的な信頼度を表します。
              </p>
              <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <div><strong className="text-green-600 dark:text-green-400">優秀:</strong> &gt;80</div>
                <div><strong className="text-blue-600 dark:text-blue-400">良好:</strong> 60-80</div>
                <div><strong className="text-yellow-600 dark:text-yellow-400">普通:</strong> 40-60</div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Accuracy Rankings */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 sm:p-6 animate-slideUp" style={{ animationDelay: '0.2s' }}>
          <h2 className="text-xl sm:text-2xl font-semibold mb-6 text-gray-800 dark:text-white flex items-center">
            <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            <span className="whitespace-nowrap">予測精度TOP10</span>
          </h2>
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <div className="inline-block min-w-full align-middle">
              <div className="overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700/50">
                    <tr>
                      <th scope="col" className="px-3 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">順位</th>
                      <th scope="col" className="px-3 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">銘柄</th>
                      <th scope="col" className="hidden sm:table-cell px-3 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">会社名</th>
                      <th scope="col" className="px-3 sm:px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">方向精度</th>
                      <th scope="col" className="hidden md:table-cell px-3 sm:px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">誤差率</th>
                      <th scope="col" className="hidden lg:table-cell px-3 sm:px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">評価数</th>
                      <th scope="col" className="px-3 sm:px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">信頼性</th>
                      <th scope="col" className="hidden xl:table-cell px-3 sm:px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">スコア</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {topAccuracy.map((ranking, idx) => (
                      <tr
                        key={ranking.symbol}
                        onClick={() => router.push(`/stock/${ranking.symbol}`)}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                      >
                        <td className="px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">
                          {idx + 1}
                        </td>
                        <td className="px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap font-mono text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium">
                          {ranking.symbol}
                        </td>
                        <td className="hidden sm:table-cell px-3 sm:px-4 py-3 sm:py-4 text-sm text-gray-900 dark:text-white max-w-[200px] truncate" title={ranking.company_name}>
                          {ranking.company_name}
                        </td>
                        <td className="px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-right text-sm font-semibold text-green-600 dark:text-green-400">
                          {ranking.direction_accuracy?.toFixed(1) ?? 'N/A'}%
                        </td>
                        <td className="hidden md:table-cell px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                          {ranking.mape?.toFixed(2) ?? 'N/A'}%
                        </td>
                        <td className="hidden lg:table-cell px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-right text-sm text-gray-600 dark:text-gray-400">
                          {ranking.sample_size}
                        </td>
                        <td className="px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-center">
                          <span className={`inline-flex px-2 sm:px-3 py-1 rounded-full text-xs font-semibold ${getReliabilityColor(ranking.reliability)}`}>
                            {getReliabilityText(ranking.reliability)}
                          </span>
                        </td>
                        <td className="hidden xl:table-cell px-3 sm:px-4 py-3 sm:py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-900 dark:text-white">
                          {ranking.reliability_score?.toFixed(1) ?? 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/rankings')}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              すべてのランキングを見る
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
