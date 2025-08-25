'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';
import { 
  NewspaperIcon,
  ClockIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

interface RelatedNewsItem {
  id: string;
  title: string;
  summary: string;
  published_at: string;
  category: string;
  source: string;
  image_url?: string;
}

interface RelatedNewsProps {
  articles: RelatedNewsItem[];
}

export default function RelatedNews({ articles }: RelatedNewsProps) {
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});

  const handleImageError = (articleId: string) => {
    setImageErrors(prev => ({ ...prev, [articleId]: true }));
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return '1時間以内';
    } else if (diffInHours < 24) {
      return `${diffInHours}時間前`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}日前`;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      '金融政策': 'text-blue-600',
      '海外市場': 'text-green-600',
      '国内市場': 'text-purple-600',
      '企業業績': 'text-orange-600',
      '経済指標': 'text-red-600',
      'テクノロジー': 'text-cyan-600',
      'エネルギー': 'text-yellow-600'
    };
    return colors[category] || 'text-gray-600';
  };

  if (articles.length === 0) {
    return (
      <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
        <div className="flex items-center mb-4">
          <NewspaperIcon className="h-5 w-5 text-accent-primary mr-2" />
          <h3 className="text-lg font-semibold text-text-primary">関連ニュース</h3>
        </div>
        
        <div className="text-center py-8">
          <div className="text-text-secondary text-sm">
            関連するニュース記事はありません
          </div>
        </div>
      </div>
    );
  }

  return (
    <section className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <NewspaperIcon className="h-5 w-5 text-accent-primary mr-2" />
          <h3 className="text-lg font-semibold text-text-primary">関連ニュース</h3>
        </div>
        <Link
          href="/news"
          className="text-sm text-accent-primary hover:text-accent-primary/80 transition-colors flex items-center"
        >
          すべて見る
          <ArrowRightIcon className="h-4 w-4 ml-1" />
        </Link>
      </div>

      {/* ニュースリスト */}
      <div className="space-y-6">
        {articles.slice(0, 3).map((article) => (
          <article
            key={article.id}
            className="flex space-x-4 p-4 rounded-lg border border-border-primary hover:bg-surface-background transition-colors group"
          >
            {/* 記事画像 */}
            <div className="flex-shrink-0">
              {article.image_url && !imageErrors[article.id] ? (
                <div className="relative w-20 h-20 rounded-lg overflow-hidden">
                  <Image
                    src={article.image_url}
                    alt={article.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={() => handleImageError(article.id)}
                  />
                </div>
              ) : (
                <div className="w-20 h-20 bg-surface-background rounded-lg flex items-center justify-center">
                  <NewspaperIcon className="h-8 w-8 text-text-secondary" />
                </div>
              )}
            </div>

            {/* 記事内容 */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                <span className={`text-xs font-medium ${getCategoryColor(article.category)}`}>
                  {article.category}
                </span>
                <span className="text-xs text-text-secondary">•</span>
                <span className="text-xs text-text-secondary">{article.source}</span>
                <span className="text-xs text-text-secondary">•</span>
                <div className="flex items-center text-xs text-text-secondary">
                  <ClockIcon className="h-3 w-3 mr-1" />
                  {formatTimeAgo(article.published_at)}
                </div>
              </div>

              <Link href={`/news/${article.id}`} className="block group">
                <h4 className="font-medium text-text-primary text-sm leading-snug mb-2 group-hover:text-accent-primary transition-colors line-clamp-2">
                  {article.title}
                </h4>
                <p className="text-xs text-text-secondary leading-relaxed line-clamp-2">
                  {article.summary}
                </p>
              </Link>
            </div>

            {/* 矢印アイコン */}
            <div className="flex-shrink-0 flex items-center">
              <ArrowRightIcon className="h-4 w-4 text-text-secondary group-hover:text-accent-primary transition-colors" />
            </div>
          </article>
        ))}
      </div>

      {/* 追加の記事がある場合のフッター */}
      {articles.length > 3 && (
        <div className="mt-6 pt-4 border-t border-border-primary text-center">
          <Link
            href="/news"
            className="inline-flex items-center text-sm text-accent-primary hover:text-accent-primary/80 font-medium transition-colors"
          >
            他の関連記事を見る ({articles.length - 3}件)
            <ArrowRightIcon className="h-4 w-4 ml-1" />
          </Link>
        </div>
      )}
    </section>
  );
}