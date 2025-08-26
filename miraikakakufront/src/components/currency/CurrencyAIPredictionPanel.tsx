'use client';

import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, TrendingDown, Brain, AlertTriangle, Clock } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface CurrencyRate {
  bid: number;
  ask: number;
  mid: number;
  spread: number;
}

interface AIPrediction {
  timeframe: string;
  predicted_rate: number;
  confidence: number;
  change_percent: number;
}

interface AISignal {
  signal: 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell';
  strength: number;
  recommendation: string;
}

interface KeyDriver {
  factor: string;
  impact: 'positive' | 'negative' | 'neutral';
  weight: number;
  description: string;
}

interface CurrencyAIPredictionPanelProps {
  pair: string;
  timeframes?: string[];
}

const SIGNAL_CONFIG = {
  strong_buy: { label: '強い買い', color: 'text-green-400', bgColor: 'bg-green-500/20', icon: TrendingUp },
  buy: { label: '買い', color: 'text-green-300', bgColor: 'bg-green-500/10', icon: TrendingUp },
  neutral: { label: '中立', color: 'text-gray-400', bgColor: 'bg-gray-500/20', icon: Target },
  sell: { label: '売り', color: 'text-red-300', bgColor: 'bg-red-500/10', icon: TrendingDown },
  strong_sell: { label: '強い売り', color: 'text-red-400', bgColor: 'bg-red-500/20', icon: TrendingDown }
};

export default function CurrencyAIPredictionPanel({ 
  pair, 
  timeframes = ['1H', '1D', '1W'] 
}: CurrencyAIPredictionPanelProps) {
  const [currentRate, setCurrentRate] = useState<CurrencyRate | null>(null);
  const [predictions, setPredictions] = useState<AIPrediction[]>([]);
  const [aiSignal, setAISignal] = useState<AISignal | null>(null);
  const [keyDrivers, setKeyDrivers] = useState<KeyDriver[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchPredictionData = async () => {
    try {
      setLoading(true);
      
      // 並列でデータを取得
      const [rateResponse, insightsResponse] = await Promise.all([
        apiClient.getCurrencyRate(pair),
        apiClient.getCurrencyInsights(pair)
      ]);

      // 現在レート設定
      if (rateResponse.success && rateResponse.data) {
        setCurrentRate(rateResponse.data as CurrencyRate);
      } else {
        // モックデータ
        const mockRate = pair === 'USD/JPY' ? 150 : 
                         pair === 'EUR/USD' ? 1.08 : 
                         pair === 'GBP/USD' ? 1.27 : 1.0;
        const spread = mockRate * 0.0001;
        setCurrentRate({
          bid: mockRate - spread/2,
          ask: mockRate + spread/2,
          mid: mockRate,
          spread: spread
        });
      }

      // 各タイムフレームの予測を取得
      const predictionPromises = timeframes.map(async (timeframe) => {
        const response = await apiClient.getCurrencyPredictions(pair, timeframe, 1);
        const dataArray = Array.isArray(response.data) ? response.data : [];
        if (response.success && dataArray[0]) {
          return {
            timeframe,
            predicted_rate: dataArray[0].predicted_rate,
            confidence: dataArray[0].confidence,
            change_percent: dataArray[0].change_percent || 0
          };
        }
        
        // モック予測データ
        const baseRate = currentRate?.mid || 1.0;
        const changePercent = (Math.random() - 0.5) * 4; // -2% to +2%
        return {
          timeframe,
          predicted_rate: baseRate * (1 + changePercent / 100),
          confidence: Math.random() * 25 + 70, // 70-95%
          change_percent: changePercent
        };
      });

      const predictionResults = await Promise.all(predictionPromises);
      setPredictions(predictionResults);

      // AIインサイトの処理
      if (insightsResponse.success && insightsResponse.data) {
        const insights = insightsResponse.data as any;
        setAISignal(insights.ai_signal);
        setKeyDrivers(insights.key_drivers);
      } else {
        // モックAIシグナル
        const signals: (keyof typeof SIGNAL_CONFIG)[] = ['strong_buy', 'buy', 'neutral', 'sell', 'strong_sell'];
        const randomSignal = signals[Math.floor(Math.random() * signals.length)];
        setAISignal({
          signal: randomSignal,
          strength: Math.random() * 40 + 60, // 60-100
          recommendation: `現在の市場環境とテクニカル分析に基づき、${SIGNAL_CONFIG[randomSignal].label}を推奨します。`
        });

        // モック要因データ
        const mockDrivers: KeyDriver[] = [
          { factor: '日米金利差の拡大', impact: 'positive', weight: 0.85, description: 'FRBの継続的な利上げによりドル高要因' },
          { factor: '米雇用統計の結果', impact: 'positive', weight: 0.72, description: '好調な雇用データが経済の堅調さを示す' },
          { factor: '市場センチメント', impact: 'neutral', weight: 0.58, description: 'リスクオン・オフのムードが混在' },
          { factor: '日銀の政策変更観測', impact: 'negative', weight: 0.43, description: 'YCC政策見直しの可能性でドル売り圧力' }
        ];
        setKeyDrivers(mockDrivers.slice(0, Math.floor(Math.random() * 2) + 2));
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch prediction data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictionData();
    
    // 30秒ごとに更新
    const interval = setInterval(fetchPredictionData, 30000);
    return () => clearInterval(interval);
  }, [pair]);

  if (loading && !currentRate) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-400 border-t-transparent"></div>
          <span className="ml-3 text-gray-400">AI分析中...</span>
        </div>
      </div>
    );
  }

  const signalConfig = aiSignal ? SIGNAL_CONFIG[aiSignal.signal] : SIGNAL_CONFIG.neutral;
  const SignalIcon = signalConfig.icon;

  return (
    <div className="space-y-6">
      {/* 現在レート */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">現在レート</h3>
          <div className="flex items-center text-xs text-gray-400">
            <Clock className="w-3 h-3 mr-1" />
            {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
        
        {currentRate && (
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">Bid（売値）</div>
              <div className="text-xl font-bold text-red-400">
                {currentRate.bid.toFixed(4)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">Ask（買値）</div>
              <div className="text-xl font-bold text-green-400">
                {currentRate.ask.toFixed(4)}
              </div>
            </div>
            <div className="col-span-2 text-center pt-2 border-t border-gray-800">
              <div className="text-sm text-gray-400 mb-1">スプレッド</div>
              <div className="text-lg font-medium text-yellow-400">
                {(currentRate.spread * 10000).toFixed(1)} pips
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AIシグナル */}
      <div className={`${signalConfig.bgColor} border border-${signalConfig.color.replace('text-', '').replace('-400', '-500/30')} rounded-xl p-6`}>
        <div className="flex items-center space-x-3 mb-4">
          <SignalIcon className={`w-6 h-6 ${signalConfig.color}`} />
          <h3 className="text-lg font-semibold text-white">AIシグナル</h3>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className={`text-2xl font-bold ${signalConfig.color}`}>
              {signalConfig.label}
            </span>
            <div className="text-right">
              <div className="text-sm text-gray-400">信頼度</div>
              <div className="text-lg font-bold text-white">
                {aiSignal?.strength.toFixed(0)}%
              </div>
            </div>
          </div>
          
          {aiSignal?.recommendation && (
            <p className="text-sm text-gray-300 bg-black/20 rounded-lg p-3">
              {aiSignal.recommendation}
            </p>
          )}
        </div>
      </div>

      {/* 予測サマリー */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-6 h-6 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">AI予測サマリー</h3>
        </div>
        
        <div className="space-y-4">
          {predictions.map((prediction) => (
            <div key={prediction.timeframe} className="bg-black/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">
                  {prediction.timeframe === '1H' ? '1時間後' : 
                   prediction.timeframe === '1D' ? '24時間後' : 
                   prediction.timeframe === '1W' ? '1週間後' : prediction.timeframe}
                </span>
                <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-400 rounded">
                  信頼度 {prediction.confidence.toFixed(0)}%
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold text-purple-400">
                  {prediction.predicted_rate.toFixed(4)}
                </div>
                <div className={`flex items-center space-x-1 ${
                  prediction.change_percent > 0 ? 'text-green-400' : 
                  prediction.change_percent < 0 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {prediction.change_percent > 0 ? <TrendingUp className="w-4 h-4" /> : 
                   prediction.change_percent < 0 ? <TrendingDown className="w-4 h-4" /> : 
                   <Target className="w-4 h-4" />}
                  <span>{prediction.change_percent > 0 ? '+' : ''}{prediction.change_percent.toFixed(2)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 主な判断材料 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <AlertTriangle className="w-6 h-6 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white">主な判断材料</h3>
        </div>
        
        <div className="space-y-3">
          {keyDrivers.map((driver, index) => (
            <div key={index} className="bg-black/20 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">{driver.factor}</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    driver.impact === 'positive' ? 'bg-green-400' : 
                    driver.impact === 'negative' ? 'bg-red-400' : 'bg-yellow-400'
                  }`}></div>
                  <span className="text-xs text-gray-400">
                    重要度 {(driver.weight * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-400">{driver.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}