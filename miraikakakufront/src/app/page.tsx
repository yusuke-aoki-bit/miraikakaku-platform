'use client';

import { useState, useEffect } from 'react';
import LoadingSpinner from '@/components/common/LoadingSpinner';

export default function Home() {
  const [isPageLoading, setIsPageLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPageLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (isPageLoading) {
    return (
      <div className="h-full bg-dark-bg text-text-light flex flex-col items-center justify-center">
        <div className="mb-layout-gap animate-fade-in">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent mb-4">
            Miraikakaku
          </h1>
          <p className="text-text-medium text-center text-lg">
            AI駆動の株価予測プラットフォーム
          </p>
        </div>
        <LoadingSpinner 
          type="ai" 
          size="lg" 
          message="AI予測システムを初期化中..."
        />
      </div>
    );
  }

  return (
    <div className="p-section-px py-section-py min-h-full">
      <h2 className="text-3xl font-bold text-text-light mb-layout-gap">
        ようこそ、[ユーザー名]さん！
      </h2>

      {/* Placeholder for Quick Stats Card */}
      <div className="bg-dark-card rounded-card-lg p-layout-gap mb-layout-gap border border-dark-border">
        <h3 className="text-xl font-semibold text-text-light mb-2">クイック統計</h3>
        <p className="text-text-medium">ポートフォリオの概要、ウォッチリストの数、最新のAI予測など</p>
      </div>

      {/* Placeholder for My Watchlist Summary Card */}
      <div className="bg-dark-card rounded-card-lg p-layout-gap mb-layout-gap border border-dark-border">
        <h3 className="text-xl font-semibold text-text-light mb-2">マイウォッチリスト</h3>
        <p className="text-text-medium">ウォッチリスト内の銘柄の簡易情報</p>
      </div>

      {/* Placeholder for AI-Powered Insights Section */}
      <div className="bg-dark-card rounded-card-lg p-layout-gap mb-layout-gap border border-dark-border">
        <h3 className="text-xl font-semibold text-text-light mb-2">AIによる洞察</h3>
        <p className="text-text-medium">AIが推奨する銘柄、高確信度予測など</p>
      </div>

      {/* Placeholder for Recent Market News Section */}
      <div className="bg-dark-card rounded-card-lg p-layout-gap mb-layout-gap border border-dark-border">
        <h3 className="text-xl font-semibold text-text-light mb-2">最新マーケットニュース</h3>
        <p className="text-text-medium">市場の動向に関する最新情報</p>
      </div>

      {/* Placeholder for Quick Search (if still needed) */}
      <div className="bg-dark-card rounded-card-lg p-layout-gap border border-dark-border">
        <h3 className="text-xl font-semibold text-text-light mb-2">銘柄を検索</h3>
        <p className="text-text-medium">新しい銘柄を検索して分析を開始</p>
      </div>
    </div>
  )
}
