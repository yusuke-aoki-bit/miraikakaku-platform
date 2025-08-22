import { apiClient } from '../api-client';
import { API_CONFIG, PAGINATION, TIME_PERIODS } from '@/config/constants';

// グローバルfetchのモック
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('APIClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  describe('基本的なリクエスト機能', () => {
    it('成功レスポンスを正しく処理する', async () => {
      const mockResponse = { success: true, data: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response);

      const result = await apiClient.searchStocks('AAPL');

      expect(result.status).toBe('success');
      expect(result.data).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/search?query=AAPL&limit=${PAGINATION.DEFAULT_PAGE_SIZE}`,
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('HTTPエラーを正しく処理する', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      } as Response);

      const result = await apiClient.searchStocks('INVALID');

      expect(result.status).toBe('error');
      expect(result.error).toBe('HTTP 404: Not Found');
    });

    it('ネットワークエラーを正しく処理する', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiClient.searchStocks('AAPL');

      expect(result.status).toBe('error');
      expect(result.error).toBe('Network error');
    });
  });

  describe('株式検索機能', () => {
    it('基本的な株式検索が動作する', async () => {
      const mockData = [{ symbol: 'AAPL', name: 'Apple Inc.' }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
      } as Response);

      const result = await apiClient.searchStocks('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/search?query=AAPL&limit=${PAGINATION.DEFAULT_PAGE_SIZE}`,
        expect.any(Object)
      );
      expect(result.status).toBe('success');
      expect(result.data).toEqual(mockData);
    });

    it('通貨フィルターが正しく適用される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

      await apiClient.searchStocks('AAPL', 10, 'USD');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/search?query=AAPL&limit=10&currency=USD`,
        expect.any(Object)
      );
    });

    it('カスタムリミットが適用される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

      await apiClient.searchStocks('AAPL', 5);

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/search?query=AAPL&limit=5`,
        expect.any(Object)
      );
    });
  });

  describe('株価データ取得機能', () => {
    it('株価履歴を正しく取得する', async () => {
      const mockPriceData = [
        { date: '2024-01-01', close_price: 150.0, volume: 1000000 }
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPriceData),
      } as Response);

      const result = await apiClient.getStockPrice('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/AAPL/price?days=${TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS}`,
        expect.any(Object)
      );
      expect(result.status).toBe('success');
      expect(result.data).toEqual(mockPriceData);
    });

    it('カスタム日数で株価を取得する', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

      await apiClient.getStockPrice('AAPL', 7);

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/AAPL/price?days=7`,
        expect.any(Object)
      );
    });
  });

  describe('予測データ取得機能', () => {
    it('株価予測を正しく取得する', async () => {
      const mockPredictionData = [
        { predicted_price: 160.0, confidence_score: 0.85 }
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPredictionData),
      } as Response);

      const result = await apiClient.getStockPredictions('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/AAPL/predictions?days=${TIME_PERIODS.DEFAULT_PREDICTION_DAYS}`,
        expect.any(Object)
      );
      expect(result.status).toBe('success');
      expect(result.data).toEqual(mockPredictionData);
    });

    it('モデルタイプフィルターが適用される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

      await apiClient.getStockPredictions('AAPL', 'LSTM', 14);

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/AAPL/predictions?days=14&model_type=LSTM`,
        expect.any(Object)
      );
    });
  });

  describe('ランキング機能', () => {
    beforeEach(() => {
      // ランキング機能で使用される価格・予測APIのモック
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ close_price: 100.0, volume: 1000000 }]),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ predicted_price: 110.0, confidence_score: 0.8 }]),
        } as Response);
    });

    it('成長ポテンシャルランキングを動的生成する', async () => {
      const result = await apiClient.getGrowthPotentialRankings(1);

      expect(result.status).toBe('success');
      expect(result.data).toHaveLength(1);
      
      const stock = result.data[0];
      expect(stock).toHaveProperty('symbol');
      expect(stock).toHaveProperty('current_price');
      expect(stock).toHaveProperty('predicted_price');
      expect(stock).toHaveProperty('growth_potential');
      expect(stock).toHaveProperty('confidence');

      // 成長ポテンシャルの計算確認: (110-100)/100*100 = 10%
      expect(stock.growth_potential).toBe(10);
    });

    it('値上がりランキングが正の成長ポテンシャルのみ返す', async () => {
      // 複数のモックレスポンスを設定
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ close_price: 100.0, volume: 1000000 }]),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ predicted_price: 110.0, confidence_score: 0.8 }]),
        } as Response);

      const result = await apiClient.getGainersRankings(1);

      expect(result.status).toBe('success');
      if (result.data.length > 0) {
        result.data.forEach(stock => {
          expect(stock.growth_potential).toBeGreaterThan(0);
        });
      }
    });

    it('値下がりランキングが負の成長ポテンシャルのみ返す', async () => {
      // 負の成長のモック
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ close_price: 100.0, volume: 1000000 }]),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ predicted_price: 90.0, confidence_score: 0.8 }]),
        } as Response);

      const result = await apiClient.getLosersRankings(1);

      expect(result.status).toBe('success');
      if (result.data.length > 0) {
        result.data.forEach(stock => {
          expect(stock.growth_potential).toBeLessThan(0);
        });
      }
    });
  });

  describe('予測生成機能', () => {
    it('予測生成リクエストが正しく送信される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      } as Response);

      const result = await apiClient.createPrediction('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/api/finance/stocks/AAPL/predict`,
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(result.status).toBe('success');
    });
  });

  describe('ヘルスチェック機能', () => {
    it('ヘルスチェックが正常に動作する', async () => {
      const mockHealthData = { status: 'healthy' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHealthData),
      } as Response);

      const result = await apiClient.healthCheck();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_CONFIG.DEFAULT_BASE_URL}/health`,
        expect.any(Object)
      );
      expect(result.status).toBe('success');
      expect(result.data).toEqual(mockHealthData);
    });
  });

  describe('設定値テスト', () => {
    it('正しいベースURLが使用される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      } as Response);

      await apiClient.searchStocks('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(API_CONFIG.DEFAULT_BASE_URL),
        expect.any(Object)
      );
    });

    it('デフォルトのページネーション設定が適用される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

      await apiClient.searchStocks('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`limit=${PAGINATION.DEFAULT_PAGE_SIZE}`),
        expect.any(Object)
      );
    });

    it('正しいContent-Typeヘッダーが設定される', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      } as Response);

      await apiClient.searchStocks('AAPL');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });
});