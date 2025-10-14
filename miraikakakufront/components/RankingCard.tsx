import React from 'react';
import { SectorBadge } from './SectorBadge';

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
    switch (type) {
      case 'gainer':
        return (
          <>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              +{item.change_percent?.toFixed(2)}%
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{item.current_price.toFixed(2)}
            </p>
          </>
        );
      case 'loser':
        return (
          <>
            <p className="text-lg font-bold text-red-600 dark:text-red-400">
              {item.change_percent?.toFixed(2)}%
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{item.current_price.toFixed(2)}
            </p>
          </>
        );
      case 'volume':
        return (
          <>
            <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
              {((item.volume || 0) / 1000000).toFixed(1)}M
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              ¥{item.current_price.toFixed(2)}
            </p>
          </>
        );
      case 'prediction':
        return (
          <>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              +{item.predicted_change?.toFixed(2)}%
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              信頼度: {((item.confidence_score || 0) * 100).toFixed(0)}%
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
