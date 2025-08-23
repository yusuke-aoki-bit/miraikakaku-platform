'use client';

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
  TimeScale,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

interface StockChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: any[];
      borderColor?: string;
      backgroundColor?: string;
      [key: string]: unknown;
    }>;
  };
  options: Record<string, unknown>;
}

export default function StockChart({ data, options }: StockChartProps) {
  return <Line data={data} options={options} />;
}
