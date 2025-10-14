'use client';

import { useEffect } from 'react';
import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Web Vitalsメトリクスをコンソールに出力（本番環境では分析ツールに送信）
    if (process.env.NODE_ENV === 'development') {
      console.log('[Web Vitals]', {
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id,
      });
    }

    // 本番環境では、ここでGoogle AnalyticsやDatadogなどに送信
    // 例:
    // window.gtag?.('event', metric.name, {
    //   value: Math.round(metric.value),
    //   event_label: metric.id,
    //   non_interaction: true,
    // });
  });

  return null;
}

export default WebVitals;
