'use client';

import { Widget } from '@/types/dashboard';

interface NewsSentimentProps {
  widget: Widget;
}

export default function NewsSentiment({ widget }: NewsSentimentProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">📰</div>
        <h4 className="font-medium text-text-primary mb-1">ニュース・センチメント</h4>
        <p className="text-sm">市場ニュースと感情分析</p>
      </div>
    </div>
  );
}