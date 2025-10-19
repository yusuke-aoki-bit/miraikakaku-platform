import React from 'react';
import { SectorBadge } from './SectorBadge';
import { formatPercentage, getSafeNumber, safeToFixed } from '@/lib/formatters';

interface RankingItem {
  symbol: string;
  company_name: string;
  exchange: string;
  current_price: number;
  change_percent?: number;
  volume?: number;
  predicted_change?: number;
  confidence_score?: number;
  sector?: string;  // Phase 4-3: セクター情報
}

interface RankingCardProps {
  item: RankingItem;
  index: number;
  onClick: () => void;
  type: 'gainer' | 'loser' | 'volume' | 'prediction';
}

const RankingCard = React.memo(({ item, index, onClick, type }: RankingCardProps) => {
  const getValueDisplay = () => {
    // 文字列の場合も考慮して数値に変換
    const safePrice = getSafeNumber(typeof item.current_price === 'string' ? parseFloat(item.current_price) : item.current_price, 0);
    const safeChangePercent = getSafeNumber(typeof item.change_percent === 'string' ? parseFloat(item.change_percent) : item.change_percent, 0);
    const safePredictedChange = getSafeNumber(typeof item.predicted_change === 'string' ? parseFloat(item.predicted_change) : item.predicted_change, 0);
    const safeConfidence = getSafeNumber(typeof item.confidence_score === 'string' ? parseFloat(item.confidence_score) : item.confidence_score, 0);
    const safeVolume = getSafeNumber(typeof item.volume === 'string' ? parseFloat(item.volume) : item.volume, 0);

    switch (type) {
      case 'gainer':
        return (
          <>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              +{formatPercentage(safeChangePercent, 2, '0.00%')}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{safeToFixed(item.current_price, 2, '0.00')}
            </p>
          </>
        );
      case 'loser':
        return (
          <>
            <p className="text-lg font-bold text-red-600 dark:text-red-400">
              {formatPercentage(safeChangePercent, 2, '0.00%')}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{safeToFixed(item.current_price, 2, '0.00')}
            </p>
          </>
        );
      case 'volume':
        return (
          <>
            <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
              {safeToFixed(safeVolume / 1000000, 1, '0.0')}M
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{safeToFixed(item.current_price, 2, '0.00')}
            </p>
          </>
        );
      case 'prediction':
        return (
          <>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              +{formatPercentage(safePredictedChange, 2, '0.00%')}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              信頼度: {safeToFixed(safeConfidence * 100, 0, '0')}%
            </p>
          </>
        );
    }
  };

  return (
    <div
      onClick={onClick}
      className="p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-label={`${item.symbol} ${item.company_name}の詳細を見る`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
            <span className="font-mono text-blue-600 dark:text-blue-400 font-semibold">
              {item.symbol}
            </span>
            {/* Phase 4-3: セクターバッジ */}
            {item.sector && (
              <SectorBadge sector={item.sector} size="sm" />
            )}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
            {item.company_name}
          </p>
        </div>
        <div className="text-right ml-2">
          {getValueDisplay()}
        </div>
      </div>
    </div>
  );
});

RankingCard.displayName = 'RankingCard';

export default RankingCard;
