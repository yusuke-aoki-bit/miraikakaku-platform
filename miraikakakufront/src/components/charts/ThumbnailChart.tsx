'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement);

interface ThumbnailChartProps {
  data: {
    dates: string[];
    actual: number[];
    lstm: number[];
    vertexai: number[];
  };
  height?: number;
  width?: string;
}

export default function ThumbnailChart({ data, height = 60, width = '100%' }: ThumbnailChartProps) {
  const chartData = {
    labels: data.dates,
    datasets: [
      {
        data: data.actual,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.4,
      },
      {
        data: data.lstm,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.4,
        borderDash: [5, 5],
      },
      {
        data: data.vertexai,
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.4,
        borderDash: [3, 3],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    scales: {
      x: { display: false },
      y: { display: false },
    },
    elements: {
      line: {
        borderWidth: 2,
      },
      point: {
        radius: 0,
        hoverRadius: 0,
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  return (
    <div style={{ height, width }}>
      <Line data={chartData} options={options} />
    </div>
  );
}