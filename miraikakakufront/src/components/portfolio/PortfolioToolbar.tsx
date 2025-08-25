'use client';

import { useState } from 'react';
import { PlusIcon, FolderPlusIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

interface Portfolio {
  id: string;
  name: string;
  created_at: string;
  is_default: boolean;
}

interface PortfolioToolbarProps {
  portfolios: Portfolio[];
  selectedPortfolioId: string;
  onPortfolioChange: (portfolioId: string) => void;
  onTransactionAdded: (transaction: any) => void;
}

export default function PortfolioToolbar({ 
  portfolios, 
  selectedPortfolioId, 
  onPortfolioChange,
  onTransactionAdded
}: PortfolioToolbarProps) {
  const [showTransactionModal, setShowTransactionModal] = useState(false);
  const [showNewPortfolioModal, setShowNewPortfolioModal] = useState(false);
  const [showPortfolioDropdown, setShowPortfolioDropdown] = useState(false);

  const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId);

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 bg-surface-elevated rounded-lg border border-border-primary">
      {/* 左側: ポートフォリオ選択 */}
      <div className="flex items-center space-x-4">
        <h1 className="text-2xl font-bold text-text-primary">ポートフォリオ</h1>
        
        <div className="relative">
          <button
            onClick={() => setShowPortfolioDropdown(!showPortfolioDropdown)}
            className="flex items-center space-x-2 px-4 py-2 bg-surface-background border border-border-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <span className="text-text-primary font-medium">
              {selectedPortfolio?.name || 'ポートフォリオを選択'}
            </span>
            <ChevronDownIcon className="w-4 h-4 text-text-secondary" />
          </button>

          {showPortfolioDropdown && (
            <div className="absolute top-full left-0 mt-2 w-64 bg-surface-elevated border border-border-primary rounded-lg shadow-lg z-10">
              <div className="py-2">
                {portfolios.map((portfolio) => (
                  <button
                    key={portfolio.id}
                    onClick={() => {
                      onPortfolioChange(portfolio.id);
                      setShowPortfolioDropdown(false);
                    }}
                    className={`w-full text-left px-4 py-3 hover:bg-surface-background transition-colors ${
                      portfolio.id === selectedPortfolioId ? 'bg-accent-primary/10 text-accent-primary' : 'text-text-primary'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{portfolio.name}</div>
                        <div className="text-xs text-text-secondary">
                          作成日: {new Date(portfolio.created_at).toLocaleDateString('ja-JP')}
                        </div>
                      </div>
                      {portfolio.is_default && (
                        <span className="text-xs bg-accent-primary/20 text-accent-primary px-2 py-1 rounded-full">
                          デフォルト
                        </span>
                      )}
                    </div>
                  </button>
                ))}
                
                <hr className="my-2 border-border-primary" />
                
                <button
                  onClick={() => {
                    setShowNewPortfolioModal(true);
                    setShowPortfolioDropdown(false);
                  }}
                  className="w-full text-left px-4 py-3 text-accent-primary hover:bg-surface-background transition-colors flex items-center space-x-2"
                >
                  <FolderPlusIcon className="w-4 h-4" />
                  <span>新しいポートフォリオを作成</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 右側: アクションボタン */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setShowTransactionModal(true)}
          className="bg-accent-primary hover:bg-accent-primary/90 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <PlusIcon className="w-4 h-4" />
          <span>取引を追加</span>
        </button>
      </div>

      {/* 取引追加モーダル */}
      {showTransactionModal && (
        <TransactionModal 
          onClose={() => setShowTransactionModal(false)}
          onTransactionAdded={onTransactionAdded}
          portfolioId={selectedPortfolioId}
        />
      )}

      {/* 新規ポートフォリオモーダル */}
      {showNewPortfolioModal && (
        <NewPortfolioModal 
          onClose={() => setShowNewPortfolioModal(false)}
          onPortfolioCreated={(portfolio) => {
            onPortfolioChange(portfolio.id);
            setShowNewPortfolioModal(false);
          }}
        />
      )}

      {/* ドロップダウン外クリック時の閉じる処理 */}
      {showPortfolioDropdown && (
        <div 
          className="fixed inset-0 z-5"
          onClick={() => setShowPortfolioDropdown(false)}
        />
      )}
    </div>
  );
}

interface TransactionModalProps {
  onClose: () => void;
  onTransactionAdded: (transaction: any) => void;
  portfolioId: string;
}

function TransactionModal({ onClose, onTransactionAdded, portfolioId }: TransactionModalProps) {
  const [transactionData, setTransactionData] = useState({
    type: 'buy',
    symbol: '',
    quantity: '',
    price: '',
    date: new Date().toISOString().split('T')[0],
    fees: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!transactionData.symbol) {
      newErrors.symbol = '銘柄コードを入力してください';
    }
    if (!transactionData.quantity || parseInt(transactionData.quantity) <= 0) {
      newErrors.quantity = '正しい数量を入力してください';
    }
    if (!transactionData.price || parseFloat(transactionData.price) <= 0) {
      newErrors.price = '正しい価格を入力してください';
    }
    if (!transactionData.date) {
      newErrors.date = '取引日を選択してください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      // TODO: API call to add transaction
      const transaction = {
        portfolio_id: portfolioId,
        type: transactionData.type,
        symbol: transactionData.symbol.toUpperCase(),
        quantity: parseInt(transactionData.quantity),
        price: parseFloat(transactionData.price),
        date: transactionData.date,
        fees: transactionData.fees ? parseFloat(transactionData.fees) : 0,
      };

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      onTransactionAdded(transaction);
      onClose();
    } catch (error) {
      console.error('Failed to add transaction:', error);
      setErrors({ submit: '取引の追加に失敗しました' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-lg shadow-xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">取引を追加</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 取引種別 */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">取引種別</label>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setTransactionData(prev => ({ ...prev, type: 'buy' }))}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                    transactionData.type === 'buy'
                      ? 'bg-green-500 text-white'
                      : 'bg-surface-background text-text-secondary hover:bg-surface-elevated'
                  }`}
                >
                  購入
                </button>
                <button
                  type="button"
                  onClick={() => setTransactionData(prev => ({ ...prev, type: 'sell' }))}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                    transactionData.type === 'sell'
                      ? 'bg-red-500 text-white'
                      : 'bg-surface-background text-text-secondary hover:bg-surface-elevated'
                  }`}
                >
                  売却
                </button>
              </div>
            </div>

            {/* 銘柄コード */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">銘柄コード</label>
              <input
                type="text"
                value={transactionData.symbol}
                onChange={(e) => setTransactionData(prev => ({ ...prev, symbol: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                  errors.symbol ? 'border-red-500' : 'border-border-primary'
                }`}
                placeholder="例: 7203, AAPL"
              />
              {errors.symbol && <p className="text-red-500 text-sm mt-1">{errors.symbol}</p>}
            </div>

            {/* 数量と価格 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">数量</label>
                <input
                  type="number"
                  value={transactionData.quantity}
                  onChange={(e) => setTransactionData(prev => ({ ...prev, quantity: e.target.value }))}
                  className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.quantity ? 'border-red-500' : 'border-border-primary'
                  }`}
                  placeholder="100"
                />
                {errors.quantity && <p className="text-red-500 text-sm mt-1">{errors.quantity}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">価格（円）</label>
                <input
                  type="number"
                  step="0.01"
                  value={transactionData.price}
                  onChange={(e) => setTransactionData(prev => ({ ...prev, price: e.target.value }))}
                  className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.price ? 'border-red-500' : 'border-border-primary'
                  }`}
                  placeholder="2800.00"
                />
                {errors.price && <p className="text-red-500 text-sm mt-1">{errors.price}</p>}
              </div>
            </div>

            {/* 取引日と手数料 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">取引日</label>
                <input
                  type="date"
                  value={transactionData.date}
                  onChange={(e) => setTransactionData(prev => ({ ...prev, date: e.target.value }))}
                  className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.date ? 'border-red-500' : 'border-border-primary'
                  }`}
                />
                {errors.date && <p className="text-red-500 text-sm mt-1">{errors.date}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">手数料（円）</label>
                <input
                  type="number"
                  step="0.01"
                  value={transactionData.fees}
                  onChange={(e) => setTransactionData(prev => ({ ...prev, fees: e.target.value }))}
                  className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
                  placeholder="0.00"
                />
              </div>
            </div>

            {errors.submit && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-500 text-sm">{errors.submit}</p>
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '追加中...' : '取引を追加'}
              </button>
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1 border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                キャンセル
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

interface NewPortfolioModalProps {
  onClose: () => void;
  onPortfolioCreated: (portfolio: any) => void;
}

function NewPortfolioModal({ onClose, onPortfolioCreated }: NewPortfolioModalProps) {
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('ポートフォリオ名を入力してください');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: API call to create portfolio
      const portfolio = {
        id: Date.now().toString(),
        name: name.trim(),
        created_at: new Date().toISOString(),
        is_default: false,
      };

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      onPortfolioCreated(portfolio);
    } catch (error) {
      console.error('Failed to create portfolio:', error);
      setError('ポートフォリオの作成に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-lg shadow-xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">新しいポートフォリオを作成</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">ポートフォリオ名</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
                placeholder="例: 長期投資用、短期トレード用"
              />
              {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '作成中...' : '作成'}
              </button>
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1 border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                キャンセル
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}