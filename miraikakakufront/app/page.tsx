'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import SkeletonCard from '@/components/SkeletonCard';
import RankingCard from '@/components/RankingCard';

interface RankingItem {
  symbol: string;
  company_name: string;
  exchange: string;
  current_price: number;
  change_percent?: number;
  volume?: number;
  predicted_change?: number;
  confidence_score?: number;
}

interface MarketStats {
  total_symbols: number;
  symbols_with_prices: number;
  total_predictions: number;
  last_update: string | null;
  avg_confidence: number;
  coverage_percent: number;
  db_status?: string;
}

export default function Home() {
  const router = useRouter();
  const [gainers, setGainers] = useState<RankingItem[]>([]);
  const [losers, setLosers] = useState<RankingItem[]>([]);
  const [volumeLeaders, setVolumeLeaders] = useState<RankingItem[]>([]);
  const [topPredictions, setTopPredictions] = useState<RankingItem[]>([]);
  const [marketStats, setMarketStats] = useState<MarketStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExchange, setSelectedExchange] = useState<string>('ALL');

  const filterByExchange = (items: RankingItem[]) => {
    if (selectedExchange === 'ALL') return items;
    return items.filter(item => {
      const exchange = item.exchange?.toUpperCase() || '';
      const symbol = item.symbol || '';

      if (selectedExchange === 'US') {
        return ['NASDAQ', 'NYSE', 'AMEX'].includes(exchange);
      }
      if (selectedExchange === 'JP') {
        // 日本株は.Tで終わるか、取引所がTOKYO/TSE/JPX
        return symbol.endsWith('.T') || exchange.includes('TOKYO') || exchange.includes('TSE') || exchange.includes('JPX');
      }
      return exchange.includes(selectedExchange);
    });
  };

  const getExchangeLabel = (exchange: string) => {
    const labels: { [key: string]: string } = {
      'ALL': '全取引所',
      'US': '米国市場',
      'JP': '日本市場',
      'NASDAQ': 'NASDAQ',
      'NYSE': 'NYSE',
      'TSE': '東証',
    };
    return labels[exchange] || exchange;
  };

  const filteredGainers = filterByExchange(gainers).slice(0, 5);
  const filteredLosers = filterByExchange(losers).slice(0, 5);
  const filteredVolumeLeaders = filterByExchange(volumeLeaders).slice(0, 5);
  const filteredTopPredictions = filterByExchange(topPredictions).slice(0, 5);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [gainersData, losersData, volumeData, predictionsData, statsData] = await Promise.all([
          apiClient.getTopGainers(50),
          apiClient.getTopLosers(50),
          apiClient.getTopVolume(50),
          apiClient.getTopPredictions(50),
          apiClient.getMarketSummaryStats(),
        ]);

        setGainers(gainersData.gainers);
        setLosers(losersData.losers);
        setVolumeLeaders(volumeData.volume_leaders);
        setTopPredictions(predictionsData.top_predictions);
        setMarketStats(statsData);
        setError('');
      } catch (error) {
        console.error('データ取得エラー:', error);
        setError('データの取得に失敗しました。しばらくしてから再度お試しください。');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const retryFetch = () => {
    setLoading(true);
    setError('');
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <LoadingSpinner size="lg" className="mb-4" />
            <p className="text-xl text-gray-700 dark:text-gray-300">データを読み込み中...</p>
          </div>

          {/* Skeleton Ranking Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-40 mb-4"></div>
              <div className="space-y-2">
                {[...Array(5)].map((_, idx) => (
                  <SkeletonCard key={idx} />
                ))}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-40 mb-4"></div>
              <div className="space-y-2">
                {[...Array(5)].map((_, idx) => (
                  <SkeletonCard key={idx} />
                ))}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-40 mb-4"></div>
              <div className="space-y-2">
                {[...Array(5)].map((_, idx) => (
                  <SkeletonCard key={idx} />
                ))}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-40 mb-4"></div>
              <div className="space-y-2">
                {[...Array(5)].map((_, idx) => (
                  <SkeletonCard key={idx} />
                ))}
              </div>
            </div>
          </div>
        </main>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="px-4 py-12 md:py-20 mb-8">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-6">
              <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">AI駆動の株価予測</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-gray-900 dark:text-white">
              未来の株価を
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> AI </span>
              で予測
            </h1>

            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              AIを活用した株価予測プラットフォーム
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <button
                onClick={() => router.push('/search')}
                className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg shadow-lg hover:shadow-xl"
              >
                銘柄を検索
              </button>
              <button
                onClick={() => router.push('/rankings')}
                className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-semibold text-lg shadow-lg"
              >
                ランキングを見る
              </button>
            </div>

            {/* Database Status Indicator */}
            {marketStats?.db_status && (
              <div className="mb-4 flex justify-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                  marketStats.db_status === 'postgres'
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                    : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${
                    marketStats.db_status === 'postgres' ? 'bg-green-500' : 'bg-yellow-500'
                  }`}></span>
                  {marketStats.db_status === 'postgres' ? 'PostgreSQL接続中' : 'SQLiteフォールバック'}
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-blue-600 dark:text-blue-400">
                  {marketStats?.total_symbols.toLocaleString() || '0'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">銘柄数</p>
              </div>
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-green-600 dark:text-green-400">
                  {marketStats?.coverage_percent.toFixed(0) || '0'}%
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">カバレッジ</p>
              </div>
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-purple-600 dark:text-purple-400">
                  {marketStats?.total_predictions.toLocaleString() || '0'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">予測データ</p>
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 pb-8">

        {/* 検索バー */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6 mb-6">
          <form onSubmit={handleSearch}>
            <div className="flex gap-2 md:gap-4">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="銘柄検索... (例: AAPL, 7203.T)"
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-4 md:px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
              >
                検索
              </button>
            </div>
          </form>
        </div>

        {/* 取引所フィルター */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">
            取引所で絞り込み
          </h2>
          <div className="flex flex-wrap gap-2">
            {['ALL', 'US', 'JP', 'NASDAQ', 'NYSE', 'TSE'].map((exchange) => (
              <button
                key={exchange}
                onClick={() => setSelectedExchange(exchange)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedExchange === exchange
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {getExchangeLabel(exchange)}
              </button>
            ))}
          </div>
          {selectedExchange !== 'ALL' && (
            <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
              現在のフィルター: <span className="font-semibold text-blue-600 dark:text-blue-400">{getExchangeLabel(selectedExchange)}</span>
            </div>
          )}
        </div>

        {/* 市場統計 */}
        {marketStats && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6 mb-6">
            <h2 className="text-xl md:text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              市場統計
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">総銘柄数</p>
                <p className="text-xl md:text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {marketStats.total_symbols.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">データあり</p>
                <p className="text-xl md:text-3xl font-bold text-green-600 dark:text-green-400">
                  {marketStats.symbols_with_prices.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">カバレッジ</p>
                <p className="text-xl md:text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {marketStats.coverage_percent.toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">最終更新</p>
                <p className="text-sm md:text-base font-medium text-gray-900 dark:text-white">
                  {formatDate(marketStats.last_update)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ランキンググリッド */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* 値上がり率ランキング */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
                値上がり率 TOP 5
              </h2>
              <button
                onClick={() => router.push('/rankings')}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                もっと見る
              </button>
            </div>
            <div className="space-y-2">
              {filteredGainers.map((item, idx) => (
                <RankingCard
                  key={item.symbol}
                  item={item}
                  index={idx}
                  onClick={() => router.push(`/stock/${item.symbol}`)}
                  type="gainer"
                />
              ))}
            </div>
          </div>

          {/* 値下がり率ランキング */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
                値下がり率 TOP 5
              </h2>
              <button
                onClick={() => router.push('/rankings')}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                もっと見る
              </button>
            </div>
            <div className="space-y-2">
              {filteredLosers.map((item, idx) => (
                <RankingCard
                  key={item.symbol}
                  item={item}
                  index={idx}
                  onClick={() => router.push(`/stock/${item.symbol}`)}
                  type="loser"
                />
              ))}
            </div>
          </div>

          {/* 出来高ランキング */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
                出来高 TOP 5
              </h2>
              <button
                onClick={() => router.push('/rankings')}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                もっと見る
              </button>
            </div>
            <div className="space-y-2">
              {filteredVolumeLeaders.map((item, idx) => (
                <RankingCard
                  key={item.symbol}
                  item={item}
                  index={idx}
                  onClick={() => router.push(`/stock/${item.symbol}`)}
                  type="volume"
                />
              ))}
            </div>
          </div>

          {/* 予測上昇率ランキング */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 md:p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
                AI予測上昇率 TOP 5
              </h2>
              <button
                onClick={() => router.push('/rankings')}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                もっと見る
              </button>
            </div>
            <div className="space-y-2">
              {filteredTopPredictions.map((item, idx) => (
                <RankingCard
                  key={item.symbol}
                  item={item}
                  index={idx}
                  onClick={() => router.push(`/stock/${item.symbol}`)}
                  type="prediction"
                />
              ))}
            </div>
          </div>
        </div>

        {/* クイックリンク */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => router.push('/rankings')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-lg transition-shadow"
          >
            <div className="text-center">
              <p className="font-semibold text-gray-900 dark:text-white">ランキング</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">詳細を見る</p>
            </div>
          </button>
          <button
            onClick={() => router.push('/search')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-lg transition-shadow"
          >
            <div className="text-center">
              <p className="font-semibold text-gray-900 dark:text-white">銘柄検索</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">銘柄を探す</p>
            </div>
          </button>
          <button
            onClick={() => router.push('/exchange/tse')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-lg transition-shadow"
          >
            <div className="text-center">
              <p className="font-semibold text-gray-900 dark:text-white">取引所</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">一覧を見る</p>
            </div>
          </button>
          <button
            onClick={() => router.push('/mypage')}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-lg transition-shadow"
          >
            <div className="text-center">
              <p className="font-semibold text-gray-900 dark:text-white">マイページ</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">お気に入り</p>
            </div>
          </button>
        </div>
        </div>
      </main>
    </div>
  );
}
