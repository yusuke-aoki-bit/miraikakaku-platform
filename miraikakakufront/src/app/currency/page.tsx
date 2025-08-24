'use client';

import React, { useState } from 'react';
import CurrencyPairSelector from '@/components/currency/CurrencyPairSelector';
import CurrencyChart from '@/components/currency/CurrencyChart';
import CurrencyAIPredictionPanel from '@/components/currency/CurrencyAIPredictionPanel';
import EconomicCalendarWidget from '@/components/currency/EconomicCalendarWidget';
import { DollarSign, Globe, TrendingUp, AlertCircle } from 'lucide-react';

export default function CurrencyPage() {
  const [selectedPair, setSelectedPair] = useState('USD/JPY');
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1H' | '4H' | '1D' | '1W'>('1D');

  // モック通貨ペアデータ
  const currencyPairs = [
    { pair: 'USD/JPY', base: 'USD', quote: 'JPY', flag1: '🇺🇸', flag2: '🇯🇵', current: 150.23, change: 0.45, changePercent: 0.30 },
    { pair: 'EUR/USD', base: 'EUR', quote: 'USD', flag1: '🇪🇺', flag2: '🇺🇸', current: 1.0852, change: -0.0023, changePercent: -0.21 },
    { pair: 'GBP/JPY', base: 'GBP', quote: 'JPY', flag1: '🇬🇧', flag2: '🇯🇵', current: 190.45, change: 1.25, changePercent: 0.66 },
    { pair: 'EUR/JPY', base: 'EUR', quote: 'JPY', flag1: '🇪🇺', flag2: '🇯🇵', current: 163.12, change: 0.89, changePercent: 0.55 },
    { pair: 'AUD/USD', base: 'AUD', quote: 'USD', flag1: '🇦🇺', flag2: '🇺🇸', current: 0.6542, change: -0.0034, changePercent: -0.52 },
    { pair: 'USD/CHF', base: 'USD', quote: 'CHF', flag1: '🇺🇸', flag2: '🇨🇭', current: 0.8823, change: 0.0012, changePercent: 0.14 },
    { pair: 'GBP/USD', base: 'GBP', quote: 'USD', flag1: '🇬🇧', flag2: '🇺🇸', current: 1.2678, change: 0.0056, changePercent: 0.44 },
    { pair: 'USD/CAD', base: 'USD', quote: 'CAD', flag1: '🇺🇸', flag2: '🇨🇦', current: 1.3612, change: -0.0023, changePercent: -0.17 },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <DollarSign className="w-6 h-6 mr-2 text-green-400" />
          為替予測
        </h1>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1 bg-green-500/20 rounded-lg">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-400">リアルタイム更新中</span>
          </div>
        </div>
      </div>

      {/* マーケットサマリー */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <Globe className="w-5 h-5 text-blue-400" />
            <span className="text-xs text-blue-400">USD強気</span>
          </div>
          <div className="text-2xl font-bold text-white">DXY 104.5</div>
          <div className="text-sm text-gray-400">ドルインデックス</div>
          <div className="text-xs text-green-400 mt-1">+0.35%</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-xs text-green-400">↑</span>
          </div>
          <div className="text-2xl font-bold text-white">5/8</div>
          <div className="text-sm text-gray-400">上昇通貨ペア</div>
          <div className="text-xs text-gray-500 mt-1">主要8通貨</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            <span className="text-xs text-yellow-400">中</span>
          </div>
          <div className="text-2xl font-bold text-white">VIX 18.2</div>
          <div className="text-sm text-gray-400">ボラティリティ</div>
          <div className="text-xs text-yellow-400 mt-1">通常レベル</div>
        </div>

        <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-5 h-5 text-purple-400" />
            <span className="text-xs text-purple-400">AI予測</span>
          </div>
          <div className="text-2xl font-bold text-white">82.5%</div>
          <div className="text-sm text-gray-400">予測精度</div>
          <div className="text-xs text-purple-400 mt-1">過去30日平均</div>
        </div>
      </div>

      {/* 通貨ペアセレクター */}
      <CurrencyPairSelector
        pairs={currencyPairs}
        selectedPair={selectedPair}
        onPairChange={setSelectedPair}
      />

      {/* メインコンテンツ：左カラム（チャート）+ 右カラム（AI予測パネル） */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左カラム：チャート（幅 2/3） */}
        <div className="lg:col-span-2">
          <CurrencyChart
            pair={selectedPair}
            timeframe={selectedTimeframe}
            height={500}
            showControls={true}
            onTimeframeChange={(tf) => setSelectedTimeframe(tf as '1H' | '4H' | '1D' | '1W')}
          />
        </div>

        {/* 右カラム：AI予測パネル（幅 1/3） */}
        <div className="lg:col-span-1">
          <CurrencyAIPredictionPanel
            pair={selectedPair}
            timeframes={['1H', '1D', '1W']}
          />
        </div>
      </div>

      {/* 経済指標カレンダー */}
      <EconomicCalendarWidget
        limit={8}
        showFilters={true}
        selectedCurrencies={[selectedPair.split('/')[0], selectedPair.split('/')[1]]}
      />

      {/* 為替戦略提案 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <h3 className="text-lg font-semibold text-white">推奨買いポジション</h3>
          </div>
          <div className="space-y-3">
            {[
              { pair: 'USD/JPY', entry: '149.50', target: '151.00', sl: '148.80', confidence: 85 },
              { pair: 'EUR/USD', entry: '1.0850', target: '1.0950', sl: '1.0780', confidence: 78 },
              { pair: 'GBP/USD', entry: '1.2700', target: '1.2850', sl: '1.2600', confidence: 72 },
            ].map(position => (
              <div key={position.pair} className="bg-black/30 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{position.pair}</span>
                  <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">
                    信頼度 {position.confidence}%
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">エントリー:</span>
                    <div className="text-white">{position.entry}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">目標:</span>
                    <div className="text-green-400">{position.target}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">損切り:</span>
                    <div className="text-red-400">{position.sl}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <h3 className="text-lg font-semibold text-white">リスク警告</h3>
          </div>
          <div className="space-y-3">
            <div className="bg-black/30 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">米FOMC</span>
                <span className="text-xs text-red-400">高リスク</span>
              </div>
              <p className="text-xs text-gray-400">
                今夜21:00のFOMC議事録発表により大きな変動の可能性があります。
                ポジションサイズの調整を推奨します。
              </p>
            </div>
            <div className="bg-black/30 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">EUR/JPY</span>
                <span className="text-xs text-yellow-400">中リスク</span>
              </div>
              <p className="text-xs text-gray-400">
                クロス円のボラティリティが上昇中。
                通常より広めのストップロスを設定してください。
              </p>
            </div>
            <div className="bg-black/30 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white">週末リスク</span>
                <span className="text-xs text-yellow-400">注意</span>
              </div>
              <p className="text-xs text-gray-400">
                金曜日のポジションは週末リスクを考慮し、
                適切なリスク管理を行ってください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}