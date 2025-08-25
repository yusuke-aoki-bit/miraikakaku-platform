'use client';

import React, { useState } from 'react';
import { Brain, Zap, Info } from 'lucide-react';
import StockSelector from '@/components/predictions/StockSelector';
import InteractivePredictionChart from '@/components/predictions/InteractivePredictionChart';
import ModelPerformanceDashboard from '@/components/predictions/ModelPerformanceDashboard';
import PredictionDataTable from '@/components/predictions/PredictionDataTable';
import AIDecisionFactorsModal from '@/components/ai/AIDecisionFactorsModal';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
  market: string;
  current_price: number;
  change_percent: number;
}

export default function PredictionsPage() {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [aiFactorsModal, setAiFactorsModal] = useState({
    isOpen: false,
    predictionId: '',
    symbol: '',
    companyName: ''
  });

  const handleShowAIFactors = (predictionId: string, symbol: string, companyName: string) => {
    setAiFactorsModal({
      isOpen: true,
      predictionId,
      symbol,
      companyName
    });
  };

  const closeAIFactorsModal = () => {
    setAiFactorsModal({
      isOpen: false,
      predictionId: '',
      symbol: '',
      companyName: ''
    });
  };

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Brain className="w-8 h-8 mr-3 text-purple-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">AI個別銘柄予測</h1>
            <p className="text-sm text-gray-400 mt-1">
              複数のAIモデルによる高精度な株価予測と詳細な分析データ
            </p>
          </div>
        </div>
        
        {selectedStock && (
          <div className="text-right">
            <div className="text-sm text-gray-400">選択中の銘柄</div>
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
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6">
          <div className="flex items-start space-x-4">
            <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                AI予測システムの特徴
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-300">
                <div>
                  <div className="flex items-center mb-2">
                    <Zap className="w-4 h-4 text-yellow-400 mr-2" />
                    <span className="font-medium">複数AI統合</span>
                  </div>
                  <p>LSTM、VertexAI、RandomForest、XGBoostの4つの異なるAIモデルから最適な予測を提供</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <Brain className="w-4 h-4 text-purple-400 mr-2" />
                    <span className="font-medium">高精度予測</span>
                  </div>
                  <p>過去のバックテストで平均85%以上の精度を達成。リアルタイムデータによる継続的な学習</p>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <Info className="w-4 h-4 text-blue-400 mr-2" />
                    <span className="font-medium">透明性</span>
                  </div>
                  <p>各モデルの性能指標、信頼度、予測根拠を詳細に表示。投資判断に必要な情報を全て提供</p>
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
        <div className="space-y-6">
          {/* 予測チャート */}
          <InteractivePredictionChart stock={selectedStock} />

          {/* 2カラムレイアウト：モデル比較とデータテーブル */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
            {/* モデルパフォーマンス */}
            <div className="xl:col-span-7">
              <ModelPerformanceDashboard stock={selectedStock} />
            </div>

            {/* 予測データテーブル */}
            <div className="xl:col-span-5">
              <PredictionDataTable 
                stock={selectedStock} 
                onShowAIFactors={handleShowAIFactors}
              />
            </div>
          </div>

          {/* 追加情報・注意事項 */}
          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
            <div className="flex items-start space-x-3">
              <Info className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-400 mb-2">投資判断に関する重要な注意事項</h4>
                <div className="text-sm text-gray-300 space-y-2">
                  <p>
                    • AI予測は過去のデータパターンに基づく統計的予測であり、実際の市場動向を保証するものではありません。
                  </p>
                  <p>
                    • 市場は多くの予測不可能な要因に影響されるため、予測と実際の結果には差異が生じる可能性があります。
                  </p>
                  <p>
                    • 投資判断は複数の情報源を総合的に検討し、リスク管理を適切に行った上で、最終的にご自身の責任で決定してください。
                  </p>
                  <p>
                    • 信頼度が高い予測であっても、必ずしも確実な結果を意味するものではないことをご理解ください。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-20">
          <Brain className="w-24 h-24 text-gray-600 mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            分析を開始してください
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            上の検索バーから分析したい銘柄を選択すると、<br />
            AIによる多角的な予測分析が開始されます。<br />
            複数のモデルによる統合予測をご活用ください。
          </p>
          
          {/* おすすめ銘柄 */}
          <div className="mt-8 max-w-2xl mx-auto">
            <div className="text-sm text-gray-400 mb-4">人気の分析銘柄</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { symbol: 'AAPL', name: 'Apple Inc.' },
                { symbol: '7203', name: 'トヨタ自動車' },
                { symbol: 'GOOGL', name: 'Alphabet' },
                { symbol: '6758', name: 'ソニーグループ' }
              ].map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={async () => {
                    // 実際のAPIから株式データを取得
                    try {
                      const response = await apiClient.request(`/api/finance/stocks/${stock.symbol}/price?limit=1`);
                      const priceData = response.data?.[0];
                      setSelectedStock({
                        symbol: stock.symbol,
                        company_name: stock.name,
                        market: stock.symbol.match(/^[A-Z]+$/) ? 'NASDAQ' : 'TSE',
                        current_price: priceData?.close_price || priceData?.price || 1000,
                        change_percent: priceData?.change_percent || 0
                      });
                    } catch (error) {
                      // API失敗時のフォールバック（固定値）
                      const defaultPrices: { [key: string]: number } = {
                        'AAPL': 175.50,
                        '7203': 2850,
                        'GOOGL': 142.50,
                        '6758': 13200
                      };
                      setSelectedStock({
                        symbol: stock.symbol,
                        company_name: stock.name,
                        market: stock.symbol.match(/^[A-Z]+$/) ? 'NASDAQ' : 'TSE',
                        current_price: defaultPrices[stock.symbol] || 1000,
                        change_percent: 0
                      });
                    }
                  }}
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

      {/* AI判断根拠モーダル */}
      <AIDecisionFactorsModal
        predictionId={aiFactorsModal.predictionId}
        symbol={aiFactorsModal.symbol}
        companyName={aiFactorsModal.companyName}
        isOpen={aiFactorsModal.isOpen}
        onClose={closeAIFactorsModal}
      />
    </div>
  );
}