'use client';

import { Widget } from '@/types/dashboard';

interface DataTableProps {
  widget: Widget;
}

export default function DataTable({ widget }: DataTableProps) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center text-text-secondary">
        <div className="text-4xl mb-3">📊</div>
        <h4 className="font-medium text-text-primary mb-1">データテーブル</h4>
        <p className="text-sm">カスタマイズ可能なデータ表</p>
      </div>
    </div>
  );
}