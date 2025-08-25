'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Newspaper, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  ExternalLink,
  Clock,
  Eye,
  Lightbulb,
  Target,
  ChevronRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ThemeDetail {
  id: string;
  name: string;
  description: string;
  overview: string;
  detailed_description: string;
  category: string;
  stock_count: number;
  performance_1m: number;
  performance_3m: number;
  performance_1y: number;
  is_featured: boolean;
  is_trending: boolean;
  background_image?: string;
  follow_count: number;
  market_cap_total: number;
  top_stocks: string[];
  risk_level: 'Low' | 'Medium' | 'High';
  growth_stage: 'Early' | 'Growth' | 'Mature';
  created_at: string;
  updated_at: string;
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  relevance_score: number;
  sentiment: 'positive' | 'negative' | 'neutral';
}

interface AIInsight {
  id: string;
  insight_type: 'opportunity' | 'risk' | 'trend' | 'prediction';
  title: string;
  description: string;
  confidence: number;
  impact_level: 'high' | 'medium' | 'low';
  time_horizon: 'short' | 'medium' | 'long';
  created_at: string;
}

interface ThemeInsightsPanelProps {
  theme: ThemeDetail;
}

export default function ThemeInsightsPanel({ theme }: ThemeInsightsPanelProps) {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [aiInsights, setAIInsights] = useState<AIInsight[]>([]);
  const [loadingNews, setLoadingNews] = useState(true);
  const [loadingInsights, setLoadingInsights] = useState(true);
  const [activeTab, setActiveTab] = useState<'news' | 'insights'>('insights');

  useEffect(() => {
    fetchThemeNews();
    fetchAIInsights();
  }, [theme.id]);

  const fetchThemeNews = async () => {
    try {
      setLoadingNews(true);
      const response = await apiClient.getThemeNews(theme.id);
      
      if (response.status === 'success' && response.data) {
        setNews(response.data);
      } else {
        // Generate mock news data
        generateMockNews();
      }
    } catch (error) {
      console.error('Failed to fetch theme news:', error);
      generateMockNews();
    } finally {
      setLoadingNews(false);
    }
  };

  const fetchAIInsights = async () => {
    try {
      setLoadingInsights(true);
      const response = await apiClient.getThemeAIInsights(theme.id);
      
      if (response.status === 'success' && response.data) {
        setAIInsights(response.data);
      } else {
        // Generate mock AI insights
        generateMockInsights();
      }
    } catch (error) {
      console.error('Failed to fetch AI insights:', error);
      generateMockInsights();
    } finally {
      setLoadingInsights(false);
    }
  };

  const generateMockNews = () => {
    const mockNews: NewsItem[] = [
      {
        id: '1',
        title: 'AI半導体需要が過去最高を記録、NVIDIA決算で明らかに',
        summary: 'NVIDIA社の最新決算によると、データセンター向けAI半導体の需要が前年同期比300%増となり、市場予想を大幅に上回った。',
        url: 'https://example.com/news/1',
        source: '日経新聞',
        published_at: '2024-02-20T09:30:00Z',
        relevance_score: 95,
        sentiment: 'positive'
      },
      {
        id: '2',
        title: '次世代3nmプロセス技術の量産開始、TSMC発表',
        summary: 'Taiwan Semiconductorが次世代3nmプロセス技術の量産を開始。AI処理性能の大幅向上が期待される。',
        url: 'https://example.com/news/2',
        source: 'TechCrunch',
        published_at: '2024-02-19T14:15:00Z',
        relevance_score: 88,
        sentiment: 'positive'
      },
      {
        id: '3',
        title: '半導体製造装置の受注残高が過去最高水準に',
        summary: '世界的な半導体需要増加により、製造装置メーカーの受注残高が過去最高を更新。長期的な成長トレンドを示唆。',
        url: 'https://example.com/news/3',
        source: 'Reuters',
        published_at: '2024-02-18T11:20:00Z',
        relevance_score: 82,
        sentiment: 'positive'
      }
    ];
    setNews(mockNews);
  };

  const generateMockInsights = () => {
    const mockInsights: AIInsight[] = [
      {
        id: '1',
        insight_type: 'opportunity',
        title: 'データセンター拡張による長期成長機会',
        description: 'クラウド大手のデータセンター投資計画により、高性能AI半導体の需要は今後3-5年間で年率25%の成長が見込まれます。特にGPU、HBMメモリ分野での恩恵が大きいと予測されます。',
        confidence: 85,
        impact_level: 'high',
        time_horizon: 'long',
        created_at: '2024-02-20T08:00:00Z'
      },
      {
        id: '2',
        insight_type: 'trend',
        title: 'エッジAI市場の急速な成長',
        description: '自動車、スマートフォン、IoTデバイスでのAI処理需要増加により、エッジAI向け半導体市場が急拡大しています。低消費電力・高効率チップの需要が特に顕著です。',
        confidence: 78,
        impact_level: 'medium',
        time_horizon: 'medium',
        created_at: '2024-02-19T16:30:00Z'
      },
      {
        id: '3',
        insight_type: 'risk',
        title: '地政学的リスクによる供給チェーン懸念',
        description: 'アジア地域の地政学的緊張により、半導体供給チェーンのリスクが高まっています。製造拠点の多様化が重要な課題となっており、短期的にはコスト増要因となる可能性があります。',
        confidence: 72,
        impact_level: 'medium',
        time_horizon: 'short',
        created_at: '2024-02-18T10:45:00Z'
      },
      {
        id: '4',
        insight_type: 'prediction',
        title: '次世代メモリ技術への転換点',
        description: 'AI処理の高速化要求により、従来のDRAMからHBM（High Bandwidth Memory）への移行が加速します。2025年までにHBM市場は現在の3倍に成長すると予測されます。',
        confidence: 91,
        impact_level: 'high',
        time_horizon: 'medium',
        created_at: '2024-02-17T13:20:00Z'
      }
    ];
    setAIInsights(mockInsights);
  };

  const formatTimeAgo = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `${diffDays}日前`;
    } else if (diffHours > 0) {
      return `${diffHours}時間前`;
    } else {
      return '1時間以内';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400 bg-green-900/20';
      case 'negative': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'ポジティブ';
      case 'negative': return 'ネガティブ';
      default: return '中立';
    }
  };

  const getInsightTypeColor = (type: string) => {
    switch (type) {
      case 'opportunity': return 'text-green-400 bg-green-900/20';
      case 'risk': return 'text-red-400 bg-red-900/20';
      case 'trend': return 'text-blue-400 bg-blue-900/20';
      case 'prediction': return 'text-purple-400 bg-purple-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getInsightTypeLabel = (type: string) => {
    switch (type) {
      case 'opportunity': return '機会';
      case 'risk': return 'リスク';
      case 'trend': return 'トレンド';
      case 'prediction': return '予測';
      default: return type;
    }
  };

  const getInsightTypeIcon = (type: string) => {
    switch (type) {
      case 'opportunity': return TrendingUp;
      case 'risk': return AlertTriangle;
      case 'trend': return Target;
      case 'prediction': return Brain;
      default: return Lightbulb;
    }
  };

  const getImpactLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getTimeHorizonLabel = (horizon: string) => {
    switch (horizon) {
      case 'short': return '短期';
      case 'medium': return '中期';
      case 'long': return '長期';
      default: return horizon;
    }
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center">
          <Lightbulb className="w-6 h-6 mr-3 text-yellow-400" />
          インサイト分析
        </h2>
        
        {/* タブ切替 */}
        <div className="flex bg-gray-800/50 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === 'insights'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            AI分析
          </button>
          <button
            onClick={() => setActiveTab('news')}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === 'news'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            関連ニュース
          </button>
        </div>
      </div>

      {/* コンテンツ */}
      <div className="space-y-4">
        {activeTab === 'insights' ? (
          // AI Insights Tab
          <div>
            {loadingInsights ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
              </div>
            ) : aiInsights.length > 0 ? (
              <div className="space-y-4">
                {aiInsights.map((insight) => {
                  const InsightIcon = getInsightTypeIcon(insight.insight_type);
                  return (
                    <div 
                      key={insight.id}
                      className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <InsightIcon className="w-4 h-4 text-purple-400" />
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getInsightTypeColor(insight.insight_type)}`}>
                            {getInsightTypeLabel(insight.insight_type)}
                          </span>
                          <span className={`text-xs ${getImpactLevelColor(insight.impact_level)}`}>
                            影響度: {insight.impact_level}
                          </span>
                        </div>
                        
                        <div className="text-xs text-gray-500">
                          信頼度: {insight.confidence}%
                        </div>
                      </div>

                      <h3 className="font-semibold text-white mb-2">
                        {insight.title}
                      </h3>
                      
                      <p className="text-sm text-gray-300 leading-relaxed mb-3">
                        {insight.description}
                      </p>

                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-3">
                          <span>時間軸: {getTimeHorizonLabel(insight.time_horizon)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatTimeAgo(insight.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <div className="text-gray-400 text-sm">AI分析結果がありません</div>
              </div>
            )}
          </div>
        ) : (
          // News Tab
          <div>
            {loadingNews ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              </div>
            ) : news.length > 0 ? (
              <div className="space-y-4">
                {news.map((item) => (
                  <div 
                    key={item.id}
                    className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-gray-600/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(item.sentiment)}`}>
                          {getSentimentLabel(item.sentiment)}
                        </span>
                        <span className="text-xs text-gray-500">
                          関連度: {item.relevance_score}%
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{formatTimeAgo(item.published_at)}</span>
                      </div>
                    </div>

                    <h3 className="font-semibold text-white mb-2 leading-snug">
                      {item.title}
                    </h3>
                    
                    <p className="text-sm text-gray-300 leading-relaxed mb-3">
                      {item.summary}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        出典: {item.source}
                      </span>
                      
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 text-sm transition-colors"
                      >
                        <span>記事を読む</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Newspaper className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <div className="text-gray-400 text-sm">関連ニュースがありません</div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* フッター */}
      <div className="mt-6 pt-4 border-t border-gray-700/50">
        <div className="text-center">
          <button className="text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors inline-flex items-center space-x-1">
            <span>すべての{activeTab === 'insights' ? 'AI分析' : 'ニュース'}を見る</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}