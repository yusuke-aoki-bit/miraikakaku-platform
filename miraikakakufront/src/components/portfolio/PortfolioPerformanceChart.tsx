'use client';

import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  TooltipItem
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PerformanceDataPoint {
  date: string;
  portfolio_value: number;
  benchmark_value?: number;
}

interface PortfolioPerformanceChartProps {
  portfolioId: string;
  performanceHistory?: PerformanceDataPoint[];
}

type TimePeriod = '1M' | '6M' | '1Y' | 'ALL';

const BENCHMARK_OPTIONS = [
  { id: 'topix', name: 'TOPIX', enabled: true },
  { id: 'nikkei225', name: '日経225', enabled: false },
  { id: 'sp500', name: 'S&P 500', enabled: false },
];

export default function PortfolioPerformanceChart({ portfolioId, performanceHistory }: PortfolioPerformanceChartProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('6M');
  const [benchmarks, setBenchmarks] = useState(BENCHMARK_OPTIONS);
  const [data, setData] = useState<PerformanceDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformanceData();
  }, [portfolioId, selectedPeriod]);

  const fetchPerformanceData = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await apiClient.getPortfolioPerformanceHistory(portfolioId, selectedPeriod);
      
      // Generate mock data for demonstration
      const mockData = generateMockPerformanceData(selectedPeriod);
      setData(mockData);
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockPerformanceData = (period: TimePeriod): PerformanceDataPoint[] => {
    const dataPoints = period === '1M' ? 30 : period === '6M' ? 180 : period === '1Y' ? 365 : 730;
    const baseValue = 2650000; // 初期ポートフォリオ価値
    const data: PerformanceDataPoint[] = [];
    
    let portfolioValue = baseValue;
    let benchmarkValue = 100; // 基準値
    
    for (let i = 0; i < dataPoints; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (dataPoints - i));
      
      // ポートフォリオの値動きをシミュレート（わずかな上昇傾向）
      const portfolioChange = (Math.random() - 0.48) * 0.02; // わずかに上昇バイアス
      portfolioValue *= (1 + portfolioChange);
      
      // ベンチマークの値動きをシミュレート（より安定した動き）
      const benchmarkChange = (Math.random() - 0.5) * 0.015;
      benchmarkValue *= (1 + benchmarkChange);
      
      data.push({
        date: date.toISOString().split('T')[0],
        portfolio_value: Math.round(portfolioValue),
        benchmark_value: benchmarkValue,
      });
    }
    
    return data;
  };

  const handleBenchmarkToggle = (benchmarkId: string) => {
    setBenchmarks(prev => 
      prev.map(b => 
        b.id === benchmarkId ? { ...b, enabled: !b.enabled } : b
      )
    );
  };

  const formatCurrency = (value: number) => {
    return `¥${(value / 1000000).toFixed(1)}M`;
  };

  const formatPercent = (value: number, baseline: number) => {
    const percent = ((value - baseline) / baseline) * 100;
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(1)}%`;
  };

  const chartData = {
    labels: data.map(d => d.date),
    datasets: [
      {
        label: 'ポートフォリオ',
        data: data.map(d => d.portfolio_value),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
      },
      // ベンチマーク（有効化されている場合）
      ...benchmarks
        .filter(b => b.enabled)
        .map((benchmark, index) => ({
          label: benchmark.name,
          data: data.map(d => {
            // ベンチマークの値をポートフォリオの初期値に正規化
            const basePortfolioValue = data[0]?.portfolio_value || 2650000;
            return (d.benchmark_value || 100) * (basePortfolioValue / 100);
          }),
          borderColor: index === 0 ? 'rgb(34, 197, 94)' : index === 1 ? 'rgb(251, 146, 60)' : 'rgb(168, 85, 247)',
          backgroundColor: 'transparent',
          borderWidth: 1.5,
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderDash: [5, 5],
        }))
    ]
  };

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: 'rgb(156, 163, 175)',
          usePointStyle: true,
          padding: 20,
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgb(31, 41, 55)',
        titleColor: 'rgb(249, 250, 251)',
        bodyColor: 'rgb(209, 213, 219)',
        borderColor: 'rgb(75, 85, 99)',
        borderWidth: 1,
        callbacks: {
          label: function(context: TooltipItem<'line'>) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            
            if (label === 'ポートフォリオ') {
              return `${label}: ${formatCurrency(value)}`;
            } else {
              // ベンチマークの場合は相対パフォーマンスも表示
              const baseValue = data[0]?.portfolio_value || 2650000;
              const benchmarkBaseValue = (data[0]?.benchmark_value || 100) * (baseValue / 100);
              return [
                `${label}: ${formatCurrency(value)}`,
                `パフォーマンス: ${formatPercent(value, benchmarkBaseValue)}`
              ];
            }
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false,
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
          maxTicksLimit: 8,
        }
      },
      y: {
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(75, 85, 99, 0.3)',
        },
        ticks: {
          color: 'rgb(107, 114, 128)',
          callback: function(value) {
            return formatCurrency(value as number);
          }
        }
      }
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    }
  };

  const periods: { id: TimePeriod; label: string }[] = [
    { id: '1M', label: '1ヶ月' },
    { id: '6M', label: '6ヶ月' },
    { id: '1Y', label: '1年' },
    { id: 'ALL', label: '全期間' },
  ];

  if (loading) {
    return (
      <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-text-primary">パフォーマンス推移</h3>
        </div>
        <div className="h-80 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-text-primary">パフォーマンス推移</h3>
        
        {/* 期間選択 */}
        <div className="flex items-center space-x-1 bg-surface-background rounded-lg p-1">
          {periods.map((period) => (
            <button
              key={period.id}
              onClick={() => setSelectedPeriod(period.id)}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                selectedPeriod === period.id
                  ? 'bg-accent-primary text-white'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>
      </div>

      {/* ベンチマーク選択 */}
      <div className="mb-4">
        <div className="flex items-center space-x-4 text-sm">
          <span className="text-text-secondary">比較対象:</span>
          {benchmarks.map((benchmark) => (
            <label key={benchmark.id} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={benchmark.enabled}
                onChange={() => handleBenchmarkToggle(benchmark.id)}
                className="rounded border-border-primary text-accent-primary focus:ring-accent-primary mr-2"
              />
              <span className="text-text-primary">{benchmark.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* チャート */}
      <div className="h-80">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* パフォーマンス統計 */}
      {data.length > 0 && (
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-border-primary">
          <div className="text-center">
            <div className="text-sm text-text-secondary mb-1">期間リターン</div>
            <div className="text-lg font-semibold text-text-primary">
              {formatPercent(data[data.length - 1].portfolio_value, data[0].portfolio_value)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-text-secondary mb-1">最高値</div>
            <div className="text-lg font-semibold text-text-primary">
              {formatCurrency(Math.max(...data.map(d => d.portfolio_value)))}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-text-secondary mb-1">最安値</div>
            <div className="text-lg font-semibold text-text-primary">
              {formatCurrency(Math.min(...data.map(d => d.portfolio_value)))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}