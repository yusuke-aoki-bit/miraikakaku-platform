'use client';

import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  TrendingUp, 
  TrendingDown,
  Target,
  Zap,
  Download,
  Eye,
  ChevronUp,
  ChevronDown,
  Brain
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
}

interface PredictionRow {
  date: string;
  predicted_price: number;
  confidence: number;
  prediction_range: {
    min: number;
    max: number;
  };
  change_from_current: number;
  change_percent: number;
  model_consensus: string;
}

interface PredictionDataTableProps {
  stock: Stock | null;
  onShowAIFactors?: (predictionId: string, symbol: string, companyName: string) => void;
}

type SortField = 'date' | 'predicted_price' | 'confidence' | 'change_percent';
type SortOrder = 'asc' | 'desc';

export default function PredictionDataTable({ stock, onShowAIFactors }: PredictionDataTableProps) {
  const [predictions, setPredictions] = useState<PredictionRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [selectedPeriod, setSelectedPeriod] = useState<'1W' | '1M' | '3M'>('1M');
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (stock) {
      fetchPredictionData();
    }
  }, [stock, selectedPeriod]);

  const fetchPredictionData = async () => {
    if (!stock) return;

    setLoading(true);
    try {
      const days = selectedPeriod === '1W' ? 7 : selectedPeriod === '1M' ? 30 : 90;
      const response = await apiClient.getStockPredictions(stock.symbol, undefined, days);
      
      if (response.success && Array.isArray(response.data)) {
        // APIデータを変換
        const transformedData: PredictionRow[] = response.data.map((item: any, index: number) => {
          const predictedPrice = item.predicted_price || (stock as any).current_price * 1.05;
          const confidence = (item.confidence || 0.75) * 100;
          const range = predictedPrice * 0.05;
          
          const date = new Date();
          date.setDate(date.getDate() + index + 1);

          return {
            date: item.date || new Date(Date.now() + index * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            predicted_price: predictedPrice,
            confidence: confidence,
            prediction_range: {
              min: item.prediction_range?.min || predictedPrice - range,
              max: item.prediction_range?.max || predictedPrice + range
            },
            change_from_current: predictedPrice - (stock as any).current_price,
            change_percent: ((predictedPrice - (stock as any).current_price) / (stock as any).current_price) * 100,
            model_consensus: getConsensusLabel(confidence)
          };
        });

        setPredictions(transformedData);
      } else {
        // APIデータが無い場合は空配列
        setPredictions([]);
      }
    } catch (error) {
      console.error('Failed to fetch prediction data:', error);
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };


  const getConsensusLabel = (confidence: number): string => {
    if (confidence >= 90) return '強い一致';
    if (confidence >= 80) return '高い一致';
    if (confidence >= 70) return '中程度一致';
    return '意見分散';
  };

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder(field === 'date' ? 'asc' : 'desc');
    }
  };

  const sortedPredictions = [...predictions].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];

    if (sortField === 'date') {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
    }

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    }

    return 0;
  });

  const formatPrice = (price: number) => {
    if (stock?.symbol.match(/^[A-Z]+$/)) {
      return `$${price.toFixed(2)}`;
    }
    return `¥${Math.round(price).toLocaleString('ja-JP')}`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const diffTime = date.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return '明日';
    if (diffDays <= 7) return `${diffDays}日後`;
    
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-400 bg-green-900/20';
    if (confidence >= 80) return 'text-blue-400 bg-blue-900/20';
    if (confidence >= 70) return 'text-yellow-400 bg-yellow-900/20';
    return 'text-red-400 bg-red-900/20';
  };

  const exportData = () => {
    const csvContent = [
      ['日付', '予測価格', '信頼度(%)', '予測レンジ(下限)', '予測レンジ(上限)', '変動率(%)'],
      ...sortedPredictions.map(pred => [
        pred.date,
        pred.predicted_price.toFixed(2),
        pred.confidence.toFixed(1),
        pred.prediction_range.min.toFixed(2),
        pred.prediction_range.max.toFixed(2),
        pred.change_percent.toFixed(2)
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${stock?.symbol}_predictions.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-left hover:text-blue-400 transition-colors"
    >
      <span>{children}</span>
      {sortField === field && (
        sortOrder === 'asc' 
          ? <ChevronUp className="w-3 h-3" />
          : <ChevronDown className="w-3 h-3" />
      )}
    </button>
  );

  if (!stock) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <Calendar className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            銘柄を選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            銘柄を選択すると詳細な予測データテーブルが表示されます
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center">
          <Target className="w-6 h-6 mr-2 text-green-400" />
          予測データテーブル
        </h2>

        <div className="flex items-center space-x-4">
          {/* 期間選択 */}
          <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
            {(['1W', '1M', '3M'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                  selectedPeriod === period
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                {period}
              </button>
            ))}
          </div>

          {/* エクスポートボタン */}
          <button
            onClick={exportData}
            disabled={predictions.length === 0}
            className="flex items-center space-x-2 px-3 py-1 bg-green-600/20 text-green-400 rounded-md hover:bg-green-600/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">CSV</span>
          </button>

          {/* 詳細表示切替 */}
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center space-x-2 px-3 py-1 bg-gray-700/50 text-gray-300 rounded-md hover:bg-gray-700/70 transition-colors"
          >
            <Eye className="w-4 h-4" />
            <span className="text-sm">{showDetails ? '簡潔表示' : '詳細表示'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
        </div>
      ) : predictions.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-gray-700/50">
              <tr className="text-sm text-gray-300">
                <th className="text-left p-3">
                  <SortButton field="date">日付</SortButton>
                </th>
                <th className="text-right p-3">
                  <SortButton field="predicted_price">予測株価</SortButton>
                </th>
                <th className="text-center p-3">
                  <SortButton field="confidence">信頼度</SortButton>
                </th>
                <th className="text-right p-3">予測レンジ</th>
                <th className="text-right p-3">
                  <SortButton field="change_percent">変動率</SortButton>
                </th>
                {showDetails && (
                  <>
                    <th className="text-center p-3">モデル一致度</th>
                    <th className="text-right p-3">価格差</th>
                  </>
                )}
                <th className="text-center p-3">判断根拠</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {sortedPredictions.map((prediction, index) => (
                <tr 
                  key={prediction.date}
                  className="hover:bg-gray-800/20 transition-colors"
                >
                  <td className="p-3">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="font-medium text-white">
                          {formatDate(prediction.date)}
                        </div>
                        <div className="text-xs text-gray-400">
                          {prediction.date}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className="font-bold text-white text-lg">
                      {formatPrice(prediction.predicted_price)}
                    </div>
                  </td>

                  <td className="p-3 text-center">
                    <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(prediction.confidence)}`}>
                      <Zap className="w-3 h-3" />
                      <span>{prediction.confidence.toFixed(0)}%</span>
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className="text-sm text-gray-300">
                      {formatPrice(prediction.prediction_range.min)}
                    </div>
                    <div className="text-xs text-gray-500">〜</div>
                    <div className="text-sm text-gray-300">
                      {formatPrice(prediction.prediction_range.max)}
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className={`font-medium flex items-center justify-end ${
                      prediction.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {prediction.change_percent >= 0 ? (
                        <TrendingUp className="w-4 h-4 mr-1" />
                      ) : (
                        <TrendingDown className="w-4 h-4 mr-1" />
                      )}
                      {prediction.change_percent >= 0 ? '+' : ''}{prediction.change_percent.toFixed(2)}%
                    </div>
                  </td>

                  {showDetails && (
                    <>
                      <td className="p-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs ${
                          prediction.confidence >= 85 ? 'bg-green-900/30 text-green-400' :
                          prediction.confidence >= 75 ? 'bg-blue-900/30 text-blue-400' :
                          'bg-yellow-900/30 text-yellow-400'
                        }`}>
                          {prediction.model_consensus}
                        </span>
                      </td>

                      <td className="p-3 text-right">
                        <div className={`text-sm ${
                          prediction.change_from_current >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {prediction.change_from_current >= 0 ? '+' : ''}{formatPrice(Math.abs(prediction.change_from_current))}
                        </div>
                      </td>
                    </>
                  )}

                  <td className="p-3 text-center">
                    <button
                      onClick={() => onShowAIFactors?.(
                        `${stock?.symbol}-${prediction.date}`, 
                        stock?.symbol || '', 
                        stock?.company_name || ''
                      )}
                      className="flex items-center space-x-1 px-3 py-1 bg-purple-600/20 text-purple-400 rounded-md hover:bg-purple-600/30 transition-colors text-sm"
                      title="AI判断根拠を表示"
                    >
                      <Brain className="w-3 h-3" />
                      <span>判断根拠</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <div>予測データがありません</div>
          <div className="text-sm mt-1">銘柄を選択し直してください</div>
        </div>
      )}

      {/* 統計サマリー */}
      {predictions.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-700/50">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-800/30 rounded-lg">
              <div className="text-sm text-gray-400">平均信頼度</div>
              <div className="text-lg font-bold text-white">
                {(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length).toFixed(1)}%
              </div>
            </div>

            <div className="text-center p-3 bg-gray-800/30 rounded-lg">
              <div className="text-sm text-gray-400">最高予測価格</div>
              <div className="text-lg font-bold text-green-400">
                {formatPrice(Math.max(...predictions.map(p => p.predicted_price)))}
              </div>
            </div>

            <div className="text-center p-3 bg-gray-800/30 rounded-lg">
              <div className="text-sm text-gray-400">最低予測価格</div>
              <div className="text-lg font-bold text-red-400">
                {formatPrice(Math.min(...predictions.map(p => p.predicted_price)))}
              </div>
            </div>

            <div className="text-center p-3 bg-gray-800/30 rounded-lg">
              <div className="text-sm text-gray-400">期間トレンド</div>
              <div className={`text-lg font-bold flex items-center justify-center ${
                predictions[predictions.length - 1]?.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {predictions[predictions.length - 1]?.change_percent >= 0 ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
                )}
                {predictions[predictions.length - 1]?.change_percent >= 0 ? '+' : ''}
                {predictions[predictions.length - 1]?.change_percent.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}