'use client';

import { ChartBarIcon } from '@heroicons/react/24/outline';
import StockMentionCard from './StockMentionCard';

interface StockData {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  context?: string;
}

interface RelatedStocksWidgetProps {
  stocks: StockData[];
  articleTitle: string;
  onWatchlistAdd?: (symbol: string) => void;
}

export default function RelatedStocksWidget({ 
  stocks, 
  articleTitle, 
  onWatchlistAdd 
}: RelatedStocksWidgetProps) {
  // 関連コンテキストを生成する関数
  const generateContext = (stock: StockData, title: string) => {
    // 記事タイトルと銘柄名から関連性の高そうなコンテキストを生成
    const contexts = [
      `${title}に関連する主要企業として注目されています`,
      `同社は業界内で重要な位置を占める企業です`,
      `この分野での事業展開により影響を受ける可能性があります`,
      `市場動向に敏感に反応する銘柄として知られています`,
      `業績への影響が期待される注目銘柄です`
    ];
    
    // 銘柄シンボルのハッシュ値を利用してコンテキストを選択
    const hash = stock.symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return contexts[hash % contexts.length];
  };

  // 株価パフォーマンスでソート（上昇率順）
  const sortedStocks = [...stocks].sort((a, b) => b.change_percent - a.change_percent);

  if (stocks.length === 0) {
    return (
      <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
        <div className="flex items-center mb-4">
          <ChartBarIcon className="h-5 w-5 text-accent-primary mr-2" />
          <h3 className="text-lg font-semibold text-text-primary">関連銘柄</h3>
        </div>
        
        <div className="text-center py-8">
          <div className="text-text-secondary text-sm">
            この記事に関連する銘柄情報はありません
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <ChartBarIcon className="h-5 w-5 text-accent-primary mr-2" />
          <h3 className="text-lg font-semibold text-text-primary">関連銘柄</h3>
        </div>
        <span className="text-sm text-text-secondary">
          {stocks.length}件
        </span>
      </div>

      {/* サマリー情報 */}
      <div className="mb-6 p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
        <h4 className="text-sm font-medium text-text-primary mb-2">
          この記事に関連する銘柄
        </h4>
        <p className="text-xs text-text-secondary">
          記事内容と関連性の高い銘柄の株価情報をリアルタイムで表示しています。
          詳細分析や投資判断にお役立てください。
        </p>
      </div>

      {/* パフォーマンス概要 */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-surface-background rounded-lg">
          <div className="text-xs text-text-secondary mb-1">上昇銘柄</div>
          <div className="text-lg font-semibold text-green-500">
            {stocks.filter(s => s.change_percent > 0).length}
          </div>
        </div>
        <div className="text-center p-3 bg-surface-background rounded-lg">
          <div className="text-xs text-text-secondary mb-1">下落銘柄</div>
          <div className="text-lg font-semibold text-red-500">
            {stocks.filter(s => s.change_percent < 0).length}
          </div>
        </div>
      </div>

      {/* 銘柄リスト */}
      <div className="space-y-4">
        {sortedStocks.map((stock, index) => (
          <StockMentionCard
            key={stock.symbol}
            stock={{
              ...stock,
              context: stock.context || generateContext(stock, articleTitle)
            }}
            onWatchlistAdd={onWatchlistAdd}
          />
        ))}
      </div>

      {/* フッター */}
      <div className="mt-6 pt-4 border-t border-border-primary">
        <div className="text-xs text-text-secondary text-center">
          <p className="mb-1">
            <span className="font-medium">投資判断に関する注意:</span>
          </p>
          <p>
            株価情報は参考情報であり、投資判断の根拠となることを意図したものではありません。
            投資はお客様ご自身の判断と責任で行ってください。
          </p>
        </div>
      </div>
    </div>
  );
}