'use client';

import React, { useMemo } from 'react';
import {
  LineChart
  Line
  XAxis
  YAxis
  CartesianGrid
  Tooltip
  Legend
  ResponsiveContainer
  ReferenceLine
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
  priceHistory
  predictions
  historicalPredictions
}: StockChartProps) {

  const chartData = useMemo(() => {
    // Ensure we have data to work with
    if (!priceHistory || priceHistory.length === 0) {
      return [];
    }
    const dataMap = new Map(
    // Add historical prices
    priceHistory.forEach(price => {
      if (price.date && price.close_price != null) {
        dataMap.set(price.date, {
          date: price.date
          actual: price.close_price
        }
      }
    }
    // Add historical predictions
    if (Array.isArray(historicalPredictions) && historicalPredictions.length > 0) {
      historicalPredictions.forEach(pred => {
        if (pred.prediction_date && pred.predicted_price != null) {
          const existing = dataMap.get(pred.prediction_date) || { date: pred.prediction_date };
          dataMap.set(pred.prediction_date, {
            ...existing
            historicalPrediction: pred.predicted_price
          }
        }
      }
    }

    // Add future predictions
    if (Array.isArray(predictions) && predictions.length > 0) {
      predictions.forEach(pred => {
        if (pred.prediction_date && pred.predicted_price != null) {
          const existing = dataMap.get(pred.prediction_date) || { date: pred.prediction_date };
          dataMap.set(pred.prediction_date, {
            ...existing
            predicted: pred.predicted_price
          }
        }
      }
    }

    // Convert to array and sort by date
    const result = Array.from(dataMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    return result;
  }, [priceHistory, predictions, historicalPredictions]
  // Show loading if no price history data
  if (!priceHistory || priceHistory.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center">
        <div className="text-center">
          <ChartLoader />
          <p className="mt-4 theme-text-secondary">チャートを読み込み中...</p>
        </div>
      </div>
  }
    predictions: { type: typeof predictions, isArray: Array.isArray(predictions)
    historicalPredictions: { type: typeof historicalPredictions, isArray: Array.isArray(historicalPredictions)
  }
  const formatXAxis = (tickItem: string) => {
    try {
      return format(parseISO(tickItem), 'MMM yyyy'
    } catch {
      return tickItem;
    }
  };

  const formatTooltipLabel = (value: string) => {
    try {
      return format(parseISO(value), 'MMM dd, yyyy'
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
        <div className="theme-card p-3">
          <p className="font-semibold mb-1 theme-text-primary">{formatTooltipLabel(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2) || 'N/A'}
            </p>
          ))}
        </div>
    }
    return null;
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="w-full h-full theme-card p-4">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--theme-border))" />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxis}
            stroke="rgb(var(--theme-text-secondary))"
            className="theme-caption"
          />
          <YAxis
            tickFormatter={formatYAxis}
            stroke="rgb(var(--theme-text-secondary))"
            className="theme-caption"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          
          {/* Reference line for today */}
          <ReferenceLine
            x={today}
            stroke="rgb(var(--theme-text-secondary))"
            strokeDasharray="5 5"
            label={{ value: "Today", position: "top" }}
          />
          
          {/* Actual price line */}
          <Line
            type="monotone"
            dataKey="actual"
            stroke="rgb(var(--theme-primary))"
            strokeWidth={2}
            dot={false}
            name="Actual Price"
            connectNulls
          />
          
          {/* Historical predictions line */}
          <Line
            type="monotone"
            dataKey="historicalPrediction"
            stroke="rgb(var(--theme-error))"
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
            stroke="rgb(var(--theme-success))"
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={false}
            name="Future Predictions"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex justify-center gap-6 text-sm theme-text-secondary">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1" style={{ backgroundColor: 'rgb(var(--theme-primary))' }}></div>
          <span>Actual Price</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1" style={{ backgroundColor: 'rgb(var(--theme-error))', borderStyle: 'dashed' }}></div>
          <span>Past AI Predictions</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1" style={{ backgroundColor: 'rgb(var(--theme-success))', borderStyle: 'dashed' }}></div>
          <span>Future AI Predictions</span>
        </div>
      </div>
    </div>
}