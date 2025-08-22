'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Target, DollarSign, Brain, Star } from 'lucide-react';
import ThumbnailChart from '../charts/ThumbnailChart';
import { INVESTMENT_CONFIG, CHART_CONFIG } from '../../config/constants';

interface PredictionAccuracy {
  model: 'LSTM' | 'VertexAI';
  accuracy: number;
  mae: number;
  profitability: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  recommendation: 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell';
  targetPrice: number;
  stopLoss: number;
  expectedReturn: number;
}

interface InvestmentRecommendationProps {
  symbol: string;
  currentPrice: number;
  showDetailed?: boolean;
}

// モック推奨データ生成
const generateRecommendation = (symbol: string, currentPrice: number): {
  models: PredictionAccuracy[];
  chartData: any;
  overallRating: number;
} => {
  const lstmAccuracy = INVESTMENT_CONFIG.LSTM_ACCURACY.BASE + Math.random() * INVESTMENT_CONFIG.LSTM_ACCURACY.VARIANCE;
  const vertexAccuracy = INVESTMENT_CONFIG.VERTEX_ACCURACY.BASE + Math.random() * INVESTMENT_CONFIG.VERTEX_ACCURACY.VARIANCE;
  
  const models: PredictionAccuracy[] = [
    {
      model: 'LSTM',
      accuracy: lstmAccuracy,
      mae: CHART_CONFIG.MAE_BASE.LSTM + Math.random() * CHART_CONFIG.MAE_VARIANCE.LSTM,
      profitability: lstmAccuracy * INVESTMENT_CONFIG.PROFITABILITY_MULTIPLIER.LSTM,
      riskLevel: lstmAccuracy > INVESTMENT_CONFIG.RISK_LEVELS.LOW_THRESHOLD ? 'Low' : lstmAccuracy > INVESTMENT_CONFIG.RISK_LEVELS.MEDIUM_THRESHOLD ? 'Medium' : 'High',
      recommendation: lstmAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.STRONG_BUY ? 'Strong Buy' : lstmAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.BUY ? 'Buy' : lstmAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.HOLD ? 'Hold' : 'Sell',
      targetPrice: currentPrice * (1 + (Math.random() * INVESTMENT_CONFIG.PRICE_VARIANCE.MAX_POSITIVE + INVESTMENT_CONFIG.PRICE_VARIANCE.MIN_NEGATIVE)),
      stopLoss: currentPrice * (INVESTMENT_CONFIG.PRICE_VARIANCE.STOP_LOSS_BASE - Math.random() * INVESTMENT_CONFIG.PRICE_VARIANCE.STOP_LOSS_VARIANCE),
      expectedReturn: (lstmAccuracy / 100) * INVESTMENT_CONFIG.EXPECTED_RETURN.LSTM
    },
    {
      model: 'VertexAI',
      accuracy: vertexAccuracy,
      mae: CHART_CONFIG.MAE_BASE.VERTEX + Math.random() * CHART_CONFIG.MAE_VARIANCE.VERTEX,
      profitability: vertexAccuracy * INVESTMENT_CONFIG.PROFITABILITY_MULTIPLIER.VERTEX,
      riskLevel: vertexAccuracy > INVESTMENT_CONFIG.RISK_LEVELS.LOW_THRESHOLD ? 'Low' : vertexAccuracy > INVESTMENT_CONFIG.RISK_LEVELS.MEDIUM_THRESHOLD ? 'Medium' : 'High',
      recommendation: vertexAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.STRONG_BUY ? 'Strong Buy' : vertexAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.BUY ? 'Buy' : vertexAccuracy > INVESTMENT_CONFIG.RECOMMENDATION_THRESHOLDS.HOLD ? 'Hold' : 'Sell',
      targetPrice: currentPrice * (1 + (Math.random() * INVESTMENT_CONFIG.PRICE_VARIANCE.MAX_POSITIVE + INVESTMENT_CONFIG.PRICE_VARIANCE.MIN_NEGATIVE)),
      stopLoss: currentPrice * (INVESTMENT_CONFIG.PRICE_VARIANCE.STOP_LOSS_BASE - Math.random() * INVESTMENT_CONFIG.PRICE_VARIANCE.STOP_LOSS_VARIANCE),
      expectedReturn: (vertexAccuracy / 100) * INVESTMENT_CONFIG.EXPECTED_RETURN.VERTEX
    }
  ];

  // チャート用データ
  const dates = Array.from({length: CHART_CONFIG.CHART_DATA_POINTS}, (_, i) => `Day ${i + 1}`);
  const actual = Array.from({length: CHART_CONFIG.CHART_DATA_POINTS}, (_, i) => 
    currentPrice + Math.sin(i/CHART_CONFIG.CHART_SIN_FREQUENCY) * CHART_CONFIG.CHART_SIN_AMPLITUDE + (Math.random() - 0.5) * CHART_CONFIG.CHART_NOISE_RANGE
  );
  const lstm = actual.map(price => price + (Math.random() - 0.5) * CHART_CONFIG.LSTM_PREDICTION_VARIANCE);
  const vertexai = actual.map(price => price + (Math.random() - 0.5) * CHART_CONFIG.VERTEX_PREDICTION_VARIANCE);

  const chartData = { dates, actual, lstm, vertexai };
  const overallRating = (lstmAccuracy + vertexAccuracy) / 2;

  return { models, chartData, overallRating };
};

export default function InvestmentRecommendation({ 
  symbol, 
  currentPrice, 
  showDetailed = true 
}: InvestmentRecommendationProps) {
  const [recommendation, setRecommendation] = useState<{
    models: PredictionAccuracy[];
    chartData: any;
    overallRating: number;
  } | null>(null);

  useEffect(() => {
    const data = generateRecommendation(symbol, currentPrice);
    setRecommendation(data);
  }, [symbol, currentPrice]);

  if (!recommendation) return null;

  const bestModel = recommendation.models.reduce((best, current) => 
    current.accuracy > best.accuracy ? current : best
  );

  const getRatingColor = (rating: number) => {
    if (rating >= CHART_CONFIG.RATING_THRESHOLDS.EXCELLENT) return 'text-green-400 bg-green-400/10 border-green-400/30';
    if (rating >= CHART_CONFIG.RATING_THRESHOLDS.GOOD) return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
    return 'text-red-400 bg-red-400/10 border-red-400/30';
  };

  const getRecommendationIcon = (rec: string) => {
    switch (rec) {
      case 'Strong Buy': return <TrendingUp className="w-5 h-5 text-green-400" />;
      case 'Buy': return <TrendingUp className="w-5 h-5 text-blue-400" />;
      case 'Hold': return <Target className="w-5 h-5 text-yellow-400" />;
      case 'Sell': return <TrendingDown className="w-5 h-5 text-orange-400" />;
      case 'Strong Sell': return <TrendingDown className="w-5 h-5 text-red-400" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-400" />;
    }
  };

  if (!showDetailed) {
    // コンパクト表示（ランキングなどで使用）
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-white font-semibold">{symbol}</span>
            <div className={`px-2 py-1 rounded-full text-xs border ${getRatingColor(recommendation.overallRating)}`}>
              {recommendation.overallRating.toFixed(0)}%
            </div>
          </div>
          {getRecommendationIcon(bestModel.recommendation)}
        </div>
        
        <div className="mb-2">
          <ThumbnailChart data={recommendation.chartData} height={CHART_CONFIG.CHART_HEIGHT.THUMBNAIL} />
        </div>
        
        <div className="text-xs text-gray-400 flex justify-between">
          <span>期待: +{bestModel.expectedReturn.toFixed(1)}%</span>
          <span>{bestModel.model}</span>
        </div>
      </div>
    );
  }

  // 詳細表示
  return (
    <div className="space-y-6">
      {/* 総合評価 */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <div>
              <h2 className="text-2xl font-bold text-white">AI投資スコア</h2>
              <p className="text-gray-400">複数モデルによる総合判定</p>
            </div>
          </div>
          <div className={`text-4xl font-bold ${getRatingColor(recommendation.overallRating).split(' ')[0]}`}>
            {recommendation.overallRating.toFixed(0)}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-black/30 rounded-lg">
            <div className="text-2xl font-bold text-white mb-1">
              ¥{bestModel.targetPrice.toLocaleString()}
            </div>
            <div className="text-gray-400 text-sm">目標株価</div>
            <div className="text-green-400 text-sm">
              +{((bestModel.targetPrice - currentPrice) / currentPrice * 100).toFixed(1)}%
            </div>
          </div>
          
          <div className="text-center p-4 bg-black/30 rounded-lg">
            <div className="text-2xl font-bold text-green-400 mb-1">
              +{bestModel.expectedReturn.toFixed(1)}%
            </div>
            <div className="text-gray-400 text-sm">期待リターン</div>
            <div className="text-gray-500 text-xs">30日予測</div>
          </div>
          
          <div className="text-center p-4 bg-black/30 rounded-lg">
            <div className="text-2xl font-bold text-red-400 mb-1">
              ¥{bestModel.stopLoss.toLocaleString()}
            </div>
            <div className="text-gray-400 text-sm">ストップロス</div>
            <div className="text-red-400 text-sm">
              -{((currentPrice - bestModel.stopLoss) / currentPrice * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* モデル比較 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {recommendation.models.map((model, index) => (
          <div key={model.model} 
               className={`border rounded-xl p-6 ${
                 model === bestModel 
                   ? 'border-yellow-500/30 bg-yellow-900/10' 
                   : 'border-gray-800/50 bg-gray-900/50'
               }`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Brain className={`w-6 h-6 ${model === bestModel ? 'text-yellow-400' : 'text-blue-400'}`} />
                <h3 className="text-xl font-bold text-white">{model.model}</h3>
                {model === bestModel && <Star className="w-5 h-5 text-yellow-400 fill-current" />}
              </div>
              <div className={`px-3 py-1 rounded-full border ${getRatingColor(model.accuracy)}`}>
                {model.accuracy.toFixed(1)}%
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-gray-400 text-sm">推奨</div>
                <div className="flex items-center space-x-2">
                  {getRecommendationIcon(model.recommendation)}
                  <span className="text-white font-semibold">{model.recommendation}</span>
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">リスク</div>
                <span className={`font-semibold ${
                  model.riskLevel === 'Low' ? 'text-green-400' : 
                  model.riskLevel === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {model.riskLevel}
                </span>
              </div>
              <div>
                <div className="text-gray-400 text-sm">MAS誤差</div>
                <div className="text-white font-semibold">{model.mae.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">収益性</div>
                <div className="text-green-400 font-semibold">{model.profitability.toFixed(1)}%</div>
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex space-x-2">
              <button className={`flex-1 py-2 px-4 rounded-lg border transition-all ${
                model.recommendation.includes('Buy') 
                  ? 'bg-green-500/20 border-green-500/30 text-green-400 hover:bg-green-500/30'
                  : model.recommendation === 'Hold'
                  ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/30'
                  : 'bg-red-500/20 border-red-500/30 text-red-400 hover:bg-red-500/30'
              }`}>
                <DollarSign className="w-4 h-4 inline mr-2" />
                {model.recommendation}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* リアルタイム予測チャート */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">予測精度比較（過去30日）</h3>
        <div className="h-48">
          <ThumbnailChart data={recommendation.chartData} height={CHART_CONFIG.CHART_HEIGHT.SMALL} />
        </div>
        <div className="flex justify-center space-x-6 mt-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-400">実績価格</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span className="text-gray-400">LSTM予測</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-purple-500"></div>
            <span className="text-gray-400">VertexAI予測</span>
          </div>
        </div>
      </div>
    </div>
  );
}