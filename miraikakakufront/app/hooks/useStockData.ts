import { useState, useEffect, useCallback } from 'react';
import { stockAPI } from '../lib/api';
import type { StockPrice, StockPrediction, HistoricalPrediction, StockDetails, AIDecisionFactor } from '../types';

interface StockDataState {
  priceHistory: StockPrice[];
  predictions: StockPrediction[];
  historicalPredictions: HistoricalPrediction[];
  details: StockDetails | null;
  aiFactors: AIDecisionFactor[];
  financialAnalysis: any | null;
  riskAnalysis: any | null;
  loading: boolean;
  error: string | null;
}

export function useStockData(symbol: string) {
  const [state, setState] = useState<StockDataState>({
    priceHistory: [],
    predictions: [],
    historicalPredictions: [],
    details: null,
    aiFactors: [],
    financialAnalysis: null,
    riskAnalysis: null,
    loading: true,
    error: null
  });
  const fetchStockData = useCallback(async (stockSymbol: string) => {
    if (!stockSymbol) return;

    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await stockAPI.getAllStockData(stockSymbol);
      setState({
        priceHistory: data.priceHistory || [],
        predictions: data.predictions || [],
        historicalPredictions: data.historicalPredictions || [],
        details: data.details,
        aiFactors: data.aiFactors || [],
        financialAnalysis: data.financialAnalysis || null,
        riskAnalysis: data.riskAnalysis || null,
        loading: false,
        error: null
      });
    } catch (err: any) {
      // Enhanced error handling based on error type and status
      let errorMessage = 'Failed to load stock data. Please try again later.';

      if (err?.response?.status === 404) {
        errorMessage = `Stock symbol '${stockSymbol}' not found. Please check the symbol and try again.`;
      } else if (err?.response?.status === 429) {
        errorMessage = 'Too many requests. Please wait a moment before trying again.';
      } else if (err?.response?.status >= 500) {
        errorMessage = 'Server error. Our team has been notified. Please try again later.';
      } else if (err?.message?.includes('Network Error') || err?.code === 'NETWORK_ERROR') {
        errorMessage = 'Network connection error. Please check your internet connection and try again.';
      } else if (err?.code === 'ECONNABORTED' || err?.message?.includes('timeout')) {
        errorMessage = 'Request timed out. Please try again.';
      } else if (err?.response?.data?.error) {
        // Use error message from API response if available
        errorMessage = err.response.data.error;
      } else if (err?.message) {
        errorMessage = err.message;
      }

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, []);
  const refetch = useCallback(() => {
    fetchStockData(symbol);
  }, [symbol, fetchStockData]);
  useEffect(() => {
    fetchStockData(symbol);
  }, [symbol, fetchStockData]);
  return {
    ...state,
    refetch
  };
}