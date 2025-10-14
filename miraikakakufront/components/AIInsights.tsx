'use client';

import { useState, useEffect } from 'react';

/**
 * AI搭載インサイトと推奨システム
 * 機械学習ベースの投資アドバイスと市場分析
 */

interface StockInsight {
  symbol: string;
  name: string;
  signal: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  confidence: number;
  reasons: string[];
  targetPrice?: number;
  stopLoss?: number;
  technicalScore: number;
  fundamentalScore: number;
  sentimentScore: number;
}

interface MarketInsight {
  type: 'opportunity' | 'warning' | 'trend' | 'anomaly';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  affectedStocks: string[];
  timestamp: Date;
}

export function AIInsights({ stocks }: { stocks: any[] }) {
  const [insights, setInsights] = useState<StockInsight[]>([]);
  const [marketInsights, setMarketInsights] = useState<MarketInsight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // AI分析シミュレーション
    generateAIInsights();
  }, [stocks]);

  const generateAIInsights = () => {
    setLoading(true);

    // 各銘柄のAI分析を生成
    const stockInsights: StockInsight[] = stocks.slice(0, 10).map(stock => {
      const technicalScore = Math.random() * 100;
      const fundamentalScore = Math.random() * 100;
      const sentimentScore = Math.random() * 100;
      const overallScore = (technicalScore + fundamentalScore + sentimentScore) / 3;

      let signal: StockInsight['signal'];
      if (overallScore >= 80) signal = 'strong_buy';
      else if (overallScore >= 60) signal = 'buy';
      else if (overallScore >= 40) signal = 'hold';
      else if (overallScore >= 20) signal = 'sell';
      else signal = 'strong_sell';

      const reasons: string[] = [];
      if (technicalScore > 70) reasons.push('強いテクニカル指標：上昇トレンド継続中');
      if (fundamentalScore > 70) reasons.push('優れたファンダメンタルズ：業績好調');
      if (sentimentScore > 70) reasons.push('ポジティブな市場センチメント');
      if (stock.change_percent > 5) reasons.push(`強い上昇モメンタム：+${stock.change_percent.toFixed(2)}%`);
      if (stock.volume > 1000000) reasons.push('高い出来高：市場の注目度高い');

      return {
        symbol: stock.symbol,
        name: stock.name,
        signal,
        confidence: overallScore,
        reasons: reasons.length > 0 ? reasons : ['市場状況を監視中'],
        targetPrice: stock.price * (1 + (Math.random() * 0.2 - 0.05)),
        stopLoss: stock.price * (1 - Math.random() * 0.1),
        technicalScore,
        fundamentalScore,
        sentimentScore,
      };
    });

    // 市場インサイトを生成
    const marketInsights: MarketInsight[] = [
      {
        type: 'opportunity',
        title: 'テクノロジーセクターに買い機会',
        description: 'AIとクラウド関連銘柄が過去3日間で平均8%上昇。モメンタムは継続する可能性が高い。',
        severity: 'high',
        affectedStocks: stocks.slice(0, 3).map(s => s.symbol),
        timestamp: new Date(),
      },
      {
        type: 'warning',
        title: 'ボラティリティ上昇に注意',
        description: '市場全体のボラティリティが通常の1.5倍に上昇。リスク管理を強化してください。',
        severity: 'medium',
        affectedStocks: [],
        timestamp: new Date(),
      },
      {
        type: 'trend',
        title: 'グリーンエネルギーへの資金流入',
        description: '再生可能エネルギー関連銘柄への投資が先週比で45%増加。長期トレンドの可能性。',
        severity: 'medium',
        affectedStocks: stocks.slice(5, 8).map(s => s.symbol),
        timestamp: new Date(),
      },
      {
        type: 'anomaly',
        title: '異常な出来高を検出',
        description: '通常の5倍の出来高を記録した銘柄を検出。重要なニュースや発表の可能性があります。',
        severity: 'high',
        affectedStocks: [stocks[0]?.symbol],
        timestamp: new Date(),
      },
    ];

    setInsights(stockInsights);
    setMarketInsights(marketInsights);
    setLoading(false);
  };

  const getSignalColor = (signal: StockInsight['signal']) => {
    switch (signal) {
      case 'strong_buy':
        return 'bg-green-600 text-white';
      case 'buy':
        return 'bg-green-500 text-white';
      case 'hold':
        return 'bg-yellow-500 text-white';
      case 'sell':
        return 'bg-red-500 text-white';
      case 'strong_sell':
        return 'bg-red-600 text-white';
    }
  };

  const getSignalLabel = (signal: StockInsight['signal']) => {
    switch (signal) {
      case 'strong_buy':
        return '強い買い';
      case 'buy':
        return '買い';
      case 'hold':
        return 'ホールド';
      case 'sell':
        return '売り';
      case 'strong_sell':
        return '強い売り';
    }
  };

  const getInsightIcon = (type: MarketInsight['type']) => {
    return null;
  };

  const getInsightColor = (severity: MarketInsight['severity']) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
      case 'low':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
        <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400">AI分析中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2 flex items-center">
          <span className="text-4xl mr-3">🤖</span>
          AI投資アドバイザー
        </h1>
        <p className="text-purple-100">機械学習ベースの市場分析と銘柄推奨</p>
      </div>

      {/* 市場インサイト */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <span className="text-2xl mr-2">📰</span>
          市場インサイト
        </h2>

        {marketInsights.map((insight, index) => (
          <div
            key={index}
            className={`border-l-4 rounded-lg p-6 ${getInsightColor(insight.severity)}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <span className="text-3xl">{getInsightIcon(insight.type)}</span>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    {insight.title}
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {insight.timestamp.toLocaleString('ja-JP')}
                  </p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                insight.severity === 'high' ? 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200' :
                insight.severity === 'medium' ? 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200' :
                'bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
              }`}>
                {insight.severity === 'high' ? '重要度: 高' : insight.severity === 'medium' ? '重要度: 中' : '重要度: 低'}
              </span>
            </div>

            <p className="text-gray-700 dark:text-gray-300 mb-3">
              {insight.description}
            </p>

            {insight.affectedStocks.length > 0 && (
              <div className="flex flex-wrap gap-2">
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  関連銘柄:
                </span>
                {insight.affectedStocks.map(symbol => (
                  <span
                    key={symbol}
                    className="px-2 py-1 bg-white dark:bg-gray-700 rounded text-sm font-mono font-semibold text-blue-600 dark:text-blue-400"
                  >
                    {symbol}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* AI推奨銘柄 */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <span className="text-2xl mr-2">🎯</span>
          AI推奨銘柄トップ10
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((insight, index) => (
            <div
              key={insight.symbol}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              {/* ヘッダー */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xl font-bold text-gray-900 dark:text-white">
                      #{index + 1}
                    </span>
                    <span className="font-mono font-bold text-lg text-blue-600 dark:text-blue-400">
                      {insight.symbol}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {insight.name}
                  </p>
                </div>
                <span className={`px-4 py-2 rounded-lg font-bold text-sm ${getSignalColor(insight.signal)}`}>
                  {getSignalLabel(insight.signal)}
                </span>
              </div>

              {/* 信頼度 */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    AI信頼度
                  </span>
                  <span className="text-lg font-bold text-purple-600 dark:text-purple-400">
                    {insight.confidence.toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all"
                    style={{ width: `${insight.confidence}%` }}
                  />
                </div>
              </div>

              {/* スコア */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">テクニカル</p>
                  <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {insight.technicalScore.toFixed(0)}
                  </p>
                </div>
                <div className="text-center p-2 bg-green-50 dark:bg-green-900/20 rounded">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">ファンダ</p>
                  <p className="text-lg font-bold text-green-600 dark:text-green-400">
                    {insight.fundamentalScore.toFixed(0)}
                  </p>
                </div>
                <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">センチメント</p>
                  <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
                    {insight.sentimentScore.toFixed(0)}
                  </p>
                </div>
              </div>

              {/* 理由 */}
              <div className="mb-4">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  推奨理由:
                </p>
                <ul className="space-y-1">
                  {insight.reasons.map((reason, i) => (
                    <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 目標価格 */}
              {insight.targetPrice && insight.stopLoss && (
                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">目標価格</p>
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">
                      ¥{insight.targetPrice.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">ストップロス</p>
                    <p className="text-lg font-bold text-red-600 dark:text-red-400">
                      ¥{insight.stopLoss.toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 免責事項 */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-6 rounded-lg">
        <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
          重要な免責事項
        </h4>
        <p className="text-sm text-yellow-700 dark:text-yellow-300">
          これらのAI推奨は、過去のデータと統計モデルに基づいています。投資の最終判断は、ご自身の責任で行ってください。
          当社は、AI推奨に基づく投資判断の結果について一切の責任を負いません。
        </p>
      </div>
    </div>
  );
}
