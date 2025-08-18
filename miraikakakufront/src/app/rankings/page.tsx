'use client';

import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Target, Medal } from 'lucide-react';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface GrowthRanking {
  symbol: string;
  company_name: string;
  growth_potential: number;
  mae_score: number;
  accuracy_score: number;
  current_price: number;
  predicted_price_7d: number;
  confidence: number;
}

interface AccuracyRanking {
  symbol: string;
  company_name: string;
  mae_score: number;
  accuracy_score: number;
  predictions_count: number;
  avg_confidence: number;
}

interface CompositeRanking {
  symbol: string;
  company_name: string;
  growth_potential: number;
  accuracy_score: number;
  mae_score: number;
  confidence: number;
  composite_score: number;
  risk_adjusted_score: number;
  current_price: number;
  predicted_price_7d: number;
  score_breakdown: {
    growth_component: number;
    accuracy_component: number;
    confidence_multiplier: number;
  };
}

export default function RankingsPage() {
  const [growthRankings, setGrowthRankings] = useState<GrowthRanking[]>([]);
  const [accuracyRankings, setAccuracyRankings] = useState<AccuracyRanking[]>([]);
  const [compositeRankings, setCompositeRankings] = useState<CompositeRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'growth' | 'accuracy' | 'composite'>('composite');

  useEffect(() => {
    fetchRankings();
  }, []);

  const fetchRankings = async () => {
    setLoading(true);
    try {
      const [growthRes, accuracyRes, compositeRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/rankings/growth-potential`),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/rankings/accuracy`),
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/rankings/composite`)
      ]);

      if (growthRes.ok) {
        const growthData = await growthRes.json();
        setGrowthRankings(growthData);
      }

      if (accuracyRes.ok) {
        const accuracyData = await accuracyRes.json();
        setAccuracyRankings(accuracyData);
      }

      if (compositeRes.ok) {
        const compositeData = await compositeRes.json();
        setCompositeRankings(compositeData);
      }
    } catch (error) {
      console.error('ランキングデータ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Medal className="w-5 h-5 text-yellow-400" />;
    if (index === 1) return <Medal className="w-5 h-5 text-gray-300" />;
    if (index === 2) return <Medal className="w-5 h-5 text-orange-400" />;
    return <span className="w-5 h-5 flex items-center justify-center text-gray-400 font-bold text-sm">{index + 1}</span>;
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <LoadingSpinner type="ai" size="lg" message="ランキングを分析中..." />
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6 flex items-center">
        <Trophy className="w-6 h-6 mr-2 text-yellow-400" />
        銘柄ランキング
      </h1>

      <div className="flex space-x-4 mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveTab('composite')}
          className={`youtube-button px-6 py-2 whitespace-nowrap ${
            activeTab === 'composite' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <Trophy className="w-4 h-4 mr-2" />
          統合ランキング
        </button>
        <button
          onClick={() => setActiveTab('growth')}
          className={`youtube-button px-6 py-2 whitespace-nowrap ${
            activeTab === 'growth' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          上昇予測ランキング
        </button>
        <button
          onClick={() => setActiveTab('accuracy')}
          className={`youtube-button px-6 py-2 whitespace-nowrap ${
            activeTab === 'accuracy' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <Target className="w-4 h-4 mr-2" />
          予測精度ランキング
        </button>
      </div>

      {activeTab === 'growth' && (
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
            7日間上昇予測ランキング
          </h2>
          <div className="space-y-3">
            {growthRankings.map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-all">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="text-white font-semibold">{stock.symbol}</h3>
                    <p className="text-gray-400 text-sm">{stock.company_name}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-green-400 font-bold text-lg">
                    +{stock.growth_potential}%
                  </div>
                  <div className="text-gray-400 text-sm">
                    ${stock.current_price} → ${stock.predicted_price_7d}
                  </div>
                  <div className="text-gray-500 text-xs">
                    精度: {(stock.accuracy_score * 100).toFixed(1)}% | 信頼度: {(stock.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'composite' && (
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Trophy className="w-5 h-5 mr-2 text-yellow-400" />
            統合指標ランキング (成長予測×予測精度)
          </h2>
          <div className="mb-4 p-3 bg-blue-600/20 border border-blue-500/30 rounded-lg">
            <p className="text-blue-300 text-sm">
              <strong>統合スコア計算式:</strong> (成長ポテンシャル 40% + 予測精度 60%) × 信頼度調整
            </p>
          </div>
          <div className="space-y-3">
            {compositeRankings.map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-all">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="text-white font-semibold">{stock.symbol}</h3>
                    <p className="text-gray-400 text-sm">{stock.company_name}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-yellow-400 font-bold text-lg">
                    {(stock.risk_adjusted_score * 100).toFixed(1)}点
                  </div>
                  <div className="text-gray-400 text-sm">
                    成長: +{stock.growth_potential}% | 精度: {(stock.accuracy_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-gray-500 text-xs">
                    基本スコア: {(stock.composite_score * 100).toFixed(1)} | 信頼度: {(stock.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="flex space-x-2 mt-1">
                    <span className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">
                      成長: {(stock.score_breakdown.growth_component * 100).toFixed(1)}
                    </span>
                    <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded">
                      精度: {(stock.score_breakdown.accuracy_component * 100).toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'accuracy' && (
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-blue-400" />
            AI予測精度ランキング (MAE基準)
          </h2>
          <div className="space-y-3">
            {accuracyRankings.map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-4 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-all">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="text-white font-semibold">{stock.symbol}</h3>
                    <p className="text-gray-400 text-sm">{stock.company_name}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-blue-400 font-bold text-lg">
                    {(stock.accuracy_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-gray-400 text-sm">
                    MAE: {(stock.mae_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-gray-500 text-xs">
                    予測数: {stock.predictions_count} | 平均信頼度: {(stock.avg_confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}