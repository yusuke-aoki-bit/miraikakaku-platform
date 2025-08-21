'use client';

import { Widget } from '@/types/dashboard';

interface TradingHistoryProps {
  widget: Widget;
}

export default function TradingHistory({ widget }: TradingHistoryProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">📜</div>
        <h4 className="font-medium text-text-primary mb-1">取引履歴</h4>
        <p className="text-sm">過去の取引記録と分析</p>
      </div>
    </div>
  );
}