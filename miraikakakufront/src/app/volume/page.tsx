'use client';

import React, { useState } from 'react';
import { BarChart3, Info, TrendingUp } from 'lucide-react';
import StockSelector from '@/components/predictions/StockSelector';
import VolumeAnalysisChart from '@/components/volume/VolumeAnalysisChart';
import VolumeInsightsPanel from '@/components/volume/VolumeInsightsPanel';

interface Stock {
  symbol: string;
  company_name: string;
  market: string;
  current_price: number;
  change_percent: number;
}

export default function VolumePage() {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <BarChart3 className="w-8 h-8 mr-3 text-green-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">出来高予測分析</h1>
            <p className="text-sm text-gray-400 mt-1">
              AIによる出来高パターン分析と未来予測で価格変動の前兆を捉える
            </p>
          </div>
        </div>
        
        {selectedStock && (
          <div className="text-right">
            <div className="text-sm text-gray-400">分析中の銘柄</div>
            <div className="text-xl font-bold text-white">
              {selectedStock.symbol}
            </div>
            <div className="text-sm text-gray-300">
              {selectedStock.company_name}
            </div>
          </div>
        )}
      </div>

      {/* 機能説明パネル */}
      {!selectedStock && (
        <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl p-6">
          <div className="flex items-start space-x-4">
            <Info className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                出来高分析の重要性
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-300">
                <div>
                  <div className="flex items-center mb-2">
                    <TrendingUp className="w-4 h-4 text-green-400 mr-2" />
                    <span className="font-medium">価格変動の先行指標</span>
                  </div>
                  <p>出来高の急増は大きな価格変動の前兆となることが多く、投資タイミングの重要な判断材料となります。</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <BarChart3 className="w-4 h-4 text-blue-400 mr-2" />
                    <span className="font-medium">機関投資家の動向</span>
                  </div>
                  <p>大口取引による出来高変化を分析することで、機関投資家の売買動向を把握できます。</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <Info className="w-4 h-4 text-purple-400 mr-2" />
                    <span className="font-medium">市場センチメント</span>
                  </div>
                  <p>出来高パターンから市場参加者の関心度や投資意欲の変化を読み取ることができます。</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 銘柄選択 */}
      <StockSelector
        selectedStock={selectedStock}
        onStockSelect={setSelectedStock}
      />

      {/* メインコンテンツ */}
      {selectedStock ? (
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* 出来高分析チャート */}
          <div className="xl:col-span-8">
            <VolumeAnalysisChart stock={selectedStock} />
          </div>

          {/* AI出来高インサイトパネル */}
          <div className="xl:col-span-4">
            <VolumeInsightsPanel stock={selectedStock} />
          </div>
        </div>
      ) : (
        <div className="text-center py-20">
          <BarChart3 className="w-24 h-24 text-gray-600 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            出来高分析を開始してください
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            上の検索バーから分析したい銘柄を選択すると、<br />
            価格と出来高の詳細な関係性分析が開始されます。<br />
            AI予測で投資機会を見つけましょう。
          </p>
          
          {/* おすすめ銘柄 */}
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="text-sm text-gray-400 mb-4">出来高分析におすすめの銘柄</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { symbol: 'TSLA', name: 'Tesla Inc.' },
                { symbol: '9984', name: 'ソフトバンクグループ' },
                { symbol: 'NVDA', name: 'NVIDIA Corp.' },
                { symbol: '7203', name: 'トヨタ自動車' }
              ].map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => setSelectedStock({
                    symbol: stock.symbol,
                    company_name: stock.name,
                    market: stock.symbol.match(/^[A-Z]+$/) ? 'NASDAQ' : 'TSE',
                    current_price: Math.random() * 2000 + 500,
                    change_percent: (Math.random() - 0.5) * 6
                  })}
                  className="p-3 bg-gray-800/30 hover:bg-gray-800/50 border border-gray-700/50 rounded-lg transition-all text-left"
                >
                  <div className="font-medium text-white text-sm">{stock.symbol}</div>
                  <div className="text-xs text-gray-400 mt-1">{stock.name}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 出来高分析の注意事項 */}
      {selectedStock && (
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-yellow-400 mb-2">出来高分析に関する注意事項</h4>
              <div className="text-sm text-gray-300 space-y-2">
                <p>
                  • 出来高は価格変動の重要な指標ですが、単独で投資判断を行うことは推奨されません。
                </p>
                <p>
                  • 市場の特殊事情（決算発表、ニュース等）により一時的に出来高が大幅に変動する場合があります。
                </p>
                <p>
                  • AI予測は過去のパターンに基づくものであり、将来の出来高を保証するものではありません。
                </p>
                <p>
                  • 出来高と価格の分析は他の技術指標や基本分析と組み合わせて総合的に判断してください。
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}