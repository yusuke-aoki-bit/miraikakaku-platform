import useSWR from 'swr';
import { apiClient } from '@/lib/api';

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

interface UseRankingsReturn {
  gainers: RankingItem[];
  losers: RankingItem[];
  volumeLeaders: RankingItem[];
  topPredictions: RankingItem[];
  marketStats: MarketStats | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
}

/**
 * SWRを使用したランキングデータ取得カスタムフック
 *
 * キャッシング戦略:
 * - refreshInterval: 60秒 (1分間キャッシュ)
 * - revalidateOnFocus: false (フォーカス時の再検証無効)
 * - dedupingInterval: 10秒 (10秒間の重複リクエスト防止)
 */
export function useRankings(): UseRankingsReturn {
  const { data: gainersData, error: gainersError } = useSWR(
    '/api/rankings/gainers',
    () => apiClient.getTopGainers(50),
    {
      refreshInterval: 60000, // 60秒ごとに自動更新
      revalidateOnFocus: false, // フォーカス時の再検証を無効化
      dedupingInterval: 10000, // 10秒間の重複リクエスト防止
    }
  );

  const { data: losersData, error: losersError } = useSWR(
    '/api/rankings/losers',
    () => apiClient.getTopLosers(50),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  const { data: volumeData, error: volumeError } = useSWR(
    '/api/rankings/volume',
    () => apiClient.getTopVolume(50),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  const { data: predictionsData, error: predictionsError } = useSWR(
    '/api/rankings/predictions',
    () => apiClient.getTopPredictions(50),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  const { data: statsData, error: statsError, mutate } = useSWR(
    '/api/stats/summary',
    () => apiClient.getMarketSummaryStats(),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  // ローディング状態を判定
  const isLoading = !gainersData && !losersData && !volumeData && !predictionsData && !statsData;

  // エラーを統合
  const error = gainersError || losersError || volumeError || predictionsError || statsError;

  return {
    gainers: gainersData?.gainers || [],
    losers: losersData?.losers || [],
    volumeLeaders: volumeData?.volume_leaders || [],
    topPredictions: predictionsData?.top_predictions || [],
    marketStats: statsData || null,
    isLoading,
    error,
    mutate,
  };
}

/**
 * 個別のランキングデータ取得フック
 */
export function useGainers(limit: number = 50) {
  return useSWR(
    `/api/rankings/gainers/${limit}`,
    () => apiClient.getTopGainers(limit),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );
}

export function useLosers(limit: number = 50) {
  return useSWR(
    `/api/rankings/losers/${limit}`,
    () => apiClient.getTopLosers(limit),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );
}

export function useVolumeLeaders(limit: number = 50) {
  return useSWR(
    `/api/rankings/volume/${limit}`,
    () => apiClient.getTopVolume(limit),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );
}

export function usePredictions(limit: number = 50) {
  return useSWR(
    `/api/rankings/predictions/${limit}`,
    () => apiClient.getTopPredictions(limit),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );
}

export function useMarketStats() {
  return useSWR(
    '/api/stats/summary',
    () => apiClient.getMarketSummaryStats(),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );
}
