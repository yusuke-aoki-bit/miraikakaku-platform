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
  private cache: Map<string, { data: any; timestamp: number }>;
  private cacheTimeout: number = 60000; // 1分間のキャッシュ

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || API_CONFIG.DEFAULT_BASE_URL;
    this.cache = new Map();
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    useCache: boolean = true
  ): Promise<APIResponse<T>> {
    try {
      // GETリクエストの場合のみキャッシュを使用
      if (useCache && options.method === undefined) {
        const cacheKey = `${endpoint}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
          return {
            status: 'success',
            data: cached.data,
          };
        }
      }

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
      
      // 成功したGETリクエストをキャッシュに保存
      if (useCache && options.method === undefined) {
        const cacheKey = `${endpoint}`;
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now(),
        });
        
        // キャッシュサイズ制限（最大100エントリ）
        if (this.cache.size > 100) {
          const firstKey = this.cache.keys().next().value;
          if (firstKey) {
            this.cache.delete(firstKey);
          }
        }
      }
      
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

  // Enhanced stock search - align with production API
  async searchStocks(query: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
    const url = `/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    return this.request(url);
  }

  // 株価履歴取得 - production API uses 'limit' not 'days'
  async getStockPrice(symbol: string, limit: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/price?limit=${limit}`);
  }

  // 株価予測取得 - production API uses 'limit' and 'model_version' not 'model_type'
  async getStockPredictions(symbol: string, modelVersion?: string, limit: number = TIME_PERIODS.DEFAULT_PREDICTION_DAYS) {
    let url = `/api/finance/stocks/${symbol}/predictions?limit=${limit}`;
    if (modelVersion) {
      url += `&model_version=${encodeURIComponent(modelVersion)}`;
    }
    return this.request(url);
  }

  // 予測生成
  async createPrediction(symbol: string) {
    return this.request(`/api/finance/stocks/${symbol}/predict`, {
      method: 'POST',
    });
  }

  // AI決定要因取得 - production API endpoint
  async getAIFactors(limit: number = PAGINATION.DEFAULT_PAGE_SIZE, offset: number = 0) {
    return this.request(`/api/ai-factors/all?limit=${limit}&offset=${offset}`);
  }

  // テーマ洞察取得 - production API endpoint  
  async getThemeInsights() {
    return this.request('/api/insights/themes');
  }

  // 特定テーマの洞察取得 - production API endpoint
  async getThemeInsightByName(themeName: string, limit: number = PAGINATION.DEFAULT_PAGE_SIZE) {
    return this.request(`/api/insights/themes/${encodeURIComponent(themeName)}?limit=${limit}`);
  }

  // ユーザープロファイル取得（モック実装）- production API endpoint
  async getUserProfile(userId: string) {
    return this.request(`/api/users/${userId}/profile`);
  }

  // 成長ポテンシャルランキング（動的生成）- updated for production API
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
                company_name: priceData.symbol || symbol,
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

  // 株式詳細情報取得（株価と予測を組み合わせ）
  async getStockDetails(symbol: string) {
    try {
      const [priceResponse, predictionResponse] = await Promise.all([
        this.getStockPrice(symbol, 30),
        this.getStockPredictions(symbol, undefined, 10)
      ]);
      
      return {
        status: 'success' as const,
        data: {
          symbol,
          prices: priceResponse.status === 'success' ? priceResponse.data : [],
          predictions: predictionResponse.status === 'success' ? predictionResponse.data : []
        }
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : '株式詳細取得エラー'
      };
    }
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


  // 出来高データ取得 - 実装済みエンドポイント
  async getVolumeData(symbol: string, limit: number = TIME_PERIODS.DEFAULT_PRICE_HISTORY_DAYS) {
    return this.request(`/api/finance/stocks/${symbol}/volume?limit=${limit}`);
  }

  // 出来高予測 - 実装済みエンドポイント
  async getVolumePredictions(symbol: string, days: number = 7) {
    return this.request(`/api/finance/stocks/${symbol}/volume-predictions?days=${days}`);
  }

  // 出来高ランキング - 実装済みエンドポイント
  async getVolumeRankings(limit: number = PAGINATION.RANKING_LIMIT) {
    return this.request(`/api/finance/volume-rankings?limit=${limit}`);
  }

  // 為替・通貨関連API - 実装済み
  async getCurrencyPairs() {
    return this.request('/api/forex/currency-pairs');
  }

  async getCurrencyRate(pair: string) {
    return this.request(`/api/forex/currency-rate/${encodeURIComponent(pair)}`);
  }

  async getCurrencyHistory(pair: string, days: number = 30) {
    return this.request(`/api/forex/currency-history/${encodeURIComponent(pair)}?days=${days}`);
  }

  async getCurrencyPredictions(pair: string, timeframe: string = '1D', limit: number = 7) {
    return this.request(`/api/forex/currency-predictions/${encodeURIComponent(pair)}?timeframe=${timeframe}&limit=${limit}`);
  }

  async getCurrencyInsights(pair: string) {
    return this.request(`/api/forex/currency-insights/${encodeURIComponent(pair)}`);
  }

  async getEconomicCalendar(date?: string, country?: string) {
    let url = '/api/forex/economic-calendar';
    const params = [];
    if (date) params.push(`date=${date}`);
    if (country) params.push(`country=${country}`);
    if (params.length > 0) url += '?' + params.join('&');
    return this.request(url);
  }

  // 過去の予測データ取得（履歴）
  async getHistoricalPredictions(symbol: string, limit: number = 30) {
    return this.request(`/api/finance/stocks/${symbol}/predictions/history?limit=${limit}`);
  }

  // セクター一覧取得
  async getSectors() {
    return this.request('/api/finance/sectors');
  }

  // セクター別銘柄取得
  async getStocksBySector(sectorId: string, limit: number = 20, currency?: string) {
    let url = `/api/finance/sectors/${encodeURIComponent(sectorId)}/stocks?limit=${limit}`;
    if (currency) {
      url += `&currency=${encodeURIComponent(currency)}`;
    }
    return this.request(url);
  }

  // 高度な検索（フィルター付き）- 既存のエンドポイントを使用
  async searchStocksAdvanced(query: string = '', filters: any = {}) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    
    // 基本的なパラメータのみ追加（既存APIに合わせる）
    if (filters.limit) params.append('limit', filters.limit.toString());
    
    const url = `/api/finance/stocks/search?${params.toString()}`;
    
    // 既存のAPIレスポンスを拡張フォーマットに変換
    const response = await this.request(url);
    if (response.status === 'success' && response.data) {
      // データを拡張フォーマットに変換
      const enhancedData = response.data.map((stock: any) => ({
        ...stock,
        market: stock.exchange || '不明',
        current_price: Math.random() * 3000 + 100, // モック価格
        change_percent: (Math.random() - 0.5) * 10, // モック変動率
        ai_score: Math.floor(Math.random() * 40) + 60, // モックAIスコア
        market_cap: Math.random() * 1000000000000, // モック時価総額
        per: Math.random() * 30 + 5, // モックPER
        pbr: Math.random() * 5 + 0.5, // モックPBR
        dividend_yield: Math.random() * 5 // モック配当利回り
      }));
      
      // フィルター適用（フロントエンドサイド）
      let filteredData = enhancedData;
      
      if (filters.markets && filters.markets.length > 0) {
        filteredData = filteredData.filter((stock: any) => {
          return filters.markets.some((market: string) => {
            if (market === 'jp') return stock.exchange?.includes('TSE') || stock.exchange?.includes('TYO');
            if (market === 'us') return stock.exchange?.includes('NASDAQ') || stock.exchange?.includes('NYSE');
            return true;
          });
        });
      }
      
      if (filters.sectors && filters.sectors.length > 0) {
        filteredData = filteredData.filter((stock: any) => 
          filters.sectors.includes(stock.sector?.toLowerCase())
        );
      }
      
      if (filters.aiScoreMin !== undefined) {
        filteredData = filteredData.filter((stock: any) => stock.ai_score >= filters.aiScoreMin);
      }
      
      if (filters.aiScoreMax !== undefined) {
        filteredData = filteredData.filter((stock: any) => stock.ai_score <= filters.aiScoreMax);
      }
      
      return {
        status: 'success' as const,
        data: filteredData.slice(0, filters.limit || 20)
      };
    }
    
    return response;
  }

  // オートコンプリート検索 - 既存の検索エンドポイントを使用
  async searchStocksAutocomplete(query: string, limit: number = 10) {
    const response = await this.request(`/api/finance/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`);
    
    if (response.status === 'success' && response.data) {
      // オートコンプリート形式に変換
      const suggestions = response.data.map((stock: any) => ({
        symbol: stock.symbol,
        company_name: stock.company_name || stock.symbol,
        market: stock.exchange || '不明',
        current_price: Math.random() * 3000 + 100,
        change_percent: (Math.random() - 0.5) * 5
      }));
      
      return {
        status: 'success' as const,
        data: suggestions
      };
    }
    
    return response;
  }

  // バッチチャートデータ取得 - モックデータで対応
  async getBatchStockChartData(symbols: string[], chartTypes: string[] = ['price', 'prediction']) {
    // 既存APIにバッチエンドポイントがないため、モックデータを返す
    const mockData: { [key: string]: any } = {};
    
    symbols.forEach(symbol => {
      mockData[symbol] = {
        historical: this.generateMockChartData(100, 30),
        past_prediction: this.generateMockChartData(95, 30),
        future_prediction: this.generateMockChartData(105, 30)
      };
    });
    
    return {
      status: 'success' as const,
      data: mockData
    };
  }

  // 財務指標データ取得 - モックデータで対応
  async getStockFinancials(symbol: string) {
    return {
      status: 'success' as const,
      data: {
        symbol,
        market_cap: Math.random() * 1000000000000,
        per: Math.random() * 30 + 5,
        pbr: Math.random() * 5 + 0.5,
        dividend_yield: Math.random() * 5,
        roe: Math.random() * 20 + 5,
        roa: Math.random() * 10 + 2
      }
    };
  }

  // バッチ財務指標データ取得 - モックデータで対応
  async getBatchStockFinancials(symbols: string[]) {
    const mockData: { [key: string]: any } = {};
    
    symbols.forEach(symbol => {
      mockData[symbol] = {
        symbol,
        market_cap: Math.random() * 1000000000000,
        per: Math.random() * 30 + 5,
        pbr: Math.random() * 5 + 0.5,
        dividend_yield: Math.random() * 5
      };
    });
    
    return {
      status: 'success' as const,
      data: mockData
    };
  }
  
  // ヘルパーメソッド: モックチャートデータ生成
  private generateMockChartData(baseValue: number, length: number): number[] {
    const data = [];
    let current = baseValue;
    
    for (let i = 0; i < length; i++) {
      current += (Math.random() - 0.5) * baseValue * 0.02;
      data.push(current);
    }
    
    return data;
  }

  // セクター関連のAPI追加
  
  // セクター履歴パフォーマンス取得
  async getSectorHistoricalPerformance(sectorId: string, period: string = '1Y') {
    // 既存APIにこのエンドポイントがないため、モックデータで対応
    const basePerformance = Math.random() * 20 - 10; // -10% to +10%
    const dataPoints = period === '1M' ? 30 : period === '6M' ? 180 : 365;
    
    const data = [];
    let current = 100;
    
    for (let i = 0; i < dataPoints; i++) {
      const trend = basePerformance > 0 ? 0.001 : -0.001;
      const randomChange = (Math.random() - 0.5) * 0.02;
      current *= (1 + trend + randomChange);
      
      const date = new Date();
      date.setDate(date.getDate() - (dataPoints - i));
      
      data.push({
        date: date.toISOString().split('T')[0],
        value: current,
        change: ((current - 100) / 100) * 100
      });
    }
    
    return {
      status: 'success' as const,
      data: {
        sector_id: sectorId,
        period,
        performance_data: data,
        summary: {
          total_return: ((current - 100) / 100) * 100,
          volatility: Math.random() * 5 + 10,
          sharpe_ratio: Math.random() * 2 + 0.5
        }
      }
    };
  }

  // AIセクター見通し取得
  async getAISectorOutlook(sectorId: string) {
    // 既存APIにこのエンドポイントがないため、モックデータで対応
    const outlooks: { [key: string]: string } = {
      'technology': 'AI・機械学習の進展により、テクノロジーセクターは中長期的な成長が期待されます。特に半導体・クラウドサービス関連企業に注目が集まっています。',
      'finance': '金利環境の変化と規制緩和により、金融セクターは安定的な収益性を維持しています。デジタル化への対応が成長の鍵となります。',
      'healthcare': '高齢化社会の進展と医療技術の革新により、ヘルスケアセクターは堅調な成長軌道にあります。バイオテクノロジー分野に特に注目です。',
      'consumer': '消費者行動の変化とEC市場の拡大により、小売業界は構造的な変化を迎えています。デジタル対応が急務となっています。',
      'industrial': '脱炭素化とインフラ投資の増加により、工業セクターは新たな成長機会を迎えています。グリーンテクノロジーへの投資が活発化しています。',
      'energy': 'エネルギー転換期にあり、再生可能エネルギーへのシフトが加速しています。従来のエネルギー企業も事業転換を進めています。'
    };
    
    return {
      status: 'success' as const,
      data: {
        sector_id: sectorId,
        ai_outlook: outlooks[sectorId] || 'このセクターは市場環境の変化に応じて、新たな成長機会を模索しています。技術革新と規制変化が今後の方向性を決める重要な要因となります。',
        confidence_score: Math.random() * 30 + 70, // 70-100%
        key_drivers: [
          '技術革新の加速',
          '規制環境の変化',
          '消費者動向の変化',
          'グローバル経済情勢'
        ].slice(0, Math.floor(Math.random() * 3) + 2),
        risk_factors: [
          '金利上昇リスク',
          '地政学的リスク',
          '競争激化',
          '規制強化'
        ].slice(0, Math.floor(Math.random() * 2) + 1)
      }
    };
  }

  // セクター用に拡張されたgetSectors
  async getSectorsWithPerformance() {
    const response = await this.getSectors();
    
    if (response.status === 'success' && response.data) {
      // パフォーマンスデータを追加
      const enhancedSectors = response.data.map((sector: any) => ({
        ...sector,
        market_cap: Math.random() * 500000000000 + 50000000000, // 500億-5000億
        daily_change: (Math.random() - 0.5) * 8, // -4% to +4%
        weekly_change: (Math.random() - 0.5) * 15, // -7.5% to +7.5%
        monthly_change: (Math.random() - 0.5) * 25, // -12.5% to +12.5%
        stock_count: Math.floor(Math.random() * 200) + 50, // 50-250銘柄
        top_performers: Math.floor(Math.random() * 10) + 5, // 5-15社
        color_intensity: Math.abs((Math.random() - 0.5) * 8) // ヒートマップ用
      }));
      
      return {
        status: 'success' as const,
        data: enhancedSectors
      };
    }
    
    return response;
  }

  // AIモデル パフォーマンス取得
  async getModelPerformance(symbol: string) {
    // 既存APIにこのエンドポイントがないため、モックデータで対応
    const models = ['LSTM', 'VertexAI', 'RandomForest', 'XGBoost'];
    
    const modelData = models.map(model => {
      const accuracy = Math.random() * 20 + 70; // 70-90%
      const mae = Math.random() * 50 + 10; // 10-60円
      const rmse = Math.random() * 80 + 20; // 20-100円
      
      // バックテストデータ生成
      const backtestData = [];
      let actualPrice = Math.random() * 2000 + 500;
      
      for (let i = 0; i < 30; i++) {
        const error = (Math.random() - 0.5) * mae * 2;
        const predictedPrice = actualPrice + error;
        
        backtestData.push({
          date: new Date(Date.now() - (30 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          actual_price: actualPrice,
          predicted_price: predictedPrice,
          error: Math.abs(error)
        });
        
        actualPrice += (Math.random() - 0.5) * 20;
      }
      
      return {
        model_name: model,
        accuracy: accuracy,
        mae: mae,
        rmse: rmse,
        ai_evaluation: getModelEvaluation(model),
        backtest_data: backtestData,
        last_updated: new Date().toISOString(),
        training_samples: Math.floor(Math.random() * 5000) + 10000
      };
    });

    return {
      status: 'success' as const,
      data: {
        symbol,
        models: modelData,
        overall_performance: {
          best_accuracy: Math.max(...modelData.map(m => m.accuracy)),
          best_model: modelData.reduce((prev, current) => 
            prev.accuracy > current.accuracy ? prev : current
          ).model_name,
          average_accuracy: modelData.reduce((sum, m) => sum + m.accuracy, 0) / modelData.length
        }
      }
    };

    function getModelEvaluation(modelName: string): string {
      const evaluations: { [key: string]: string } = {
        'LSTM': '長期トレンドの予測に優れており、時系列パターンの学習能力が高い。短期的なボラティリティには若干弱い傾向があります。',
        'VertexAI': 'Google Cloudの最新技術を活用し、多様なデータソースを組み合わせた高精度な予測を実現。特に複雑な市場環境での予測力が強みです。',
        'RandomForest': '安定した予測性能を提供し、過学習を抑制する能力に優れています。解釈しやすい特徴量の重要度も提供します。',
        'XGBoost': '勾配ブースティングによる高い予測精度が特徴。特に短期から中期の価格変動予測において優れた性能を発揮します。'
      };
      return evaluations[modelName] || '高度な機械学習アルゴリズムにより、市場データから有意義なパターンを抽出し予測を行います。';
    }
  }

  // AI出来高インサイト取得
  async getAIVolumeInsights(symbol: string) {
    // 既存APIにこのエンドポイントがないため、モックデータで対応
    const insights = [
      "過去5日間、平均を上回る出来高を伴って株価が上昇しており、強い買い圧力が示唆されます。",
      "来週、出来高が急増する可能性をAIが予測しています。重要なニュースが発表される可能性があります。",
      "現在の出来高は20日平均の1.8倍に達しており、機関投資家の関心の高さが表れています。",
      "出来高パターンから判断すると、短期的な調整局面が近い可能性があります。",
      "最近の出来高増加は、新製品発表やM&A関連の憶測によるものと推測されます。"
    ];

    const volumeTrends = [
      "急増トレンド", "安定推移", "減少傾向", "波動的変化", "集中買い"
    ];

    const currentVolume = Math.floor(Math.random() * 5000000) + 1000000; // 100万-600万株
    const averageVolume = Math.floor(currentVolume * (0.7 + Math.random() * 0.6)); // 平均の70%-130%
    const deviation = ((currentVolume - averageVolume) / averageVolume) * 100;

    // 未来の出来高予測を生成
    const futurePredictions = [];
    for (let i = 1; i <= 7; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      
      const baseTrend = Math.random() > 0.5 ? 1.1 : 0.9; // 上昇または下降トレンド
      const volatility = 0.8 + Math.random() * 0.4; // 80%-120%の変動
      const predictedVolume = Math.floor(averageVolume * baseTrend * volatility);
      const changePercent = ((predictedVolume - averageVolume) / averageVolume) * 100;

      futurePredictions.push({
        date: date.toISOString().split('T')[0],
        predicted_volume: predictedVolume,
        change_percent: changePercent,
        confidence: Math.random() * 30 + 70, // 70-100%
        day_name: i === 1 ? '明日' : i === 2 ? '明後日' : `${i}日後`
      });
    }

    return {
      status: 'success' as const,
      data: {
        symbol,
        current_analysis: {
          current_volume: currentVolume,
          average_volume_20d: averageVolume,
          deviation_percent: deviation,
          deviation_ratio: currentVolume / averageVolume,
          trend: volumeTrends[Math.floor(Math.random() * volumeTrends.length)],
          analysis_date: new Date().toISOString()
        },
        ai_insights: insights
          .sort(() => 0.5 - Math.random())
          .slice(0, Math.floor(Math.random() * 3) + 2), // 2-4個のインサイト
        future_predictions: futurePredictions,
        risk_factors: [
          "市場全体のボラティリティ上昇",
          "業界特有のニュース発表",
          "四半期決算発表の影響",
          "機関投資家のポジション変更"
        ].slice(0, Math.floor(Math.random() * 2) + 1),
        confidence_score: Math.random() * 25 + 75 // 75-100%
      }
    };
  }

  // ウォッチリスト関連API
  async getWatchlist(userId?: string) {
    // サーバーサイドが未実装の場合はlocalStorageから取得
    if (!userId) {
      return {
        status: 'success' as const,
        data: JSON.parse(localStorage.getItem('watchlist') || '[]')
      };
    }
    return this.request(`/api/users/${userId}/watchlist`);
  }

  async addToWatchlist(symbol: string, userId?: string) {
    if (!userId) {
      // localStorageでの管理
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      if (!watchlist.includes(symbol)) {
        watchlist.push(symbol);
        localStorage.setItem('watchlist', JSON.stringify(watchlist));
      }
      return {
        status: 'success' as const,
        data: { added: symbol }
      };
    }
    return this.request(`/api/users/${userId}/watchlist`, {
      method: 'POST',
      body: JSON.stringify({ symbol })
    }, false);
  }

  async removeFromWatchlist(symbol: string, userId?: string) {
    if (!userId) {
      // localStorageでの管理
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      const filtered = watchlist.filter((s: string) => s !== symbol);
      localStorage.setItem('watchlist', JSON.stringify(filtered));
      return {
        status: 'success' as const,
        data: { removed: symbol }
      };
    }
    return this.request(`/api/users/${userId}/watchlist/${encodeURIComponent(symbol)}`, {
      method: 'DELETE'
    }, false);
  }

  async getBatchStockDetails(symbols: string[]) {
    if (symbols.length === 0) {
      return {
        status: 'success' as const,
        data: {}
      };
    }

    try {
      // 並列でデータを取得（効率化）
      const batchPromises = symbols.map(async (symbol) => {
        const [priceResponse, predictionResponse, financialResponse] = await Promise.all([
          this.getStockPrice(symbol, 30),
          this.getStockPredictions(symbol, undefined, 10),
          this.getStockFinancials(symbol)
        ]);

        let stockData: any = {
          symbol,
          error: null,
          prices: [],
          predictions: [],
          financials: {}
        };

        if (priceResponse.status === 'success') {
          stockData.prices = priceResponse.data || [];
          if (stockData.prices.length > 0) {
            const latest = stockData.prices[stockData.prices.length - 1];
            stockData.current_price = latest.close_price;
            stockData.change_percent = latest.change_percent || 0;
            stockData.volume = latest.volume;
            stockData.last_updated = latest.timestamp;
          }
        }

        if (predictionResponse.status === 'success') {
          stockData.predictions = predictionResponse.data || [];
          if (stockData.predictions.length > 0) {
            stockData.ai_score = Math.round(stockData.predictions[0].confidence_score * 100);
            stockData.prediction_trend = stockData.predictions[0].predicted_price > stockData.current_price ? 'up' : 'down';
          }
        }

        if (financialResponse.status === 'success') {
          stockData.financials = financialResponse.data || {};
          stockData.market_cap = stockData.financials.market_cap;
          stockData.per = stockData.financials.per;
          stockData.pbr = stockData.financials.pbr;
          stockData.dividend_yield = stockData.financials.dividend_yield;
        }

        // 会社名を設定（模擬データ）
        const companyNames: { [key: string]: string } = {
          'AAPL': 'Apple Inc.',
          'GOOGL': 'Alphabet Inc.',
          'MSFT': 'Microsoft Corporation',
          'TSLA': 'Tesla, Inc.',
          'AMZN': 'Amazon.com Inc.',
          'NVDA': 'NVIDIA Corporation',
          'META': 'Meta Platforms Inc.',
          '7203': 'トヨタ自動車',
          '6758': 'ソニーグループ',
          '9984': 'ソフトバンクグループ'
        };
        stockData.company_name = companyNames[symbol] || symbol;

        return stockData;
      });

      const results = await Promise.all(batchPromises);
      
      // シンボルをキーとしたオブジェクトに変換
      const batchData: { [key: string]: any } = {};
      results.forEach(stock => {
        batchData[stock.symbol] = stock;
      });

      return {
        status: 'success' as const,
        data: batchData
      };
    } catch (error) {
      return {
        status: 'error' as const,
        error: error instanceof Error ? error.message : 'バッチデータ取得エラー'
      };
    }
  }

  // ウォッチリストの並び順を保存
  async updateWatchlistOrder(symbols: string[], userId?: string) {
    if (!userId) {
      localStorage.setItem('watchlist', JSON.stringify(symbols));
      return {
        status: 'success' as const,
        data: { order_updated: true }
      };
    }
    return this.request(`/api/users/${userId}/watchlist/order`, {
      method: 'PUT',
      body: JSON.stringify({ symbols })
    }, false);
  }

  // ヘルスチェック
  async healthCheck() {
    return this.request('/health', {}, false); // ヘルスチェックはキャッシュしない
  }
  
  // キャッシュクリア
  clearCache() {
    this.cache.clear();
  }
  
  // 特定エンドポイントのキャッシュクリア
  clearCacheForEndpoint(endpoint: string) {
    this.cache.delete(endpoint);
  }
}

export const apiClient = new APIClient();
export default apiClient;