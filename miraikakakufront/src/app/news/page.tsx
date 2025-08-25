'use client';

import React, { useState, useEffect } from 'react';
import { Newspaper, Clock, TrendingUp, Filter, Search, ArrowRight, Bookmark, BookmarkCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  content: string;
  publishedAt: string;
  source: string;
  category: 'market' | 'economic' | 'corporate' | 'global' | 'ai';
  sentiment: 'positive' | 'negative' | 'neutral';
  relatedStocks: string[];
  imageUrl?: string;
  readTime: number;
  isBookmarked: boolean;
}

interface NewsCategory {
  id: string;
  label: string;
  icon: React.ElementType;
  count: number;
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
    { id: 'all', label: 'すべて', icon: Newspaper, count: 0 },
    { id: 'market', label: 'マーケット', icon: TrendingUp, count: 0 },
    { id: 'economic', label: '経済', icon: Clock, count: 0 },
    { id: 'corporate', label: '企業', icon: Bookmark, count: 0 },
    { id: 'global', label: '海外', icon: ArrowRight, count: 0 },
    { id: 'ai', label: 'AI・テック', icon: TrendingUp, count: 0 }
  ];

  // Mock data generation
  useEffect(() => {
    const generateMockNews = (): NewsArticle[] => {
      const headlines = [
        '日経平均、3日連続上昇で3万円台を回復',
        'トヨタ、EV戦略見直しで新工場建設を発表',
        '米FRB、金利据え置きを決定。市場は好反応',
        'AI関連銘柄が急騰、ChatGPT効果で注目集まる',
        '円安進行で輸出企業に追い風、自動車株が高い',
        '半導体不足解消の兆し、関連企業の業績に期待',
        '再生可能エネルギー関連株が買われる展開',
        '中国経済回復期待で商社株が軒並み上昇',
        'バイオテック企業の新薬承認で株価急騰',
        '不動産市況改善で建設・住宅関連株に注目'
      ];

      const sources = ['日経新聞', 'ロイター', 'Bloomberg', 'Yahoo!ファイナンス', '東洋経済', 'ダイヤモンド'];
      const categories: NewsArticle['category'][] = ['market', 'economic', 'corporate', 'global', 'ai'];
      const sentiments: NewsArticle['sentiment'][] = ['positive', 'negative', 'neutral'];

      return Array.from({ length: 50 }, (_, i) => ({
        id: `news-${i + 1}`,
        title: headlines[i % headlines.length] + (i > 9 ? ` (${Math.floor(i / 10) + 1})` : ''),
        summary: 'この記事では、最新の市場動向と投資家への影響について詳しく解説します。専門家の分析と今後の見通しもお伝えします。',
        content: 'フル記事内容...',
        publishedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        source: sources[Math.floor(Math.random() * sources.length)],
        category: categories[Math.floor(Math.random() * categories.length)],
        sentiment: sentiments[Math.floor(Math.random() * sentiments.length)],
        relatedStocks: ['7203', '6758', '9984', '4063'].slice(0, Math.floor(Math.random() * 3) + 1),
        readTime: Math.floor(Math.random() * 8) + 2,
        isBookmarked: Math.random() > 0.8
      }));
    };

    setTimeout(() => {
      const mockNews = generateMockNews();
      setNews(mockNews);
      setFilteredNews(mockNews);
      setLoading(false);
    }, 1000);
  }, []);

  // Filter and search logic
  useEffect(() => {
    let filtered = news;

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(article => article.category === selectedCategory);
    }

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

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'latest':
          return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
        case 'popular':
          return b.relatedStocks.length - a.relatedStocks.length;
        case 'relevant':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    setFilteredNews(filtered);
  }, [news, selectedCategory, searchQuery, sortBy, bookmarkedOnly]);

  const toggleBookmark = (newsId: string) => {
    setNews(prev => prev.map(article => 
      article.id === newsId 
        ? { ...article, isBookmarked: !article.isBookmarked }
        : article
    ));
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
      case 'market': return 'bg-blue-500/20 text-blue-400';
      case 'economic': return 'bg-purple-500/20 text-purple-400';
      case 'corporate': return 'bg-green-500/20 text-green-400';
      case 'global': return 'bg-orange-500/20 text-orange-400';
      case 'ai': return 'bg-pink-500/20 text-pink-400';
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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Array.from({ length: 9 }).map((_, i) => (
                <div key={i} className="h-64 bg-gray-800 rounded-xl"></div>
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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center">
              <Newspaper className="w-8 h-8 mr-3 text-blue-400" />
              マーケットニュース
            </h1>
            <p className="text-gray-400 mt-2">最新の市場動向と投資情報をお届けします</p>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="ニュースを検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {/* Sort and Filters */}
            <div className="flex gap-4">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="latest">最新順</option>
                <option value="popular">人気順</option>
                <option value="relevant">関連度順</option>
              </select>

              <button
                onClick={() => setBookmarkedOnly(!bookmarkedOnly)}
                className={`px-4 py-3 rounded-lg border transition-colors ${
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
          <div className="flex flex-wrap gap-2 mt-6">
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
        </div>

        {/* News Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNews.map((article, index) => (
            <motion.div
              key={article.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden hover:border-gray-700 transition-colors group"
            >
              <Link href={`/news/${article.id}`}>
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4">
                    <span className={`px-3 py-1 rounded-lg text-xs font-medium ${getCategoryColor(article.category)}`}>
                      {categories.find(c => c.id === article.category)?.label}
                    </span>
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

                  {/* Title */}
                  <h3 className="text-lg font-semibold text-white mb-3 group-hover:text-blue-400 transition-colors line-clamp-2">
                    {article.title}
                  </h3>

                  {/* Summary */}
                  <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                    {article.summary}
                  </p>

                  {/* Related Stocks */}
                  {article.relatedStocks.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {article.relatedStocks.map((stock) => (
                        <span key={stock} className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-300">
                          {stock}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span>{article.source}</span>
                      <span className={getSentimentColor(article.sentiment)}>
                        {article.sentiment === 'positive' ? '↗' : 
                         article.sentiment === 'negative' ? '↘' : '→'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>{article.readTime}分</span>
                      <span>•</span>
                      <span>{formatTimeAgo(article.publishedAt)}</span>
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Load More */}
        {filteredNews.length === 0 && (
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl text-gray-400 mb-2">記事が見つかりませんでした</h3>
            <p className="text-gray-500">検索条件を変更してお試しください</p>
          </div>
        )}
      </div>
    </div>
  );
}