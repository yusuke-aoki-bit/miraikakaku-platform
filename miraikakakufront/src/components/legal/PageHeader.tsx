'use client';

import { CalendarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

interface PageHeaderProps {
  title: string;
  lastUpdated: string;
  description?: string;
  icon?: 'terms' | 'privacy';
}

export default function PageHeader({ title, lastUpdated, description, icon }: PageHeaderProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getIcon = () => {
    switch (icon) {
      case 'terms':
        return (
          <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4">
            <DocumentTextIcon className="w-6 h-6 text-blue-500" />
          </div>
        );
      case 'privacy':
        return (
          <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-12 h-12 bg-accent-primary/10 rounded-xl flex items-center justify-center mb-4">
            <DocumentTextIcon className="w-6 h-6 text-accent-primary" />
          </div>
        );
    }
  };

  return (
    <header className="bg-surface-elevated border-b border-border-primary">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          {/* アイコン */}
          <div className="flex justify-center">
            {getIcon()}
          </div>

          {/* タイトル */}
          <h1 className="text-3xl md:text-4xl font-bold text-text-primary mb-4">
            {title}
          </h1>

          {/* 説明文 */}
          {description && (
            <p className="text-lg text-text-secondary mb-6 max-w-2xl mx-auto leading-relaxed">
              {description}
            </p>
          )}

          {/* 最終更新日 */}
          <div className="flex items-center justify-center text-sm text-text-secondary">
            <CalendarIcon className="w-4 h-4 mr-2" />
            <span>最終更新日: {formatDate(lastUpdated)}</span>
          </div>
        </div>

        {/* 重要事項の注意書き */}
        <div className="mt-8 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg max-w-2xl mx-auto">
          <div className="flex items-start space-x-2">
            <svg className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">重要事項</p>
              <p>
                以下の内容を十分にお読みいただき、同意いただいた上でサービスをご利用ください。
                内容についてご不明な点がございましたら、お気軽にお問い合わせください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}