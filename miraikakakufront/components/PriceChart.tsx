'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PriceData {
  date: string;
  close_price: number | null;
  predicted_price?: number;
}

interface PriceChartProps {
  data: PriceData[];
  showPredictions?: boolean;
}

export default function PriceChart({ data, showPredictions = false }: PriceChartProps) {
  // データを日付順にソート（古い順）
  const sortedData = [...data].sort((a, b) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // 日付をフォーマット
  const formattedData = sortedData.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric'
    }),
    close_price: item.close_price || 0,
  }));

  // 最新30件のみ表示（チャートが見やすくなる）
  const displayData = formattedData.slice(-30);

  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={displayData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
          <XAxis
            dataKey="date"
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: 'none',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
            formatter={(value: number) => [`¥${value.toFixed(2)}`, '価格']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="close_price"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={false}
            name="株価"
            activeDot={{ r: 6 }}
          />
          {showPredictions && (
            <Line
              type="monotone"
              dataKey="predicted_price"
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="予測価格"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
