'use client';

import React, { useState } from 'react';
import { Calculator, DollarSign, Percent, TrendingUp } from 'lucide-react';

export default function ToolsPage() {
  const [investment, setInvestment] = useState(10000);
  const [expectedReturn, setExpectedReturn] = useState(7);
  const [years, setYears] = useState(5);
  const [monthlyContribution, setMonthlyContribution] = useState(500);
  
  const calculateCompoundReturn = () => {
    const monthlyRate = expectedReturn / 100 / 12;
    const months = years * 12;
    
    // 元本の複利計算
    const principalReturn = investment * Math.pow(1 + expectedReturn / 100, years);
    
    // 毎月積立の複利計算
    const monthlyReturn = monthlyContribution * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
    
    return principalReturn + monthlyReturn;
  };

  const finalAmount = calculateCompoundReturn();
  const totalContributions = investment + (monthlyContribution * years * 12);
  const totalGains = finalAmount - totalContributions;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6 flex items-center">
        <Calculator className="w-6 h-6 mr-2 text-blue-400" />
        投資計算機
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 計算機 */}
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">複利計算</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm mb-2">初期投資額 ($)</label>
              <input
                type="number"
                value={investment}
                onChange={(e) => setInvestment(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 text-sm mb-2">期待年利回り (%)</label>
              <input
                type="number"
                value={expectedReturn}
                onChange={(e) => setExpectedReturn(Number(e.target.value))}
                step="0.1"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 text-sm mb-2">投資期間 (年)</label>
              <input
                type="number"
                value={years}
                onChange={(e) => setYears(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 text-sm mb-2">毎月積立額 ($)</label>
              <input
                type="number"
                value={monthlyContribution}
                onChange={(e) => setMonthlyContribution(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* 結果表示 */}
        <div className="youtube-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">計算結果</h2>
          
          <div className="space-y-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <DollarSign className="w-5 h-5 text-green-400 mr-2" />
                <span className="text-gray-300">最終資産額</span>
              </div>
              <p className="text-2xl font-bold text-green-400">
                ${finalAmount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </p>
            </div>
            
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <TrendingUp className="w-5 h-5 text-blue-400 mr-2" />
                <span className="text-gray-300">総利益</span>
              </div>
              <p className="text-xl font-bold text-blue-400">
                ${totalGains.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </p>
            </div>
            
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <Percent className="w-5 h-5 text-purple-400 mr-2" />
                <span className="text-gray-300">総投資額</span>
              </div>
              <p className="text-lg font-semibold text-white">
                ${totalContributions.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </p>
            </div>
            
            <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 p-4 rounded-lg border border-green-500/30">
              <p className="text-green-400 font-semibold">
                利益率: {((totalGains / totalContributions) * 100).toFixed(1)}%
              </p>
              <p className="text-gray-300 text-sm">
                {years}年間で約{(totalGains / totalContributions * 100).toFixed(0)}%の成長
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* リスク分析 */}
      <div className="youtube-card p-6 mt-6">
        <h2 className="text-lg font-semibold text-white mb-4">リスク分析</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-red-600/20 p-4 rounded-lg border border-red-500/30">
            <h3 className="text-red-400 font-semibold mb-2">悲観シナリオ (-3%)</h3>
            <p className="text-white text-lg">
              ${(totalContributions * Math.pow(0.97, years)).toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </p>
          </div>
          
          <div className="bg-yellow-600/20 p-4 rounded-lg border border-yellow-500/30">
            <h3 className="text-yellow-400 font-semibold mb-2">現実的シナリオ ({expectedReturn}%)</h3>
            <p className="text-white text-lg">
              ${finalAmount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </p>
          </div>
          
          <div className="bg-green-600/20 p-4 rounded-lg border border-green-500/30">
            <h3 className="text-green-400 font-semibold mb-2">楽観シナリオ (+3%)</h3>
            <p className="text-white text-lg">
              ${(finalAmount * Math.pow(1.03, years)).toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}