'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { apiClient, StockPrice, StockPrediction } from '@/lib/api';
import PriceChart from '@/components/PriceChart';
import StockPredictionChart from '@/components/StockPredictionChart';
import { useToast } from '@/components/Toast';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import { useStockDetails } from '@/hooks/useStockDetails';
import { SectorBadge } from '@/components/SectorBadge';

interface StockDetail {
  symbol: string;
  company_name: string;
  exchange: string;
  price_history: StockPrice[];
}

interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

interface AccuracyMetrics {
  mae: number;
  mape: number;
  direction_accuracy: number;
  std_deviation: number;
  reliability: 'excellent' | 'good' | 'fair' | 'poor';
  reliability_score: number;
}

interface AccuracyData {
  symbol: string;
  evaluation_available: boolean;
  sample_size?: number;
  evaluation_period_days?: number;
  metrics?: AccuracyMetrics;
  message?: string;
}

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { data: session, status } = useSession();
  const { showToast } = useToast();
  const symbol = params.symbol as string;

  // Phase 4-1: セクター情報取得用フック
  const { data: stockDetailsData } = useStockDetails(symbol);

  const [stockInfo, setStockInfo] = useState<StockDetail | null>(null);
  const [predictions, setPredictions] = useState<StockPrediction[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accuracyData, setAccuracyData] = useState<AccuracyData | null>(null);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [watchlistLoading, setWatchlistLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [infoData, priceData, predData, accuracy] = await Promise.all([
          apiClient.getStockInfo(symbol),
          apiClient.getPriceHistory(symbol, 365),
          apiClient.getPredictions(symbol, 365, currentPage, 1000, undefined, 'date_asc'),
          apiClient.getPredictionAccuracy(symbol, 90).catch(() => null),
        ]);
        setStockInfo({...infoData, price_history: priceData});
        setPredictions(predData.predictions);
        setPagination(predData.pagination);
        setAccuracyData(accuracy);
      } catch (err) {
        setError(err instanceof Error ? err.message : '銘柄情報の取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };
    if (symbol) {
      fetchData();
    }
  }, [symbol, currentPage]);

  useEffect(() => {
    const checkWatchlist = async () => {
      if (status === 'authenticated' && session && symbol) {
        try {
          const token = (session as any)?.accessToken;
          if (token) {
            const result = await apiClient.checkInWatchlist(token, symbol);
            setInWatchlist(result.in_watchlist);
          }
        } catch (err) {
          console.error('Failed to check watchlist:', err);
        }
      }
    };
    checkWatchlist();
  }, [status, session, symbol]);

  const handleToggleWatchlist = async () => {
    if (status !== 'authenticated' || !session) {
      router.push('/login');
      return;
    }

    setWatchlistLoading(true);
    try {
      const token = (session as any)?.accessToken;
      if (!token) return;

      if (inWatchlist) {
        await apiClient.removeFromWatchlist(token, symbol);
        setInWatchlist(false);
        showToast('ウォッチリストから削除しました', 'success');
      } else {
        await apiClient.addToWatchlist(token, symbol);
        setInWatchlist(true);
        showToast('ウォッチリストに追加しました', 'success');
      }
    } catch (err) {
      console.error('Failed to toggle watchlist:', err);
      showToast('ウォッチリストの更新に失敗しました', 'error');
    } finally {
      setWatchlistLoading(false);
    }
  };

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
          <p className="text-xl text-gray-700 dark:text-gray-300">銘柄データを読み込み中...</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">{symbol}</p>
        </div>
      </div>
    );
  }

  if (error || !stockInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="max-w-md w-full">
          <ErrorMessage
            title="銘柄情報の取得エラー"
            message={error || '銘柄が見つかりません'}
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

  const latestPrice = stockInfo.price_history[0];
  const oldestPrice = stockInfo.price_history[stockInfo.price_history.length - 1];
  const priceChange = latestPrice && oldestPrice ? ((latestPrice.close_price! - oldestPrice.close_price!) / oldestPrice.close_price!) * 100 : 0;
  const handlePageChange = (newPage: number) => { setCurrentPage(newPage); setLoading(true); };

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button onClick={() => router.push('/')} className="text-blue-600 dark:text-blue-400 hover:underline mb-4">← ホームに戻る</button>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">{stockInfo.company_name}</h1>
              <div className="flex items-center gap-4 flex-wrap">
                <span className="text-2xl font-mono text-blue-600 dark:text-blue-400">{stockInfo.symbol}</span>
                <span className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm">{stockInfo.exchange}</span>
                {/* Phase 4-1: セクターバッジ */}
                {stockDetailsData?.sector && (
                  <SectorBadge sector={stockDetailsData.sector} size="md" />
                )}
                {/* Phase 4-1: 業種表示 */}
                {stockDetailsData?.industry && (
                  <span className="px-3 py-1 bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-sm">
                    {stockDetailsData.industry}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={handleToggleWatchlist}
              disabled={watchlistLoading}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                inWatchlist
                  ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <svg className="w-5 h-5" fill={inWatchlist ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
              <span>{watchlistLoading ? '処理中...' : inWatchlist ? 'ウォッチリスト登録済み' : 'ウォッチリストに追加'}</span>
            </button>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">価格情報</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div><p className="text-sm text-gray-600 dark:text-gray-400">最新価格</p><p className="text-2xl font-bold text-gray-900 dark:text-white">{latestPrice?.close_price?.toFixed(2) || 'N/A'}</p></div>
            <div><p className="text-sm text-gray-600 dark:text-gray-400">変動率</p><p className={`text-2xl font-bold ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>{priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%</p></div>
            <div><p className="text-sm text-gray-600 dark:text-gray-400">出来高</p><p className="text-2xl font-bold text-gray-900 dark:text-white">{latestPrice?.volume?.toLocaleString() || 'N/A'}</p></div>
            <div><p className="text-sm text-gray-600 dark:text-gray-400">データ件数</p><p className="text-2xl font-bold text-gray-900 dark:text-white">{stockInfo.price_history.length}日</p></div>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <StockPredictionChart
              priceHistory={stockInfo.price_history}
              predictions={predictions}
              symbol={stockInfo.symbol}
            />
          </div>
        </div>
        {accuracyData && accuracyData.evaluation_available && accuracyData.metrics && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">予測精度評価</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">信頼性</p>
                <div className={`inline-block px-4 py-2 rounded-full text-lg font-bold ${
                  accuracyData.metrics.reliability === 'excellent' ? 'bg-green-100 text-green-800' :
                  accuracyData.metrics.reliability === 'good' ? 'bg-blue-100 text-blue-800' :
                  accuracyData.metrics.reliability === 'fair' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {accuracyData.metrics.reliability === 'excellent' ? '優秀' :
                   accuracyData.metrics.reliability === 'good' ? '良好' :
                   accuracyData.metrics.reliability === 'fair' ? '普通' : '改善必要'}
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">平均誤差率 (MAPE)</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{accuracyData.metrics.mape.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">方向精度</p>
                <p className="text-2xl font-bold text-green-600">{accuracyData.metrics.direction_accuracy.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">標準偏差</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{accuracyData.metrics.std_deviation.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">評価サンプル</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{accuracyData.sample_size}件</p>
              </div>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              過去{accuracyData.evaluation_period_days}日間の予測と実際の価格を比較した精度評価です。
              MAPEが低いほど、方向精度が高いほど、予測の信頼性が高くなります。
            </div>
          </div>
        )}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">LSTM AI予測 ({pagination?.total || 0}件)</h2>
            {pagination && <div className="text-sm text-gray-600 dark:text-gray-400">ページ {pagination.page} / {pagination.total_pages}</div>}
          </div>
          {predictions.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400">予測日</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">予測価格</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">予測時点価格</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">実際の価格</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">変動予測</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">精度</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">予測期間</th>
                      <th className="text-right py-3 px-4 text-gray-600 dark:text-gray-400">信頼度</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictions.map((pred, idx) => {
                      const predictedChange = pred.current_price ? ((pred.predicted_price - pred.current_price) / pred.current_price) * 100 : 0;
                      const accuracy = pred.actual_price ? ((1 - Math.abs(pred.predicted_price - pred.actual_price) / pred.actual_price) * 100) : null;
                      const accuracyColor = accuracy !== null ? (
                        accuracy >= 95 ? 'text-green-600' :
                        accuracy >= 90 ? 'text-blue-600' :
                        accuracy >= 85 ? 'text-yellow-600' : 'text-red-600'
                      ) : '';

                      return (
                        <tr key={idx} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{new Date(pred.prediction_date).toLocaleDateString('ja-JP')}</td>
                          <td className="py-3 px-4 text-right font-semibold text-blue-600 dark:text-blue-400">{pred.predicted_price.toFixed(2)}</td>
                          <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">{pred.current_price?.toFixed(2) || 'N/A'}</td>
                          <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                            {pred.actual_price ? pred.actual_price.toFixed(2) : '-'}
                          </td>
                          <td className={`py-3 px-4 text-right font-semibold ${predictedChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {predictedChange >= 0 ? '+' : ''}{predictedChange.toFixed(2)}%
                          </td>
                          <td className={`py-3 px-4 text-right font-semibold ${accuracyColor}`}>
                            {accuracy !== null ? `${accuracy.toFixed(1)}%` : '-'}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-900 dark:text-white">{pred.prediction_days || 'N/A'}日</td>
                          <td className="py-3 px-4 text-right text-gray-900 dark:text-white">{(pred.confidence_score * 100).toFixed(1)}%</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {pagination && pagination.total_pages > 1 && (
                <div className="flex justify-center items-center gap-2 mt-6">
                  <button onClick={() => handlePageChange(1)} disabled={currentPage === 1} className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700">{'<<'}</button>
                  <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1} className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700">{'<'}</button>
                  {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                    let pageNum;
                    if (pagination.total_pages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= pagination.total_pages - 2) {
                      pageNum = pagination.total_pages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    return <button key={pageNum} onClick={() => handlePageChange(pageNum)} className={`px-3 py-1 border rounded ${currentPage === pageNum ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>{pageNum}</button>;
                  })}
                  <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === pagination.total_pages} className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700">{'>'}</button>
                  <button onClick={() => handlePageChange(pagination.total_pages)} disabled={currentPage === pagination.total_pages} className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700">{'>>'}</button>
                </div>
              )}
            </>
          ) : <p className="text-gray-600 dark:text-gray-400">予測データがありません</p>}
        </div>
      </div>
    </div>
  );
}
