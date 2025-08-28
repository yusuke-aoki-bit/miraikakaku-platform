'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import CurrencyPairSelector from '@/components/currency/CurrencyPairSelector';
import CurrencyChart from '@/components/currency/CurrencyChart';
import CurrencyAIPredictionPanel from '@/components/currency/CurrencyAIPredictionPanel';
import EconomicCalendarWidget from '@/components/currency/EconomicCalendarWidget';
import { DollarSign, Globe, TrendingUp, AlertCircle } from 'lucide-react';

export default function CurrencyPage() {
  const [selectedPair, setSelectedPair] = useState('USD/JPY');
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1H' | '4H' | '1D' | '1W'>('1D');

  const [currencyPairs, setCurrencyPairs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrencyPairs = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getCurrencyPairs();
        
        if (response.success && response.data) {
          const pairs = Array.isArray(response.data) ? response.data : [];
          setCurrencyPairs(pairs);
          
          // デフォルト選択がリストにない場合は最初のペアを選択
          if (pairs.length > 0 && !pairs.find(p => p.pair === selectedPair)) {
            setSelectedPair(pairs[0].pair);
          }
        } else {
          setCurrencyPairs([]);
        }
      } catch (error) {
        console.error('Failed to fetch currency pairs:', error);
        setCurrencyPairs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCurrencyPairs();
  }, [selectedPair]);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-400 border-t-transparent"></div>
          <span className="ml-3 text-gray-400">通貨ペアデータ読み込み中...</span>
        </div>
      </div>
    );
  }

  if (currencyPairs.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-yellow-400 opacity-50" />
          <h3 className="text-white font-semibold mb-2">通貨データが利用できません</h3>
          <p className="text-gray-400">しばらく経ってから再度お試しください。</p>
        </div>
      </div>
    );
  }

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

      {/* 通貨ペア数の表示 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{currencyPairs.length}</div>
          <div className="text-sm text-gray-400">利用可能な通貨ペア</div>
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

      {/* 注意事項 */}
      <div className="bg-gradient-to-r from-yellow-900/20 to-orange-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-center space-x-2 mb-4">
          <AlertCircle className="w-5 h-5 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white">為替取引に関する注意事項</h3>
        </div>
        <div className="space-y-3 text-sm text-gray-300">
          <p>• 為替相場は様々な経済要因により大きく変動する可能性があります。</p>
          <p>• 投資判断は十分な情報収集と分析に基づいて慎重に行ってください。</p>
          <p>• リスク管理を徹底し、投資資金の範囲内で取引を行うことをお勧めします。</p>
        </div>
      </div>
    </div>
  );
}