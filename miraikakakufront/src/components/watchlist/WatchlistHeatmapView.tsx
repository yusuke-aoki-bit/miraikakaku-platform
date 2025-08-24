'use client';

import React, { useMemo, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  market_cap?: number;
  ai_score?: number;
  volume?: number;
}

interface WatchlistHeatmapViewProps {
  stocks: WatchlistStock[];
  onStockClick: (symbol: string) => void;
  loading?: boolean;
}

interface TreemapItem {
  symbol: string;
  company_name: string;
  change_percent: number;
  market_cap: number;
  current_price: number;
  ai_score?: number;
  volume?: number;
  size: number; // 相対サイズ（0-1）
  color: string; // CSS カラー
  width: number; // 実際の幅（%）
  height: number; // 実際の高さ（%）
  x: number; // X座標（%）
  y: number; // Y座標（%）
}

export default function WatchlistHeatmapView({
  stocks,
  onStockClick,
  loading = false
}: WatchlistHeatmapViewProps) {
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [tooltipData, setTooltipData] = useState<{
    stock: WatchlistStock;
    x: number;
    y: number;
  } | null>(null);

  // 株価変動率に基づく色計算
  const getColorFromChange = (changePercent: number): string => {
    const intensity = Math.min(Math.abs(changePercent) / 5, 1); // 5%で最大強度
    
    if (changePercent > 0) {
      // 緑色 - 上昇
      const opacity = 0.2 + intensity * 0.6; // 0.2-0.8の範囲
      return `rgba(34, 197, 94, ${opacity})`;
    } else if (changePercent < 0) {
      // 赤色 - 下落
      const opacity = 0.2 + intensity * 0.6; // 0.2-0.8の範囲
      return `rgba(239, 68, 68, ${opacity})`;
    } else {
      // グレー - 変動なし
      return 'rgba(107, 114, 128, 0.3)';
    }
  };

  // ツリーマップレイアウト計算
  const treemapData = useMemo(() => {
    if (stocks.length === 0) return [];

    // 時価総額でフィルタリング（データがある銘柄のみ）
    const stocksWithMarketCap = stocks.filter(stock => stock.market_cap && stock.market_cap > 0);
    
    if (stocksWithMarketCap.length === 0) {
      // 時価総額データがない場合は均等サイズ
      const equalSize = 1 / stocks.length;
      return stocks.map((stock, index) => ({
        ...stock,
        market_cap: 100000000, // デフォルト値
        size: equalSize,
        color: getColorFromChange(stock.change_percent),
        width: 100 / Math.ceil(Math.sqrt(stocks.length)),
        height: 100 / Math.ceil(stocks.length / Math.ceil(Math.sqrt(stocks.length))),
        x: (index % Math.ceil(Math.sqrt(stocks.length))) * (100 / Math.ceil(Math.sqrt(stocks.length))),
        y: Math.floor(index / Math.ceil(Math.sqrt(stocks.length))) * (100 / Math.ceil(stocks.length / Math.ceil(Math.sqrt(stocks.length))))
      }));
    }

    // 時価総額の合計を計算
    const totalMarketCap = stocksWithMarketCap.reduce((sum, stock) => sum + (stock.market_cap || 0), 0);

    // 相対サイズを計算
    const stocksWithSize = stocksWithMarketCap.map(stock => ({
      ...stock,
      size: (stock.market_cap || 0) / totalMarketCap,
      color: getColorFromChange(stock.change_percent)
    }));

    // サイズでソート（大きい順）
    stocksWithSize.sort((a, b) => b.size - a.size);

    // 簡易ツリーマップレイアウト算出
    const items: TreemapItem[] = [];
    let currentX = 0;
    let currentY = 0;
    let rowHeight = 0;
    const containerWidth = 100;
    const containerHeight = 100;

    stocksWithSize.forEach((stock, index) => {
      // アスペクト比を考慮したサイズ計算
      const area = stock.size * containerWidth * containerHeight;
      const width = Math.sqrt(area * 1.6); // 1.6:1のアスペクト比を目指す
      const height = area / width;

      // 行に収まるかチェック
      if (currentX + width > containerWidth && index > 0) {
        currentX = 0;
        currentY += rowHeight;
        rowHeight = 0;
      }

      // 残りスペースに合わせて調整
      const remainingWidth = containerWidth - currentX;
      const remainingHeight = containerHeight - currentY;
      
      const finalWidth = Math.min(width, remainingWidth);
      const finalHeight = Math.min(height, remainingHeight);

      items.push({
        ...stock,
        width: finalWidth,
        height: finalHeight,
        x: currentX,
        y: currentY
      });

      currentX += finalWidth;
      rowHeight = Math.max(rowHeight, finalHeight);

      // 次の行への準備
      if (currentX >= containerWidth * 0.9) { // 90%で改行
        currentX = 0;
        currentY += rowHeight;
        rowHeight = 0;
      }
    });

    return items;
  }, [stocks]);

  const handleStockHover = (event: React.MouseEvent, stock: WatchlistStock) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipData({
      stock,
      x: event.clientX,
      y: event.clientY
    });
  };

  const handleStockLeave = () => {
    setTooltipData(null);
  };

  const formatMarketCap = (marketCap: number): string => {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(1)}兆円`;
    } else if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(0)}億円`;
    } else {
      return `${(marketCap / 100000000).toFixed(1)}億円`;
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="h-96 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-400 border-t-transparent"></div>
          <span className="ml-4 text-gray-400">ヒートマップを生成中...</span>
        </div>
      </div>
    );
  }

  if (stocks.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-12 text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gray-800/50 rounded-full flex items-center justify-center">
          <span className="text-4xl text-gray-600">🗺️</span>
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">
          ウォッチリストは空です
        </h3>
        <p className="text-gray-400">
          銘柄を追加してヒートマップで全体のパフォーマンスを確認しましょう
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヒートマップの説明 */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-blue-300 mb-1">ヒートマップの見方</h4>
            <p className="text-xs text-blue-200/80">
              • <strong>面積の大きさ</strong>: 時価総額（大きいほど時価総額が高い）<br/>
              • <strong>色の濃さ</strong>: 今日の変動率（緑=上昇、赤=下落、濃いほど変動幅が大きい）
            </p>
          </div>
        </div>
      </div>

      {/* ヒートマップ */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="relative w-full" style={{ height: '500px' }}>
          <svg width="100%" height="100%" className="absolute inset-0">
            {treemapData.map((item) => (
              <g key={item.symbol}>
                {/* 背景矩形 */}
                <rect
                  x={`${item.x}%`}
                  y={`${item.y}%`}
                  width={`${item.width}%`}
                  height={`${item.height}%`}
                  fill={item.color}
                  stroke="rgba(75, 85, 99, 0.5)"
                  strokeWidth="1"
                  rx="4"
                  className={`transition-all duration-200 cursor-pointer ${
                    selectedStock === item.symbol ? 'stroke-blue-400 stroke-2' : 'hover:stroke-gray-400'
                  }`}
                  onClick={() => {
                    setSelectedStock(item.symbol);
                    onStockClick(item.symbol);
                  }}
                  onMouseEnter={(e) => handleStockHover(e as any, item)}
                  onMouseLeave={handleStockLeave}
                />

                {/* テキストラベル（サイズに応じて表示を調整） */}
                {item.width > 15 && item.height > 10 && (
                  <g>
                    {/* シンボル */}
                    <text
                      x={`${item.x + item.width / 2}%`}
                      y={`${item.y + item.height / 2 - 1}%`}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="fill-white font-bold text-sm pointer-events-none"
                      style={{ fontSize: `${Math.min(item.width / 8, item.height / 4, 16)}px` }}
                    >
                      {item.symbol}
                    </text>
                    
                    {/* 変動率 */}
                    {item.width > 20 && item.height > 15 && (
                      <text
                        x={`${item.x + item.width / 2}%`}
                        y={`${item.y + item.height / 2 + 3}%`}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className={`font-medium text-xs pointer-events-none ${
                          item.change_percent > 0 ? 'fill-green-200' :
                          item.change_percent < 0 ? 'fill-red-200' : 'fill-gray-300'
                        }`}
                        style={{ fontSize: `${Math.min(item.width / 12, item.height / 6, 12)}px` }}
                      >
                        {item.change_percent > 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                      </text>
                    )}
                  </g>
                )}
              </g>
            ))}
          </svg>
        </div>

        {/* 凡例 */}
        <div className="mt-6 flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-400 rounded"></div>
              <span className="text-gray-400">上昇</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-400 rounded"></div>
              <span className="text-gray-400">下落</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gray-500 rounded"></div>
              <span className="text-gray-400">変動なし</span>
            </div>
          </div>
          
          <div className="text-gray-400">
            合計 {stocks.length} 銘柄
          </div>
        </div>
      </div>

      {/* パフォーマンスサマリー */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 最大上昇 */}
        {(() => {
          const topGainer = stocks.reduce((max, stock) => 
            (stock.change_percent > max.change_percent) ? stock : max, stocks[0]
          );
          
          return (
            <div className="bg-gradient-to-r from-green-900/20 to-green-800/20 border border-green-500/30 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <span className="text-sm text-green-400 font-medium">最大上昇</span>
              </div>
              <div className="text-lg font-bold text-white">{topGainer?.symbol}</div>
              <div className="text-sm text-gray-400">{topGainer?.company_name}</div>
              <div className="text-lg font-bold text-green-400 mt-1">
                +{topGainer?.change_percent.toFixed(2)}%
              </div>
            </div>
          );
        })()}

        {/* 最大下落 */}
        {(() => {
          const topLoser = stocks.reduce((min, stock) => 
            (stock.change_percent < min.change_percent) ? stock : min, stocks[0]
          );
          
          return (
            <div className="bg-gradient-to-r from-red-900/20 to-red-800/20 border border-red-500/30 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingDown className="w-5 h-5 text-red-400" />
                <span className="text-sm text-red-400 font-medium">最大下落</span>
              </div>
              <div className="text-lg font-bold text-white">{topLoser?.symbol}</div>
              <div className="text-sm text-gray-400">{topLoser?.company_name}</div>
              <div className="text-lg font-bold text-red-400 mt-1">
                {topLoser?.change_percent.toFixed(2)}%
              </div>
            </div>
          );
        })()}

        {/* 平均パフォーマンス */}
        {(() => {
          const avgPerformance = stocks.reduce((sum, stock) => sum + stock.change_percent, 0) / stocks.length;
          
          return (
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Minus className="w-5 h-5 text-gray-400" />
                <span className="text-sm text-gray-400 font-medium">平均パフォーマンス</span>
              </div>
              <div className="text-lg font-bold text-white">ウォッチリスト全体</div>
              <div className="text-sm text-gray-400">{stocks.length} 銘柄平均</div>
              <div className={`text-lg font-bold mt-1 ${
                avgPerformance > 0 ? 'text-green-400' :
                avgPerformance < 0 ? 'text-red-400' : 'text-gray-400'
              }`}>
                {avgPerformance > 0 ? '+' : ''}{avgPerformance.toFixed(2)}%
              </div>
            </div>
          );
        })()}
      </div>

      {/* ツールチップ */}
      {tooltipData && (
        <div
          className="fixed z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-3 pointer-events-none"
          style={{
            left: tooltipData.x + 10,
            top: tooltipData.y - 10,
            transform: 'translateY(-100%)'
          }}
        >
          <div className="text-white font-semibold">{tooltipData.stock.symbol}</div>
          <div className="text-gray-400 text-sm">{tooltipData.stock.company_name}</div>
          <div className="flex items-center space-x-4 mt-2 text-sm">
            <div>
              <span className="text-gray-400">株価: </span>
              <span className="text-white">¥{tooltipData.stock.current_price.toLocaleString()}</span>
            </div>
            <div className={tooltipData.stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}>
              {tooltipData.stock.change_percent >= 0 ? '+' : ''}{tooltipData.stock.change_percent.toFixed(2)}%
            </div>
          </div>
          {tooltipData.stock.market_cap && (
            <div className="text-sm mt-1">
              <span className="text-gray-400">時価総額: </span>
              <span className="text-white">{formatMarketCap(tooltipData.stock.market_cap)}</span>
            </div>
          )}
          {tooltipData.stock.ai_score && (
            <div className="text-sm mt-1">
              <span className="text-gray-400">AIスコア: </span>
              <span className="text-white">{tooltipData.stock.ai_score}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}