'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient, StockPrice } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

interface CompareStock {
  symbol: string;
  company_name: string;
  price_history: StockPrice[];
  predictions?: any[];
  color: string;
  currentPrice?: number;
  predictedPrice?: number;
  predictionChange?: number;
}

interface SearchResult {
  symbol: string;
  company_name: string;
  exchange: string;
}

interface SavedSet {
  name: string;
  symbols: string[];
  createdAt: string;
}

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
const STORAGE_KEY = 'miraikakaku_saved_compare_sets';

const DEFAULT_SETS: SavedSet[] = [
  {
    name: '米国テック大手',
    symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    createdAt: new Date().toISOString()
  },
  {
    name: '日本主要株',
    symbols: ['7203.T', '6758.T', '9984.T', '8306.T'],
    createdAt: new Date().toISOString()
  },
  {
    name: '半導体関連',
    symbols: ['NVDA', 'AMD', 'INTC', 'TSM'],
    createdAt: new Date().toISOString()
  }
];

export default function ComparePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const symbolsParam = searchParams.get('symbols');

  const [stocks, setStocks] = useState<CompareStock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(
    symbolsParam ? symbolsParam.split(',') : []
  );
    const [showPredictions, setShowPredictions] = useState(true);
  const [savedSets, setSavedSets] = useState<SavedSet[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [newSetName, setNewSetName] = useState('');
  const [showSavedSets, setShowSavedSets] = useState(false);

  useEffect(() => {
    if (selectedSymbols.length > 0) {
      fetchStocks();
    }
  }, [selectedSymbols]);

  // Load saved sets from localStorage
  useEffect(() => {
    const loadSavedSets = () => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const sets = JSON.parse(stored);
          setSavedSets(sets);
        } catch (err) {
          console.error('Failed to load saved sets:', err);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_SETS));
          setSavedSets(DEFAULT_SETS);
        }
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_SETS));
        setSavedSets(DEFAULT_SETS);
      }
    };
    loadSavedSets();
  }, []);

  useEffect(() => {
    const delaySearch = setTimeout(() => {
      if (searchTerm.length >= 2) {
        searchStocks();
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(delaySearch);
  }, [searchTerm]);

  const saveCurrentSet = () => {
    if (!newSetName.trim()) {
      setError('セット名を入力してください');
      return;
    }
    if (selectedSymbols.length === 0) {
      setError('保存する銘柄を選択してください');
      return;
    }

    const newSet: SavedSet = {
      name: newSetName.trim(),
      symbols: [...selectedSymbols],
      createdAt: new Date().toISOString()
    };

    const updatedSets = [...savedSets, newSet];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSets));
    setSavedSets(updatedSets);
    setShowSaveDialog(false);
    setNewSetName('');
    setError('');
  };

  const loadSavedSet = (set: SavedSet) => {
    setSelectedSymbols(set.symbols);
    setShowSavedSets(false);
    setError('');
  };

  const deleteSavedSet = (setName: string) => {
    const updatedSets = savedSets.filter(s => s.name !== setName);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSets));
    setSavedSets(updatedSets);
  };

  const searchStocks = async () => {
    setIsSearching(true);
    try {
      // 修正: 正しいポート8081を使用
      const response = await fetch(`http://localhost:8081/api/search?q=${encodeURIComponent(searchTerm)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results.slice(0, 10));
      }
    } catch (err) {
      console.error('Search failed:', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const fetchStocks = async () => {
    setLoading(true);
    setError('');

    try {
      const stocksData = await Promise.all(
        selectedSymbols.map(async (symbol, index) => {
          try {
            const data = await apiClient.getStockInfo(symbol);

            // 予測データも取得
            let predictions = [];
            let predictedPrice = undefined;
            const currentPrice = data.price_history[0]?.close_price || undefined;

            try {
              const predictionResponse = await fetch(`http://localhost:8081/api/predictions/${symbol}`);
              if (predictionResponse.ok) {
                const predData = await predictionResponse.json();
                predictions = predData.predictions || [];
                if (predictions.length > 0) {
                  predictedPrice = predictions[0].predicted_price;
                }
              }
            } catch (predErr) {
              console.warn(`Failed to fetch predictions for ${symbol}:`, predErr);
            }

            return {
              symbol: data.symbol,
              company_name: data.company_name,
              price_history: data.price_history.slice(0, 30), // 直近30日
              predictions,
              currentPrice,
              predictedPrice,
              predictionChange: predictedPrice && currentPrice
                ? ((predictedPrice - currentPrice) / currentPrice) * 100
                : undefined,
              color: CHART_COLORS[index % CHART_COLORS.length],
            };
          } catch (err) {
            console.error(`Failed to fetch data for ${symbol}:`, err);
            throw err;
          }
        })
      );
      setStocks(stocksData);
    } catch (err) {
      setError('銘柄データの取得に失敗しました。銘柄コードを確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const addSymbol = (symbol?: string) => {
    const symbolToAdd = symbol || searchTerm.trim().toUpperCase();
    if (!symbolToAdd) return;

    if (selectedSymbols.includes(symbolToAdd)) {
      setError('この銘柄は既に追加されています');
      return;
    }

    if (selectedSymbols.length >= 6) {
      setError('最大6銘柄まで比較できます');
      return;
    }

    setSelectedSymbols([...selectedSymbols, symbolToAdd]);
    setSearchTerm('');
    setSearchResults([]);
    setError('');
  };

  const removeSymbol = (symbol: string) => {
    setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
    setStocks(stocks.filter(s => s.symbol !== symbol));
  };

  const prepareChartData = () => {
    if (stocks.length === 0) return [];

    // すべての銘柄の日付を収集
    const allDates = new Set<string>();
    stocks.forEach(stock => {
      stock.price_history.forEach(price => {
        allDates.add(price.date);
      });
    });

    // 日付でソート
    const sortedDates = Array.from(allDates).sort((a, b) =>
      new Date(a).getTime() - new Date(b).getTime()
    );

    // チャートデータを作成
    return sortedDates.map(date => {
      const dataPoint: any = { date: new Date(date).toLocaleDateString('ja-JP') };

      stocks.forEach(stock => {
        const priceData = stock.price_history.find(p => p.date === date);
        if (priceData && priceData.close_price) {
          dataPoint[stock.symbol] = priceData.close_price;
        }
      });

      return dataPoint;
    });
  };

  const retryFetch = () => {
    setError('');
    fetchStocks();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 dark:text-blue-400 hover:underline mb-4"
          >
            ← ホームに戻る
          </button>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            銘柄比較
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            最大6銘柄の株価推移とAI予測を同時に比較
          </p>
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setShowSavedSets(!showSavedSets)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              保存セット
            </button>
            {selectedSymbols.length > 0 && (
              <button
                onClick={() => setShowSaveDialog(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                現在のセットを保存
              </button>
            )}
          </div>
        </div>

        {/* Saved Sets Display */}
        {showSavedSets && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
              保存済みセット
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {savedSets.map((set) => (
                <div
                  key={set.name}
                  className="border-2 border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
                >
                  <h3 className="font-bold text-gray-900 dark:text-white mb-2">{set.name}</h3>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {set.symbols.map(symbol => (
                      <span
                        key={symbol}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                      >
                        {symbol}
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => loadSavedSet(set)}
                      className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm font-semibold"
                    >
                      このセットを読み込む
                    </button>
                    <button
                      onClick={() => deleteSavedSet(set.name)}
                      className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm font-semibold"
                    >
                      削除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Save Dialog */}
        {showSaveDialog && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border-2 border-green-500">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
              現在のセットを保存
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              保存する銘柄: {selectedSymbols.join(', ')}
            </p>
            <div className="flex gap-4">
              <input
                type="text"
                value={newSetName}
                onChange={(e) => setNewSetName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && saveCurrentSet()}
                placeholder="セット名を入力（例: 私のポートフォリオ）"
                className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <button
                onClick={saveCurrentSet}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold"
              >
                保存
              </button>
              <button
                onClick={() => {
                  setShowSaveDialog(false);
                  setNewSetName('');
                }}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
              >
                キャンセル
              </button>
            </div>
          </div>
        )}

        {/* Symbol Input */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
            銘柄を追加
          </h2>
          <div className="relative">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
                placeholder="銘柄コード・企業名で検索 (例: AAPL, トヨタ, 7203.T)"
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <button
                onClick={() => addSymbol()}
                disabled={!searchTerm.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                追加
              </button>
            </div>

            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-700 rounded-lg shadow-xl border border-gray-200 dark:border-gray-600 max-h-96 overflow-y-auto">
                {searchResults.map((result) => (
                  <button
                    key={result.symbol}
                    onClick={() => addSymbol(result.symbol)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-600 flex justify-between items-center border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                  >
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{result.symbol}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{result.company_name}</div>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{result.exchange}</div>
                  </button>
                ))}
              </div>
            )}

            {isSearching && (
              <div className="absolute right-4 top-4">
                <LoadingSpinner size="sm" />
              </div>
            )}
          </div>

          <div className="flex items-center justify-between mt-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {selectedSymbols.length}/6 銘柄選択中
            </p>

            {/* Prediction Toggle */}
            {stocks.length > 0 && (
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showPredictions}
                  onChange={(e) => setShowPredictions(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  AI予測を表示
                </span>
              </label>
            )}
          </div>

          {/* Selected Symbols */}
          {selectedSymbols.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {selectedSymbols.map((symbol, index) => (
                <div
                  key={symbol}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg"
                  style={{ backgroundColor: `${CHART_COLORS[index % CHART_COLORS.length]}20` }}
                >
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                  />
                  <span className="font-medium text-gray-900 dark:text-white">{symbol}</span>
                  <button
                    onClick={() => removeSymbol(symbol)}
                    className="ml-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 font-bold"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} onRetry={error.includes('取得に失敗') ? retryFetch : undefined} />
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12">
            <div className="text-center">
              <LoadingSpinner size="lg" className="mb-4" />
              <p className="text-gray-600 dark:text-gray-400">銘柄データを読み込み中...</p>
            </div>
          </div>
        )}

        {/* Chart */}
        {!loading && stocks.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              株価推移比較（直近30日）
            </h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={prepareChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {stocks.map((stock) => (
                    <Line
                      key={stock.symbol}
                      type="monotone"
                      dataKey={stock.symbol}
                      stroke={stock.color}
                      strokeWidth={2}
                      dot={false}
                      name={`${stock.symbol} - ${stock.company_name}`}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Statistics */}
        {!loading && stocks.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              統計情報{showPredictions && ' & AI予測'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {stocks.map((stock) => {
                const latestPrice = stock.price_history[0]?.close_price;
                const oldestPrice = stock.price_history[stock.price_history.length - 1]?.close_price;
                const change = latestPrice && oldestPrice ? ((latestPrice - oldestPrice) / oldestPrice) * 100 : 0;

                return (
                  <div
                    key={stock.symbol}
                    className="p-4 border-2 rounded-lg"
                    style={{ borderColor: stock.color }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: stock.color }}
                      />
                      <h3 className="font-bold text-gray-900 dark:text-white">{stock.symbol}</h3>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{stock.company_name}</p>
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">最新価格</p>
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          ¥{latestPrice?.toFixed(2) || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">30日変動率</p>
                        <p className={`text-lg font-bold ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                        </p>
                      </div>

                      {/* AI予測情報 */}
                      {showPredictions && stock.predictedPrice && (
                        <>
                          <div className="border-t pt-2">
                            <p className="text-xs text-gray-600 dark:text-gray-400">AI予測価格</p>
                            <p className="text-lg font-bold text-blue-600">
                              ¥{stock.predictedPrice.toFixed(2)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400">予測変動率</p>
                            <p className={`text-lg font-bold ${
                              stock.predictionChange && stock.predictionChange >= 0
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}>
                              {stock.predictionChange && stock.predictionChange >= 0 ? '+' : ''}
                              {stock.predictionChange?.toFixed(2) || 'N/A'}%
                            </p>
                          </div>
                        </>
                      )}

                      {showPredictions && !stock.predictedPrice && (
                        <div className="border-t pt-2">
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            AI予測データなし
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && stocks.length === 0 && selectedSymbols.length === 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                銘柄を追加して比較を開始
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                上のフォームから最大6銘柄を選択して、株価推移とAI予測を比較できます
              </p>
              <div className="text-sm text-gray-500 dark:text-gray-400 space-y-1">
                <p>💡 ヒント:</p>
                <p>• 銘柄コード（例: AAPL, 7203.T）を直接入力可能</p>
                <p>• 企業名（例: トヨタ）で検索も可能</p>
                <p>• AIによる予測変動率も表示されます</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
