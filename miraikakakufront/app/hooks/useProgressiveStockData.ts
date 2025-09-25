import { useState, useEffect, useCallback } from 'react';
import { stockAPI } from '../lib/api';
import type { StockPrice, StockPrediction, HistoricalPrediction, StockDetails, AIDecisionFactor } from '../types';

interface ProgressiveStockDataState {
  // Core data (Stage 1)
  details: StockDetails | null;
  latestPrice: StockPrice | null;

  // Chart data (Stage 2)
  priceHistory: StockPrice[];
  predictions: StockPrediction[];
  historicalPredictions: HistoricalPrediction[];

  // Analysis data (Stage 3)
  aiFactors: AIDecisionFactor[];
  financialAnalysis: any | null;
  riskAnalysis: any | null;

  // Loading states
  stage1Loading: boolean;
  stage2Loading: boolean;
  stage3Loading: boolean;

  // Completion flags
  stage1Complete: boolean;
  stage2Complete: boolean;
  stage3Complete: boolean;

  error: string | null;
}

export function useProgressiveStockData(symbol: string) {
  const [state, setState] = useState<ProgressiveStockDataState>({
    details: null
    latestPrice: null
    priceHistory: []
    predictions: []
    historicalPredictions: []
    aiFactors: []
    financialAnalysis: null
    riskAnalysis: null
    stage1Loading: true
    stage2Loading: false
    stage3Loading: false
    stage1Complete: false
    stage2Complete: false
    stage3Complete: false
    error: null
  }
  // Stage 1: Critical data (details + latest price)
  const fetchStage1Data = useCallback(async (stockSymbol: string) => {
    setState(prev => ({ ...prev, stage1Loading: true, error: null })
    try {
      const startTime = performance.now(
      const [details, latestPriceData] = await Promise.all([
        stockAPI.getStockDetails(stockSymbol)
        stockAPI.getPriceHistory(stockSymbol, 1), // Get just latest price
      ]
      const latestPrice = latestPriceData && latestPriceData.length > 0 ? latestPriceData[latestPriceData.length - 1] : null;

      const elapsed = performance.now() - startTime;
      }ms`
      setState(prev => ({
        ...prev
        details
        latestPrice
        stage1Loading: false
        stage1Complete: true
        error: null
      })
    } catch (error: any) {
      setState(prev => ({
        ...prev
        stage1Loading: false
        error
      })
    }
  }, []
  // Stage 2: Chart data (price history + predictions)
  const fetchStage2Data = useCallback(async (stockSymbol: string) => {
    setState(prev => ({ ...prev, stage2Loading: true })
    try {
      const startTime = performance.now(
      const [priceHistory, predictions] = await Promise.all([
        stockAPI.getPriceHistory(stockSymbol)
        stockAPI.getPredictions(stockSymbol)
      ]
      const elapsed = performance.now() - startTime;
      }ms`
      setState(prev => ({
        ...prev
        priceHistory: priceHistory || []
        predictions: predictions || []
        stage2Loading: false
        stage2Complete: true
      })
    } catch (error: any) {
      setState(prev => ({
        ...prev
        stage2Loading: false
        // Don't set error for non-critical data
      })
    }
  }, []
  // Stage 3: Analysis data (non-critical)
  const fetchStage3Data = useCallback(async (stockSymbol: string) => {
    setState(prev => ({ ...prev, stage3Loading: true })
    try {
      const startTime = performance.now(
      // Use Promise.allSettled to allow partial failures
      const results = await Promise.allSettled([
        stockAPI.getHistoricalPredictions(stockSymbol)
        stockAPI.getAIFactors(stockSymbol)
        stockAPI.getFinancialAnalysis(stockSymbol)
        stockAPI.getRiskAnalysis(stockSymbol)
      ]
      const elapsed = performance.now() - startTime;
      }ms`
      setState(prev => ({
        ...prev
        historicalPredictions: results[0].status === 'fulfilled' ? results[0].value || [] : []
        aiFactors: results[1].status === 'fulfilled' ? results[1].value || [] : []
        financialAnalysis: results[2].status === 'fulfilled' ? results[2].value : null
        riskAnalysis: results[3].status === 'fulfilled' ? results[3].value : null
        stage3Loading: false
        stage3Complete: true
      })
    } catch (error: any) {
      setState(prev => ({
        ...prev
        stage3Loading: false
        stage3Complete: true, // Mark as complete even if failed
      })
    }
  }, []
  // Main data fetching function
  const fetchData = useCallback(async (stockSymbol: string) => {
    if (!stockSymbol) return;

    // Reset state
    setState({
      details: null
      latestPrice: null
      priceHistory: []
      predictions: []
      historicalPredictions: []
      aiFactors: []
      financialAnalysis: null
      riskAnalysis: null
      stage1Loading: true
      stage2Loading: false
      stage3Loading: false
      stage1Complete: false
      stage2Complete: false
      stage3Complete: false
      error: null
    }
    // Execute stages sequentially with overlapping
    await fetchStage1Data(stockSymbol
    // Start stage 2 after stage 1 completes
    setTimeout(() => fetchStage2Data(stockSymbol), 100
    // Start stage 3 after a short delay
    setTimeout(() => fetchStage3Data(stockSymbol), 500
  }, [fetchStage1Data, fetchStage2Data, fetchStage3Data]
  // Refetch function
  const refetch = useCallback(() => {
    if (symbol) {
      fetchData(symbol
    }
  }, [symbol, fetchData]
  // Effect to start data fetching
  useEffect(() => {
    fetchData(symbol
  }, [symbol, fetchData]
  // Compute overall loading state
  const isLoading = state.stage1Loading;
  const hasBasicData = state.stage1Complete && state.details;
  const hasChartData = state.stage2Complete;
  const hasAnalysisData = state.stage3Complete;

  return {
    // Data
    ...state
    // Computed states
    isLoading
    hasBasicData
    hasChartData
    hasAnalysisData
    // Actions
    refetch
  };
}