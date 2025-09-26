'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Target } from 'lucide-react';

interface PredictionData {
  symbol: string;
  company_name?: string;
  current_price: number;
  predicted_price: number;
  prediction_change_percent: number;
  prediction_date: string;
  confidence_score: number;
  timeframe: string;
  dataSource?: string;
  isRealData?: boolean;
}

interface RankingCardProps {
  title: string;
  icon: string;
  timeframe: '7d' | '30d' | '90d';
  type: 'best_predictions' | 'highest_confidence' | 'largest_gains' | 'recent_predictions';
  onSelectStock: (symbol: string) => void;
}



const getApiType = (type: 'best_predictions' | 'highest_confidence' | 'largest_gains' | 'recent_predictions') => {
  switch (type) {
    case 'best_predictions':
    case 'largest_gains':
      return '7day';
    case 'highest_confidence':
      return '30day';
    case 'recent_predictions':
      return '90day';
    default:
      return '7day';
  }
};

export default function RankingCard({ title, icon, timeframe, type, onSelectStock }: RankingCardProps) {
  const [predictionData, setPredictionData] = useState<PredictionData[]>([]);
  const [dataSourceInfo, setDataSourceInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const fetchPredictionRankings = async () => {
      setIsLoading(true);
      setHasError(false);
      try {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
        const url = `${apiBaseUrl}/api/finance/rankings/predictions?type=${getApiType(type)}&limit=5`;

        const response = await fetch(url);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        if (data.success && data.predictions_ranking && Array.isArray(data.predictions_ranking)) {
          const normalizedPredictions = data.predictions_ranking.map((item: any) => ({
            symbol: item.symbol,
            company_name: item.company_name,
            current_price: item.current_price || item.avg_current_price,
            predicted_price: item.predicted_price || item.avg_predicted_price,
            prediction_change_percent: item.prediction_change_percent,
            prediction_date: item.prediction_date || '2024-01-15',
            confidence_score: item.confidence_score || item.avg_confidence_score,
            timeframe: timeframe,
            dataSource: 'database',
            isRealData: true
          }));

          const sortedPredictions = normalizedPredictions.sort((a: PredictionData, b: PredictionData) => {
            switch (type) {
              case 'best_predictions':
              case 'largest_gains':
                return b.prediction_change_percent - a.prediction_change_percent;
              case 'highest_confidence':
                return b.confidence_score - a.confidence_score;
              case 'recent_predictions':
                return new Date(b.prediction_date).getTime() - new Date(a.prediction_date).getTime();
              default:
                return b.prediction_change_percent - a.prediction_change_percent;
            }
          });

          const finalPredictions = sortedPredictions.slice(0, 5);
          setPredictionData(finalPredictions);
          setDataSourceInfo(data.data_source_info);
          setIsLoading(false);
          setHasError(false);
        } else {
          if (process.env.NODE_ENV === 'development') {
            console.warn('Invalid API response format', { dataKeys: Object.keys(data) });
          }
          throw new Error('Invalid API response format');
        }
      } catch (error) {
        setPredictionData([]);
        setDataSourceInfo({
          real_data_count: 0,
          fallback_data_count: 0,
          total_count: 0,
          has_real_data: false,
          has_fallback_data: false,
          error: true,
          error_message: error instanceof Error ? error.message : 'API接続エラー'
        });
        setIsLoading(false);
        setHasError(true);
      }
    };

    fetchPredictionRankings();
  }, [timeframe, type, title]);

  const formatValue = (value: number, type: 'price' | 'percent' | 'confidence') => {
    if (value === undefined || value === null || isNaN(value)) {
      switch (type) {
        case 'price':
          return '$0.00';
        case 'percent':
          return '0.00%';
        case 'confidence':
          return '0%';
        default:
          return '0';
      }
    }

    switch (type) {
      case 'price':
        return `$${value.toFixed(2)}`;
      case 'percent':
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
      case 'confidence':
        return `${(value * 100).toFixed(0)}%`;
      default:
        return value.toString();
    }
  };


  if (isLoading) {
    return (
      <div className="theme-section">
        <div className="flex items-center mb-4">
          <span className="text-3xl mr-4">{icon}</span>
          <h4 className="theme-heading-md">{title}</h4>
        </div>
        <div className="text-center py-8">
          <div className="theme-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="theme-caption">データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="theme-section">
        <div className="flex items-center mb-4">
          <span className="text-3xl mr-4">{icon}</span>
          <h4 className="theme-heading-md">{title}</h4>
        </div>
        <div className="text-center py-8">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h5 className="theme-heading-sm mb-2">接続エラー</h5>
          <p className="theme-caption mb-2">
            {dataSourceInfo?.error_message || 'APIサーバーに接続できません'}
          </p>
          <p className="theme-caption">
            データを表示するにはサーバーとの接続が必要です
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-section">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <span className="text-3xl mr-4">{icon}</span>
          <h4 className="theme-heading-md">{title}</h4>
        </div>
      </div>

      <div className="space-y-4">
        {predictionData.map((prediction, index) => (
          <button
            key={prediction.symbol}
            onClick={() => onSelectStock(prediction.symbol)}
            className="theme-ranking-card"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 min-w-0 flex-1">
                  <span className="theme-ranking-number">{index + 1}</span>
                  <div className="min-w-0 flex-1">
                    <div className="font-bold text-sm leading-tight theme-text-primary mb-1" title={prediction.company_name || prediction.symbol}>
                      {prediction.company_name || prediction.symbol}
                    </div>
                    <div className="theme-ranking-symbol">{prediction.symbol}</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="theme-caption mb-1">現在価格 → 予測価格</div>
                  <div className="theme-ranking-price">
                    {formatValue(prediction.current_price, 'price')} → {formatValue(prediction.predicted_price, 'price')}
                  </div>
                </div>

                <div className="text-right ml-6">
                  <div className={prediction.prediction_change_percent >= 0 ? 'theme-ranking-change-positive' : 'theme-ranking-change-negative'}>
                    {prediction.prediction_change_percent >= 0 ? (
                      <TrendingUp className="w-5 h-5 mr-1" />
                    ) : (
                      <TrendingDown className="w-5 h-5 mr-1" />
                    )}
                    {formatValue(prediction.prediction_change_percent, 'percent')}
                  </div>
                  <div className="theme-caption flex items-center justify-end mt-1">
                    <Target className="w-4 h-4 mr-1" />
                    信頼度: {formatValue(prediction.confidence_score, 'confidence')}
                  </div>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}