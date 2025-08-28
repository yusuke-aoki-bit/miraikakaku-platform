'use client';

import React, { useState, useEffect } from 'react';
import { Newspaper, Clock, TrendingUp, Search, ArrowRight, Bookmark, BookmarkCheck, Filter, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import { apiClient } from '@/lib/api-client';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  content: string;
  publishedAt: string;
  source: string;
  category: 'market' | 'economic' | 'corporate' | 'global' | 'ai' | 'technology';
  sentiment: 'positive' | 'negative' | 'neutral';
  relatedStocks: string[];
  imageUrl?: string;
  readTime: number;
  isBookmarked: boolean;
  url?: string;
}

interface NewsCategory {
  id: string;
  label: string;
  icon: React.ElementType;
  description: string;
}

export default function NewsPage() {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [filteredNews, setFilteredNews] = useState<NewsArticle[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'latest' | 'popular' | 'relevant'>('latest');
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  const categories: NewsCategory[] = [
    { id: 'all', label: 'すべて', icon: Newspaper, description: '全カテゴリのニュース' },
    { id: 'market', label: 'マーケット', icon: TrendingUp, description: '株式・為替・商品市場' },
    { id: 'economic', label: '経済', icon: Clock, description: '経済指標・政策' },
    { id: 'corporate', label: '企業', icon: Bookmark, description: '企業業績・IR情報' },
    { id: 'global', label: '海外', icon: ArrowRight, description: '海外市場・国際情勢' },
    { id: 'ai', label: 'AI・テック', icon: TrendingUp, description: 'テクノロジー・AI関連' }
  ];

  // Fetch real news data from API
  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getNews({
          category: selectedCategory === 'all' ? undefined : selectedCategory,
          limit: 30,
          sort: sortBy
        });

        if (response.success && response.data) {
          setNews(response.data);
          setFilteredNews(response.data);
        } else {
          console.error('Failed to fetch news:', response.error);
          setNews([]);
          setFilteredNews([]);
        }
      } catch (error) {
        console.error('Error fetching news:', error);
        setNews([]);
        setFilteredNews([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [selectedCategory, sortBy]);

  // Filter and search logic
  useEffect(() => {
    let filtered = news;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(article => 
        article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        article.summary.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Bookmark filter
    if (bookmarkedOnly) {
      filtered = filtered.filter(article => article.isBookmarked);
    }

    setFilteredNews(filtered);
  }, [news, searchQuery, bookmarkedOnly]);

  const toggleBookmark = async (newsId: string) => {
    try {
      const article = news.find(n => n.id === newsId);
      if (!article) return;

      const response = await apiClient.toggleNewsBookmark(newsId);

      if (response.success) {
        setNews(prev => prev.map(article => 
          article.id === newsId 
            ? { ...article, isBookmarked: !article.isBookmarked }
            : article
        ));
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
    }
  };

  const getSentimentColor = (sentiment: NewsArticle['sentiment']) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400';
      case 'negative': return 'text-red-400';
      case 'neutral': return 'text-gray-400';
    }
  };

  const getCategoryColor = (category: NewsArticle['category']) => {
    switch (category) {
      case 'market': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'economic': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'corporate': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'global': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'ai': return 'bg-pink-500/20 text-pink-400 border-pink-500/30';
      case 'technology': return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return '1時間前';
    if (diffInHours < 24) return `${diffInHours}時間前`;
    return `${Math.floor(diffInHours / 24)}日前`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-48 mb-8"></div>
            <div className="flex space-x-4 mb-8">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-10 bg-gray-800 rounded w-24"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-80 bg-gray-800 rounded-xl"></div>
                  ))}
                </div>
              </div>
              <div className="space-y-6">
                <div className="h-96 bg-gray-800 rounded-xl"></div>
                <div className="h-64 bg-gray-800 rounded-xl"></div>
              </div>
            </div>
          </div>
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
          <h1 className="text-3xl font-bold text-white flex items-center mb-2">
            <Newspaper className="w-8 h-8 mr-3 text-blue-400" />
            マーケットニュース
          </h1>
          <p className="text-gray-400">
            最新の市場動向と投資情報をリアルタイムでお届けします
          </p>
        </motion.div>

        {/* Filters and Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 mb-8"
        >
          <div className="flex flex-col lg:flex-row gap-6 mb-6">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="記事タイトル、キーワードで検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Sort and Filters */}
            <div className="flex gap-4">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'latest' | 'popular' | 'relevant')}
                className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="latest">最新順</option>
                <option value="popular">人気順</option>
                <option value="relevant">関連度順</option>
              </select>

              <button
                onClick={() => setBookmarkedOnly(!bookmarkedOnly)}
                className={`px-4 py-3 rounded-lg border transition-colors flex items-center ${
                  bookmarkedOnly
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-blue-500'
                }`}
              >
                <BookmarkCheck className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Categories */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
              const Icon = category.icon;
              const count = category.id === 'all' 
                ? news.length 
                : news.filter(n => n.category === category.id).length;
              
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {category.label}
                  <span className="ml-2 px-2 py-1 bg-gray-700 rounded text-xs">
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Main Content Grid - 2/3 + 1/3 Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Area (2/3) */}
          <div className="lg:col-span-2 space-y-6">
            {/* News Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredNews.map((article, index) => (
                <motion.div
                  key={article.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.05 }}
                  className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden hover:border-gray-700 transition-all group"
                >
                  <Link href={`/news/${article.id}`} className="block">
                    <div className="p-6">
                      {/* Header */}
                      <div className="flex items-center justify-between mb-4">
                        <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getCategoryColor(article.category)}`}>
                          {categories.find(c => c.id === article.category)?.label}
                        </span>
                        <div className="flex items-center space-x-2">
                          {article.url && (
                            <ExternalLink className="w-4 h-4 text-gray-400" />
                          )}
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              toggleBookmark(article.id);
                            }}
                            className="text-gray-400 hover:text-blue-400 transition-colors"
                          >
                            {article.isBookmarked ? (
                              <BookmarkCheck className="w-5 h-5 text-blue-400" />
                            ) : (
                              <Bookmark className="w-5 h-5" />
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Title */}
                      <h3 className="text-lg font-semibold text-white mb-3 group-hover:text-blue-400 transition-colors line-clamp-2">
                        {article.title}
                      </h3>

                      {/* Summary */}
                      <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                        {article.summary}
                      </p>

                      {/* Related Stocks */}
                      {article.relatedStocks && article.relatedStocks.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-4">
                          {article.relatedStocks.slice(0, 3).map((stock) => (
                            <span key={stock} className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-blue-400">
                              {stock}
                            </span>
                          ))}
                          {article.relatedStocks.length > 3 && (
                            <span className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-400">
                              +{article.relatedStocks.length - 3}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Footer */}
                      <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-gray-800">
                        <div className="flex items-center space-x-3">
                          <span className="text-gray-400">{article.source}</span>
                          <span className={`flex items-center ${getSentimentColor(article.sentiment)}`}>
                            {article.sentiment === 'positive' ? '↗' : 
                             article.sentiment === 'negative' ? '↘' : '→'}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="w-3 h-3" />
                          <span>{article.readTime || 3}分</span>
                          <span>•</span>
                          <span>{formatTimeAgo(article.publishedAt)}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>

            {/* Empty State */}
            {filteredNews.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-20"
              >
                <Newspaper className="w-20 h-20 text-gray-600 mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-gray-400 mb-3">
                  記事が見つかりませんでした
                </h3>
                <p className="text-gray-500 max-w-md mx-auto">
                  検索条件やカテゴリを変更してお試しください。<br />
                  新しい記事は随時追加されます。
                </p>
              </motion.div>
            )}
          </div>

          {/* Sidebar (1/3) */}
          <div className="space-y-6">
            {/* AdSense Unit */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <AdSenseUnit
                adSlot="1234567891"
                className="w-full"
                style={{ minHeight: '600px' }}
              />
            </motion.div>

            {/* News Categories Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Filter className="w-5 h-5 mr-2 text-blue-400" />
                カテゴリガイド
              </h3>
              <div className="space-y-3">
                {categories.slice(1).map((category) => {
                  const Icon = category.icon;
                  const count = news.filter(n => n.category === category.id).length;
                  return (
                    <div key={category.id} className="flex items-start">
                      <Icon className="w-4 h-4 text-gray-400 mr-3 mt-1" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-white text-sm font-medium">{category.label}</span>
                          <span className="text-xs text-gray-500">{count}件</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-1">{category.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>

            {/* Amazon Product Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <Newspaper className="w-6 h-6 text-blue-600 mr-2" />
                  <h3 className="text-xl font-semibold text-gray-800">
                    {amazonRecommendations.news.title}
                  </h3>
                </div>
                <p className="text-gray-600 mb-4">{amazonRecommendations.news.description}</p>
                <div className="grid grid-cols-1 gap-4">
                  {amazonRecommendations.news.products.slice(0, 2).map((product) => (
                    <AmazonProductCard
                      key={product.id}
                      product={product}
                      compact={true}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}