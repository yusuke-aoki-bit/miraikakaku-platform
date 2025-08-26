'use client';

import { useState, useEffect, useCallback } from 'react';
import PortfolioToolbar from '@/components/portfolio/PortfolioToolbar';
import PortfolioSummary from '@/components/portfolio/PortfolioSummary';
import PortfolioPerformanceChart from '@/components/portfolio/PortfolioPerformanceChart';
import HoldingsAllocation from '@/components/portfolio/HoldingsAllocation';
import HoldingsTable from '@/components/portfolio/HoldingsTable';

interface Portfolio {
  id: string;
  name: string;
  created_at: string;
  is_default: boolean;
}

interface HoldingData {
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
  transactions: TransactionData[];
}

interface TransactionData {
  date: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
}

interface PerformanceData {
  date: string;
  value: number;
  return_percent: number;
}

interface PortfolioData {
  id: string;
  name: string;
  summary: {
    total_value: number;
    total_cost: number;
    total_profit_loss: number;
    total_profit_loss_percent: number;
    daily_change: number;
    daily_change_percent: number;
    annual_dividend_estimate: number;
  };
  holdings: HoldingData[];
  performance_history: PerformanceData[];
}

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [currentPortfolio, setCurrentPortfolio] = useState<PortfolioData | null>(null);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const fetchInitialData = useCallback(async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API calls
      // Mock data for demonstration
      const mockPortfolios: Portfolio[] = [
        {
          id: 'default',
          name: 'メインポートフォリオ',
          created_at: '2024-01-01T00:00:00Z',
          is_default: true,
        },
        {
          id: 'trading',
          name: '短期トレード用',
          created_at: '2024-02-01T00:00:00Z',
          is_default: false,
        },
      ];

      const mockPortfolioData: PortfolioData = {
        id: 'default',
        name: 'メインポートフォリオ',
        summary: {
          total_value: 2715000,
          total_cost: 2650000,
          total_profit_loss: 65000,
          total_profit_loss_percent: 2.45,
          daily_change: 25000,
          daily_change_percent: 0.93,
          annual_dividend_estimate: 45000,
        },
        holdings: [
          {
            id: '1',
            symbol: '7203',
            company_name: 'トヨタ自動車',
            sector: '自動車',
            quantity: 100,
            average_cost: 2800,
            current_price: 2950,
            market_value: 295000,
            unrealized_pnl: 15000,
            unrealized_pnl_percent: 5.36,
            allocation_percent: 10.86,
            transactions: [
              { date: '2024-01-15', type: 'buy', quantity: 100, price: 2800 },
            ],
          },
          {
            id: '2',
            symbol: '6758',
            company_name: 'ソニーグループ',
            sector: 'テクノロジー',
            quantity: 50,
            average_cost: 13500,
            current_price: 13200,
            market_value: 660000,
            unrealized_pnl: -15000,
            unrealized_pnl_percent: -2.22,
            allocation_percent: 24.31,
            transactions: [
              { date: '2024-02-10', type: 'buy', quantity: 50, price: 13500 },
            ],
          },
          {
            id: '3',
            symbol: '9984',
            company_name: 'ソフトバンクグループ',
            sector: 'テクノロジー',
            quantity: 200,
            average_cost: 8500,
            current_price: 8800,
            market_value: 1760000,
            unrealized_pnl: 60000,
            unrealized_pnl_percent: 3.53,
            allocation_percent: 64.83,
            transactions: [
              { date: '2024-01-20', type: 'buy', quantity: 150, price: 8400 },
              { date: '2024-03-05', type: 'buy', quantity: 50, price: 8800 },
            ],
          },
        ],
        performance_history: [], // Will be populated by component
      };

      setPortfolios(mockPortfolios);
      setCurrentPortfolio(mockPortfolioData);
      setSelectedPortfolioId('default');
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const handlePortfolioChange = async (portfolioId: string) => {
    setSelectedPortfolioId(portfolioId);
    // TODO: Fetch specific portfolio data
    // For now, just simulate loading
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 500);
  };

  const handleTransactionAdded = (transaction: TransactionData) => {
    // Refresh portfolio data after transaction
    fetchInitialData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mx-auto mb-4"></div>
          <div className="text-text-secondary">ポートフォリオを読み込み中...</div>
        </div>
      </div>
    );
  }

  if (!currentPortfolio) {
    return (
      <div className="min-h-screen bg-surface-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-text-primary text-lg mb-2">ポートフォリオが見つかりません</div>
          <div className="text-text-secondary">新しいポートフォリオを作成してください</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* ツールバー */}
        <PortfolioToolbar
          portfolios={portfolios}
          selectedPortfolioId={selectedPortfolioId}
          onPortfolioChange={handlePortfolioChange}
          onTransactionAdded={handleTransactionAdded}
        />

        {/* サマリーカード */}
        <PortfolioSummary summary={currentPortfolio.summary} />

        {/* パフォーマンスチャートと資産配分 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioPerformanceChart
            portfolioId={currentPortfolio.id}
            performanceHistory={currentPortfolio.performance_history.map(p => ({
              date: p.date,
              portfolio_value: p.value
            }))}
          />
          <HoldingsAllocation holdings={currentPortfolio.holdings} />
        </div>

        {/* 保有銘柄テーブル */}
        <HoldingsTable
          holdings={currentPortfolio.holdings}
          onTransactionAdded={handleTransactionAdded}
        />
      </div>
    </div>
  );
}