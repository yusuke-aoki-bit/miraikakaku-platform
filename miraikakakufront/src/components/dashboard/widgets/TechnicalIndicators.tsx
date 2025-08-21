'use client';

import { Widget } from '@/types/dashboard';

interface TechnicalIndicatorsProps {
  widget: Widget;
}

export default function TechnicalIndicators({ widget }: TechnicalIndicatorsProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">🎯</div>
        <h4 className="font-medium text-text-primary mb-1">テクニカル指標</h4>
        <p className="text-sm">RSI、MACD等のテクニカル分析</p>
      </div>
    </div>
  );
}