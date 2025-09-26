'use client';

import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { Plus, X, GitCompare } from 'lucide-react';
import { StockPrice } from '../types';

interface ComparisonStock {
  symbol: string;
  name?: string;
  data: StockPrice[];
  color: string;
}

interface StockComparisonProps {
  primaryStock: {
    symbol: string;
    name?: string;
    data: StockPrice[];
  };
  className?: string;
}

const COMPARISON_COLORS = [
  '#8884d8', // Primary stock (blue)
  '#82ca9d', // Green
  '#ffc658', // Yellow
  '#ff7c7c', // Red
  '#8dd1e1', // Light blue
  '#d084d0', // Purple
  '#ffb347', // Orange
  '#87ceeb'  // Sky blue
];

export default function StockComparison({ primaryStock, className = '' }: StockComparisonProps) {
  const [comparisonStocks, setComparisonStocks] = useState<ComparisonStock[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddingStock, setIsAddingStock] = useState(false);
  const [normalizePrices, setNormalizePrices] = useState(true);
  // Mock search function - in real app, this would call an API
  const searchStocks = async (query: string) => {
    // Mock data for demonstration
    const mockResults = [
      { symbol: 'AAPL', name: 'Apple Inc.' },
      { symbol: 'GOOGL', name: 'Alphabet Inc.' },
      { symbol: 'MSFT', name: 'Microsoft Corporation' },
      { symbol: 'AMZN', name: 'Amazon.com Inc.' },
      { symbol: 'TSLA', name: 'Tesla Inc.' },
      { symbol: '7203.T', name: 'Toyota Motor Corporation' },
      { symbol: '6758.T', name: 'Sony Group Corporation' }
    ];

    return mockResults.filter(stock =>
      stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
      stock.name.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 5);
  };

  const [searchResults, setSearchResults] = useState<any[]>([]);
  const handleSearch = async (value: string) => {
    setSearchTerm(value);
    if (value.length > 1) {
      const results = await searchStocks(value);
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  };

  const addComparisonStock = async (symbol: string, name?: string) => {
    if (comparisonStocks.length >= 6) {
      alert('最大6銘柄まで比較できます');
      return;
    }

    if (symbol === primaryStock.symbol || comparisonStocks.some(s => s.symbol === symbol)) {
      alert('この銘柄は既に追加されています');
      return;
    }

    try {
      // 実際のAPIからデータを取得
      const response = await fetch(`http://localhost:8080/api/finance/stocks/${symbol}/price`);
      if (!response.ok) {
        throw new Error('API接続エラー');
      }
      const data = await response.json();
      const newStock: ComparisonStock = {
        symbol,
        ...(name && { name }),
        data: Array.isArray(data) ? data : [],
        color: COMPARISON_COLORS[(comparisonStocks.length + 1) % COMPARISON_COLORS.length] || '#3b82f6'
      };

      setComparisonStocks(prev => [...prev, newStock]);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      alert(`${symbol}のデータを取得できませんでした。サーバーに接続できません。`);
    }

    setSearchTerm('');
    setSearchResults([]);
    setIsAddingStock(false);
  };

  const removeComparisonStock = (symbol: string) => {
    setComparisonStocks(prev => prev.filter(stock => stock.symbol !== symbol));
  };


  // Normalize prices to percentage change from first data point
  const normalizeData = (data: StockPrice[]) => {
    if (data.length === 0) return [];
    const firstPrice = data[0]!.close_price || 1;
    return data.map(item => ({
      ...item,
      normalized_price: ((item.close_price || 0) - firstPrice) / firstPrice * 100
    }));
  };

  // Combine all stock data for chart
  const chartData = useMemo(() => {
    const dataMap = new Map();
    // Add primary stock data
    const primaryData = normalizePrices ? normalizeData(primaryStock.data) : primaryStock.data;
    primaryData.forEach(item => {
      dataMap.set(item.date, {
        date: item.date,
        [primaryStock.symbol]: normalizePrices ? item.normalized_price : item.close_price
      });
    });
    // Add comparison stocks data
    comparisonStocks.forEach(stock => {
      const stockData = normalizePrices ? normalizeData(stock.data) : stock.data;
      stockData.forEach(item => {
        const existing = dataMap.get(item.date) || { date: item.date };
        dataMap.set(item.date, {
          ...existing,
          [stock.symbol]: normalizePrices ? item.normalized_price : item.close_price
        });
      });
    });
    return Array.from(dataMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [primaryStock, comparisonStocks, normalizePrices]);
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="p-3 border rounded shadow-lg" style={{
          backgroundColor: '#0f0f0f',
          borderColor: '#333333',
          color: '#f1f1f1'
        }}>
          <p className="font-semibold" style={{ color: '#f1f1f1' }}>
            {format(parseISO(label), 'yyyy/MM/dd')}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.dataKey}: {normalizePrices
                ? `${entry.value > 0 ? '+' : ''}${entry.value.toFixed(2)}%`
                : `¥${entry.value.toFixed(2)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center" style={{ color: '#f1f1f1' }}>
          <GitCompare className="w-5 h-5 mr-2" />
          銘柄比較
        </h3>
        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2 text-sm" style={{ color: '#f1f1f1' }}>
            <input
              type="checkbox"
              checked={normalizePrices}
              onChange={(e) => setNormalizePrices(e.target.checked)}
              className="rounded"
              style={{
                accentColor: 'var(--yt-music-primary)'
              }}
            />
            <span>正規化表示（%変化）</span>
          </label>
        </div>
      </div>

      {/* Add Stock Section */}
      <div className="border rounded-lg p-4" style={{
        backgroundColor: '#0f0f0f',
        borderColor: '#333333'
      }}>
        {!isAddingStock ? (
          <button
            onClick={() => setIsAddingStock(true)}
            className="flex items-center space-x-2 transition-colors"
            style={{ color: 'var(--yt-music-primary)' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--yt-music-primary-hover)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--yt-music-primary)';
            }}
          >
            <Plus className="w-4 h-4" />
            <span>比較銘柄を追加</span>
          </button>
        ) : (
          <div className="space-y-3">
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="銘柄コードまたは企業名を入力 (例: AAPL, Apple)"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent"
                style={{
                  backgroundColor: '#0f0f0f',
                  borderColor: '#333333',
                  color: '#f1f1f1',
                  '--tw-ring-color': 'var(--yt-music-primary)'
                } as React.CSSProperties}
                autoFocus
              />
              {searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 border rounded-lg mt-1 shadow-lg z-10" style={{
                  backgroundColor: '#0f0f0f',
                  borderColor: '#333333'
                }}>
                  {searchResults.map((result, index) => (
                    <button
                      key={index}
                      onClick={() => addComparisonStock(result.symbol, result.name)}
                      className="w-full px-3 py-2 text-left first:rounded-t-lg last:rounded-b-lg transition-colors"
                      style={{ color: '#f1f1f1' }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <div className="font-medium" style={{ color: '#f1f1f1' }}>
                        {result.symbol}
                      </div>
                      <div className="text-sm" style={{ color: '#aaaaaa' }}>
                        {result.name}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setIsAddingStock(false);
                  setSearchTerm('');
                  setSearchResults([]);
                }}
                className="px-3 py-1 text-sm rounded-lg transition-colors"
                style={{
                  backgroundColor: 'var(--yt-music-surface-variant)',
                  color: '#f1f1f1'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                }}
              >
                キャンセル
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Current Comparison Stocks */}
      {comparisonStocks.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium" style={{ color: '#f1f1f1' }}>比較中の銘柄:</h4>
          <div className="flex flex-wrap gap-2">
            <div className="flex items-center space-x-2 px-3 py-1 rounded-lg text-sm" style={{
              backgroundColor: 'var(--yt-music-primary)',
              color: 'white'
            }}>
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COMPARISON_COLORS[0] }}></div>
              <span className="font-medium">{primaryStock.symbol}</span>
              <span>{primaryStock.name || ''}</span>
            </div>
            {comparisonStocks.map((stock) => (
              <div key={stock.symbol} className="flex items-center space-x-2 px-3 py-1 rounded-lg text-sm" style={{
                backgroundColor: 'var(--yt-music-surface-variant)',
                color: '#f1f1f1'
              }}>
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: stock.color }}></div>
                <span className="font-medium">{stock.symbol}</span>
                <span style={{ color: '#aaaaaa' }}>{stock.name || ''}</span>
                <button
                  onClick={() => removeComparisonStock(stock.symbol)}
                  className="transition-colors"
                  style={{ color: '#aaaaaa' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--yt-music-error)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#aaaaaa';
                  }}
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Chart */}
      <div className="h-96 border rounded-lg p-4" style={{
        backgroundColor: '#0f0f0f',
        borderColor: '#333333'
      }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MM/dd')}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <YAxis
              tickFormatter={(value) => normalizePrices ? `${value.toFixed(1)}%` : `¥${value.toFixed(0)}`}
              tick={{ fill: '#aaaaaa', fontSize: 12 }}
              axisLine={{ stroke: '#333333' }}
              tickLine={{ stroke: '#333333' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                color: '#f1f1f1',
                paddingTop: '20px'
              }}
            />

            {/* Primary stock line */}
            <Line
              type="monotone"
              dataKey={primaryStock.symbol}
              stroke={COMPARISON_COLORS[0]}
              strokeWidth={3}
              dot={false}
              name={`${primaryStock.symbol}${primaryStock.name ? ` (${primaryStock.name})` : ''}`}
            />

            {/* Comparison stock lines */}
            {comparisonStocks.map((stock) => (
              <Line
                key={stock.symbol}
                type="monotone"
                dataKey={stock.symbol}
                stroke={stock.color}
                strokeWidth={2}
                dot={false}
                name={`${stock.symbol}${stock.name ? ` (${stock.name})` : ''}`}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Summary */}
      {comparisonStocks.length > 0 && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[{ ...primaryStock, color: COMPARISON_COLORS[0] }, ...comparisonStocks].map((stock) => {
            const latestData = stock.data[stock.data.length - 1];
            const firstData = stock.data[0];
            const totalReturn = firstData && latestData ? ((latestData.close_price || 0) - (firstData.close_price || 0)) / (firstData.close_price || 1) * 100 : 0;

            return (
              <div key={stock.symbol} className="border rounded-lg p-3" style={{
                backgroundColor: 'var(--yt-music-bg)',
                borderColor: '#333333'
              }}>
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: stock.color }}></div>
                  <span className="font-medium">{stock.symbol}</span>
                </div>
                <div className="text-sm space-y-1">
                  <div className="flex justify-between">
                    <span style={{ color: '#aaaaaa' }}>現在価格:</span>
                    <span className="font-medium" style={{ color: '#f1f1f1' }}>¥{(latestData?.close_price || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: '#aaaaaa' }}>期間収益率:</span>
                    <span className={`font-medium`} style={{
                      color: totalReturn >= 0 ? 'var(--yt-music-chart-green)' : 'var(--yt-music-chart-red)'
                    }}>
                      {totalReturn > 0 ? '+' : ''}{totalReturn.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}