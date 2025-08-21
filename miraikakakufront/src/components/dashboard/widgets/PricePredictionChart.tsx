'use client';

import { useState, useEffect } from 'react';
import { Widget } from '@/types/dashboard';
import PredictionChart from '@/components/charts/PredictionChart';
import { Loader } from 'lucide-react';

interface PricePredictionChartProps {
  widget: Widget;
}

interface MockPredictionData {
  timestamp: number;
  date: string;
  actual_price?: number;
  predicted_price: number;
  confidence_90_lower: number;
  confidence_90_upper: number;
  confidence_95_lower: number;
  confidence_95_upper: number;
  confidence_99_lower: number;
  confidence_99_upper: number;
  model_confidence: number;
  prediction_type: 'historical' | 'forecast';
}

const generateMockData = (): MockPredictionData[] => {
  const data: MockPredictionData[] = [];
  const basePrice = 2500;
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;

  // Historical data (last 30 days)
  for (let i = 30; i >= 0; i--) {
    const timestamp = now - (i * oneDay);
    const randomFactor = (Math.random() - 0.5) * 0.1;
    const trend = Math.sin((30 - i) * 0.2) * 0.05;
    const price = basePrice * (1 + trend + randomFactor);
    
    const confidence = 0.7 + Math.random() * 0.25; // 70-95%
    const variance = price * (1 - confidence) * 2;
    
    data.push({
      timestamp,
      date: new Date(timestamp).toISOString(),
      actual_price: price * (1 + (Math.random() - 0.5) * 0.02), // Actual with small variance
      predicted_price: price,
      confidence_90_lower: price - variance * 0.5,
      confidence_90_upper: price + variance * 0.5,
      confidence_95_lower: price - variance * 0.7,
      confidence_95_upper: price + variance * 0.7,
      confidence_99_lower: price - variance * 1.0,
      confidence_99_upper: price + variance * 1.0,
      model_confidence: confidence,
      prediction_type: 'historical'
    });
  }

  // Forecast data (next 7 days)
  const lastPrice = data[data.length - 1].predicted_price;
  for (let i = 1; i <= 7; i++) {
    const timestamp = now + (i * oneDay);
    const randomFactor = (Math.random() - 0.5) * 0.08;
    const trendFactor = Math.sin(i * 0.3) * 0.03;
    const price = lastPrice * (1 + trendFactor + randomFactor);
    
    const confidence = Math.max(0.5, 0.8 - (i * 0.03)); // Decreasing confidence
    const variance = price * (1 - confidence) * 3;
    
    data.push({
      timestamp,
      date: new Date(timestamp).toISOString(),
      predicted_price: price,
      confidence_90_lower: price - variance * 0.5,
      confidence_90_upper: price + variance * 0.5,
      confidence_95_lower: price - variance * 0.7,
      confidence_95_upper: price + variance * 0.7,
      confidence_99_lower: price - variance * 1.0,
      confidence_99_upper: price + variance * 1.0,
      model_confidence: confidence,
      prediction_type: 'forecast'
    });
  }

  return data;
};

const mockMetadata = {
  model_name: 'LSTM-Transformer Ensemble v2.1',
  accuracy: 0.847,
  r_squared: 0.723,
  mae: 45.2,
  last_trained: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
  feature_importance: {
    '価格履歴': 0.35,
    '出来高': 0.22,
    '市場センチメント': 0.18,
    'マクロ経済指標': 0.15,
    'ニュース分析': 0.10
  },
  data_freshness: 2 // hours
};

export default function PricePredictionChart({ widget }: PricePredictionChartProps) {
  const [data, setData] = useState<MockPredictionData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate API call
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // For demo purposes, use mock data
        // In production, this would be an actual API call:
        // const response = await fetch(`/api/predictions/${symbol}`);
        // const data = await response.json();
        
        const mockData = generateMockData();
        setData(mockData);
      } catch (err) {
        setError('予測データの取得に失敗しました');
        console.error('Failed to load prediction data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [widget.config]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin text-brand-primary mx-auto mb-3" />
          <p className="text-text-secondary text-sm">AI予測データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-text-primary font-medium mb-1">データ取得エラー</p>
          <p className="text-text-secondary text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-hidden">
      <PredictionChart
        symbol="NIKKEI"
        data={data}
        metadata={mockMetadata}
        className="border-0 bg-transparent p-0 h-full"
        height={widget.size.height > 6 ? 300 : 200}
        showControls={widget.size.height > 6}
      />
    </div>
  );
}