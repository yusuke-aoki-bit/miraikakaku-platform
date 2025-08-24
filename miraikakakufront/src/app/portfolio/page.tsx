'use client';

import React, { useState, useEffect } from 'react';
import { PieChart, TrendingUp, TrendingDown, DollarSign, BarChart3, Plus, Edit2, Trash2 } from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';

interface Position {
  id: string;
  symbol: string;
  company_name: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  value: number;
  profit_loss: number;
  profit_loss_percent: number;
  allocation: number;
}

interface PortfolioSummary {
  total_value: number;
  total_cost: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
  positions_count: number;
}

export default function PortfolioPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary>({
    total_value: 0,
    total_cost: 0,
    total_profit_loss: 0,
    total_profit_loss_percent: 0,
    positions_count: 0
  });
  const [showAddPosition, setShowAddPosition] = useState(false);
  const [newPosition, setNewPosition] = useState({
    symbol: '',
    quantity: 0,
    average_cost: 0
  });

  // モックデータの初期化
  useEffect(() => {
    // LocalStorageから取得（実際の実装では APIから取得）
    const savedPositions = localStorage.getItem('portfolio_positions');
    if (savedPositions) {
      const parsed = JSON.parse(savedPositions);
      setPositions(parsed);
      calculateSummary(parsed);
    } else {
      // デモデータ
      const demoPositions: Position[] = [
        {
          id: '1',
          symbol: '7203',
          company_name: 'トヨタ自動車',
          quantity: 100,
          average_cost: 2800,
          current_price: 2950,
          value: 295000,
          profit_loss: 15000,
          profit_loss_percent: 5.36,
          allocation: 25
        },
        {
          id: '2',
          symbol: '6758',
          company_name: 'ソニーグループ',
          quantity: 50,
          average_cost: 13500,
          current_price: 13200,
          value: 660000,
          profit_loss: -15000,
          profit_loss_percent: -2.22,
          allocation: 35
        },
        {
          id: '3',
          symbol: '9984',
          company_name: 'ソフトバンクグループ',
          quantity: 200,
          average_cost: 8500,
          current_price: 8800,
          value: 1760000,
          profit_loss: 60000,
          profit_loss_percent: 3.53,
          allocation: 40
        }
      ];
      setPositions(demoPositions);
      calculateSummary(demoPositions);
    }
  }, []);

  const calculateSummary = (positions: Position[]) => {
    const total_value = positions.reduce((sum, p) => sum + p.value, 0);
    const total_cost = positions.reduce((sum, p) => sum + (p.average_cost * p.quantity), 0);
    const total_profit_loss = total_value - total_cost;
    const total_profit_loss_percent = total_cost > 0 ? (total_profit_loss / total_cost) * 100 : 0;

    setSummary({
      total_value,
      total_cost,
      total_profit_loss,
      total_profit_loss_percent,
      positions_count: positions.length
    });
  };

  const handleAddPosition = () => {
    if (!newPosition.symbol || newPosition.quantity <= 0 || newPosition.average_cost <= 0) return;

    const position: Position = {
      id: Date.now().toString(),
      symbol: newPosition.symbol,
      company_name: '新規銘柄', // 実際はAPIから取得
      quantity: newPosition.quantity,
      average_cost: newPosition.average_cost,
      current_price: newPosition.average_cost * 1.05, // モック
      value: newPosition.quantity * newPosition.average_cost * 1.05,
      profit_loss: newPosition.quantity * newPosition.average_cost * 0.05,
      profit_loss_percent: 5,
      allocation: 0
    };

    const updatedPositions = [...positions, position];
    setPositions(updatedPositions);
    calculateSummary(updatedPositions);
    localStorage.setItem('portfolio_positions', JSON.stringify(updatedPositions));
    
    setNewPosition({ symbol: '', quantity: 0, average_cost: 0 });
    setShowAddPosition(false);
  };

  const handleDeletePosition = (id: string) => {
    const updatedPositions = positions.filter(p => p.id !== id);
    setPositions(updatedPositions);
    calculateSummary(updatedPositions);
    localStorage.setItem('portfolio_positions', JSON.stringify(updatedPositions));
  };

  // チャートデータ
  const allocationChartData = {
    labels: positions.map(p => p.symbol),
    datasets: [{
      data: positions.map(p => p.value),
      backgroundColor: [
        'rgba(59, 130, 246, 0.5)',
        'rgba(16, 185, 129, 0.5)',
        'rgba(251, 146, 60, 0.5)',
        'rgba(147, 51, 234, 0.5)',
        'rgba(236, 72, 153, 0.5)',
      ],
      borderColor: [
        'rgba(59, 130, 246, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(251, 146, 60, 1)',
        'rgba(147, 51, 234, 1)',
        'rgba(236, 72, 153, 1)',
      ],
      borderWidth: 1
    }]
  };

  const performanceChartData = {
    labels: ['1日前', '1週間前', '1ヶ月前', '3ヶ月前', '6ヶ月前', '今日'],
    datasets: [{
      label: 'ポートフォリオ価値',
      data: [2500000, 2550000, 2600000, 2450000, 2700000, summary.total_value],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  };

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <PieChart className="w-6 h-6 mr-2 text-blue-400" />
          ポートフォリオ
        </h1>
        <button
          onClick={() => setShowAddPosition(!showAddPosition)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          ポジション追加
        </button>
      </div>

      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-5 h-5 text-blue-400" />
            <span className="text-xs text-blue-400">総資産</span>
          </div>
          <div className="text-2xl font-bold text-white">
            ¥{summary.total_value.toLocaleString()}
          </div>
        </div>

        <div className={`bg-gradient-to-r ${
          summary.total_profit_loss > 0 
            ? 'from-green-900/20 to-emerald-900/20 border-green-500/30' 
            : 'from-red-900/20 to-pink-900/20 border-red-500/30'
        } border rounded-xl p-4`}>
          <div className="flex items-center justify-between mb-2">
            {summary.total_profit_loss > 0 ? (
              <TrendingUp className="w-5 h-5 text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
            <span className={`text-xs ${summary.total_profit_loss > 0 ? 'text-green-400' : 'text-red-400'}`}>
              損益
            </span>
          </div>
          <div className="text-2xl font-bold text-white">
            {summary.total_profit_loss > 0 ? '+' : ''}¥{summary.total_profit_loss.toLocaleString()}
          </div>
          <div className={`text-sm ${summary.total_profit_loss > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {summary.total_profit_loss_percent > 0 ? '+' : ''}{summary.total_profit_loss_percent.toFixed(2)}%
          </div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            <span className="text-xs text-purple-400">銘柄数</span>
          </div>
          <div className="text-2xl font-bold text-white">{summary.positions_count}</div>
          <div className="text-sm text-gray-400">保有銘柄</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-5 h-5 text-yellow-400" />
            <span className="text-xs text-yellow-400">取得総額</span>
          </div>
          <div className="text-2xl font-bold text-white">
            ¥{summary.total_cost.toLocaleString()}
          </div>
        </div>
      </div>

      {/* ポジション追加フォーム */}
      {showAddPosition && (
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">新規ポジション追加</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="銘柄コード"
              value={newPosition.symbol}
              onChange={(e) => setNewPosition({...newPosition, symbol: e.target.value})}
              className="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white"
            />
            <input
              type="number"
              placeholder="数量"
              value={newPosition.quantity || ''}
              onChange={(e) => setNewPosition({...newPosition, quantity: parseInt(e.target.value) || 0})}
              className="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white"
            />
            <input
              type="number"
              placeholder="平均取得単価"
              value={newPosition.average_cost || ''}
              onChange={(e) => setNewPosition({...newPosition, average_cost: parseFloat(e.target.value) || 0})}
              className="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white"
            />
            <button
              onClick={handleAddPosition}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              追加
            </button>
          </div>
        </div>
      )}

      {/* チャート */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 資産配分 */}
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">資産配分</h2>
          <div className="h-64">
            <Doughnut 
              data={allocationChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right',
                    labels: { color: 'white' }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* パフォーマンス */}
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">パフォーマンス推移</h2>
          <div className="h-64">
            <Line 
              data={performanceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: 'gray' }
                  },
                  y: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                      color: 'gray',
                      callback: (value) => `¥${(value as number / 1000000).toFixed(1)}M`
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* ポジション一覧 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">保有銘柄</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left text-gray-400 pb-3">銘柄</th>
                <th className="text-right text-gray-400 pb-3">数量</th>
                <th className="text-right text-gray-400 pb-3">平均取得</th>
                <th className="text-right text-gray-400 pb-3">現在価格</th>
                <th className="text-right text-gray-400 pb-3">評価額</th>
                <th className="text-right text-gray-400 pb-3">損益</th>
                <th className="text-center text-gray-400 pb-3">操作</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position) => (
                <tr key={position.id} className="border-b border-gray-800/50">
                  <td className="py-3">
                    <button
                      onClick={() => window.location.href = `/stock/${position.symbol}`}
                      className="text-left hover:text-blue-400 transition-colors"
                    >
                      <div className="font-medium text-white">{position.symbol}</div>
                      <div className="text-sm text-gray-400">{position.company_name}</div>
                    </button>
                  </td>
                  <td className="text-right text-white py-3">{position.quantity}</td>
                  <td className="text-right text-white py-3">¥{position.average_cost.toLocaleString()}</td>
                  <td className="text-right text-white py-3">¥{position.current_price.toLocaleString()}</td>
                  <td className="text-right text-white py-3">¥{position.value.toLocaleString()}</td>
                  <td className={`text-right py-3 ${position.profit_loss > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    <div>{position.profit_loss > 0 ? '+' : ''}¥{position.profit_loss.toLocaleString()}</div>
                    <div className="text-sm">
                      ({position.profit_loss_percent > 0 ? '+' : ''}{position.profit_loss_percent.toFixed(2)}%)
                    </div>
                  </td>
                  <td className="text-center py-3">
                    <button
                      onClick={() => handleDeletePosition(position.id)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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