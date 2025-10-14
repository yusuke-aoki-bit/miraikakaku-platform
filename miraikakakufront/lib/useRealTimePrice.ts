import { useState, useEffect, useRef } from 'react';
import { apiClient } from './api';

interface RealtimePriceData {
  symbol: string;
  current_price: number;
  change_percent: number;
  volume: number;
  last_update: string;
}

/**
 * リアルタイム価格更新フック
 * 定期的に価格データを更新する
 */
export function useRealtimePrice(
  symbol: string,
  intervalMs: number = 60000 // デフォルト1分
) {
  const [priceData, setPriceData] = useState<RealtimePriceData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchPrice = async () => {
    try {
      const data = await apiClient.getStockInfo(symbol);

      if (data.price_history && data.price_history.length > 0) {
        const latest = data.price_history[data.price_history.length - 1];
        const previous = data.price_history[data.price_history.length - 2];

        const current_price = latest.close_price || 0;
        const previous_price = previous?.close_price || current_price;
        const change_percent = previous_price > 0
          ? ((current_price - previous_price) / previous_price) * 100
          : 0;

        setPriceData({
          symbol: data.symbol,
          current_price,
          change_percent,
          volume: latest.volume || 0,
          last_update: latest.date,
        });
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch price');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!symbol) return;

    // 初回取得
    fetchPrice();

    // 定期更新
    intervalRef.current = setInterval(fetchPrice, intervalMs);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, intervalMs]);

  const refresh = () => {
    setIsLoading(true);
    fetchPrice();
  };

  return {
    priceData,
    isLoading,
    error,
    refresh,
  };
}

/**
 * 複数銘柄のリアルタイム価格更新フック
 */
export function useRealtimePrices(
  symbols: string[],
  intervalMs: number = 60000
) {
  const [pricesData, setPricesData] = useState<Map<string, RealtimePriceData>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchPrices = async () => {
    try {
      const results = await Promise.allSettled(
        symbols.map(symbol => apiClient.getStockInfo(symbol))
      );

      const newPrices = new Map<string, RealtimePriceData>();

      results.forEach((result) => {
        if (result.status === 'fulfilled') {
          const data = result.value;
          if (data.price_history && data.price_history.length > 0) {
            const latest = data.price_history[data.price_history.length - 1];
            const previous = data.price_history[data.price_history.length - 2];

            const current_price = latest.close_price || 0;
            const previous_price = previous?.close_price || current_price;
            const change_percent = previous_price > 0
              ? ((current_price - previous_price) / previous_price) * 100
              : 0;

            newPrices.set(data.symbol, {
              symbol: data.symbol,
              current_price,
              change_percent,
              volume: latest.volume || 0,
              last_update: latest.date,
            });
          }
        }
      });

      setPricesData(newPrices);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prices');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (symbols.length === 0) return;

    // 初回取得
    fetchPrices();

    // 定期更新
    intervalRef.current = setInterval(fetchPrices, intervalMs);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbols.length, intervalMs]);

  const refresh = () => {
    setIsLoading(true);
    fetchPrices();
  };

  return {
    pricesData,
    isLoading,
    error,
    refresh,
  };
}
