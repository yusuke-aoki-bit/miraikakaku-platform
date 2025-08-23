// Real stock data client
export interface StockPriceData {
  symbol: string;
  date: string;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  close_price: number;
  volume?: number;
  data_source?: string;
}

export interface StockPrediction {
  symbol: string;
  prediction_date: string;
  predicted_price: number;
  confidence_score?: number;
  model_type?: string;
  prediction_horizon?: string;
  is_active?: boolean;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  type: 'actual' | 'historical_prediction' | 'future_prediction';
}

export interface IndexData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  lastUpdate: string;
  actualData: ChartDataPoint[];
  historicalPredictions: ChartDataPoint[];
  futurePredictions: ChartDataPoint[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Major indices mapping
const INDEX_SYMBOL_MAP = {
  'NIKKEI': 'nikkei',   // Nikkei 225
  'TOPIX': 'topix',     // Tokyo Stock Price Index
  'DOW': 'dow',         // Dow Jones Industrial Average
  'SP500': 'sp500',     // S&P 500
  'NVDA': 'NVDA',   // NVIDIA Corporation
  'META': 'META',   // Meta Platforms Inc.
  'JPM': 'JPM',     // JPMorgan Chase & Co.
  'V': 'V',         // Visa Inc.
  'WMT': 'WMT'      // Walmart Inc.
};

const INDEX_NAMES = {
  'NIKKEI': '日経平均株価',
  'TOPIX': '東証株価指数',
  'DOW': 'ダウ工業株30種',
  'SP500': 'S&P 500'
};

export class StockDataClient {
  private async fetchWithTimeout(url: string, timeout = 10000): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async getStockPrice(symbol: string, days: number = 30): Promise<StockPriceData[]> {
    try {
      const actualSymbol = INDEX_SYMBOL_MAP[symbol as keyof typeof INDEX_SYMBOL_MAP] || symbol.toLowerCase();
      const url = `${API_BASE_URL}/api/finance/test/indices/${actualSymbol}?days=${days}`;
      
      const response = await this.fetchWithTimeout(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      // Convert the new API format to the expected format
      return result.data?.map((item: any) => ({
        symbol: result.symbol,
        date: item.date,
        open_price: item.open,
        high_price: item.high,
        low_price: item.low,
        close_price: item.close,
        volume: item.volume,
        data_source: 'yahoo_finance'
      })) || [];
    } catch (error) {
      console.error(`Failed to fetch stock price for ${symbol}:`, error);
      return [];
    }
  }

  async getStockPredictions(symbol: string, days: number = 7): Promise<StockPrediction[]> {
    try {
      const actualSymbol = INDEX_SYMBOL_MAP[symbol as keyof typeof INDEX_SYMBOL_MAP] || symbol.toLowerCase();
      const url = `${API_BASE_URL}/api/finance/test/indices/${actualSymbol}/predictions?days=${days}`;
      
      const response = await this.fetchWithTimeout(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      // Convert future predictions to the expected format
      return result.data?.future_predictions?.map((item: any) => ({
        symbol: result.symbol,
        prediction_date: item.date,
        predicted_price: item.value,
        confidence_score: item.confidence,
        model_type: 'LSTM-Dynamic',
        prediction_horizon: 'daily',
        is_active: true
      })) || [];
    } catch (error) {
      console.error(`Failed to fetch predictions for ${symbol}:`, error);
      return [];
    }
  }

  async getIndexData(symbol: string): Promise<IndexData | null> {
    try {
      const actualSymbol = INDEX_SYMBOL_MAP[symbol as keyof typeof INDEX_SYMBOL_MAP] || symbol.toLowerCase();
      
      // Get comprehensive predictions data
      const predictionsUrl = `${API_BASE_URL}/api/finance/test/indices/${actualSymbol}/predictions?days=30`;
      const response = await this.fetchWithTimeout(predictionsUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }

      // Convert data from new API format
      const actualData: ChartDataPoint[] = result.data?.actual?.map((item: any) => ({
        date: item.date,
        value: item.value,
        type: 'actual' as const
      })) || [];

      const historicalPredictions: ChartDataPoint[] = result.data?.historical_predictions?.map((item: any) => ({
        date: item.date,
        value: item.value,
        type: 'historical_prediction' as const
      })) || [];

      const futurePredictions: ChartDataPoint[] = result.data?.future_predictions?.map((item: any) => ({
        date: item.date,
        value: item.value,
        type: 'future_prediction' as const
      })) || [];

      if (actualData.length === 0) {
        throw new Error(`No data available for ${symbol}`);
      }

      // Calculate latest price info
      const latestPrice = actualData[actualData.length - 1];
      const previousPrice = actualData[actualData.length - 2];
      const change = previousPrice ? latestPrice.value - previousPrice.value : 0;
      const changePercent = previousPrice ? (change / previousPrice.value) * 100 : 0;

      return {
        symbol: result.symbol || symbol,
        name: INDEX_NAMES[symbol as keyof typeof INDEX_NAMES] || result.name || symbol,
        price: latestPrice.value,
        change,
        changePercent,
        volume: 0, // Volume not provided in current API
        lastUpdate: new Date().toLocaleTimeString(),
        actualData,
        historicalPredictions,
        futurePredictions
      };
    } catch (error) {
      console.error(`Failed to get index data for ${symbol}:`, error);
      return null;
    }
  }
}

export const stockDataClient = new StockDataClient();