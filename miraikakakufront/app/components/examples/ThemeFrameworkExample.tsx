'use client';

import { useState } from 'react';
import { TrendingUp, TrendingDown, Target, Calendar, Activity, Search } from 'lucide-react';

// Theme Framework Implementation Example

export default function ThemeFrameworkExample() {
  const [selectedStock, setSelectedStock] = useState('AAPL');
  const [searchQuery, setSearchQuery] = useState('');
  // Sample data
  const stockData = {
    symbol: 'AAPL',
    company: 'Apple Inc.',
    currentPrice: 175.43,
    change: 2.35,
    changePercent: 1.36,
    high52w: 198.23,
    low52w: 124.17,
    predictions: [
      { date: '2024-01-20', price: 178.50, confidence: 0.85, type: 'LSTM' },
      { date: '2024-01-21', price: 181.20, confidence: 0.82, type: 'GRU' },
      { date: '2024-01-22', price: 176.80, confidence: 0.79, type: 'Transformer' }
    ],
    priceHistory: [
      { date: '2024-01-15', open: 172.50, high: 174.20, low: 171.80, close: 173.90, volume: 58234567 },
      { date: '2024-01-16', open: 174.10, high: 176.30, low: 173.50, close: 175.43, volume: 62145890 },
      { date: '2024-01-17', open: 175.60, high: 177.80, low: 174.90, close: 176.25, volume: 55987432 }
    ]
  };

  const rankings = [
    { rank: 1, symbol: 'VET-USD', company: 'VeChain USD', currentPrice: 0.0229, predictedPrice: 0.0236, change: 3.06, confidence: 74.76 },
    { rank: 2, symbol: 'TRX-USD', company: 'TRON USD', currentPrice: 0.3353, predictedPrice: 0.3431, change: 2.33, confidence: 74.12 },
    { rank: 3, symbol: 'AAPL', company: 'Apple Inc.', currentPrice: 175.43, predictedPrice: 178.50, change: 1.75, confidence: 85.20 }
  ];

  return (
    <div className="theme-page">
      <div className="theme-container pt-8">

        {/* Header Section */}
        <div className="theme-section">
          <h1 className="theme-heading-xl mb-4">株価予測システム</h1>
          <p className="theme-caption">
            最新のAI技術を活用した株価予測とリアルタイム分析
          </p>
          <p className="theme-text-secondary mt-2">
            選択中の銘柄: {selectedStock}
          </p>
        </div>

        {/* Search Section */}
        <div className="theme-section">
          <h2 className="theme-heading-md mb-4">銘柄検索</h2>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 theme-text-secondary" />
            </div>
            <input
              type="text"
              className="theme-input pl-10"
              placeholder="銘柄コードまたは会社名を入力..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Rankings Section */}
        <div className="theme-section">
          <div className="flex items-center justify-between mb-6">
            <h2 className="theme-heading-md">🏆 高信頼度予測ランキング</h2>
            <div className="theme-badge-success">
              🔗 DB実データ
            </div>
          </div>

          <div className="space-y-4">
            {rankings.map((stock) => (
              <button
                key={stock.symbol}
                className="theme-ranking-card w-full text-left"
                onClick={() => setSelectedStock(stock.symbol)}
              >
                <div className="space-y-3">
                  {/* Row 1: Rank, Company Name */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="theme-ranking-number">{stock.rank}</span>
                      <div className="min-w-0 flex-1">
                        <span className="theme-ranking-company" title={stock.company}>
                          {stock.company}
                        </span>
                        <span className="theme-ranking-symbol block">
                          {stock.symbol}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Row 2: Price Info and Performance */}
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="theme-caption mb-1">
                        現在価格 → 予測価格
                      </div>
                      <div className="theme-ranking-price">
                        ${stock.currentPrice.toFixed(4)} → ${stock.predictedPrice.toFixed(4)}
                      </div>
                    </div>

                    <div className="text-right ml-6">
                      <div className={stock.change >= 0 ? 'theme-ranking-change-positive' : 'theme-ranking-change-negative'}>
                        {stock.change >= 0 ? (
                          <TrendingUp className="w-5 h-5 mr-1" />
                        ) : (
                          <TrendingDown className="w-5 h-5 mr-1" />
                        )}
                        +{stock.change.toFixed(2)}%
                      </div>
                      <div className="theme-caption flex items-center justify-end mt-1">
                        <Target className="w-4 h-4 mr-1" />
                        信頼度: {stock.confidence.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Stock Details Section */}
        <div className="theme-stock-header">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="theme-heading-xl mb-2">
                {stockData.symbol}
              </h1>
              <p className="theme-body mb-4 md:mb-0">
                {stockData.company}
              </p>
            </div>
            <div className="text-right">
              <div className="theme-heading-xl mb-1">
                ${stockData.currentPrice.toFixed(2)}
              </div>
              <div className={`flex items-center justify-end ${
                stockData.change >= 0 ? 'theme-status-success' : 'theme-status-error'
              }`}>
                {stockData.change >= 0 ? (
                  <TrendingUp className="w-5 h-5 mr-1" />
                ) : (
                  <TrendingDown className="w-5 h-5 mr-1" />
                )}
                <span className="theme-body">
                  ${Math.abs(stockData.change).toFixed(2)} ({stockData.changePercent >= 0 ? '+' : ''}{stockData.changePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="theme-stock-metrics">
          <div className="theme-stock-metric-card">
            <div className="flex items-center">
              <TrendingUp className="theme-stock-metric-icon text-green-500" />
              <div>
                <p className="theme-stock-metric-label">52週高値</p>
                <p className="theme-stock-metric-value">${stockData.high52w.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="theme-stock-metric-card">
            <div className="flex items-center">
              <TrendingDown className="w-5 h-5 mr-2 text-red-500" />
              <div>
                <p className="theme-stock-metric-label">52週安値</p>
                <p className="theme-stock-metric-value">${stockData.low52w.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="theme-stock-metric-card">
            <div className="flex items-center">
              <Activity className="theme-stock-metric-icon" />
              <div>
                <p className="theme-stock-metric-label">価格履歴</p>
                <p className="theme-stock-metric-value">{stockData.priceHistory.length}日分</p>
              </div>
            </div>
          </div>

          <div className="theme-stock-metric-card">
            <div className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" style={{ color: 'rgb(var(--theme-accent))' }} />
              <div>
                <p className="theme-stock-metric-label">AI予測</p>
                <p className="theme-stock-metric-value">{stockData.predictions.length}件</p>
              </div>
            </div>
          </div>
        </div>

        {/* Predictions Section */}
        <div className="theme-section">
          <h2 className="theme-heading-md mb-4">AI予測</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stockData.predictions.map((prediction, index) => (
              <div key={index} className="theme-card">
                <div className="flex justify-between items-center mb-2">
                  <span className="theme-caption">予測日</span>
                  <span className="theme-body font-medium">{prediction.date}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="theme-caption">予測価格</span>
                  <span className="theme-body font-bold">
                    ${prediction.price.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="theme-caption">信頼度</span>
                  <span className="theme-body font-medium">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="theme-caption">モデル</span>
                  <span className="theme-body font-medium">{prediction.type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Price History Table */}
        <div className="theme-section">
          <h2 className="theme-heading-md mb-4">価格履歴</h2>
          <div className="overflow-x-auto">
            <table className="theme-table">
              <thead className="theme-table-header">
                <tr>
                  <th>日付</th>
                  <th>始値</th>
                  <th>高値</th>
                  <th>安値</th>
                  <th>終値</th>
                  <th>出来高</th>
                </tr>
              </thead>
              <tbody>
                {stockData.priceHistory.map((item, index) => (
                  <tr key={index} className="theme-table-row">
                    <td className="theme-table-cell">{item.date}</td>
                    <td className="theme-table-cell">${item.open.toFixed(2)}</td>
                    <td className="theme-table-cell text-green-500">${item.high.toFixed(2)}</td>
                    <td className="theme-table-cell text-red-500">${item.low.toFixed(2)}</td>
                    <td className="theme-table-cell font-medium">${item.close.toFixed(2)}</td>
                    <td className="theme-table-cell theme-text-secondary">{item.volume.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="theme-section">
          <div className="flex flex-wrap gap-4">
            <button className="theme-btn-primary">
              詳細分析を実行
            </button>
            <button className="theme-btn-secondary">
              アラートを設定
            </button>
            <button className="theme-btn-ghost">
              データをエクスポート
            </button>
          </div>
        </div>

        {/* Status Alerts */}
        <div className="space-y-4">
          <div className="theme-alert-success">
            <strong>✅ システム正常動作中:</strong> リアルタイムデータ更新が正常に機能しています。
          </div>

          <div className="theme-alert-info">
            <strong>ℹ️ 情報:</strong> 次回のAI予測更新は15分後に実行されます。
          </div>

          <div className="theme-alert-warning">
            <strong>⚠️ 注意:</strong> 一部の銘柄でデータ遅延が発生しています。
          </div>
        </div>

        {/* Loading and Status Components */}
        <div className="theme-section">
          <h2 className="theme-heading-md mb-4">ステータス表示例</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

            <div className="theme-card text-center">
              <div className="theme-spinner w-8 h-8 mx-auto mb-2"></div>
              <p className="theme-caption">データ読み込み中...</p>
            </div>

            <div className="theme-card">
              <div className="theme-badge-success mb-2">正常動作</div>
              <p className="theme-caption">API接続: 正常</p>
            </div>

            <div className="theme-card">
              <div className="theme-badge-warning mb-2">部分的遅延</div>
              <p className="theme-caption">バッチ処理: 遅延中</p>
            </div>

            <div className="theme-card">
              <div className="theme-badge-error mb-2">接続エラー</div>
              <p className="theme-caption">外部API: エラー</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}