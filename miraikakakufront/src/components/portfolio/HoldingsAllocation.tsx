'use client';

import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Holding {
  id: string;
  symbol: string;
  company_name: string;
  sector: string;
  market_value: number;
  allocation_percent: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
}

interface HoldingsAllocationProps {
  holdings: Holding[];
}

export default function HoldingsAllocation({ holdings }: HoldingsAllocationProps) {
  // 色のパレット
  const colors = [
    { bg: 'rgba(59, 130, 246, 0.8)', border: 'rgba(59, 130, 246, 1)' },
    { bg: 'rgba(16, 185, 129, 0.8)', border: 'rgba(16, 185, 129, 1)' },
    { bg: 'rgba(251, 146, 60, 0.8)', border: 'rgba(251, 146, 60, 1)' },
    { bg: 'rgba(147, 51, 234, 0.8)', border: 'rgba(147, 51, 234, 1)' },
    { bg: 'rgba(236, 72, 153, 0.8)', border: 'rgba(236, 72, 153, 1)' },
    { bg: 'rgba(14, 165, 233, 0.8)', border: 'rgba(14, 165, 233, 1)' },
    { bg: 'rgba(34, 197, 94, 0.8)', border: 'rgba(34, 197, 94, 1)' },
    { bg: 'rgba(249, 115, 22, 0.8)', border: 'rgba(249, 115, 22, 1)' },
  ];

  // 銘柄別アロケーション
  const stockAllocationData = {
    labels: holdings.map(h => h.symbol),
    datasets: [{
      data: holdings.map(h => h.market_value),
      backgroundColor: holdings.map((_, index) => colors[index % colors.length].bg),
      borderColor: holdings.map((_, index) => colors[index % colors.length].border),
      borderWidth: 2,
      hoverOffset: 8,
    }]
  };

  // セクター別アロケーション
  const sectorData = holdings.reduce((acc, holding) => {
    const sector = holding.sector || 'その他';
    acc[sector] = (acc[sector] || 0) + holding.market_value;
    return acc;
  }, {} as Record<string, number>);

  const sectorAllocationData = {
    labels: Object.keys(sectorData),
    datasets: [{
      data: Object.values(sectorData),
      backgroundColor: Object.keys(sectorData).map((_, index) => colors[index % colors.length].bg),
      borderColor: Object.keys(sectorData).map((_, index) => colors[index % colors.length].border),
      borderWidth: 2,
      hoverOffset: 8,
    }]
  };

  const chartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgb(156, 163, 175)',
          padding: 15,
          usePointStyle: true,
          font: {
            size: 12,
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgb(31, 41, 55)',
        titleColor: 'rgb(249, 250, 251)',
        bodyColor: 'rgb(209, 213, 219)',
        borderColor: 'rgb(75, 85, 99)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0) as number;
            const percentage = ((value / total) * 100).toFixed(1);
            const formattedValue = `¥${value.toLocaleString('ja-JP')}`;
            return `${label}: ${formattedValue} (${percentage}%)`;
          }
        }
      }
    },
    cutout: '60%',
  };

  const formatCurrency = (amount: number) => {
    return `¥${amount.toLocaleString('ja-JP')}`;
  };

  const formatPercent = (percent: number) => {
    return `${percent.toFixed(1)}%`;
  };

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      <h3 className="text-lg font-semibold text-text-primary mb-6">保有資産アロケーション</h3>

      <div className="space-y-8">
        {/* 銘柄別アロケーション */}
        <div>
          <h4 className="text-md font-medium text-text-primary mb-4">銘柄別配分</h4>
          <div className="flex items-center space-x-6">
            {/* ドーナツチャート */}
            <div className="w-48 h-48 flex-shrink-0">
              <Doughnut data={stockAllocationData} options={chartOptions} />
            </div>

            {/* 銘柄リスト */}
            <div className="flex-1 max-h-48 overflow-y-auto">
              <div className="space-y-2">
                {holdings
                  .sort((a, b) => b.market_value - a.market_value)
                  .map((holding, index) => (
                    <div key={holding.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-surface-background transition-colors">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: colors[holdings.findIndex(h => h.id === holding.id) % colors.length].border }}
                        />
                        <div>
                          <div className="font-medium text-text-primary text-sm">{holding.symbol}</div>
                          <div className="text-xs text-text-secondary truncate max-w-24">{holding.company_name}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-text-primary">
                          {formatPercent(holding.allocation_percent)}
                        </div>
                        <div className="text-xs text-text-secondary">
                          {formatCurrency(holding.market_value)}
                        </div>
                      </div>
                    </div>
                  ))
                }
              </div>
            </div>
          </div>
        </div>

        {/* 区切り線 */}
        <hr className="border-border-primary" />

        {/* セクター別アロケーション */}
        <div>
          <h4 className="text-md font-medium text-text-primary mb-4">セクター別配分</h4>
          <div className="flex items-center space-x-6">
            {/* ドーナツチャート */}
            <div className="w-48 h-48 flex-shrink-0">
              <Doughnut data={sectorAllocationData} options={chartOptions} />
            </div>

            {/* セクターリスト */}
            <div className="flex-1 max-h-48 overflow-y-auto">
              <div className="space-y-2">
                {Object.entries(sectorData)
                  .sort(([,a], [,b]) => b - a)
                  .map(([sector, value], index) => {
                    const percentage = (value / holdings.reduce((sum, h) => sum + h.market_value, 0)) * 100;
                    return (
                      <div key={sector} className="flex items-center justify-between p-2 rounded-lg hover:bg-surface-background transition-colors">
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-3 h-3 rounded-full flex-shrink-0"
                            style={{ backgroundColor: colors[index % colors.length].border }}
                          />
                          <div className="font-medium text-text-primary text-sm">{sector}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-text-primary">
                            {formatPercent(percentage)}
                          </div>
                          <div className="text-xs text-text-secondary">
                            {formatCurrency(value)}
                          </div>
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 統計情報 */}
      <div className="mt-6 pt-4 border-t border-border-primary">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-sm text-text-secondary mb-1">総銘柄数</div>
            <div className="text-lg font-semibold text-text-primary">{holdings.length}</div>
          </div>
          <div>
            <div className="text-sm text-text-secondary mb-1">最大保有比率</div>
            <div className="text-lg font-semibold text-text-primary">
              {formatPercent(Math.max(...holdings.map(h => h.allocation_percent)))}
            </div>
          </div>
          <div>
            <div className="text-sm text-text-secondary mb-1">セクター数</div>
            <div className="text-lg font-semibold text-text-primary">
              {Object.keys(sectorData).length}
            </div>
          </div>
          <div>
            <div className="text-sm text-text-secondary mb-1">集中度</div>
            <div className="text-lg font-semibold text-text-primary">
              {holdings.length <= 5 ? '高' : holdings.length <= 10 ? '中' : '低'}
            </div>
          </div>
        </div>
      </div>

      {/* リスク警告 */}
      {holdings.some(h => h.allocation_percent > 30) && (
        <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <div className="flex items-start space-x-2">
            <div className="w-1 h-1 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <div className="text-sm font-medium text-yellow-600 mb-1">集中リスクに注意</div>
              <div className="text-xs text-yellow-700">
                特定の銘柄の保有比率が30%を超えています。リスク分散のため、ポートフォリオのリバランスを検討してください。
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}