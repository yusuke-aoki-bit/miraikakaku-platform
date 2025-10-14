import { useEffect, useState } from 'react';

interface StockDetails {
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  latest_price?: number;
  price_change_1d?: number;
  price_change_percent_1d?: number;
  volume?: number;
  market_cap?: number;
  predictions?: Array<{
    prediction_date: string;
    predicted_price: number;
    current_price?: number;
    prediction_days?: number;
    confidence_score: number;
  }>;
  accuracy_metrics?: {
    mae: number;
    mape: number;
    direction_accuracy: number;
    std_deviation: number;
    reliability: 'excellent' | 'good' | 'fair' | 'poor';
    reliability_score: number;
  };
  price_history?: Array<{
    date: string;
    open_price: number | null;
    high_price: number | null;
    low_price: number | null;
    close_price: number | null;
    volume: number | null;
  }>;
}

interface UseStockDetailsResult {
  data: StockDetails | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStockDetails(symbol: string | undefined): UseStockDetailsResult {
  const [data, setData] = useState<StockDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = async () => {
    if (!symbol) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // API呼び出し
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-465603676610.us-central1.run.app';
      const response = await fetch(`${API_BASE_URL}/api/stocks/${symbol}/details`);

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '銘柄詳細の取得に失敗しました';
      setError(errorMessage);
      console.error('Failed to fetch stock details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [symbol]);

  return {
    data,
    loading,
    error,
    refetch: fetchDetails
  };
}
