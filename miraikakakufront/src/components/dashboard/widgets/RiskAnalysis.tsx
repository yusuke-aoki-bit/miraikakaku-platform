'use client';

import { Widget } from '@/types/dashboard';

interface RiskAnalysisProps {
  widget: Widget;
}

export default function RiskAnalysis({ widget }: RiskAnalysisProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">⚠️</div>
        <h4 className="font-medium text-text-primary mb-1">リスク分析</h4>
        <p className="text-sm">VaR、相関分析、リスク指標</p>
      </div>
    </div>
  );
}