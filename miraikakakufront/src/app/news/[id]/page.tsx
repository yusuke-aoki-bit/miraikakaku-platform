'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import ArticleHeader from '@/components/news/ArticleHeader';
import ArticleBody from '@/components/news/ArticleBody';
import SocialShare from '@/components/news/SocialShare';
import RelatedStocksWidget from '@/components/news/RelatedStocksWidget';
import RelatedNews from '@/components/news/RelatedNews';
import { apiClient } from '@/lib/api-client';

interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  published_at: string;
  category: string;
  source: string;
  author?: string;
  image_url?: string;
  related_stocks: string[];
  tags: string[];
}

interface StockData {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  context?: string;
}

interface RelatedNewsItem {
  id: string;
  title: string;
  summary: string;
  published_at: string;
  category: string;
  source: string;
  image_url?: string;
}

export default function NewsDetailPage() {
  const params = useParams();
  const articleId = params.id as string;
  
  const [article, setArticle] = useState<NewsArticle | null>(null);
  const [relatedStocks, setRelatedStocks] = useState<StockData[]>([]);
  const [relatedNews, setRelatedNews] = useState<RelatedNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (articleId) {
      fetchArticleData();
    }
  }, [articleId]);

  const fetchArticleData = async () => {
    setLoading(true);
    setError('');

    try {
      // 記事データを取得
      const articleResponse = await apiClient.getNewsArticle(articleId);
      
      if (articleResponse.status === 'success' && articleResponse.data) {
        const articleData = articleResponse.data as NewsArticle;
        setArticle(articleData);

        // 関連銘柄データを取得
        if (articleData.related_stocks.length > 0) {
          const stocksResponse = await apiClient.getBatchStockDetails(articleData.related_stocks);
          if (stocksResponse.status === 'success') {
            const stocksData = Object.values(stocksResponse.data || {}) as StockData[];
            setRelatedStocks(stocksData);
          }
        }

        // 関連ニュースを取得
        const relatedResponse = await apiClient.getRelatedNews(articleId);
        if (relatedResponse.status === 'success') {
          setRelatedNews(relatedResponse.data || []);
        }
      } else {
        setError('記事が見つかりませんでした。');
      }
    } catch (error) {
      console.error('Failed to fetch article:', error);
      setError('記事の読み込み中にエラーが発生しました。');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-surface-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="text-red-500 text-lg font-medium mb-4">
              {error || '記事が見つかりませんでした'}
            </div>
            <button
              onClick={fetchArticleData}
              className="bg-accent-primary hover:bg-accent-primary/90 text-white px-4 py-2 rounded-lg transition-colors"
            >
              再試行
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 記事ヘッダー */}
        <ArticleHeader article={article} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* メインコンテンツ（左カラム、2/3幅） */}
          <div className="lg:col-span-2 space-y-6">
            {/* ソーシャル共有ボタン */}
            <SocialShare 
              title={article.title}
              url={typeof window !== 'undefined' ? window.location.href : ''}
            />

            {/* 記事本文 */}
            <ArticleBody 
              content={article.content}
              imageUrl={article.image_url}
            />

            {/* 関連ニュース（記事下部） */}
            <RelatedNews articles={relatedNews} />
          </div>

          {/* サイドバー（右カラム、1/3幅） */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* 関連銘柄ウィジェット */}
              <RelatedStocksWidget 
                stocks={relatedStocks}
                articleTitle={article.title}
              />

              {/* 追加のサイドバーコンテンツ（今後拡張可能） */}
              <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">記事情報</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">カテゴリ</span>
                    <span className="text-text-primary font-medium">{article.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">情報源</span>
                    <span className="text-text-primary font-medium">{article.source}</span>
                  </div>
                  {article.author && (
                    <div className="flex justify-between">
                      <span className="text-text-secondary">記者</span>
                      <span className="text-text-primary font-medium">{article.author}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-text-secondary">公開日</span>
                    <span className="text-text-primary font-medium">
                      {new Date(article.published_at).toLocaleDateString('ja-JP', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>

                {/* タグ表示 */}
                {article.tags.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border-primary">
                    <div className="text-sm text-text-secondary mb-2">タグ</div>
                    <div className="flex flex-wrap gap-2">
                      {article.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-accent-primary/10 text-accent-primary text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}