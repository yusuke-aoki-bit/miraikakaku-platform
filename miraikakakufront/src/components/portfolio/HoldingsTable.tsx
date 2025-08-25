'use client';

import { useState } from 'react';
import { 
  ChevronDownIcon, 
  ChevronUpIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface Transaction {
  date: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
}

interface Holding {
  id: string;
  symbol: string;
  company_name: string;
  sector: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  allocation_percent: number;
  transactions: Transaction[];
}

interface HoldingsTableProps {
  holdings: Holding[];
  onTransactionAdded: (transaction: any) => void;
}

type SortField = 'symbol' | 'market_value' | 'unrealized_pnl' | 'allocation_percent' | 'unrealized_pnl_percent';
type SortDirection = 'asc' | 'desc';

export default function HoldingsTable({ holdings, onTransactionAdded }: HoldingsTableProps) {
  const [sortField, setSortField] = useState<SortField>('market_value');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [showEditModal, setShowEditModal] = useState<string | null>(null);

  const formatCurrency = (amount: number) => {
    return `¥${amount.toLocaleString('ja-JP')}`;
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedHoldings = [...holdings].sort((a, b) => {
    let aValue: number | string = 0;
    let bValue: number | string = 0;

    switch (sortField) {
      case 'symbol':
        aValue = a.symbol;
        bValue = b.symbol;
        break;
      case 'market_value':
        aValue = a.market_value;
        bValue = b.market_value;
        break;
      case 'unrealized_pnl':
        aValue = a.unrealized_pnl;
        bValue = b.unrealized_pnl;
        break;
      case 'allocation_percent':
        aValue = a.allocation_percent;
        bValue = b.allocation_percent;
        break;
      case 'unrealized_pnl_percent':
        aValue = a.unrealized_pnl_percent;
        bValue = b.unrealized_pnl_percent;
        break;
    }

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }

    return sortDirection === 'asc' 
      ? (aValue as number) - (bValue as number)
      : (bValue as number) - (aValue as number);
  });

  const toggleRowExpansion = (holdingId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(holdingId)) {
      newExpanded.delete(holdingId);
    } else {
      newExpanded.add(holdingId);
    }
    setExpandedRows(newExpanded);
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-text-secondary hover:text-text-primary transition-colors"
    >
      <span>{children}</span>
      {sortField === field && (
        sortDirection === 'asc' ? (
          <ArrowUpIcon className="w-4 h-4" />
        ) : (
          <ArrowDownIcon className="w-4 h-4" />
        )
      )}
    </button>
  );

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary overflow-hidden">
      <div className="p-6 border-b border-border-primary">
        <h3 className="text-lg font-semibold text-text-primary">保有銘柄一覧</h3>
        <p className="text-sm text-text-secondary mt-1">
          各行をクリックすると取引履歴が表示されます
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-surface-background">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-medium">
                <SortButton field="symbol">銘柄</SortButton>
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium text-text-secondary">
                保有数量
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium text-text-secondary">
                平均取得単価
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium text-text-secondary">
                現在値
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium">
                <SortButton field="market_value">評価額</SortButton>
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium">
                <SortButton field="unrealized_pnl">評価損益</SortButton>
              </th>
              <th className="text-right px-6 py-4 text-sm font-medium">
                <SortButton field="allocation_percent">比率</SortButton>
              </th>
              <th className="text-center px-6 py-4 text-sm font-medium text-text-secondary">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-primary">
            {sortedHoldings.map((holding) => (
              <React.Fragment key={holding.id}>
                {/* メインの行 */}
                <tr 
                  onClick={() => toggleRowExpansion(holding.id)}
                  className="hover:bg-surface-background transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      {expandedRows.has(holding.id) ? (
                        <ChevronUpIcon className="w-4 h-4 text-text-secondary" />
                      ) : (
                        <ChevronDownIcon className="w-4 h-4 text-text-secondary" />
                      )}
                      <div>
                        <div className="font-medium text-text-primary">{holding.symbol}</div>
                        <div className="text-sm text-text-secondary truncate max-w-32">
                          {holding.company_name}
                        </div>
                        <div className="text-xs text-text-secondary">{holding.sector}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-text-primary font-medium">
                    {holding.quantity.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right text-text-primary">
                    {formatCurrency(holding.average_cost)}
                  </td>
                  <td className="px-6 py-4 text-right text-text-primary">
                    {formatCurrency(holding.current_price)}
                  </td>
                  <td className="px-6 py-4 text-right text-text-primary font-medium">
                    {formatCurrency(holding.market_value)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className={`${holding.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      <div className="font-medium">
                        {holding.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(holding.unrealized_pnl)}
                      </div>
                      <div className="text-sm">
                        ({formatPercent(holding.unrealized_pnl_percent)})
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-text-primary font-medium">
                    {formatPercent(holding.allocation_percent)}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowEditModal(holding.id);
                        }}
                        className="text-accent-primary hover:text-accent-primary/80 transition-colors"
                        title="編集"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Handle delete
                        }}
                        className="text-red-500 hover:text-red-400 transition-colors"
                        title="削除"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>

                {/* 展開された取引履歴 */}
                {expandedRows.has(holding.id) && (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 bg-surface-background">
                      <div className="ml-7">
                        <h4 className="text-sm font-medium text-text-primary mb-3">取引履歴</h4>
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="text-xs text-text-secondary">
                                <th className="text-left py-2">日付</th>
                                <th className="text-left py-2">種類</th>
                                <th className="text-right py-2">数量</th>
                                <th className="text-right py-2">価格</th>
                                <th className="text-right py-2">金額</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-border-primary/50">
                              {holding.transactions.map((transaction, index) => (
                                <tr key={index} className="text-sm">
                                  <td className="py-2 text-text-primary">
                                    {new Date(transaction.date).toLocaleDateString('ja-JP')}
                                  </td>
                                  <td className="py-2">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                      transaction.type === 'buy'
                                        ? 'bg-green-500/20 text-green-600'
                                        : 'bg-red-500/20 text-red-600'
                                    }`}>
                                      {transaction.type === 'buy' ? '購入' : '売却'}
                                    </span>
                                  </td>
                                  <td className="py-2 text-right text-text-primary">
                                    {transaction.quantity.toLocaleString()}
                                  </td>
                                  <td className="py-2 text-right text-text-primary">
                                    {formatCurrency(transaction.price)}
                                  </td>
                                  <td className="py-2 text-right text-text-primary font-medium">
                                    {formatCurrency(transaction.quantity * transaction.price)}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* 編集モーダル（簡易版） */}
      {showEditModal && (
        <EditHoldingModal
          holding={sortedHoldings.find(h => h.id === showEditModal)!}
          onClose={() => setShowEditModal(null)}
          onSave={(updatedHolding) => {
            // TODO: Handle update
            console.log('Updated holding:', updatedHolding);
            setShowEditModal(null);
          }}
        />
      )}
    </div>
  );
}

interface EditHoldingModalProps {
  holding: Holding;
  onClose: () => void;
  onSave: (holding: Holding) => void;
}

function EditHoldingModal({ holding, onClose, onSave }: EditHoldingModalProps) {
  const [editData, setEditData] = useState({
    quantity: holding.quantity.toString(),
    average_cost: holding.average_cost.toString(),
  });

  const handleSave = () => {
    const updatedHolding = {
      ...holding,
      quantity: parseInt(editData.quantity),
      average_cost: parseFloat(editData.average_cost),
      market_value: parseInt(editData.quantity) * holding.current_price,
      unrealized_pnl: (parseInt(editData.quantity) * holding.current_price) - (parseInt(editData.quantity) * parseFloat(editData.average_cost)),
    };
    
    updatedHolding.unrealized_pnl_percent = ((updatedHolding.unrealized_pnl / (updatedHolding.quantity * updatedHolding.average_cost)) * 100);
    
    onSave(updatedHolding);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-lg shadow-xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            {holding.symbol} を編集
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">保有数量</label>
              <input
                type="number"
                value={editData.quantity}
                onChange={(e) => setEditData(prev => ({ ...prev, quantity: e.target.value }))}
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">平均取得単価</label>
              <input
                type="number"
                step="0.01"
                value={editData.average_cost}
                onChange={(e) => setEditData(prev => ({ ...prev, average_cost: e.target.value }))}
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                onClick={handleSave}
                className="flex-1 bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                保存
              </button>
              <button
                onClick={onClose}
                className="flex-1 border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}