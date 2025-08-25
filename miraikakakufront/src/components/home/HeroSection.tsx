'use client';

import React, { useState } from 'react';
import { Search, TrendingUp, Brain } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HeroSection() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`;
    }
  };

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20 rounded-2xl p-8 md:p-12">
      {/* 背景アニメーション */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-green-500/10 to-blue-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [0, -90, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      {/* コンテンツ */}
      <div className="relative z-10">
        {/* ロゴとタイトル */}
        <div className="flex items-center space-x-3 mb-4">
          <h1 className="text-2xl font-bold text-white">リアルタイムダッシュボード</h1>
        </div>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-white">
            Miraikakaku
          </h1>
        </div>

        {/* キャッチコピー */}
        <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl">
          AIがあなたの投資判断を加速させる
        </p>

        {/* グローバル検索バー */}
        <form onSubmit={handleSearch} className="max-w-2xl">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-25 group-hover:opacity-40 transition-opacity" />
            <div className="relative flex items-center bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-700/50 hover:border-blue-500/50 transition-all">
              <Search className="absolute left-4 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="銘柄コード、企業名で検索..."
                className="w-full pl-12 pr-4 py-4 bg-transparent text-white placeholder-gray-400 focus:outline-none"
              />
              <button
                type="submit"
                className="px-6 py-2 m-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all"
              >
                検索
              </button>
            </div>
          </div>
        </form>

        {/* クイックアクセス */}
        <div className="flex flex-wrap gap-3 mt-6">
          <button
            onClick={() => window.location.href = '/rankings'}
            className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all flex items-center space-x-2"
          >
            <TrendingUp className="w-4 h-4" />
            <span>ランキングを見る</span>
          </button>
          <button
            onClick={() => window.location.href = '/predictions'}
            className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all flex items-center space-x-2"
          >
            <Brain className="w-4 h-4" />
            <span>AI予測を見る</span>
          </button>
        </div>
      </div>
    </div>
  );
}