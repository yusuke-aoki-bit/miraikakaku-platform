'use client';

import { Widget } from '@/types/dashboard';

interface WatchlistProps {
  widget: Widget;
}

export default function Watchlist({ widget }: WatchlistProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">⭐</div>
        <h4 className="font-medium text-text-primary mb-1">ウォッチリスト</h4>
        <p className="text-sm">関心銘柄の一覧と価格変動</p>
      </div>
    </div>
  );
}