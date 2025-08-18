'use client';

import { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface PageLoaderProps {
  children: React.ReactNode;
  minLoadTime?: number;
}

export default function PageLoader({ children, minLoadTime = 1000 }: PageLoaderProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    
    // プログレスバーのアニメーション
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 15;
      });
    }, 100);

    // 最小ロード時間を保証
    const timer = setTimeout(() => {
      setProgress(100);
      setTimeout(() => setIsLoading(false), 200);
    }, minLoadTime);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(timer);
    };
  }, [minLoadTime]);

  if (isLoading) {
    return (
      <div className="h-screen bg-black text-white flex flex-col items-center justify-center">
        {/* ロゴ */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent mb-4">
            Miraikakaku
          </h1>
          <p className="text-gray-400 text-center text-lg">
            AI駆動の株価予測プラットフォーム
          </p>
        </div>

        {/* メインローディングスピナー */}
        <div className="mb-8">
          <LoadingSpinner 
            type="ai" 
            size="lg" 
            message="AI予測システムを初期化中..."
          />
        </div>

        {/* プログレスバー */}
        <div className="w-80 mb-4">
          <div className="bg-gray-800 rounded-full h-2 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-red-500 to-pink-500 transition-all duration-200 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* ローディングステップ */}
        <div className="text-center text-sm text-gray-400 animate-pulse">
          {progress < 30 && "市場データを取得中..."}
          {progress >= 30 && progress < 60 && "AIモデルを読み込み中..."}
          {progress >= 60 && progress < 90 && "チャートコンポーネントを準備中..."}
          {progress >= 90 && "完了"}
        </div>

        {/* 装飾的な要素 */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-r from-red-500/10 to-pink-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-20 right-20 w-48 h-48 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      </div>
    );
  }

  return <div className="animate-fade-in">{children}</div>;
}