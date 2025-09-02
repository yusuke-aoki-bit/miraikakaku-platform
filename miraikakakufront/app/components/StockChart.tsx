'use client';

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { StockPrice, StockPrediction, HistoricalPrediction } from '../types';
import { ChartLoader } from './LoadingSpinner';

interface StockChartProps {
  priceHistory: StockPrice[];
  predictions: StockPrediction[];
  historicalPredictions: HistoricalPrediction[];
}

export default function StockChart({ 
  priceHistory, 
  predictions, 
  historicalPredictions 
}: StockChartProps) {
  
  // Show loading if no price history data
  if (!priceHistory || priceHistory.length === 0) {
    return <ChartLoader />;
  }
  
  const chartData = useMemo(() => {
    const dataMap = new Map();
    
    // Add historical prices
    priceHistory.forEach(price => {
      dataMap.set(price.date, {
        date: price.date,
        actual: price.close_price,
      });
    });
    
    // Add historical predictions
    historicalPredictions.forEach(pred => {
      const existing = dataMap.get(pred.prediction_date) || { date: pred.prediction_date };
      dataMap.set(pred.prediction_date, {
        ...existing,
        historicalPrediction: pred.predicted_price,
      });
    });
    
    // Add future predictions
    predictions.forEach(pred => {
      const existing = dataMap.get(pred.prediction_date) || { date: pred.prediction_date };
      dataMap.set(pred.prediction_date, {
        ...existing,
        predicted: pred.predicted_price,
      });
    });
    
    // Convert to array and sort by date
    return Array.from(dataMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [priceHistory, predictions, historicalPredictions]);

  const formatXAxis = (tickItem: string) => {
    try {
      return format(parseISO(tickItem), 'MMM yyyy');
    } catch {
      return tickItem;
    }
  };

  const formatTooltipLabel = (value: string) => {
    try {
      return format(parseISO(value), 'MMM dd, yyyy');
    } catch {
      return value;
    }
  };

  const formatYAxis = (value: number) => {
    return `$${value.toFixed(2)}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-semibold mb-1">{formatTooltipLabel(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2) || 'N/A'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="w-full h-full bg-white rounded-lg shadow-md p-4">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatXAxis}
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            tickFormatter={formatYAxis}
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          
          {/* Reference line for today */}
          <ReferenceLine 
            x={today} 
            stroke="#666" 
            strokeDasharray="5 5" 
            label={{ value: "Today", position: "top" }}
          />
          
          {/* Actual price line */}
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="Actual Price"
            connectNulls
          />
          
          {/* Historical predictions line */}
          <Line
            type="monotone"
            dataKey="historicalPrediction"
            stroke="#dc2626"
            strokeWidth={1.5}
            strokeDasharray="5 5"
            dot={false}
            name="Past Predictions"
            connectNulls
          />
          
          {/* Future predictions line */}
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#16a34a"
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={false}
            name="Future Predictions"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-blue-600"></div>
          <span>Actual Price</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-red-600 border-dashed"></div>
          <span>Past AI Predictions</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-green-600 border-dashed"></div>
          <span>Future AI Predictions</span>
        </div>
      </div>
    </div>
  );
}