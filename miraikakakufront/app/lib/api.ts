import axios from 'axios';
import { 
  StockPrice, 
  StockPrediction, 
  HistoricalPrediction, 
  StockDetails, 
  AIDecisionFactor,
  SearchResult 
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // Ensure proper URL encoding for Japanese characters
  paramsSerializer: (params) => {
    return Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
  },
});

// Error handler
const handleApiError = (error: any) => {
  if (error.response) {
    throw new Error(error.response.data.detail || error.response.data.message || 'API Error');
  } else if (error.request) {
    throw new Error('Network Error: Unable to reach the server');
  } else {
    throw new Error('Request Error: ' + error.message);
  }
};

export const stockAPI = {
  // Search stocks using real API endpoint
  search: async (query: string, limit: number = 10): Promise<SearchResult[]> => {
    try {
      // Enhanced company name to symbol mapping for Japanese queries
      const companyNameMap: { [key: string]: string } = {
        // Japanese companies - full and partial matches
        'アップル': 'AAPL',
        'マイクロソフト': 'MSFT',
        'グーグル': 'GOOGL',
        'グーグル': 'GOOGL',
        'アマゾン': 'AMZN',
        'テスラ': 'TSLA',
        'エヌビディア': 'NVDA',
        'メタ': 'META',
        'フェイスブック': 'META',
        'ネットフリックス': 'NFLX',
        'トヨタ': '7203.T',
        'トヨタ自動車': '7203.T',
        'ソニー': '6758.T',
        'ソニーグループ': '6758.T',
        // English companies
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'nvidia': 'NVDA',
        'meta': 'META',
        'facebook': 'META',
        'netflix': 'NFLX',
        'toyota': '7203.T',
        'sony': '6758.T',
        // Rankings/Categories - return growth potential rankings
        '値上がり率': 'growth-potential',
        '成長率': 'growth-potential',
        'gainers': 'growth-potential',
        'growth': 'growth-potential',
        'performance': 'growth-potential'
      };
      
      const lowerQuery = query.toLowerCase().trim();
      const mappedSymbol = companyNameMap[query] || companyNameMap[lowerQuery];
      
      // If query matches a ranking category, return growth potential rankings
      if (mappedSymbol === 'growth-potential') {
        try {
          const response = await api.get('/api/finance/rankings/growth-potential');
          if (response.data && Array.isArray(response.data)) {
            return response.data.slice(0, limit).map((item: any) => ({
              symbol: item.symbol,
              shortName: item.company_name,
              longName: item.company_name,
              sector: item.sector,
              currentPrice: item.current_price
            }));
          }
        } catch (err) {
          console.error('Rankings fetch error:', err);
        }
      }
      
      // Use the mapped symbol if available, otherwise use original query
      const searchQuery = mappedSymbol && mappedSymbol !== 'growth-potential' ? mappedSymbol : query;
      
      // If we have a Japanese query that mapped to a symbol, return it directly
      if (mappedSymbol && mappedSymbol !== 'growth-potential') {
        try {
          const response = await api.get('/api/finance/stocks/search', {
            params: { q: mappedSymbol, limit }
          });
          
          if (response.data && Array.isArray(response.data)) {
            return response.data;
          }
        } catch (error) {
          console.error('Mapped symbol search error:', error);
        }
      }
      
      // Only send non-Japanese characters to API to avoid encoding issues
      const containsJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(query);
      if (containsJapanese) {
        // For Japanese queries without mapping, return empty array
        return [];
      }
      
      // Use the real search API endpoint for English queries
      const response = await api.get('/api/finance/stocks/search', {
        params: { q: searchQuery, limit }
      });
      
      if (response.data && Array.isArray(response.data)) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  },

  // Get stock price history
  getPriceHistory: async (symbol: string, days: number = 730): Promise<StockPrice[]> => {
    try {
      const possibleEndpoints = [
        `/api/finance/stocks/${symbol}/price`,
        `/finance/stocks/${symbol}/price`,
        `/stocks/${symbol}/price`,
        `/${symbol}/price`
      ];
      
      for (const endpoint of possibleEndpoints) {
        try {
          const response = await api.get(endpoint, {
            params: { days }
          });
          if (response.data && Array.isArray(response.data)) {
            return response.data;
          }
        } catch (err) {
          continue;
        }
      }
      
      return [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  },

  // Get future predictions using real API endpoint
  getPredictions: async (symbol: string, days: number = 180): Promise<StockPrediction[]> => {
    try {
      const response = await api.get(`/api/finance/stocks/${symbol}/predictions`, {
        params: { days }
      });
      
      if (response.data && Array.isArray(response.data)) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  },

  // Get historical predictions using real API endpoint
  getHistoricalPredictions: async (symbol: string, days: number = 730): Promise<HistoricalPrediction[]> => {
    try {
      const response = await api.get(`/api/finance/stocks/${symbol}/predictions/history`, {
        params: { days }
      });
      
      const data = response.data;
      if (data) {
        return data.historical_predictions || data || [];
      }
      
      return [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  },

  // Get AI decision factors using real API endpoint
  getAIFactors: async (symbol: string): Promise<AIDecisionFactor[]> => {
    try {
      const response = await api.get(`/api/ai/factors/${symbol}`);
      
      const data = response.data;
      if (data) {
        return data.factors || data || [];
      }
      
      return [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  },

  // Get stock details
  getStockDetails: async (symbol: string): Promise<StockDetails | null> => {
    try {
      const searchResults = await stockAPI.search(symbol, 1);
      if (searchResults.length > 0) {
        return searchResults[0] as StockDetails;
      }
      return null;
    } catch (error) {
      handleApiError(error);
      return null;
    }
  },

  // Get all data for a stock
  getAllStockData: async (symbol: string) => {
    try {
      const [priceHistory, predictions, historicalPredictions, details, aiFactors] = await Promise.all([
        stockAPI.getPriceHistory(symbol),
        stockAPI.getPredictions(symbol),
        stockAPI.getHistoricalPredictions(symbol),
        stockAPI.getStockDetails(symbol),
        stockAPI.getAIFactors(symbol),
      ]);

      return {
        priceHistory,
        predictions,
        historicalPredictions,
        details,
        aiFactors,
      };
    } catch (error) {
      throw error;
    }
  },
};