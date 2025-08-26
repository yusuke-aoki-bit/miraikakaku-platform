'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Star, TrendingUp, TrendingDown, BarChart3, Brain, Newspaper, BookOpen, Target } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import TripleChart from '@/components/charts/TripleChart';
import AdSenseUnit from '@/components/ads/AdSenseUnit';
import { AmazonProductGrid } from '@/components/amazon/AmazonProductCard';
import { apiClient } from '@/lib/api-client';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface StockData {
  symbol: string;
  companyName: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  volume: number;
  marketCap: number;
  per: number;
  pbr: number;
  dividendYield: number;
  sector: string;
  themes: string[];
}

interface AIAnalysis {
  prediction: {
    direction: 'bullish' | 'bearish' | 'neutral';
    confidence: number;
    targetPrice: number;
    timeHorizon: string;
  };
  factors: {
    positive: string[];
    negative: string[];
    neutral: string[];
  };
  riskLevel: 'low' | 'medium' | 'high';
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  publishedAt: string;
  source: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params?.symbol as string;
  
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'ai' | 'themes' | 'news' | 'books'>('ai');

  // Fetch all stock data
  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol) return;
      
      try {
        setLoading(true);
        
        // Fetch stock price data
        const priceResponse = await apiClient.getStockPrice(symbol);
        
        // Fetch AI analysis
        const aiResponse = await apiClient.getAIStockDecisionFactors(symbol);
        
        // Fetch related news
        const newsResponse = await apiClient.getStockNews(symbol);
        
        // Check watchlist status
        const watchlistResponse = await apiClient.getWatchlist();
        const isInWatchlist = watchlistResponse.success && Array.isArray(watchlistResponse.data)
          ? watchlistResponse.data.some((item: any) => item.symbol === symbol)
          : false;

        if (priceResponse.success && priceResponse.data) {
          const data = priceResponse.data as any;
          setStockData({
            symbol: symbol,
            companyName: data.company_name || symbol,
            currentPrice: data.current_price || 0,
            change: data.price_change || 0,
            changePercent: data.price_change_percent || 0,
            high: data.day_high || 0,
            low: data.day_low || 0,
            open: data.day_open || 0,
            previousClose: data.previous_close || 0,
            volume: data.volume || 0,
            marketCap: data.market_cap || 0,
            per: data.pe_ratio || 0,
            pbr: data.pb_ratio || 0,
            dividendYield: data.dividend_yield || 0,
            sector: data.sector || '',
            themes: data.themes || []
          });
        }

        if (aiResponse.success && aiResponse.data) {
          const aiData = aiResponse.data as any;
          setAiAnalysis({
            prediction: {
              direction: aiData.prediction?.direction || 'neutral',
              confidence: aiData.prediction?.confidence || 0,
              targetPrice: aiData.prediction?.target_price || 0,
              timeHorizon: aiData.prediction?.time_horizon || '1ヶ月'
            },
            factors: {
              positive: aiData.positive_factors || [],
              negative: aiData.negative_factors || [],
              neutral: aiData.neutral_factors || []
            },
            riskLevel: aiData.risk_level || 'medium'
          });
        }

        if (newsResponse.success && newsResponse.data) {
          setNews(newsResponse.data as NewsItem[]);
        }

        setIsInWatchlist(isInWatchlist);
      } catch (error) {
        console.error('Error fetching stock data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [symbol]);

  const toggleWatchlist = async () => {
    if (!stockData) return;
    
    try {
      if (isInWatchlist) {
        await apiClient.removeFromWatchlist(symbol);
      } else {
        await apiClient.addToWatchlist(stockData.symbol);
      }
      setIsInWatchlist(!isInWatchlist);
    } catch (error) {
      console.error('Error updating watchlist:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="flex items-center space-x-4 mb-8">
              <div className="w-8 h-8 bg-gray-800 rounded"></div>
              <div className="h-8 bg-gray-800 rounded w-48"></div>
            </div>
            <div className="h-12 bg-gray-800 rounded mb-8"></div>
            <div className="h-96 bg-gray-800 rounded mb-8"></div>
            <div className="grid grid-cols-4 gap-4 mb-8">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-20 bg-gray-800 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return (
      <div className="min-h-screen bg-gray-950 p-6 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">株式データが見つかりません</h1>
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
        {/* AssetHeader - 銘柄情報 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                aria-label="戻る"
              >
                <ArrowLeft className="w-5 h-5 text-gray-400" />
              </Link>
              <div>
                <div className="flex items-center space-x-3 mb-1">
                  <h1 className="text-3xl font-bold text-white">{stockData.symbol}</h1>
                  <button
                    onClick={toggleWatchlist}
                    className={`p-2 rounded-lg transition-all ${
                      isInWatchlist 
                        ? 'bg-yellow-500/20 text-yellow-400' 
                        : 'bg-gray-800 text-gray-400 hover:text-yellow-400'
                    }`}
                    aria-label={isInWatchlist ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
                  >
                    <Star className={`w-5 h-5 ${isInWatchlist ? 'fill-current' : ''}`} />
                  </button>
                </div>
                <p className="text-xl text-gray-300 mb-2">{stockData.companyName}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <span>セクター: {stockData.sector}</span>
                  {stockData.themes.length > 0 && (
                    <span>テーマ: {stockData.themes.slice(0, 2).join(', ')}</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-4xl font-bold text-white mb-1">
                ¥{stockData.currentPrice.toLocaleString()}
              </div>
              <div className={`flex items-center justify-end space-x-2 text-lg ${
                stockData.change > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {stockData.change > 0 ? (
                  <TrendingUp className="w-5 h-5" />
                ) : (
                  <TrendingDown className="w-5 h-5" />
                )}
                <span className="font-medium">
                  {stockData.change > 0 ? '+' : ''}
                  {stockData.change.toLocaleString()} 
                  ({stockData.changePercent > 0 ? '+' : ''}
                  {stockData.changePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* PriceChart - 過去実績＋未来予測チャート */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center mb-4">
              <BarChart3 className="w-6 h-6 mr-2 text-blue-400" />
              <h2 className="text-xl font-bold text-white">価格チャート・予測</h2>
            </div>
            <TripleChart symbol={symbol} />
          </div>
        </motion.div>

        {/* KeyMetrics - 重要指標 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">主要指標</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <KeyMetricCard label="始値" value={`¥${stockData.open.toLocaleString()}`} />
              <KeyMetricCard label="高値" value={`¥${stockData.high.toLocaleString()}`} />
              <KeyMetricCard label="安値" value={`¥${stockData.low.toLocaleString()}`} />
              <KeyMetricCard label="前日終値" value={`¥${stockData.previousClose.toLocaleString()}`} />
              <KeyMetricCard 
                label="出来高" 
                value={stockData.volume > 1000000 
                  ? `${(stockData.volume / 1000000).toFixed(1)}M` 
                  : stockData.volume.toLocaleString()
                } 
              />
              <KeyMetricCard 
                label="時価総額" 
                value={stockData.marketCap > 1000000000000 
                  ? `${(stockData.marketCap / 1000000000000).toFixed(1)}兆円` 
                  : `${(stockData.marketCap / 100000000).toFixed(1)}億円`
                } 
              />
              <KeyMetricCard label="PER" value={`${stockData.per.toFixed(1)}倍`} />
              <KeyMetricCard label="配当利回り" value={`${stockData.dividendYield.toFixed(2)}%`} />
            </div>
          </div>
        </motion.div>

        {/* AdSense Unit - KeyMetricsとInfoTabsの間 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <AdSenseUnit
            adSlot="1234567892"
            width={728}
            height={90}
            className="w-full flex justify-center"
          />
        </motion.div>

        {/* InfoTabs - タブコンテンツエリア */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            {/* Tab Navigation */}
            <div className="flex border-b border-gray-800 mb-6">
              {[
                { key: 'ai', label: 'AI分析', icon: Brain },
                { key: 'themes', label: '関連テーマ', icon: Target },
                { key: 'news', label: '関連ニュース', icon: Newspaper },
                { key: 'books', label: '関連書籍', icon: BookOpen }
              ].map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key as any)}
                  className={`flex items-center px-4 py-3 border-b-2 font-medium transition-colors ${
                    activeTab === key
                      ? 'border-blue-400 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px]">
              {activeTab === 'ai' && (
                <AIAnalysisTab analysis={aiAnalysis} />
              )}
              {activeTab === 'themes' && (
                <ThemesTab themes={stockData.themes} sector={stockData.sector} />
              )}
              {activeTab === 'news' && (
                <NewsTab news={news} symbol={symbol} />
              )}
              {activeTab === 'books' && (
                <BooksTab />
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

// Component: KeyMetricCard - 重要指標カード
function KeyMetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-800/30 border border-gray-700/50 rounded-lg p-4">
      <div className="text-gray-400 text-sm mb-1">{label}</div>
      <div className="text-white font-semibold text-lg">{value}</div>
    </div>
  );
}

// Component: AIAnalysisTab - AI分析タブ
function AIAnalysisTab({ analysis }: { analysis: AIAnalysis | null }) {
  if (!analysis) {
    return (
      <div className="text-center py-12">
        <Brain className="w-12 h-12 mx-auto mb-4 text-gray-600" />
        <p className="text-gray-400">AI分析データを読み込み中...</p>
      </div>
    );
  }

  const getPredictionColor = (direction: string) => {
    switch (direction) {
      case 'bullish': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'bearish': return 'text-red-400 bg-red-500/20 border-red-500/30';
      default: return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-400';
      case 'high': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* AI予測 */}
      <div className={`p-4 border rounded-lg ${getPredictionColor(analysis.prediction.direction)}`}>
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold">AI予測</h4>
          <span className="text-sm">信頼度: {analysis.prediction.confidence}%</span>
        </div>
        <div className="space-y-2">
          <p className="font-medium">
            {analysis.prediction.direction === 'bullish' ? '🚀 強気' : 
             analysis.prediction.direction === 'bearish' ? '📉 弱気' : '➡️ 中立'}
          </p>
          <p className="text-sm">
            目標価格: ¥{analysis.prediction.targetPrice.toLocaleString()} 
            ({analysis.prediction.timeHorizon})
          </p>
        </div>
      </div>

      {/* 決定要因 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <h5 className="font-medium text-green-400">ポジティブ要因</h5>
          <ul className="space-y-1">
            {analysis.factors.positive.map((factor, index) => (
              <li key={index} className="text-sm text-gray-300 bg-green-500/10 p-2 rounded">
                + {factor}
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-2">
          <h5 className="font-medium text-red-400">リスク要因</h5>
          <ul className="space-y-1">
            {analysis.factors.negative.map((factor, index) => (
              <li key={index} className="text-sm text-gray-300 bg-red-500/10 p-2 rounded">
                - {factor}
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-2">
          <h5 className="font-medium text-gray-400">中立要因</h5>
          <ul className="space-y-1">
            {analysis.factors.neutral.map((factor, index) => (
              <li key={index} className="text-sm text-gray-300 bg-gray-500/10 p-2 rounded">
                • {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* リスクレベル */}
      <div className="flex items-center justify-between p-4 bg-gray-800/30 rounded-lg">
        <span className="font-medium text-gray-300">総合リスクレベル</span>
        <span className={`font-semibold ${getRiskColor(analysis.riskLevel)}`}>
          {analysis.riskLevel === 'low' ? '低リスク' :
           analysis.riskLevel === 'high' ? '高リスク' : '中リスク'}
        </span>
      </div>
    </div>
  );
}

// Component: ThemesTab - 関連テーマタブ
function ThemesTab({ themes, sector }: { themes: string[]; sector: string }) {
  return (
    <div className="space-y-6">
      <div>
        <h4 className="font-semibold text-white mb-4">セクター</h4>
        <div className="inline-block px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg">
          {sector}
        </div>
      </div>

      {themes.length > 0 && (
        <div>
          <h4 className="font-semibold text-white mb-4">関連テーマ</h4>
          <div className="flex flex-wrap gap-2">
            {themes.map((theme, index) => (
              <Link
                key={index}
                href={`/themes/${theme.toLowerCase().replace(/\s+/g, '-')}`}
                className="px-3 py-2 bg-gray-800/50 text-gray-300 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                {theme}
              </Link>
            ))}
          </div>
        </div>
      )}

      {themes.length === 0 && (
        <div className="text-center py-12">
          <Target className="w-12 h-12 mx-auto mb-4 text-gray-600" />
          <p className="text-gray-400">関連テーマ情報がありません</p>
        </div>
      )}
    </div>
  );
}

// Component: NewsTab - 関連ニュースタブ
function NewsTab({ news, symbol }: { news: NewsItem[]; symbol: string }) {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400';
      case 'negative': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  if (news.length === 0) {
    return (
      <div className="text-center py-12">
        <Newspaper className="w-12 h-12 mx-auto mb-4 text-gray-600" />
        <p className="text-gray-400">関連ニュースがありません</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {news.map((article) => (
        <div key={article.id} className="border border-gray-700 rounded-lg p-4 hover:bg-gray-800/30 transition-colors">
          <div className="flex items-start justify-between mb-2">
            <h5 className="font-medium text-white pr-4">{article.title}</h5>
            <span className={`text-xs px-2 py-1 rounded ${getSentimentColor(article.sentiment)} bg-current/10`}>
              {article.sentiment === 'positive' ? 'ポジティブ' :
               article.sentiment === 'negative' ? 'ネガティブ' : '中立'}
            </span>
          </div>
          <p className="text-sm text-gray-400 mb-3">{article.summary}</p>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{article.source}</span>
            <span>{new Date(article.publishedAt).toLocaleString('ja-JP')}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

// Component: BooksTab - 関連書籍タブ
function BooksTab() {
  return (
    <div className="space-y-6">
      <AmazonProductGrid
        products={amazonRecommendations.stock.products}
        title={amazonRecommendations.stock.title}
        description={amazonRecommendations.stock.description}
        maxItems={4}
        gridCols={2}
      />
    </div>
  );
}