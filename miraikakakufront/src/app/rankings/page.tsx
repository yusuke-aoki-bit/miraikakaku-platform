'use client';

import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Target, Medal } from 'lucide-react';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import InvestmentRecommendation from '@/components/investment/InvestmentRecommendation';

interface GrowthRanking {
  symbol: string;
  company_name: string;
  current_price: number;
  predicted_price: number;
  growth_potential: number;
  confidence: number;
}

interface AccuracyRanking {
  symbol: string;
  company_name: string;
  accuracy_score: number;
  prediction_count: number;
}

interface CompositeRanking {
  symbol: string;
  company_name: string;
  composite_score: number;
  accuracy_score: number;
  growth_potential: number;
  prediction_count: number;
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
        setGrowthRankings(Array.isArray(growthData) ? growthData : []);
      }

      if (accuracyRes.ok) {
        const accuracyData = await accuracyRes.json();
        setAccuracyRankings(Array.isArray(accuracyData) ? accuracyData : []);
      }

      if (compositeRes.ok) {
        const compositeData = await compositeRes.json();
        setCompositeRankings(Array.isArray(compositeData) ? compositeData : []);
      }
    } catch (error) {
      console.error('ランキングデータ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Medal className="w-5 h-5 text-icon-green" />;
    if (index === 1) return <Medal className="w-5 h-5 text-base-gray-400" />;
    if (index === 2) return <Medal className="w-5 h-5 text-icon-red" />;
    return <span className="w-5 h-5 flex items-center justify-center text-base-gray-400 font-bold text-sm">{index + 1}</span>;
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <LoadingSpinner type="ai" size="lg" message="ランキングを分析中..." />
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-content">
        <div className="page-header">
          <h1 className="page-title flex items-center">
            <Trophy className="w-6 h-6 mr-2 text-icon-green" />
            銘柄ランキング
          </h1>
        </div>

        <div className="flex space-x-4 mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('composite')}
            className={`${activeTab === 'composite' ? 'btn-primary' : 'btn-secondary'} px-6 py-2 whitespace-nowrap`}
          >
            <Trophy className="w-4 h-4 mr-2" />
            統合ランキング
          </button>
          <button
            onClick={() => setActiveTab('growth')}
            className={`${activeTab === 'growth' ? 'btn-primary' : 'btn-secondary'} px-6 py-2 whitespace-nowrap`}
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            上昇予測ランキング
          </button>
          <button
            onClick={() => setActiveTab('accuracy')}
            className={`${activeTab === 'accuracy' ? 'btn-primary' : 'btn-secondary'} px-6 py-2 whitespace-nowrap`}
          >
            <Target className="w-4 h-4 mr-2" />
            予測精度ランキング
          </button>
        </div>

        {activeTab === 'growth' && (
          <div className="card-primary card-content">
            <h2 className="card-title mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-icon-green" />
            7日間上昇予測ランキング
          </h2>
          <div className="space-y-3">
            {growthRankings.filter(stock => stock && stock.symbol).map((stock, index) => (
              <div key={stock.symbol} className="stock-card grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="stock-symbol">{stock.symbol || 'N/A'}</h3>
                    <p className="stock-name">{stock.company_name || 'N/A'}</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <InvestmentRecommendation 
                    symbol={stock.symbol} 
                    currentPrice={stock.current_price || 100}
                    showDetailed={false}
                  />
                </div>
                
                <div className="text-right flex flex-col justify-center">
                  <div className="text-icon-green font-bold text-lg">
                    +{(stock.growth_potential || 0).toFixed(2)}%
                  </div>
                  <div className="text-base-gray-400 text-sm">
                    ${(stock.current_price || 0).toFixed(2)} → ${(stock.predicted_price || 0).toFixed(2)}
                  </div>
                  <div className="text-base-gray-500 text-xs">
                    信頼度: {((stock.confidence || 0) * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'composite' && (
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-text-white mb-4 flex items-center">
            <Trophy className="w-5 h-5 mr-2 text-icon-green" />
            統合指標ランキング (成長予測×予測精度)
          </h2>
          <div className="mb-4 p-3 bg-base-blue-600/20 border border-base-blue-500/30 rounded-lg">
            <p className="text-base-blue-400 text-sm">
              <strong>統合スコア計算式:</strong> (成長ポテンシャル 40% + 予測精度 60%) × 信頼度調整
            </p>
          </div>
          <div className="space-y-3">
            {compositeRankings.filter(stock => stock && stock.symbol).map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-4 rounded-lg bg-base-gray-800/30 hover:bg-base-gray-800/50 transition-all">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="stock-symbol">{stock.symbol || 'N/A'}</h3>
                    <p className="stock-name">{stock.company_name || 'N/A'}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-icon-green font-bold text-lg">
                    {(stock.composite_score || 0).toFixed(1)}点
                  </div>
                  <div className="text-base-gray-400 text-sm">
                    成長: +{(stock.growth_potential || 0).toFixed(2)}% | 精度: {(stock.accuracy_score || 0).toFixed(1)}%
                  </div>
                  <div className="text-base-gray-500 text-xs">
                    予測数: {stock.prediction_count || 0}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'accuracy' && (
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-text-white mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-base-blue-500" />
            AI予測精度ランキング (MAE基準)
          </h2>
          <div className="space-y-3">
            {accuracyRankings.filter(stock => stock && stock.symbol).map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-4 rounded-lg bg-base-gray-800/30 hover:bg-base-gray-800/50 transition-all">
                <div className="flex items-center space-x-4">
                  {getRankIcon(index)}
                  <div>
                    <h3 className="stock-symbol">{stock.symbol || 'N/A'}</h3>
                    <p className="stock-name">{stock.company_name || 'N/A'}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-base-blue-500 font-bold text-lg">
                    {(stock.accuracy_score || 0).toFixed(1)}%
                  </div>
                  <div className="text-base-gray-500 text-xs">
                    予測数: {stock.prediction_count || 0}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        )}
      </div>
    </div>
  );
}