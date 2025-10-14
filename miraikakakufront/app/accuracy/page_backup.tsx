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
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'good':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'fair':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      default:
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
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
            AI予測精度ダッシュボード
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            LSTMモデルの予測性能と信頼性の分析
          </p>
        </div>

        {/* Overall Summary */}
        {summary && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              全体サマリー
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">評価銘柄数</p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {summary.evaluated_symbols}
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">総予測数</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {summary.total_predictions?.toLocaleString() ?? 'N/A'}
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均誤差率</p>
                <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {summary.overall_mape?.toFixed(2) ?? 'N/A'}%
                </p>
              </div>
              <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">方向精度</p>
                <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                  {summary.overall_direction_accuracy?.toFixed(1) ?? 'N/A'}%
                </p>
              </div>
              <div className="text-center p-4 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均絶対誤差</p>
                <p className="text-3xl font-bold text-pink-600 dark:text-pink-400">
                  {summary.overall_mae?.toFixed(2) ?? 'N/A'}
                </p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>評価期間:</strong> {summary.evaluation_period}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                ※ MAPEは平均絶対パーセンテージ誤差、MAEは平均絶対誤差を示します。数値が低いほど予測精度が高いことを示します。
              </p>
            </div>
          </div>
        )}

        {/* Accuracy Metrics Explanation */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
            評価指標について
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">MAPE (平均誤差率)</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                予測値と実際の価格との誤差をパーセンテージで表します。値が小さいほど精度が高いです。
              </p>
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                <strong>良好:</strong> &lt;5% | <strong>普通:</strong> 5-10% | <strong>改善必要:</strong> &gt;10%
              </div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">方向精度</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                価格の上昇・下降の方向を正しく予測できた割合。トレードの意思決定に重要な指標です。
              </p>
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                <strong>優秀:</strong> &gt;70% | <strong>良好:</strong> 60-70% | <strong>普通:</strong> 50-60%
              </div>
            </div>
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">信頼性スコア</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                複数の指標を総合的に評価したスコア。予測の全体的な信頼度を表します。
              </p>
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                <strong>優秀:</strong> &gt;80 | <strong>良好:</strong> 60-80 | <strong>普通:</strong> 40-60
              </div>
            </div>
          </div>
        </div>

        {/* Top Accuracy Rankings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
            予測精度 TOP 10
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">順位</th>
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">銘柄</th>
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">会社名</th>
                  <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">方向精度</th>
                  <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">誤差率</th>
                  <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">評価数</th>
                  <th className="text-center py-3 px-4 text-gray-600 dark:text-gray-400">信頼性</th>
                  <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">スコア</th>
                </tr>
              </thead>
              <tbody>
                {topAccuracy.map((ranking, idx) => (
                  <tr
                    key={ranking.symbol}
                    onClick={() => router.push(`/stock/${ranking.symbol}`)}
                    className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  >
                    <td className="py-3 px-4 text-gray-900 dark:text-white font-semibold">
                      {idx + 1}
                    </td>
                    <td className="py-3 px-4 font-mono text-blue-600 dark:text-blue-400 hover:underline">
                      {ranking.symbol}
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {ranking.company_name}
                    </td>
                    <td className="py-3 px-4 text-right text-green-600 dark:text-green-400 font-semibold">
                      {ranking.direction_accuracy?.toFixed(1) ?? 'N/A'}%
                    </td>
                    <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                      {ranking.mape?.toFixed(2) ?? 'N/A'}%
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                      {ranking.sample_size}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getReliabilityColor(ranking.reliability)}`}>
                        {getReliabilityText(ranking.reliability)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-gray-900 dark:text-white font-semibold">
                      {ranking.reliability_score?.toFixed(1) ?? 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-center">
            <button
              onClick={() => router.push('/rankings')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              すべてのランキングを見る
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
