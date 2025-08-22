'use client';

import EnhancedStockChart from './EnhancedStockChart';

interface TripleChartProps {
  symbol: string;
}

export default function TripleChart({ symbol }: TripleChartProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-4">
        <h3 className="text-lg font-bold text-white mb-2 text-center">実績</h3>
        <EnhancedStockChart symbol={symbol} showThumbnail={true} chartType="historical" />
      </div>
      <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-4">
        <h3 className="text-lg font-bold text-white mb-2 text-center">過去予測</h3>
        <EnhancedStockChart symbol={symbol} showThumbnail={true} chartType="past-prediction" />
      </div>
      <div className="bg-gray-900/50 rounded-2xl border border-gray-800/50 p-4">
        <h3 className="text-lg font-bold text-white mb-2 text-center">未来予測</h3>
        <EnhancedStockChart symbol={symbol} showThumbnail={true} chartType="future-prediction" />
      </div>
    </div>
  );
}
