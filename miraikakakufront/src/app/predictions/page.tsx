'use client';

import React, { useState, useEffect } from 'react';
import { Brain, Target, TrendingUp, TrendingDown, Star, Filter, Calendar, Zap } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import AdSenseUnit from '@/components/ads/AdSenseUnit';
import { apiClient } from '@/lib/api-client';

interface PredictionData {
  id: string;
  symbol: string;
  company_name: string;
  current_price: number;
  predicted_price: number;
  change_percent: number;
  confidence_score: number;
  time_horizon: '24h' | '1w' | '1m';
  prediction_date: string;
  model_used: string;
  risk_level: 'low' | 'medium' | 'high';
}

interface PredictionCategory {
  id: string;
  label: string;
  description: string;
  filter_params: {
    direction?: 'up' | 'down';
    time_horizon?: string;
    min_confidence?: number;
    min_change?: number;
    max_risk?: string;
  };
}

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string>('24h_up');
  const [filteredPredictions, setFilteredPredictions] = useState<PredictionData[]>([]);

  const categories: PredictionCategory[] = [
    {
      id: '24h_up',
      label: '24時間後の上昇予測',
      description: '短期的な価格上昇が期待される銘柄',
      filter_params: { direction: 'up', time_horizon: '24h', min_confidence: 70 }
    },
    {
      id: '1w_up',
      label: '1週間後の上昇予測',
      description: '中期的な成長ポテンシャルのある銘柄',
      filter_params: { direction: 'up', time_horizon: '1w', min_confidence: 65 }
    },
    {
      id: 'high_confidence',
      label: '高信頼度予測',
      description: '信頼度90%以上の確実性の高い予測',
      filter_params: { min_confidence: 90 }
    },
    {
      id: 'high_return',
      label: '高リターン期待',
      description: '10%以上の価格変動が予測される銘柄',
      filter_params: { min_change: 10 }
    },
    {
      id: 'low_risk',
      label: 'ローリスク予測',
      description: 'リスクが低く安定的な投資機会',
      filter_params: { max_risk: 'low', min_confidence: 75 }
    }
  ];

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getAIPredictions({
          category: activeCategory,
          limit: 30
        });

        if (response.success && response.data) {
          setPredictions(response.data);
        }
      } catch (error) {
        console.error('Error fetching predictions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, [activeCategory]);

  useEffect(() => {
    const category = categories.find(c => c.id === activeCategory);
    if (!category) {
      setFilteredPredictions(predictions);
      return;
    }

    let filtered = predictions;

    // Apply filters based on category
    const params = category.filter_params;
    
    if (params.direction) {
      filtered = filtered.filter(p => 
        params.direction === 'up' ? p.change_percent > 0 : p.change_percent < 0
      );
    }

    if (params.time_horizon) {
      filtered = filtered.filter(p => p.time_horizon === params.time_horizon);
    }

    if (params.min_confidence !== undefined) {
      filtered = filtered.filter(p => p.confidence_score >= params.min_confidence!);
    }

    if (params.min_change !== undefined) {
      filtered = filtered.filter(p => Math.abs(p.change_percent) >= params.min_change!);
    }

    if (params.max_risk) {
      filtered = filtered.filter(p => p.risk_level === params.max_risk);
    }

    setFilteredPredictions(filtered);
  }, [predictions, activeCategory, categories]);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-500/20';
      case 'high': return 'text-red-400 bg-red-500/20';
      default: return 'text-yellow-400 bg-yellow-500/20';
    }
  };

  const getChangeColor = (change: number) => {
    return change > 0 ? 'text-green-400' : 'text-red-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-8"></div>
            <div className="flex space-x-4 mb-8">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-12 bg-gray-800 rounded w-32"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 9 }).map((_, i) => (
                <div key={i} className="h-48 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white flex items-center mb-2">
            <Brain className="w-8 h-8 mr-3 text-blue-400" />
            AI予測ピックアップ
          </h1>
          <p className="text-gray-400">
            AIが生成した投資機会を様々な観点から発見できます
          </p>
        </motion.div>

        {/* Category Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeCategory === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50 hover:text-white'
                }`}
              >
                {category.label}
              </button>
            ))}
          </div>
          
          {/* Active category description */}
          <div className="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <div className="flex items-center">
              <Target className="w-5 h-5 text-blue-400 mr-2" />
              <p className="text-gray-300">
                {categories.find(c => c.id === activeCategory)?.description}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Prediction Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPredictions.map((prediction, index) => (
            <motion.div
              key={prediction.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.05 }}
            >
              <PredictionCard prediction={prediction} />
              
              {/* AdSense Unit - Insert ads every 6 cards */}
              {(index + 1) % 6 === 0 && (
                <div className="mt-6">
                  <AdSenseUnit
                    adSlot="1234567897"
                    responsive={true}
                    adStyle="in-feed"
                    className="w-full"
                  />
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredPredictions.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <Brain className="w-24 h-24 text-gray-600 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-gray-400 mb-3">
              予測データがありません
            </h3>
            <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
              選択したカテゴリの予測データが見つかりません。<br />
              他のカテゴリをお試しください。
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}

// Component: PredictionCard - 予測カード
function PredictionCard({ prediction }: { prediction: PredictionData }) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'high': return 'text-red-400 bg-red-500/20 border-red-500/30';
      default: return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    }
  };

  const getChangeColor = (change: number) => {
    return change > 0 ? 'text-green-400' : 'text-red-400';
  };

  const getTimeHorizonLabel = (horizon: string) => {
    switch (horizon) {
      case '24h': return '24時間';
      case '1w': return '1週間';
      case '1m': return '1ヶ月';
      default: return horizon;
    }
  };

  return (
    <Link
      href={`/stock/${prediction.symbol}`}
      className="block bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:bg-gray-800/50 transition-all hover:border-gray-700 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">
            {prediction.symbol}
          </h3>
          <p className="text-sm text-gray-400">{prediction.company_name}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs rounded border ${getRiskColor(prediction.risk_level)}`}>
            {prediction.risk_level === 'low' ? 'ローリスク' :
             prediction.risk_level === 'high' ? 'ハイリスク' : 'ミドルリスク'}
          </span>
        </div>
      </div>

      {/* Price Info */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-400">現在価格</span>
          <span className="text-white font-semibold">
            ¥{prediction.current_price.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">予測価格</span>
          <span className="text-white font-semibold">
            ¥{prediction.predicted_price.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400">期待変動</span>
          <div className={`flex items-center font-semibold ${getChangeColor(prediction.change_percent)}`}>
            {prediction.change_percent > 0 ? (
              <TrendingUp className="w-4 h-4 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 mr-1" />
            )}
            {prediction.change_percent > 0 ? '+' : ''}{prediction.change_percent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Confidence and Time */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Target className="w-4 h-4 text-blue-400 mr-1" />
          <span className="text-sm text-gray-400">信頼度</span>
          <span className="text-sm text-white font-medium ml-1">
            {prediction.confidence_score}%
          </span>
        </div>
        <div className="flex items-center">
          <Calendar className="w-4 h-4 text-purple-400 mr-1" />
          <span className="text-sm text-gray-400">
            {getTimeHorizonLabel(prediction.time_horizon)}
          </span>
        </div>
      </div>

      {/* Model and Date */}
      <div className="pt-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
        <span>モデル: {prediction.model_used}</span>
        <span>{new Date(prediction.prediction_date).toLocaleDateString('ja-JP')}</span>
      </div>

      {/* Confidence Bar */}
      <div className="mt-3">
        <div className="w-full bg-gray-800 rounded-full h-1">
          <div 
            className="bg-blue-500 h-1 rounded-full transition-all duration-300" 
            style={{ width: `${prediction.confidence_score}%` }}
          />
        </div>
      </div>
    </Link>
  );
}