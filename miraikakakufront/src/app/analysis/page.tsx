import React from 'react';
import { Metadata } from 'next';
import AnalysisClientPage from './client';

export const metadata: Metadata = {
  title: 'AI株価分析 - Miraikakaku',
  description: 'AI技術を活用した高精度な株価分析とトレンド予測',
};

export default function AnalysisPage() {
  return <AnalysisClientPage />;
}