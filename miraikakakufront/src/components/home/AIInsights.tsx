'use client';

import { useState, useEffect } from 'react';
import { Brain, Sparkles, Target, TrendingUp, Shield, Zap } from 'lucide-react';
import ThumbnailChart from '../charts/ThumbnailChart';

interface Prediction {
  id: string;
  symbol: string;
  companyName: string;
  prediction: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
  confidence: number;
  targetPrice: number;
  currentPrice: number;
  potentialReturn: number;
  reasoning: string;
}

export default function AIInsights() {
  const [activePrediction, setActivePrediction] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const predictions: Prediction[] = [
    {
      id: '1',
      symbol: '7203',
      companyName: 'トヨタ自動車',
      prediction: 'STRONG_BUY',
      confidence: 92,
      targetPrice: 2850,
      currentPrice: 2543,
      potentialReturn: 12.1,
      reasoning: 'EV市場での競争力強化と堅調な業績予想'
    },
    {
      id: '2',
      symbol: '6861',
      companyName: 'キーエンス',
      prediction: 'BUY',
      confidence: 85,
      targetPrice: 72000,
      currentPrice: 68450,
      potentialReturn: 5.2,
      reasoning: 'FA機器需要の回復と高い利益率維持'
    },
    {
      id: '3',
      symbol: '9984',
      companyName: 'ソフトバンクグループ',
      prediction: 'HOLD',
      confidence: 73,
      targetPrice: 7000,
      currentPrice: 6834,
      potentialReturn: 2.4,
      reasoning: 'AI投資の成長期待とリスクのバランス'
    }
  ];

  const predictionColors = {
    STRONG_BUY: 'from-green-500 to-emerald-500',
    BUY: 'from-green-400 to-green-500',
    HOLD: 'from-yellow-400 to-orange-400',
    SELL: 'from-red-400 to-red-500',
    STRONG_SELL: 'from-red-500 to-red-600'
  };

  const predictionLabels = {
    STRONG_BUY: '強い買い推奨',
    BUY: '買い推奨',
    HOLD: '中立',
    SELL: '売り推奨',
    STRONG_SELL: '強い売り推奨'
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => {
        setActivePrediction((prev) => (prev + 1) % predictions.length);
        setIsAnimating(false);
      }, 300);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const currentPrediction = predictions[activePrediction];

  return (
    <div className="bg-gradient-to-br from-purple-950/20 via-gray-900/50 to-blue-950/20 backdrop-blur-sm rounded-2xl border border-purple-800/30 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <h2 className="text-2xl font-bold text-white">AI予測インサイト</h2>
          <Sparkles className="w-5 h-5 text-yellow-400 animate-pulse" />
        </div>
        <div className="flex items-center space-x-2">
          <Shield className="w-4 h-4 text-green-400" />
          <span className="text-sm text-gray-400">精度: 87.3%</span>
        </div>
      </div>

      {/* Main Prediction Card */}
      <div className={`transition-all duration-300 ${isAnimating ? 'opacity-0 transform scale-95' : 'opacity-100 transform scale-100'}`}>
        <div className="bg-black/40 rounded-xl p-6 border border-gray-800/50 mb-4">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-3xl font-bold text-white">{currentPrediction.symbol}</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${predictionColors[currentPrediction.prediction]} text-white`}>
                  {predictionLabels[currentPrediction.prediction]}
                </span>
              </div>
              <p className="text-gray-300 text-lg">{currentPrediction.companyName}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400 mb-1">信頼度</div>
              <div className="flex items-center space-x-2">
                <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${predictionColors[currentPrediction.prediction]} transition-all duration-500`}
                    style={{ width: `${currentPrediction.confidence}%` }}
                  />
                </div>
                <span className="text-white font-bold">{currentPrediction.confidence}%</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">現在値</div>
              <div className="text-xl font-bold text-white">¥{currentPrediction.currentPrice.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">目標株価</div>
              <div className="text-xl font-bold text-green-400">¥{currentPrediction.targetPrice.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">期待リターン</div>
              <div className="text-xl font-bold text-yellow-400">+{currentPrediction.potentialReturn}%</div>
            </div>
          </div>

          <div className="p-4 bg-gray-800/30 rounded-lg">
            <div className="flex items-center space-x-2 mb-3">
              <Target className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-400">AI分析理由</span>
            </div>
            <p className="text-gray-300 mb-3">{currentPrediction.reasoning}</p>
            
            {/* サムネイルチャート */}
            <div className="mt-3">
              <ThumbnailChart 
                data={{
                  dates: Array.from({length: 7}, (_, i) => `Day ${i + 1}`),
                  actual: Array.from({length: 7}, (_, i) => currentPrediction.currentPrice + Math.sin(i) * 5),
                  lstm: Array.from({length: 7}, (_, i) => currentPrediction.currentPrice + Math.sin(i) * 5 + 2),
                  vertexai: Array.from({length: 7}, (_, i) => currentPrediction.currentPrice + Math.sin(i) * 5 + 1)
                }}
                height={50}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Indicators */}
      <div className="flex justify-center space-x-2">
        {predictions.map((_, index) => (
          <button
            key={index}
            onClick={() => setActivePrediction(index)}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index === activePrediction 
                ? 'w-8 bg-gradient-to-r from-purple-400 to-blue-400' 
                : 'bg-gray-600 hover:bg-gray-500'
            }`}
          />
        ))}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
        <QuickStat icon={<TrendingUp />} label="本日の予測" value="42" color="text-green-400" />
        <QuickStat icon={<Zap />} label="的中率" value="87.3%" color="text-yellow-400" />
        <QuickStat icon={<Target />} label="平均リターン" value="+8.2%" color="text-blue-400" />
        <QuickStat icon={<Shield />} label="リスクレベル" value="低" color="text-purple-400" />
      </div>
    </div>
  );
}

function QuickStat({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <div className="bg-black/30 rounded-lg p-3 border border-gray-800/50">
      <div className="flex items-center space-x-2 mb-1">
        <div className={`w-4 h-4 ${color}`}>{icon}</div>
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <div className={`text-lg font-bold ${color}`}>{value}</div>
    </div>
  );
}