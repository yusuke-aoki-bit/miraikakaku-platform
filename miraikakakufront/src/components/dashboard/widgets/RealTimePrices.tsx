'use client';

import { Widget } from '@/types/dashboard';

interface RealTimePricesProps {
  widget: Widget;
}

export default function RealTimePrices({ widget }: RealTimePricesProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">📊</div>
        <h4 className="font-medium text-text-primary mb-1">リアルタイム価格</h4>
        <p className="text-sm">リアルタイムの株価と出来高</p>
      </div>
    </div>
  );
}