'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Brain, TrendingUp, BarChart3, DollarSign, Target, Settings, BookOpen } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import { apiClient } from '@/lib/api-client';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: 'buy' | 'sell' | 'hold';
  description: string;
  period?: number;
}

interface FundamentalData {
  metric: string;
  current: number;
  previous: number;
  industry_avg: number;
  year_1: number;
  year_2: number;
  year_3: number;
  year_4: number;
  year_5: number;
}

interface AIDecisionFactor {
  factor: string;
  impact_percentage: number;
  category: 'technical' | 'fundamental' | 'sentiment' | 'external';
  description: string;
}

interface AnalysisData {
  symbol: string;
  company_name: string;
  current_price: number;
  technical_indicators: TechnicalIndicator[];
  fundamental_data: FundamentalData[];
  ai_decision_factors: AIDecisionFactor[];
  overall_recommendation: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  confidence_score: number;
}

export default function AIAnalysisPage() {
  const params = useParams();
  const symbol = params?.symbol as string;
  
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<'technical' | 'fundamental' | 'ai'>('technical');
  const [technicalSettings, setTechnicalSettings] = useState({
    rsi_period: 14,
    macd_fast: 12,
    macd_slow: 26,
    bb_period: 20
  });

  useEffect(() => {
    const fetchAnalysisData = async () => {
      if (!symbol) return;
      
      try {
        setLoading(true);
        
        // Fetch comprehensive analysis data
        const analysisResponse = await apiClient.getDetailedAnalysis(symbol);

        if (analysisResponse.success && analysisResponse.data) {
          setAnalysisData(analysisResponse.data as AnalysisData);
        }
      } catch (error) {
        console.error('Error fetching analysis data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, [symbol, technicalSettings]);

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'strong_buy': return 'text-green-500 bg-green-500/20 border-green-500/30';
      case 'buy': return 'text-green-400 bg-green-400/20 border-green-400/30';
      case 'hold': return 'text-yellow-400 bg-yellow-400/20 border-yellow-400/30';
      case 'sell': return 'text-red-400 bg-red-400/20 border-red-400/30';
      case 'strong_sell': return 'text-red-500 bg-red-500/20 border-red-500/30';
      default: return 'text-gray-400 bg-gray-400/20 border-gray-400/30';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy': return 'text-green-400';
      case 'sell': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-8"></div>
            <div className="h-32 bg-gray-800 rounded mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-6">
                <div className="h-96 bg-gray-800 rounded"></div>
                <div className="h-96 bg-gray-800 rounded"></div>
              </div>
              <div className="space-y-6">
                <div className="h-64 bg-gray-800 rounded"></div>
                <div className="h-96 bg-gray-800 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-950 p-6 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">分析データが見つかりません</h1>
          <p className="text-gray-400 mb-4">銘柄コード: {symbol}</p>
          <Link
            href="/"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            ホームに戻る
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-4 mb-4">
            <Link 
              href={`/stock/${symbol}`}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              aria-label="株式詳細に戻る"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center">
                <Brain className="w-8 h-8 mr-3 text-blue-400" />
                {analysisData.company_name} - AI詳細分析
              </h1>
              <div className="flex items-center space-x-4 mt-2">
                <p className="text-gray-400">{analysisData.symbol}</p>
                <p className="text-xl text-white font-semibold">
                  ¥{analysisData.current_price.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          {/* Overall Recommendation */}
          <div className={`inline-flex items-center px-6 py-3 border rounded-lg ${getRecommendationColor(analysisData.overall_recommendation)}`}>
            <Target className="w-5 h-5 mr-2" />
            <span className="font-semibold mr-2">
              総合判定: {
                analysisData.overall_recommendation === 'strong_buy' ? '強い買い' :
                analysisData.overall_recommendation === 'buy' ? '買い' :
                analysisData.overall_recommendation === 'hold' ? 'ホールド' :
                analysisData.overall_recommendation === 'sell' ? '売り' :
                '強い売り'
              }
            </span>
            <span className="text-sm">
              信頼度: {analysisData.confidence_score}%
            </span>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content (3/4) */}
          <div className="lg:col-span-3 space-y-8">
            {/* Section Navigation */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex border-b border-gray-800 mb-6">
                {[
                  { key: 'technical', label: 'テクニカル分析', icon: BarChart3 },
                  { key: 'fundamental', label: 'ファンダメンタルズ分析', icon: DollarSign },
                  { key: 'ai', label: 'AI決定要因', icon: Brain }
                ].map(({ key, label, icon: Icon }) => (
                  <button
                    key={key}
                    onClick={() => setActiveSection(key as any)}
                    className={`flex items-center px-6 py-3 border-b-2 font-medium transition-colors ${
                      activeSection === key
                        ? 'border-blue-400 text-blue-400'
                        : 'border-transparent text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {label}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Technical Analysis Section */}
            {activeSection === 'technical' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-white">テクニカル指標</h2>
                    <button className="flex items-center px-3 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors">
                      <Settings className="w-4 h-4 mr-1" />
                      設定
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {analysisData.technical_indicators.map((indicator, index) => (
                      <div key={index} className="bg-gray-800/30 border border-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-semibold text-white">{indicator.name}</h3>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getSignalColor(indicator.signal)} bg-current/10`}>
                            {indicator.signal === 'buy' ? '買い' : indicator.signal === 'sell' ? '売り' : 'ホールド'}
                          </span>
                        </div>
                        <div className="space-y-2">
                          <div className="text-2xl font-bold text-white">
                            {indicator.value.toFixed(2)}
                            {indicator.period && <span className="text-sm text-gray-400 ml-1">({indicator.period}日)</span>}
                          </div>
                          <p className="text-sm text-gray-400">{indicator.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Interactive Charts Placeholder */}
                <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">インタラクティブチャート</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {['RSI', 'MACD', 'ボリンジャーバンド', '移動平均線'].map((chartType) => (
                      <div key={chartType} className="h-64 bg-gray-800/50 rounded-lg flex items-center justify-center">
                        <div className="text-center text-gray-400">
                          <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                          <p>{chartType}チャート</p>
                          <p className="text-sm">（実装予定）</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Fundamental Analysis Section */}
            {activeSection === 'fundamental' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
              >
                <h2 className="text-xl font-bold text-white mb-6">ファンダメンタルズ分析</h2>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-800">
                        <th className="text-left py-3 px-4 font-medium text-gray-400">指標</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">現在値</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">前期</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">業界平均</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">5年前</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">4年前</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">3年前</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">2年前</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-400">1年前</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisData.fundamental_data.map((data, index) => (
                        <tr key={index} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                          <td className="py-3 px-4 font-medium text-white">{data.metric}</td>
                          <td className="py-3 px-4 text-right font-semibold text-blue-400">
                            {data.current.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-300">
                            {data.previous.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-400">
                            {data.industry_avg.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">
                            {data.year_5.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">
                            {data.year_4.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">
                            {data.year_3.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">
                            {data.year_2.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-400">
                            {data.year_1.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {/* AI Decision Factors Section */}
            {activeSection === 'ai' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
              >
                <h2 className="text-xl font-bold text-white mb-6">AI決定要因</h2>
                <p className="text-gray-400 mb-6">
                  AIが「{analysisData.overall_recommendation === 'buy' || analysisData.overall_recommendation === 'strong_buy' ? '買い' : 
                  analysisData.overall_recommendation === 'sell' || analysisData.overall_recommendation === 'strong_sell' ? '売り' : 'ホールド'}」
                  と判断した根拠を影響度の高い順に表示しています。
                </p>
                
                <div className="space-y-4">
                  {analysisData.ai_decision_factors
                    .sort((a, b) => b.impact_percentage - a.impact_percentage)
                    .map((factor, index) => (
                      <div key={index} className="bg-gray-800/30 border border-gray-700 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center mb-2">
                              <h3 className="font-semibold text-white mr-3">{factor.factor}</h3>
                              <span className={`px-2 py-1 text-xs rounded ${
                                factor.category === 'technical' ? 'bg-blue-500/20 text-blue-400' :
                                factor.category === 'fundamental' ? 'bg-green-500/20 text-green-400' :
                                factor.category === 'sentiment' ? 'bg-purple-500/20 text-purple-400' :
                                'bg-orange-500/20 text-orange-400'
                              }`}>
                                {factor.category === 'technical' ? 'テクニカル' :
                                 factor.category === 'fundamental' ? 'ファンダメンタルズ' :
                                 factor.category === 'sentiment' ? 'センチメント' :
                                 '外部要因'}
                              </span>
                            </div>
                            <p className="text-sm text-gray-400">{factor.description}</p>
                          </div>
                          <div className="text-right ml-4">
                            <div className="text-2xl font-bold text-white">
                              {factor.impact_percentage.toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-400">影響度</div>
                          </div>
                        </div>
                        
                        {/* Impact Bar */}
                        <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${factor.impact_percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Sidebar (1/4) */}
          <div className="space-y-6">
            {/* AdSense Unit */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <AdSenseUnit
                adSlot="1234567894"
                className="w-full"
                style={{ minHeight: '600px' }}
              />
            </motion.div>

            {/* Amazon Product Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center mb-4">
                  <BookOpen className="w-5 h-5 mr-2 text-blue-400" />
                  <h3 className="text-lg font-semibold text-white">専門書籍</h3>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <BookOpen className="w-6 h-6 text-blue-600 mr-2" />
                    <h3 className="text-xl font-semibold text-gray-800">
                      テクニカル・ファンダメンタルズ分析
                    </h3>
                  </div>
                  <p className="text-gray-600 mb-4">投資分析のスキルアップに</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {amazonRecommendations.analysis.products.slice(0, 2).map((product) => (
                      <AmazonProductCard
                        key={product.id}
                        product={product}
                        compact={true}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Quick Analysis Summary */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
            >
              <h3 className="text-lg font-bold text-white mb-4">分析サマリー</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">テクニカル評価</span>
                  <span className="text-green-400 font-medium">
                    {analysisData.technical_indicators.filter(i => i.signal === 'buy').length > 
                     analysisData.technical_indicators.filter(i => i.signal === 'sell').length ? '強気' : '弱気'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">バリュエーション</span>
                  <span className="text-blue-400 font-medium">適正</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">センチメント</span>
                  <span className="text-yellow-400 font-medium">中立</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">総合信頼度</span>
                  <span className="text-white font-semibold">{analysisData.confidence_score}%</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}