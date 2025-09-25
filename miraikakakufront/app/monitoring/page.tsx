import React from 'react';
import { MonitoringDashboard } from '../components/MonitoringDashboard';
import { PerformanceOptimizer } from '../components/PerformanceOptimizer';

export default function MonitoringPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8 space-y-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          システム監視 & パフォーマンス最適化
        </h1>

        {/* Performance Optimizer Section */}
        <PerformanceOptimizer />

        {/* Monitoring Dashboard */}
        <MonitoringDashboard />
      </div>
    </div>
}

export const metadata = {
  title: 'システム監視 - Miraikakaku'
  description: 'Miraikakaku システムの監視ダッシュボード'
};