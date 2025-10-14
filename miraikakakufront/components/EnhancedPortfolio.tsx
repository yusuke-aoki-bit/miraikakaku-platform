'use client';

import { useState, useEffect } from 'react';
import { PortfolioManager, PortfolioPosition } from '@/lib/portfolio';
import { useRealtimePrices } from '@/lib/useRealTimePrice';
import { useRouter } from 'next/navigation';

export default function EnhancedPortfolio() {
  const router = useRouter();
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  // フォーム状態
  const [symbol, setSymbol] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [exchange, setExchange] = useState('');
  const [quantity, setQuantity] = useState('');
  const [averagePrice, setAveragePrice] = useState('');
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');

  // リアルタイム価格取得
  const symbols = positions.map(p => p.symbol);
  const { pricesData, refresh } = useRealtimePrices(symbols, 60000); // 1分ごと

  useEffect(() => {
    loadPositions();
  }, []);

  const loadPositions = () => {
    setPositions(PortfolioManager.getPositions());
  };

  const resetForm = () => {
    setSymbol('');
    setCompanyName('');
    setExchange('');
    setQuantity('');
    setAveragePrice('');
    setPurchaseDate(new Date().toISOString().split('T')[0]);
    setNotes('');
    setEditingId(null);
  };

  const handleAddPosition = () => {
    const qty = parseFloat(quantity);
    const price = parseFloat(averagePrice);

    if (!symbol || !companyName || isNaN(qty) || isNaN(price) || qty <= 0 || price <= 0) {
      alert('すべての必須項目を正しく入力してください');
      return;
    }

    if (editingId) {
      PortfolioManager.updatePosition(editingId, {
        company_name: companyName,
        exchange,
        quantity: qty,
        average_price: price,
        purchase_date: purchaseDate,
        notes,
      });
    } else {
      PortfolioManager.addPosition(
        symbol.toUpperCase(),
        companyName,
        exchange,
        qty,
        price,
        purchaseDate,
        notes
      );
    }

    resetForm();
    setShowAddForm(false);
    loadPositions();
  };

  const handleEditPosition = (position: PortfolioPosition) => {
    setSymbol(position.symbol);
    setCompanyName(position.company_name);
    setExchange(position.exchange);
    setQuantity(position.quantity.toString());
    setAveragePrice(position.average_price.toString());
    setPurchaseDate(position.purchase_date);
    setNotes(position.notes || '');
    setEditingId(position.id);
    setShowAddForm(true);
  };

  const handleRemovePosition = (id: string) => {
    if (confirm('このポジションを削除しますか？')) {
      PortfolioManager.removePosition(id);
      loadPositions();
    }
  };

  const handleExport = () => {
    const currentPrices = new Map<string, number>();
    pricesData.forEach((data, symbol) => {
      currentPrices.set(symbol, data.current_price);
    });

    const csv = PortfolioManager.exportToCSV(positions, currentPrices);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // サマリー計算
  const currentPrices = new Map<string, number>();
  pricesData.forEach((data, symbol) => {
    currentPrices.set(symbol, data.current_price);
  });
  const summary = PortfolioManager.calculateSummary(positions, currentPrices);

  return (
    <div className="space-y-6">
      {/* ヘッダーとアクション */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          ポートフォリオ
        </h1>
        <div className="flex gap-2">
          <button
            onClick={refresh}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
          >
            🔄 更新
          </button>
          {positions.length > 0 && (
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
            >
              📊 CSV出力
            </button>
          )}
          <button
            onClick={() => {
              resetForm();
              setShowAddForm(!showAddForm);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            {showAddForm ? 'キャンセル' : '+ ポジション追加'}
          </button>
        </div>
      </div>

      {/* サマリーカード */}
      {positions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">総評価額</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              ¥{summary.total_value.toLocaleString()}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">総取得金額</p>
            <p className="text-2xl font-bold text-gray-700 dark:text-gray-300">
              ¥{summary.total_cost.toLocaleString()}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">評価損益</p>
            <p className={`text-2xl font-bold ${
              summary.total_profit_loss >= 0
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}>
              {summary.total_profit_loss >= 0 ? '+' : ''}¥{summary.total_profit_loss.toLocaleString()}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">損益率</p>
            <p className={`text-2xl font-bold ${
              summary.total_profit_loss_percent >= 0
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}>
              {summary.total_profit_loss_percent >= 0 ? '+' : ''}{summary.total_profit_loss_percent.toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      {/* 追加フォーム */}
      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {editingId ? 'ポジション編集' : 'ポジション追加'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                銘柄コード *
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="例: AAPL, 7203.T"
                disabled={!!editingId}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                企業名 *
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="例: Apple Inc."
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                取引所
              </label>
              <input
                type="text"
                value={exchange}
                onChange={(e) => setExchange(e.target.value)}
                placeholder="例: NASDAQ, TSE"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                保有数 *
              </label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="例: 100"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                平均取得価格 *
              </label>
              <input
                type="number"
                value={averagePrice}
                onChange={(e) => setAveragePrice(e.target.value)}
                placeholder="例: 150.50"
                step="0.01"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                購入日
              </label>
              <input
                type="date"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                メモ
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="メモを入力..."
                rows={2}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={handleAddPosition}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {editingId ? '更新' : '追加'}
            </button>
            <button
              onClick={() => {
                resetForm();
                setShowAddForm(false);
              }}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
            >
              キャンセル
            </button>
          </div>
        </div>
      )}

      {/* ポジション一覧 */}
      {positions.length > 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    銘柄
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    保有数
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    平均取得価格
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    現在価格
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    評価損益
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    損益率
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    アクション
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {positions.map((position) => {
                  const currentPrice = pricesData.get(position.symbol)?.current_price;
                  const profitLoss = PortfolioManager.calculatePositionProfitLoss(position, currentPrice);

                  return (
                    <tr
                      key={position.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                      onClick={() => router.push(`/stock/${position.symbol}`)}
                    >
                      <td className="px-4 py-4">
                        <div>
                          <p className="font-mono font-semibold text-blue-600 dark:text-blue-400">
                            {position.symbol}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {position.company_name}
                          </p>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-right text-gray-900 dark:text-white">
                        {position.quantity.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-right text-gray-900 dark:text-white">
                        ¥{position.average_price.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-right">
                        {currentPrice ? (
                          <span className="text-gray-900 dark:text-white">
                            ¥{currentPrice.toLocaleString()}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-right">
                        {profitLoss ? (
                          <span className={profitLoss.profit_loss >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                            {profitLoss.profit_loss >= 0 ? '+' : ''}¥{profitLoss.profit_loss.toLocaleString()}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-right">
                        {profitLoss ? (
                          <span className={profitLoss.profit_loss_percent >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                            {profitLoss.profit_loss_percent >= 0 ? '+' : ''}{profitLoss.profit_loss_percent.toFixed(2)}%
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-center">
                        <div className="flex gap-2 justify-center" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleEditPosition(position)}
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
                          >
                            編集
                          </button>
                          <button
                            onClick={() => handleRemovePosition(position.id)}
                            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm font-medium"
                          >
                            削除
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            ポジションが登録されていません
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            最初のポジションを追加する
          </button>
        </div>
      )}
    </div>
  );
}
