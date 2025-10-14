'use client';

import { useState, useEffect, useMemo } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * ポートフォリオ管理システム
 * 保有銘柄の追跡、パフォーマンス分析、リバランス提案
 */

interface PortfolioPosition {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  sector?: string;
  addedDate: Date;
}

interface Transaction {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  date: Date;
  notes?: string;
}

export function PortfolioManager() {
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newPosition, setNewPosition] = useState({
    symbol: '',
    name: '',
    quantity: 0,
    avgCost: 0,
    currentPrice: 0,
    sector: '',
  });

  // LocalStorageから読み込み
  useEffect(() => {
    const savedPositions = localStorage.getItem('portfolio_positions');
    const savedTransactions = localStorage.getItem('portfolio_transactions');

    if (savedPositions) {
      setPositions(JSON.parse(savedPositions).map((p: any) => ({
        ...p,
        addedDate: new Date(p.addedDate)
      })));
    }

    if (savedTransactions) {
      setTransactions(JSON.parse(savedTransactions).map((t: any) => ({
        ...t,
        date: new Date(t.date)
      })));
    }
  }, []);

  // LocalStorageに保存
  useEffect(() => {
    if (positions.length > 0) {
      localStorage.setItem('portfolio_positions', JSON.stringify(positions));
    }
    if (transactions.length > 0) {
      localStorage.setItem('portfolio_transactions', JSON.stringify(transactions));
    }
  }, [positions, transactions]);

  // ポートフォリオ統計
  const portfolioStats = useMemo(() => {
    const totalValue = positions.reduce((sum, p) => sum + (p.quantity * p.currentPrice), 0);
    const totalCost = positions.reduce((sum, p) => sum + (p.quantity * p.avgCost), 0);
    const totalGainLoss = totalValue - totalCost;
    const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;

    const bestPerformer = positions.length > 0
      ? positions.reduce((best, p) => {
          const gainPercent = ((p.currentPrice - p.avgCost) / p.avgCost) * 100;
          const bestGainPercent = ((best.currentPrice - best.avgCost) / best.avgCost) * 100;
          return gainPercent > bestGainPercent ? p : best;
        })
      : null;

    const worstPerformer = positions.length > 0
      ? positions.reduce((worst, p) => {
          const gainPercent = ((p.currentPrice - p.avgCost) / p.avgCost) * 100;
          const worstGainPercent = ((worst.currentPrice - worst.avgCost) / worst.avgCost) * 100;
          return gainPercent < worstGainPercent ? p : worst;
        })
      : null;

    return {
      totalValue,
      totalCost,
      totalGainLoss,
      totalGainLossPercent,
      positionCount: positions.length,
      bestPerformer,
      worstPerformer,
    };
  }, [positions]);

  // セクター別配分
  const sectorAllocation = useMemo(() => {
    const sectorMap = new Map<string, number>();

    positions.forEach(position => {
      const sector = position.sector || 'その他';
      const value = position.quantity * position.currentPrice;
      sectorMap.set(sector, (sectorMap.get(sector) || 0) + value);
    });

    return Array.from(sectorMap.entries()).map(([name, value]) => ({
      name,
      value,
      percentage: (value / portfolioStats.totalValue) * 100
    })).sort((a, b) => b.value - a.value);
  }, [positions, portfolioStats.totalValue]);

  // 銘柄別配分
  const positionAllocation = useMemo(() => {
    return positions.map(p => ({
      name: p.symbol,
      value: p.quantity * p.currentPrice,
      percentage: ((p.quantity * p.currentPrice) / portfolioStats.totalValue) * 100
    })).sort((a, b) => b.value - a.value);
  }, [positions, portfolioStats.totalValue]);

  // ポジション追加
  const addPosition = () => {
    if (!newPosition.symbol || newPosition.quantity <= 0 || newPosition.avgCost <= 0) {
      alert('すべての必須フィールドを入力してください');
      return;
    }

    const position: PortfolioPosition = {
      id: `pos-${Date.now()}`,
      ...newPosition,
      addedDate: new Date(),
    };

    setPositions([...positions, position]);

    const transaction: Transaction = {
      id: `tx-${Date.now()}`,
      symbol: newPosition.symbol,
      type: 'buy',
      quantity: newPosition.quantity,
      price: newPosition.avgCost,
      date: new Date(),
      notes: '初回購入',
    };

    setTransactions([transaction, ...transactions]);

    setNewPosition({
      symbol: '',
      name: '',
      quantity: 0,
      avgCost: 0,
      currentPrice: 0,
      sector: '',
    });

    setShowAddModal(false);
  };

  // ポジション削除
  const removePosition = (id: string) => {
    if (confirm('この銘柄を削除しますか？')) {
      setPositions(positions.filter(p => p.id !== id));
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center">
              <span className="text-4xl mr-3">💼</span>
              ポートフォリオ管理
            </h1>
            <p className="text-indigo-100">保有銘柄の追跡とパフォーマンス分析</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-6 py-3 bg-white text-indigo-600 font-bold rounded-lg hover:bg-indigo-50 transition-colors flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>銘柄を追加</span>
          </button>
        </div>
      </div>

      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">総資産額</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            ¥{portfolioStats.totalValue.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
            取得原価: ¥{portfolioStats.totalCost.toLocaleString()}
          </p>
        </div>

        <div className={`rounded-lg shadow-lg p-6 ${
          portfolioStats.totalGainLoss >= 0
            ? 'bg-green-50 dark:bg-green-900/20'
            : 'bg-red-50 dark:bg-red-900/20'
        }`}>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">評価損益</p>
          <p className={`text-3xl font-bold ${
            portfolioStats.totalGainLoss >= 0
              ? 'text-green-600 dark:text-green-400'
              : 'text-red-600 dark:text-red-400'
          }`}>
            {portfolioStats.totalGainLoss >= 0 ? '+' : ''}
            ¥{portfolioStats.totalGainLoss.toLocaleString()}
          </p>
          <p className={`text-sm font-semibold mt-2 ${
            portfolioStats.totalGainLoss >= 0
              ? 'text-green-600 dark:text-green-400'
              : 'text-red-600 dark:text-red-400'
          }`}>
            {portfolioStats.totalGainLossPercent >= 0 ? '+' : ''}
            {portfolioStats.totalGainLossPercent.toFixed(2)}%
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">保有銘柄数</p>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
            {portfolioStats.positionCount}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
            セクター: {sectorAllocation.length}種類
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">取引履歴</p>
          <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
            {transactions.length}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
            件の取引記録
          </p>
        </div>
      </div>

      {/* パフォーマー */}
      {portfolioStats.bestPerformer && portfolioStats.worstPerformer && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-green-800 dark:text-green-200 mb-3 flex items-center">
              <span className="text-2xl mr-2">🏆</span>
              ベストパフォーマー
            </h3>
            <p className="font-mono font-bold text-xl text-gray-900 dark:text-white mb-1">
              {portfolioStats.bestPerformer.symbol}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {portfolioStats.bestPerformer.name}
            </p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              +{(((portfolioStats.bestPerformer.currentPrice - portfolioStats.bestPerformer.avgCost) / portfolioStats.bestPerformer.avgCost) * 100).toFixed(2)}%
            </p>
          </div>

          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-red-800 dark:text-red-200 mb-3 flex items-center">
              <span className="text-2xl mr-2">📉</span>
              ワーストパフォーマー
            </h3>
            <p className="font-mono font-bold text-xl text-gray-900 dark:text-white mb-1">
              {portfolioStats.worstPerformer.symbol}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {portfolioStats.worstPerformer.name}
            </p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">
              {(((portfolioStats.worstPerformer.currentPrice - portfolioStats.worstPerformer.avgCost) / portfolioStats.worstPerformer.avgCost) * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      {/* 配分チャート */}
      {positions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* セクター別配分 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              セクター別配分
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sectorAllocation}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage.toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sectorAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `¥${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 銘柄別配分 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              銘柄別配分
            </h3>
            <div className="space-y-3">
              {positionAllocation.slice(0, 5).map((position, index) => (
                <div key={position.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-semibold text-gray-900 dark:text-white">
                      {position.name}
                    </span>
                    <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                      {position.percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${position.percentage}%`,
                        backgroundColor: COLORS[index % COLORS.length]
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    ¥{position.value.toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ポジション一覧 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            保有銘柄一覧
          </h3>
        </div>

        {positions.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              まだ銘柄が登録されていません
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              最初の銘柄を追加
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">銘柄</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">数量</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">平均取得価格</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">現在価格</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">評価額</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">損益</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {positions.map(position => {
                  const value = position.quantity * position.currentPrice;
                  const cost = position.quantity * position.avgCost;
                  const gainLoss = value - cost;
                  const gainLossPercent = (gainLoss / cost) * 100;

                  return (
                    <tr key={position.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-mono font-bold text-blue-600 dark:text-blue-400">
                            {position.symbol}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {position.name}
                          </p>
                          {position.sector && (
                            <span className="inline-block mt-1 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                              {position.sector}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right font-semibold text-gray-900 dark:text-white">
                        {position.quantity.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-right text-gray-900 dark:text-white">
                        ¥{position.avgCost.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-right font-semibold text-gray-900 dark:text-white">
                        ¥{position.currentPrice.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-right font-bold text-gray-900 dark:text-white">
                        ¥{value.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className={`font-bold ${
                          gainLoss >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}>
                          {gainLoss >= 0 ? '+' : ''}
                          ¥{gainLoss.toLocaleString()}
                        </div>
                        <div className={`text-sm ${
                          gainLoss >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}>
                          {gainLossPercent >= 0 ? '+' : ''}
                          {gainLossPercent.toFixed(2)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => removePosition(position.id)}
                          className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 追加モーダル */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-md w-full p-6">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              銘柄を追加
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  銘柄コード *
                </label>
                <input
                  type="text"
                  value={newPosition.symbol}
                  onChange={(e) => setNewPosition({ ...newPosition, symbol: e.target.value.toUpperCase() })}
                  placeholder="例: 7203.T"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  銘柄名 *
                </label>
                <input
                  type="text"
                  value={newPosition.name}
                  onChange={(e) => setNewPosition({ ...newPosition, name: e.target.value })}
                  placeholder="例: トヨタ自動車"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    数量 *
                  </label>
                  <input
                    type="number"
                    value={newPosition.quantity || ''}
                    onChange={(e) => setNewPosition({ ...newPosition, quantity: Number(e.target.value) })}
                    placeholder="100"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    平均取得価格 *
                  </label>
                  <input
                    type="number"
                    value={newPosition.avgCost || ''}
                    onChange={(e) => setNewPosition({ ...newPosition, avgCost: Number(e.target.value) })}
                    placeholder="2500"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  現在価格 *
                </label>
                <input
                  type="number"
                  value={newPosition.currentPrice || ''}
                  onChange={(e) => setNewPosition({ ...newPosition, currentPrice: Number(e.target.value) })}
                  placeholder="2600"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  セクター
                </label>
                <input
                  type="text"
                  value={newPosition.sector}
                  onChange={(e) => setNewPosition({ ...newPosition, sector: e.target.value })}
                  placeholder="例: 自動車"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={addPosition}
                className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors"
              >
                追加
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-4 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-bold rounded-lg transition-colors"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
