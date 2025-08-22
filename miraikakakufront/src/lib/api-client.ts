// 統一APIクライアント

import { API_CONFIG, PAGINATION, TIME_PERIODS } from '@/config/constants';

interface APIResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status: 'success' | 'error';
}

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || API_CONFIG.DEFAULT_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        return {
          status: 'error',
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return {
        status: 'success',
        data,
      };
    } catch (error) {
      return {
        status: 'error',
        error: error instanceof Error ? error.message : '不明なエラー',
      };
    }
  }

  // Enhanced stock search with currency filter
  async searchStocks(query: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE, currency?: string) {
    let url = `/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    if (currency) {
      url += `&currency=${currency}`;
    }
    return this.request(url);
  }

  // Get all available sectors
  async getSectors() {
    return this.request('/api/finance/stocks/sectors');
  }

  // Get stocks by sector
  async getStocksBySector(sectorId: string, limit: number = PAGINATION.SECTOR_STOCKS_LIMIT, currency: string = 'JPY') {
    return this.request(`/api/finance/stocks/sector/${encodeURIComponent(sectorId)}?limit=${limit}&currency=${currency}`);
  }

  // 株価履歴取得
  async getStockPrice(symbol: string, days: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/price?days=${days}`);
  }

  // 株価予測取得
  async getStockPredictions(symbol: string, modelType?: string, days: number = TIME_PERIODS.DEFAULT_PREDICTION_DAYS) {
    let url = `/api/finance/stocks/${symbol}/predictions?days=${days}`;
    if (modelType) {
      url += `&model_type=${encodeURIComponent(modelType)}`;
    }
    return this.request(url);
  }

  // 予測生成
  async createPrediction(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/predict`, {
      method: 'POST',
    });
  }

  // 成長ポテンシャルランキング（動的生成）
  async getGrowthPotentialRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    try {
      // まず人気銘柄のリストを取得
      const popularSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', '7203', '6758', '9984'];
      const stocks = [];
      
      for (const symbol of popularSymbols.slice(0, limit)) {
        try {
          const priceResponse = await this.getStockPrice(symbol, 1);
          const predictionResponse = await this.getStockPredictions(symbol, undefined, 1);
          
          if (priceResponse.status === 'success' && predictionResponse.status === 'success') {
            const priceData = (priceResponse as any).data?.[0];
            const predictionData = (predictionResponse as any).data?.[0];
            
            if (priceData && predictionData) {
              const currentPrice = priceData.close_price;
              const predictedPrice = predictionData.predicted_price;
              const growthPotential = ((predictedPrice - currentPrice) / currentPrice) * 100;
              
              stocks.push({
                symbol,
                company_name: priceData.symbol,
                current_price: currentPrice,
                predicted_price: predictedPrice,
                growth_potential: growthPotential,
                confidence: predictionData.confidence_score || 0.75,
                prediction_count: 1
              });
            }
          }
        } catch (error) {
          console.warn(`Failed to get data for ${symbol}:`, error);
        }
      }
      
      // 成長ポテンシャルでソート
      stocks.sort((a, b) => b.growth_potential - a.growth_potential);
      
      return {
        status: 'success' as const,
        data: stocks
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '成長ポテンシャル取得エラー'
      };
    }
  }

  // 総合ランキング（動的生成）
  async getCompositeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 精度ランキング（動的生成）
  async getAccuracyRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getGrowthPotentialRankings(limit);
  }

  // 過去予測データと実績の比較
  async getHistoricalPredictions(symbol: string, days: number = TIME_PERIODS.HISTORICAL_PREDICTIONS_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/historical-predictions?days=${days}`);
  }

  // マーケット概況（トレンド株）
  async getTrendingStocks(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit);
    if (response.status === 'success' && response.data) {
      // 上位成長ポテンシャル銘柄をトレンドとして表示
      const trending = response.data.slice(0, limit);
      return { ...response, data: trending };
    }
    return response;
  }

  // 値上がりランキング
  async getGainersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit * 2);
    if (response.status === 'success' && response.data) {
      // 成長ポテンシャルがプラスの銘柄を抽出
      const gainers = response.data
        .filter((stock: any) => stock.growth_potential > 0)
        .sort((a: any, b: any) => b.growth_potential - a.growth_potential)
        .slice(0, limit);
      return { ...response, data: gainers };
    }
    return response;
  }

  // 値下がりランキング  
  async getLosersRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    const response = await this.getGrowthPotentialRankings(limit * 2);
    if (response.status === 'success' && response.data) {
      // 成長ポテンシャルが負の銘柄を抽出
      const losers = response.data
        .filter((stock: any) => stock.growth_potential < 0)
        .sort((a: any, b: any) => a.growth_potential - b.growth_potential)
        .slice(0, limit);
      return { ...response, data: losers };
    }
    return response;
  }

  // 出来高ランキング（総合ランキングをベースに）
  async getVolumeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.getCompositeRankings(limit);
  }

  // 出来高データ取得
  async getVolumeData(symbol: string, days: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    try {
      // 実際のAPIが実装されるまでモックデータを生成
      const mockVolumeData = Array.from({ length: days }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (days - i - 1));
        
        const baseVolume = 10000000;
        const actualVolume = baseVolume * (1 + (Math.random() - 0.5) * 0.4);
        const predictedVolume = actualVolume * (1 + (Math.random() - 0.5) * 0.2);
        
        return {
          date: date.toISOString().split('T')[0],
          symbol,
          actual_volume: actualVolume,
          predicted_volume: i >= days * 0.7 ? predictedVolume : actualVolume,
          average_volume: baseVolume,
          volume_ratio: actualVolume / baseVolume
        };
      });

      return {
        status: 'success' as const,
        data: mockVolumeData
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '出来高データ取得エラー'
      };
    }
  }

  // 出来高予測
  async getVolumePredictions(symbol: string, days: number = 7) {
    try {
      const mockPredictions = Array.from({ length: days }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() + i + 1);
        
        const baseVolume = 10000000;
        const predictedVolume = baseVolume * (1 + (Math.random() - 0.5) * 0.3);
        
        return {
          date: date.toISOString().split('T')[0],
          symbol,
          predicted_volume: predictedVolume,
          confidence: 70 + Math.random() * 25,
          factors: ['market_sentiment', 'technical_indicators', 'news_impact']
        };
      });

      return {
        status: 'success' as const,
        data: mockPredictions
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '出来高予測エラー'
      };
    }
  }

  // 通貨ペアリスト取得
  async getCurrencyPairs() {
    try {
      const mockPairs = [
        { pair: 'USD/JPY', base: 'USD', quote: 'JPY', name: '米ドル/円' },
        { pair: 'EUR/USD', base: 'EUR', quote: 'USD', name: 'ユーロ/米ドル' },
        { pair: 'GBP/USD', base: 'GBP', quote: 'USD', name: '英ポンド/米ドル' },
        { pair: 'EUR/JPY', base: 'EUR', quote: 'JPY', name: 'ユーロ/円' },
        { pair: 'AUD/USD', base: 'AUD', quote: 'USD', name: '豪ドル/米ドル' },
        { pair: 'USD/CHF', base: 'USD', quote: 'CHF', name: '米ドル/スイスフラン' },
        { pair: 'USD/CAD', base: 'USD', quote: 'CAD', name: '米ドル/カナダドル' },
        { pair: 'NZD/USD', base: 'NZD', quote: 'USD', name: 'NZドル/米ドル' },
      ];

      return {
        status: 'success' as const,
        data: mockPairs
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '通貨ペア取得エラー'
      };
    }
  }

  // 通貨レート取得
  async getCurrencyRate(pair: string) {
    try {
      const baseRates = {
        'USD/JPY': 150.25,
        'EUR/USD': 1.0845,
        'GBP/USD': 1.2715,
        'EUR/JPY': 162.90,
        'AUD/USD': 0.6523,
        'USD/CHF': 0.8834,
        'USD/CAD': 1.3598,
        'NZD/USD': 0.6145
      };

      const baseRate = baseRates[pair as keyof typeof baseRates] || 1.0000;
      const rate = baseRate * (1 + (Math.random() - 0.5) * 0.01);
      const change = (Math.random() - 0.5) * 0.02;
      
      return {
        status: 'success' as const,
        data: {
          pair,
          rate,
          change,
          changePercent: (change / rate) * 100,
          timestamp: new Date().toISOString(),
          bid: rate - 0.0001,
          ask: rate + 0.0001,
          spread: 0.0002
        }
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '為替レート取得エラー'
      };
    }
  }

  // 通貨予測
  async getCurrencyPredictions(pair: string, timeframe: string = '1D') {
    try {
      const hours = timeframe === '1H' ? 1 : 
                   timeframe === '1D' ? 24 : 
                   timeframe === '1W' ? 168 : 720;

      const rateResponse = await this.getCurrencyRate(pair);
      if (rateResponse.status !== 'success') {
        throw new Error('Failed to get current rate');
      }

      const currentRate = (rateResponse as any).data.rate;
      const predictions = [];

      for (let i = 1; i <= Math.min(hours, 48); i++) {
        const time = new Date();
        time.setHours(time.getHours() + i);
        
        const trendFactor = (Math.random() - 0.5) * 0.002;
        const volatility = Math.random() * 0.001;
        const predictedRate = currentRate * (1 + trendFactor + (Math.random() - 0.5) * volatility);
        
        predictions.push({
          timestamp: time.toISOString(),
          predicted_rate: predictedRate,
          confidence: 70 + Math.random() * 25,
          upper_bound: predictedRate * 1.002,
          lower_bound: predictedRate * 0.998,
          factors: ['technical_analysis', 'market_sentiment', 'economic_indicators']
        });
      }

      return {
        status: 'success' as const,
        data: {
          pair,
          timeframe,
          current_rate: currentRate,
          predictions
        }
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '通貨予測エラー'
      };
    }
  }

  // 経済指標カレンダー
  async getEconomicCalendar(date?: string) {
    try {
      const targetDate = date ? new Date(date) : new Date();
      
      const mockEvents = [
        {
          time: '08:30',
          country: 'US',
          event: '米雇用統計',
          impact: 'high',
          actual: null,
          forecast: '+195K',
          previous: '+187K',
          currency: 'USD'
        },
        {
          time: '10:00',
          country: 'EU',
          event: 'ECB政策金利',
          impact: 'high',
          actual: null,
          forecast: '4.25%',
          previous: '4.25%',
          currency: 'EUR'
        },
        {
          time: '14:00',
          country: 'JP',
          event: '日銀短観',
          impact: 'medium',
          actual: null,
          forecast: '+12',
          previous: '+10',
          currency: 'JPY'
        }
      ];

      return {
        status: 'success' as const,
        data: {
          date: targetDate.toISOString().split('T')[0],
          events: mockEvents
        }
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '経済指標カレンダー取得エラー'
      };
    }
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiClient = new APIClient();
export default apiClient;