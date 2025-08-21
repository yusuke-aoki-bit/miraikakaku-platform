'use client';

import { Widget } from '@/types/dashboard';

interface KPIScorecardProps {
  widget: Widget;
}

export default function KPIScorecard({ widget }: KPIScorecardProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">📈</div>
        <h4 className="font-medium text-text-primary mb-1">KPIスコアカード</h4>
        <p className="text-sm">重要指標の一覧表示</p>
      </div>
    </div>
  );
}