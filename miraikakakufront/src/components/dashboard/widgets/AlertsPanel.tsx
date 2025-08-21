'use client';

import { Widget } from '@/types/dashboard';

interface AlertsPanelProps {
  widget: Widget;
}

export default function AlertsPanel({ widget }: AlertsPanelProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">🔔</div>
        <h4 className="font-medium text-text-primary mb-1">アラートパネル</h4>
        <p className="text-sm">価格アラートと通知設定</p>
      </div>
    </div>
  );
}