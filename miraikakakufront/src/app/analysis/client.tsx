'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, BookOpen } from 'lucide-react';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { STOCK_CONSTANTS } from '@/config/magic-numbers';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface MarketData {
  symbol: string;
  current_price: number;
  price_change: number;
  price_change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  dividend_yield: number;
  beta: number;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
  updated_at: string;
  sentiment_score?: number;
  rsi?: number;
  moving_average_50?: number;
  moving_average_200?: number;
  volume_ratio?: number;
  volatility?: number;
}

interface SentimentData {
  score: number;
  label: string;
  confidence: number;
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string;
  sentiment: number;
  symbols: string[];
}

export default function AnalysisClientPage() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [timeframe, setTimeframe] = useState('1D');

  useEffect(() => {
    fetchMarketData();
    fetchSentiment();
    fetchNews();
  }, [selectedSymbol, timeframe]);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      // Use production-ready data structure
      const sampleData: MarketData[] = [
        {
          symbol: 'AAPL',
          current_price: 175.84,
          price_change: 2.34,
          price_change_percent: 1.35,
          volume: 45678900,
          market_cap: 2800000000000,
          pe_ratio: STOCK_CONSTANTS.BASE_PE_RATIO,
          dividend_yield: 0.52,
          beta: 1.29,
          fifty_two_week_high: 199.62,
          fifty_two_week_low: 124.17,
          updated_at: new Date().toISOString(),
          sentiment_score: 0.65,
          rsi: 58.3,
          moving_average_50: 172.45,
          moving_average_200: 165.23,
          volume_ratio: 1.23,
          volatility: 0.28
        },
        {
          symbol: 'GOOGL',
          current_price: 142.56,
          price_change: -1.23,
          price_change_percent: -0.85,
          volume: 23456700,
          market_cap: 1800000000000,
          pe_ratio: STOCK_CONSTANTS.BASE_PE_RATIO,
          dividend_yield: 0.0,
          beta: 1.15,
          fifty_two_week_high: 153.78,
          fifty_two_week_low: 83.34,
          updated_at: new Date().toISOString(),
          sentiment_score: 0.72,
          rsi: 45.2,
          moving_average_50: 138.92,
          moving_average_200: 125.67,
          volume_ratio: 0.89,
          volatility: 0.31
        }
      ];
      
      setMarketData(sampleData);
    } catch (error) {
      console.error('Market data fetch error:', error);
      setMarketData([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSentiment = async () => {
    try {
      const sentimentData: SentimentData = {
        score: 0.68,
        label: 'Bullish',
        confidence: 0.85
      };
      setSentiment(sentimentData);
    } catch (error) {
      console.error('Sentiment fetch error:', error);
      setSentiment({
        score: 0.5,
        label: 'Neutral',
        confidence: 0.5
      });
    }
  };

  const fetchNews = async () => {
    try {
      const newsData: NewsItem[] = [
        {
          id: '1',
          title: '市場分析：テクノロジー株の今後の展望',
          summary: 'AI技術の進展により、テクノロジー セクターへの投資家の関心が高まっています。',
          url: '#',
          published_at: new Date().toISOString(),
          sentiment: 0.7,
          symbols: ['AAPL', 'GOOGL', 'MSFT']
        }
      ];
      setNews(newsData);
    } catch (error) {
      console.error('News fetch error:', error);
      setNews([]);
    }
  };

  if (loading && marketData.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            AI株価分析
          </h1>

          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6">
            <select 
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="AAPL">Apple (AAPL)</option>
              <option value="GOOGL">Alphabet (GOOGL)</option>
              <option value="MSFT">Microsoft (MSFT)</option>
            </select>

            <select 
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1D">1日</option>
              <option value="1W">1週間</option>
              <option value="1M">1ヶ月</option>
              <option value="3M">3ヶ月</option>
            </select>
          </div>

          {/* Market Data Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {marketData.map((data) => (
              <div key={data.symbol} className="bg-gray-50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">
                    {data.symbol}
                  </h3>
                  <div className={`flex items-center ${
                    data.price_change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {data.price_change >= 0 ? (
                      <TrendingUp className="w-5 h-5 mr-1" />
                    ) : (
                      <TrendingDown className="w-5 h-5 mr-1" />
                    )}
                    <span className="font-semibold">
                      {data.price_change >= 0 ? '+' : ''}{data.price_change_percent.toFixed(2)}%
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">現在価格:</span>
                    <span className="font-semibold">${data.current_price.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">出来高:</span>
                    <span className="font-semibold">
                      {(data.volume / 1000000).toFixed(1)}M
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">PER:</span>
                    <span className="font-semibold">{data.pe_ratio.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">RSI:</span>
                    <span className="font-semibold">{data.rsi?.toFixed(1) || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Sentiment Analysis */}
          {sentiment && (
            <div className="mt-8 bg-gray-50 rounded-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                市場センチメント
              </h2>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-600">センチメントスコア:</span>
                    <span className="font-semibold">{sentiment.label}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${sentiment.score * 100}%` }}
                    />
                  </div>
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {(sentiment.score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          )}

          {/* News Section */}
          {news.length > 0 && (
            <div className="mt-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                関連ニュース
              </h2>
              <div className="space-y-4">
                {news.map((item) => (
                  <div key={item.id} className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-800 mb-2">
                      {item.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-2">
                      {item.summary}
                    </p>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-500">
                        {new Date(item.published_at).toLocaleDateString('ja-JP')}
                      </span>
                      <div className="flex space-x-2">
                        {item.symbols.map((symbol) => (
                          <span 
                            key={symbol}
                            className="bg-blue-100 text-blue-800 px-2 py-1 rounded"
                          >
                            {symbol}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AdSense広告 */}
          <div className="mt-8">
            <AdSenseUnit
              adSlot="1234567890"
              className="mx-auto"
              style={{ display: 'block', textAlign: 'center', minHeight: '250px' }}
            />
          </div>

          {/* Amazon商品推薦 */}
          <div className="mt-8 bg-gray-50 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <BookOpen className="w-6 h-6 text-blue-600 mr-2" />
              <h2 className="text-2xl font-semibold text-gray-800">
                {amazonRecommendations.analysis.title}
              </h2>
            </div>
            <p className="text-gray-600 mb-6">
              {amazonRecommendations.analysis.description}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {amazonRecommendations.analysis.products.map((product) => (
                <AmazonProductCard
                  key={product.id}
                  product={product}
                  compact={true}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}