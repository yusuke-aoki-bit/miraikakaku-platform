'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
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
      // API呼び出しでポートフォリオリストを取得
      const portfoliosResponse = await apiClient.listPortfolios();
      
      if (portfoliosResponse.success && portfoliosResponse.data) {
        const portfolios = Array.isArray(portfoliosResponse.data) ? portfoliosResponse.data : [];
        setPortfolios(portfolios);
        
        // デフォルトポートフォリオまたは最初のポートフォリオを選択
        const defaultPortfolio = portfolios.find(p => p.is_default) || portfolios[0];
        if (defaultPortfolio) {
          setSelectedPortfolioId(defaultPortfolio.id);
          
          // 選択されたポートフォリオの詳細データを取得
          const portfolioDetailResponse = await apiClient.getPortfolio(defaultPortfolio.id);
          if (portfolioDetailResponse.success && portfolioDetailResponse.data) {
            setCurrentPortfolio(portfolioDetailResponse.data);
          }
        }
      } else {
        // データがない場合は空の状態を表示
        setPortfolios([]);
        setCurrentPortfolio(null);
        setSelectedPortfolioId('');
      }
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
    setLoading(true);
    
    try {
      const portfolioDetailResponse = await apiClient.getPortfolio(portfolioId);
      if (portfolioDetailResponse.success && portfolioDetailResponse.data) {
        setCurrentPortfolio(portfolioDetailResponse.data);
      }
    } catch (error) {
      console.error('Failed to fetch portfolio details:', error);
    } finally {
      setLoading(false);
    }
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