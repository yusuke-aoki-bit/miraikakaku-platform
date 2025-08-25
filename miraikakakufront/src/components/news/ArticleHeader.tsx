'use client';

import Link from 'next/link';
import { ChevronRightIcon, ClockIcon, TagIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  published_at: string;
  category: string;
  source: string;
  author?: string;
}

interface ArticleHeaderProps {
  article: NewsArticle;
}

export default function ArticleHeader({ article }: ArticleHeaderProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      '金融政策': 'bg-blue-500/10 text-blue-600 border-blue-500/20',
      '海外市場': 'bg-green-500/10 text-green-600 border-green-500/20',
      '国内市場': 'bg-purple-500/10 text-purple-600 border-purple-500/20',
      '企業業績': 'bg-orange-500/10 text-orange-600 border-orange-500/20',
      '経済指標': 'bg-red-500/10 text-red-600 border-red-500/20',
      'テクノロジー': 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
      'エネルギー': 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20'
    };
    return colors[category] || 'bg-gray-500/10 text-gray-600 border-gray-500/20';
  };

  return (
    <header className="space-y-6">
      {/* パンくずリスト */}
      <nav className="flex items-center text-sm text-text-secondary" aria-label="パンくずナビゲーション">
        <Link 
          href="/" 
          className="hover:text-accent-primary transition-colors"
        >
          ホーム
        </Link>
        <ChevronRightIcon className="h-4 w-4 mx-2" />
        <Link 
          href="/news" 
          className="hover:text-accent-primary transition-colors"
        >
          ニュース
        </Link>
        <ChevronRightIcon className="h-4 w-4 mx-2" />
        <span className="text-text-primary font-medium truncate max-w-xs">
          {article.title}
        </span>
      </nav>

      {/* 記事メタデータ */}
      <div className="flex flex-wrap items-center gap-4 text-sm">
        {/* カテゴリ */}
        <div className="flex items-center">
          <TagIcon className="h-4 w-4 mr-2 text-text-secondary" />
          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(article.category)}`}>
            {article.category}
          </span>
        </div>

        {/* 公開日時 */}
        <div className="flex items-center text-text-secondary">
          <ClockIcon className="h-4 w-4 mr-2" />
          <time dateTime={article.published_at}>
            {formatDate(article.published_at)}
          </time>
        </div>

        {/* 情報提供元 */}
        <div className="flex items-center text-text-secondary">
          <BuildingOfficeIcon className="h-4 w-4 mr-2" />
          <span>{article.source}</span>
          {article.author && (
            <span className="ml-2 text-text-primary">
              / {article.author}
            </span>
          )}
        </div>
      </div>

      {/* 記事タイトル */}
      <div className="space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold text-text-primary leading-tight">
          {article.title}
        </h1>
        
        {/* 記事要約 */}
        {article.summary && (
          <p className="text-lg text-text-secondary leading-relaxed border-l-4 border-accent-primary pl-6 bg-accent-primary/5 py-4 rounded-r-lg">
            {article.summary}
          </p>
        )}
      </div>

      {/* 区切り線 */}
      <div className="border-t border-border-primary pt-6" />
    </header>
  );
}