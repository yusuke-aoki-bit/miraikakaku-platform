'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Activity } from 'lucide-react';
import { StockPrice } from '../types';

interface TechnicalAnalysisProps {
  priceHistory: StockPrice[];
}

interface TechnicalIndicator {
  name: string;
  value: number | string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  description: string;
}

export default function TechnicalAnalysis({ priceHistory }: TechnicalAnalysisProps) {
  const { t } = useTranslation('common');
  // Calculate technical indicators
  const calculateTechnicalIndicators = (): TechnicalIndicator[] => {
    if (!priceHistory || priceHistory.length < 20) {
      return [];
    }

    const prices = priceHistory.map(p => p.close_price).filter((p): p is number => p != null && p > 0);
    const volumes = priceHistory.map(p => p.volume).filter((v): v is number => v != null && v > 0);
    if (prices.length < 20) return [];

    const currentPrice = prices[prices.length - 1];

    // Simple Moving Average (20-day)
    const sma20 = prices.slice(-20).reduce((sum, price) => sum + price, 0) / 20;

    // Simple Moving Average (50-day)
    const sma50 = prices.length >= 50
      ? prices.slice(-50).reduce((sum, price) => sum + price, 0) / 50
      : sma20;

    // RSI calculation (simplified 14-day)
    const calculateRSI = () => {
      if (prices.length < 14) return 50;

      let gains = 0;
      let losses = 0;

      for (let i = prices.length - 14; i < prices.length - 1; i++) {
        const currentPrice = prices[i];
        const nextPrice = prices[i + 1];
        if (currentPrice !== undefined && nextPrice !== undefined) {
          const change = nextPrice - currentPrice;
          if (change > 0) gains += change;
          else losses += Math.abs(change);
        }
      }

      const avgGain = gains / 14;
      const avgLoss = losses / 14;

      if (avgLoss === 0) return 100;
      const rs = avgGain / avgLoss;
      return 100 - (100 / (1 + rs));
    };

    // Volatility calculation
    const calculateVolatility = () => {
      if (prices.length < 20) return 0;
      const recent = prices.slice(-20);
      const avg = recent.reduce((sum, price) => sum + price, 0) / recent.length;
      const variance = recent.reduce((sum, price) => sum + Math.pow(price - avg, 2), 0) / recent.length;
      return Math.sqrt(variance);
    };

    // Volume analysis
    const calculateVolumeSignal = () => {
      if (volumes.length < 20) return 'HOLD';
      const recentVolumes = volumes.slice(-10);
      const olderVolumes = volumes.slice(-20, -10);
      const recentAvg = recentVolumes.reduce((sum, vol) => sum + vol, 0) / recentVolumes.length;
      const olderAvg = olderVolumes.reduce((sum, vol) => sum + vol, 0) / olderVolumes.length;

      const volumeIncrease = (recentAvg - olderAvg) / olderAvg;

      if (volumeIncrease > 0.2) return 'BUY';
      if (volumeIncrease < -0.2) return 'SELL';
      return 'HOLD';
    };

    const indicators: TechnicalIndicator[] = [];

    // Add RSI indicator
    const rsiValue = calculateRSI();
    let rsiSignal: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    if (rsiValue < 30) rsiSignal = 'BUY';
    else if (rsiValue > 70) rsiSignal = 'SELL';

    indicators.push({
      name: t('stockDetails.technicalAnalysis.rsi'),
      value: rsiValue.toFixed(2),
      signal: rsiSignal,
      description: t('stockDetails.technicalAnalysis.rsiDescription')
    });
    // Add Moving Average indicator
    let smaSignal: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    if (currentPrice !== undefined && currentPrice > sma20 && sma20 > sma50) smaSignal = 'BUY';
    else if (currentPrice !== undefined && currentPrice < sma20 && sma20 < sma50) smaSignal = 'SELL';

    indicators.push({
      name: t('stockDetails.technicalAnalysis.movingAverage'),
      value: smaSignal,
      signal: smaSignal,
      description: t('stockDetails.technicalAnalysis.movingAverageDescription')
    });
    // Add Volatility indicator
    const volatility = calculateVolatility();
    const volatilityPercentage = currentPrice !== undefined ? (volatility / currentPrice) * 100 : 0;
    let volatilitySignal: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    if (volatilityPercentage < 1) volatilitySignal = 'BUY';
    else if (volatilityPercentage > 3) volatilitySignal = 'SELL';

    indicators.push({
      name: t('stockDetails.technicalAnalysis.volatility'),
      value: `${volatilityPercentage.toFixed(2)}%`,
      signal: volatilitySignal,
      description: t('stockDetails.technicalAnalysis.volatilityDescription')
    });
    // Add Volume indicator
    const volumeSignal = calculateVolumeSignal();
    indicators.push({
      name: t('stockDetails.technicalAnalysis.volume'),
      value: volumeSignal,
      signal: volumeSignal,
      description: t('stockDetails.technicalAnalysis.volumeDescription')
    });
    return indicators;
  };

  const indicators = calculateTechnicalIndicators();
  if (!priceHistory || priceHistory.length === 0) {
    return (
      <div className="rounded-lg shadow-md p-6" style={{
        backgroundColor: 'var(--yt-music-surface)',
        border: '1px solid var(--yt-music-border)'
      }}>
        <h2 className="text-2xl font-semibold mb-4 flex items-center" style={{ color: 'var(--yt-music-text-primary)' }}>
          <Activity className="w-6 h-6 mr-2" />
          {t('stockDetails.technicalAnalysis.title')}
        </h2>
        <p className="text-gray-500 italic">{t('stockDetails.technicalAnalysis.insufficientData')}</p>
      </div>
    );
  }

  // Calculate overall signal
  const calculateOverallSignal = () => {
    if (indicators.length === 0) return 'HOLD';

    const signals = indicators.map(i => i.signal);
    const buyCount = signals.filter(s => s === 'BUY').length;
    const sellCount = signals.filter(s => s === 'SELL').length;

    if (buyCount > sellCount && buyCount >= 2) return 'BUY';
    if (sellCount > buyCount && sellCount >= 2) return 'SELL';
    return 'HOLD';
  };

  const overallSignal = calculateOverallSignal();
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-green-600 bg-green-50 border-green-200';
      case 'SELL': return 'text-red-600 bg-red-50 border-red-200';
      case 'HOLD': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="rounded-lg shadow-md p-6" style={{
      backgroundColor: 'var(--yt-music-surface)',
      border: '1px solid var(--yt-music-border)'
    }}>
      <h2 className="text-2xl font-semibold mb-4 flex items-center" style={{ color: 'var(--yt-music-text-primary)' }}>
        <Activity className="w-6 h-6 mr-2" />
        {t('stockDetails.technicalAnalysis.title')}
      </h2>

      {indicators.length > 0 ? (
        <div className="space-y-4">
          {/* Overall Signal */}
          <div className="border-b pb-4">
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>
              {t('stockDetails.technicalAnalysis.overallSignal')}
            </h3>
            <div className="flex items-center space-x-2">
              <div className={`px-4 py-2 rounded-lg border text-lg font-bold ${getSignalColor(overallSignal)}`}>
                {overallSignal}
              </div>
              <span style={{ color: 'var(--yt-music-text-secondary)' }}>
                {overallSignal === 'BUY' ? t('stockDetails.technicalAnalysis.buySignal') :
                 overallSignal === 'SELL' ? t('stockDetails.technicalAnalysis.sellSignal') :
                 t('stockDetails.technicalAnalysis.holdSignal')}
              </span>
            </div>
          </div>

          {/* Individual Indicators */}
          <div className="grid md:grid-cols-2 gap-4">
            {indicators.map((indicator, index) => (
              <div key={index} className="border rounded-lg p-4" style={{
                backgroundColor: 'var(--yt-music-bg)',
                borderColor: 'var(--yt-music-border)'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium" style={{ color: 'var(--yt-music-text-primary)' }}>
                    {indicator.name}
                  </h4>
                  <div className={`px-2 py-1 rounded text-xs font-medium border ${getSignalColor(indicator.signal)}`}>
                    {indicator.signal}
                  </div>
                </div>
                <div className="text-2xl font-bold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {indicator.value}
                </div>
                <p className="text-sm" style={{ color: 'var(--yt-music-text-secondary)' }}>
                  {indicator.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-gray-500 italic">{t('stockDetails.technicalAnalysis.insufficientData')}</p>
      )}
    </div>
  );
}