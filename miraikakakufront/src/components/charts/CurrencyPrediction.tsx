'use client';

import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { TrendingUp, TrendingDown, Globe, AlertTriangle, Target } from 'lucide-react';

interface CurrencyPair {
  pair: string;
  base: string;
  quote: string;
  current: number;
  predicted: number;
  change: number;
  changePercent: number;
  confidence: number;
  volatility: 'low' | 'medium' | 'high';
}

interface CurrencyPredictionProps {
  selectedPair?: string;
}

// 主要通貨ペア
const CURRENCY_PAIRS = [
  { pair: 'USD/JPY', base: 'USD', quote: 'JPY', flag1: '🇺🇸', flag2: '🇯🇵' },
  { pair: 'EUR/USD', base: 'EUR', quote: 'USD', flag1: '🇪🇺', flag2: '🇺🇸' },
  { pair: 'GBP/USD', base: 'GBP', quote: 'USD', flag1: '🇬🇧', flag2: '🇺🇸' },
  { pair: 'EUR/JPY', base: 'EUR', quote: 'JPY', flag1: '🇪🇺', flag2: '🇯🇵' },
  { pair: 'AUD/USD', base: 'AUD', quote: 'USD', flag1: '🇦🇺', flag2: '🇺🇸' },
  { pair: 'USD/CHF', base: 'USD', quote: 'CHF', flag1: '🇺🇸', flag2: '🇨🇭' },
  { pair: 'USD/CAD', base: 'USD', quote: 'CAD', flag1: '🇺🇸', flag2: '🇨🇦' },
  { pair: 'NZD/USD', base: 'NZD', quote: 'USD', flag1: '🇳🇿', flag2: '🇺🇸' },
];

export default function CurrencyPrediction({ selectedPair = 'USD/JPY' }: CurrencyPredictionProps) {
  const [currencyData, setCurrencyData] = useState<CurrencyPair[]>([]);
  const [selectedCurrency, setSelectedCurrency] = useState(selectedPair);
  const [timeFrame, setTimeFrame] = useState<'1H' | '1D' | '1W' | '1M'>('1D');
  const [loading, setLoading] = useState(true);

  // モックデータ生成
  const generateCurrencyData = () => {
    const data: CurrencyPair[] = CURRENCY_PAIRS.map(pair => {
      const baseRate = pair.pair === 'USD/JPY' ? 150 : 
                      pair.pair === 'EUR/USD' ? 1.08 :
                      pair.pair === 'GBP/USD' ? 1.27 :
                      pair.pair === 'EUR/JPY' ? 162 :
                      pair.pair === 'AUD/USD' ? 0.65 :
                      pair.pair === 'USD/CHF' ? 0.88 :
                      pair.pair === 'USD/CAD' ? 1.36 :
                      0.61;

      const current = baseRate * (1 + (Math.random() - 0.5) * 0.02);
      const changePercent = (Math.random() - 0.5) * 3;
      const predicted = current * (1 + changePercent / 100);
      
      return {
        pair: pair.pair,
        base: pair.base,
        quote: pair.quote,
        current,
        predicted,
        change: predicted - current,
        changePercent,
        confidence: 70 + Math.random() * 25,
        volatility: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low'
      };
    });

    setCurrencyData(data);
    setLoading(false);
  };

  useEffect(() => {
    generateCurrencyData();
    // リアルタイム更新のシミュレーション
    const interval = setInterval(generateCurrencyData, 30000);
    return () => clearInterval(interval);
  }, []);

  // 選択された通貨ペアのデータ
  const selectedData = currencyData.find(c => c.pair === selectedCurrency);

  // チャートデータ生成
  const generateChartData = () => {
    if (!selectedData) return { labels: [], datasets: [] };

    const hours = timeFrame === '1H' ? 60 : 
                  timeFrame === '1D' ? 24 : 
                  timeFrame === '1W' ? 168 : 720;
    
    const labels = [];
    const actualData = [];
    const predictedData = [];
    const upperBound = [];
    const lowerBound = [];

    
    for (let i = 0; i < hours; i++) {
      labels.push(
        timeFrame === '1H' ? `${i}分前` :
        timeFrame === '1D' ? `${hours - i}時間前` :
        `${Math.floor((hours - i) / 24)}日前`
      );

      const baseValue = selectedData.current;
      const noise = (Math.random() - 0.5) * baseValue * 0.005;
      const trend = (i / hours) * selectedData.change;
      
      if (i < hours * 0.7) {
        // 過去データ
        actualData.push(baseValue - trend + noise);
        predictedData.push(null);
        upperBound.push(null);
        lowerBound.push(null);
      } else {
        // 予測データ
        actualData.push(null);
        const predictValue = baseValue + trend * ((i - hours * 0.7) / (hours * 0.3)) + noise;
        predictedData.push(predictValue);
        upperBound.push(predictValue * 1.002);
        lowerBound.push(predictValue * 0.998);
      }
    }

    return {
      labels,
      datasets: [
        {
          label: '実績',
          data: actualData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: 'AI予測',
          data: predictedData,
          borderColor: 'rgb(255, 159, 64)',
          backgroundColor: 'rgba(255, 159, 64, 0.1)',
          borderDash: [5, 5],
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: '予測上限',
          data: upperBound,
          borderColor: 'rgba(255, 99, 132, 0.3)',
          backgroundColor: 'transparent',
          borderDash: [2, 2],
          pointRadius: 0,
          fill: false,
        },
        {
          label: '予測下限',
          data: lowerBound,
          borderColor: 'rgba(54, 162, 235, 0.3)',
          backgroundColor: 'transparent',
          borderDash: [2, 2],
          pointRadius: 0,
          fill: false,
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        labels: { color: 'white' }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value?.toFixed(4)}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: 'gray', maxTicksLimit: 10 }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { 
          color: 'gray',
          callback: (value: any) => value.toFixed(3)
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">為替データを読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Globe className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-bold text-white">為替予測</h2>
        </div>
        
        {/* 時間枠選択 */}
        <div className="flex space-x-2">
          {(['1H', '1D', '1W', '1M'] as const).map(tf => (
            <button
              key={tf}
              onClick={() => setTimeFrame(tf)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                timeFrame === tf 
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* 通貨ペア選択 */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {CURRENCY_PAIRS.map(pair => {
          const data = currencyData.find(c => c.pair === pair.pair);
          const isSelected = selectedCurrency === pair.pair;
          
          return (
            <button
              key={pair.pair}
              onClick={() => setSelectedCurrency(pair.pair)}
              className={`p-3 rounded-xl border transition-all ${
                isSelected 
                  ? 'bg-blue-500/20 border-blue-500/50' 
                  : 'bg-gray-900/50 border-gray-800/50 hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-center justify-center space-x-1 mb-1">
                <span>{pair.flag1}</span>
                <span className="text-gray-400">/</span>
                <span>{pair.flag2}</span>
              </div>
              <div className="text-xs font-medium text-white">{pair.pair}</div>
              {data && (
                <div className={`text-xs mt-1 ${
                  data.changePercent > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {data.changePercent > 0 ? '↑' : '↓'} {Math.abs(data.changePercent).toFixed(2)}%
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* メインチャート */}
      {selectedData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-900/50 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">{selectedCurrency}</h3>
                <div className="flex items-center space-x-2">
                  {selectedData.volatility === 'high' && (
                    <div className="flex items-center space-x-1 px-2 py-1 bg-red-500/20 rounded-lg">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="text-xs text-red-400">高ボラティリティ</span>
                    </div>
                  )}
                  <div className="text-sm text-gray-400">
                    信頼度: <span className="text-white font-medium">{selectedData.confidence.toFixed(0)}%</span>
                  </div>
                </div>
              </div>
              
              <Line data={generateChartData()} options={chartOptions} />
            </div>
          </div>

          {/* 詳細情報パネル */}
          <div className="space-y-4">
            {/* 現在価格 */}
            <div className="bg-gray-900/50 rounded-xl p-4">
              <div className="text-gray-400 text-sm mb-2">現在価格</div>
              <div className="text-2xl font-bold text-white">
                {selectedData.current.toFixed(4)}
              </div>
              <div className={`flex items-center space-x-1 mt-2 ${
                selectedData.change > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {selectedData.change > 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span>{selectedData.change > 0 ? '+' : ''}{selectedData.change.toFixed(4)}</span>
                <span>({selectedData.changePercent > 0 ? '+' : ''}{selectedData.changePercent.toFixed(2)}%)</span>
              </div>
            </div>

            {/* AI予測 */}
            <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span className="text-gray-400 text-sm">AI予測価格</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">
                {selectedData.predicted.toFixed(4)}
              </div>
              <div className="mt-2 text-xs text-gray-400">
                予測時間: {timeFrame === '1H' ? '1時間後' : timeFrame === '1D' ? '24時間後' : timeFrame === '1W' ? '1週間後' : '1ヶ月後'}
              </div>
            </div>

            {/* 取引シグナル */}
            <div className="bg-gray-900/50 rounded-xl p-4">
              <div className="text-gray-400 text-sm mb-3">取引シグナル</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">買いシグナル</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5].map(i => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i <= (selectedData.changePercent > 1 ? 5 : selectedData.changePercent > 0 ? 3 : 1)
                            ? 'bg-green-400'
                            : 'bg-gray-700'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">売りシグナル</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5].map(i => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i <= (selectedData.changePercent < -1 ? 5 : selectedData.changePercent < 0 ? 3 : 1)
                            ? 'bg-red-400'
                            : 'bg-gray-700'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* テクニカル指標 */}
            <div className="bg-gray-900/50 rounded-xl p-4">
              <div className="text-gray-400 text-sm mb-3">テクニカル指標</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">RSI</span>
                  <span className="text-white">{(30 + Math.random() * 40).toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">MACD</span>
                  <span className={`${Math.random() > 0.5 ? 'text-green-400' : 'text-red-400'}`}>
                    {Math.random() > 0.5 ? '買い' : '売り'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ストキャスティクス</span>
                  <span className="text-white">{(20 + Math.random() * 60).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 為替相関マトリックス */}
      <div className="bg-gray-900/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">通貨ペア相関</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left text-gray-400 pb-2">ペア</th>
                <th className="text-right text-gray-400 pb-2">現在価格</th>
                <th className="text-right text-gray-400 pb-2">変動率</th>
                <th className="text-right text-gray-400 pb-2">予測</th>
                <th className="text-right text-gray-400 pb-2">信頼度</th>
                <th className="text-center text-gray-400 pb-2">ボラティリティ</th>
              </tr>
            </thead>
            <tbody>
              {currencyData.map(currency => (
                <tr key={currency.pair} className="border-t border-gray-800/50">
                  <td className="py-2 text-white font-medium">{currency.pair}</td>
                  <td className="text-right text-white">{currency.current.toFixed(4)}</td>
                  <td className={`text-right ${currency.changePercent > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {currency.changePercent > 0 ? '+' : ''}{currency.changePercent.toFixed(2)}%
                  </td>
                  <td className="text-right text-purple-400">{currency.predicted.toFixed(4)}</td>
                  <td className="text-right text-white">{currency.confidence.toFixed(0)}%</td>
                  <td className="text-center">
                    <span className={`px-2 py-1 rounded text-xs ${
                      currency.volatility === 'high' ? 'bg-red-500/20 text-red-400' :
                      currency.volatility === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'
                    }`}>
                      {currency.volatility === 'high' ? '高' :
                       currency.volatility === 'medium' ? '中' : '低'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}