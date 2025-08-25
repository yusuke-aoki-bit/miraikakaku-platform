'use client';

import React, { useState, useEffect } from 'react';
import { Trophy, Users, TrendingUp, Award, Medal, Crown, Star, Target, Calendar, Filter } from 'lucide-react';
import { motion } from 'framer-motion';

interface UserRanking {
  id: string;
  username: string;
  displayName: string;
  avatar?: string;
  rank: number;
  totalScore: number;
  accuracy: number;
  contestsWon: number;
  contestsParticipated: number;
  winRate: number;
  averageReturn: number;
  bestPrediction: number;
  streak: number;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert' | 'master';
  badges: string[];
  joinedDate: string;
  lastActive: string;
}

interface RankingPeriod {
  id: string;
  label: string;
  period: 'daily' | 'weekly' | 'monthly' | 'alltime';
}

interface RankingCategory {
  id: string;
  label: string;
  icon: React.ElementType;
  description: string;
}

export default function UserRankingsPage() {
  const [rankings, setRankings] = useState<UserRanking[]>([]);
  const [filteredRankings, setFilteredRankings] = useState<UserRanking[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('weekly');
  const [selectedCategory, setSelectedCategory] = useState<string>('overall');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  const periods: RankingPeriod[] = [
    { id: 'daily', label: '日間', period: 'daily' },
    { id: 'weekly', label: '週間', period: 'weekly' },
    { id: 'monthly', label: '月間', period: 'monthly' },
    { id: 'alltime', label: '総合', period: 'alltime' }
  ];

  const categories: RankingCategory[] = [
    { id: 'overall', label: '総合ランキング', icon: Trophy, description: '全体のパフォーマンス' },
    { id: 'accuracy', label: '予測精度', icon: Target, description: '予測の正確性' },
    { id: 'contests', label: 'コンテスト勝利', icon: Crown, description: 'コンテスト勝利数' },
    { id: 'streak', label: '連勝記録', icon: TrendingUp, description: '連続正解数' }
  ];

  const levels = [
    { id: 'all', label: 'すべて' },
    { id: 'beginner', label: '初心者' },
    { id: 'intermediate', label: '中級者' },
    { id: 'advanced', label: '上級者' },
    { id: 'expert', label: 'エキスパート' },
    { id: 'master', label: 'マスター' }
  ];

  // Mock data generation
  useEffect(() => {
    const generateMockRankings = (): UserRanking[] => {
      const usernames = [
        'AITrader2024', 'MarketMaster', 'StockNinja', 'PredictorPro', 'BullMarketKing',
        'InvestGuru', 'TradingLegend', 'MarketAnalyst', 'StockHunter', 'AIPredictor',
        'DataDriven', 'QuantTrader', 'MarketSage', 'TradingAce', 'ProfitMaker',
        'ChartMaster', 'TrendFollower', 'ValueInvestor', 'GrowthHunter', 'RiskTaker'
      ];

      const badges = [
        '🏆 コンテスト王者', '🎯 精密射手', '🔥 連勝記録', '💎 ダイヤモンド会員',
        '🚀 急成長', '🧠 AI使い', '📈 上昇トレンド', '💰 利益マスター',
        '🌟 新星', '⚡ 瞬時判断', '🎨 チャート芸術家', '🔮 未来予知'
      ];

      const levels: UserRanking['level'][] = ['beginner', 'intermediate', 'advanced', 'expert', 'master'];

      return Array.from({ length: 50 }, (_, i) => {
        const level = levels[Math.floor(Math.random() * levels.length)];
        const accuracy = Math.random() * 40 + 60; // 60-100%
        const contestsParticipated = Math.floor(Math.random() * 50) + 10;
        const contestsWon = Math.floor(contestsParticipated * (Math.random() * 0.3 + 0.1));
        
        return {
          id: `user-${i + 1}`,
          username: usernames[i % usernames.length] + (i > 19 ? `${Math.floor(i / 20) + 1}` : ''),
          displayName: usernames[i % usernames.length],
          rank: i + 1,
          totalScore: Math.floor(Math.random() * 10000) + 1000,
          accuracy,
          contestsWon,
          contestsParticipated,
          winRate: (contestsWon / contestsParticipated) * 100,
          averageReturn: (Math.random() * 30 - 5), // -5% to 25%
          bestPrediction: Math.random() * 50 + 10, // 10-60%
          streak: Math.floor(Math.random() * 20),
          level,
          badges: badges.slice(0, Math.floor(Math.random() * 4) + 1),
          joinedDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
          lastActive: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
        };
      });
    };

    setTimeout(() => {
      const mockRankings = generateMockRankings();
      setRankings(mockRankings);
      setFilteredRankings(mockRankings);
      setLoading(false);
    }, 1000);
  }, []);

  // Filter logic
  useEffect(() => {
    let filtered = rankings;

    // Level filter
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(user => user.level === selectedLevel);
    }

    // Sort by category
    filtered.sort((a, b) => {
      switch (selectedCategory) {
        case 'overall':
          return b.totalScore - a.totalScore;
        case 'accuracy':
          return b.accuracy - a.accuracy;
        case 'contests':
          return b.contestsWon - a.contestsWon;
        case 'streak':
          return b.streak - a.streak;
        default:
          return a.rank - b.rank;
      }
    });

    // Update ranks based on filtered results
    filtered = filtered.map((user, index) => ({ ...user, rank: index + 1 }));

    setFilteredRankings(filtered);
  }, [rankings, selectedCategory, selectedLevel, selectedPeriod]);

  const getLevelColor = (level: UserRanking['level']) => {
    switch (level) {
      case 'beginner': return 'text-gray-400 bg-gray-500/20';
      case 'intermediate': return 'text-green-400 bg-green-500/20';
      case 'advanced': return 'text-blue-400 bg-blue-500/20';
      case 'expert': return 'text-purple-400 bg-purple-500/20';
      case 'master': return 'text-yellow-400 bg-yellow-500/20';
    }
  };

  const getLevelLabel = (level: UserRanking['level']) => {
    switch (level) {
      case 'beginner': return '初心者';
      case 'intermediate': return '中級者';
      case 'advanced': return '上級者';
      case 'expert': return 'エキスパート';
      case 'master': return 'マスター';
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="w-6 h-6 text-yellow-400" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Award className="w-6 h-6 text-orange-400" />;
    return <span className="text-2xl font-bold text-gray-400">#{rank}</span>;
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return '1時間前';
    if (diffInHours < 24) return `${diffInHours}時間前`;
    return `${Math.floor(diffInHours / 24)}日前`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-8"></div>
            <div className="space-y-4">
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="h-20 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center">
              <Users className="w-8 h-8 mr-3 text-blue-400" />
              ユーザーランキング
            </h1>
            <p className="text-gray-400 mt-2">トップトレーダーの実績と順位をチェック</p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Period */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">期間</label>
              <div className="flex rounded-lg bg-gray-800 p-1">
                {periods.map((period) => (
                  <button
                    key={period.id}
                    onClick={() => setSelectedPeriod(period.id)}
                    className={`flex-1 px-3 py-2 text-sm rounded-md transition-colors ${
                      selectedPeriod === period.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">カテゴリ</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Level */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">レベル</label>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {levels.map((level) => (
                  <option key={level.id} value={level.id}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Stats */}
            <div className="flex items-end">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{filteredRankings.length}</div>
                <div className="text-sm text-gray-400">参加者数</div>
              </div>
            </div>
          </div>
        </div>

        {/* Top 3 Podium */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {filteredRankings.slice(0, 3).map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              className={`relative bg-gradient-to-b ${
                index === 0 
                  ? 'from-yellow-500/20 to-gray-900/50 border-yellow-500/30' 
                  : index === 1
                  ? 'from-gray-400/20 to-gray-900/50 border-gray-400/30'
                  : 'from-orange-500/20 to-gray-900/50 border-orange-500/30'
              } border rounded-xl p-6 text-center`}
            >
              <div className="flex justify-center mb-4">
                {getRankIcon(user.rank)}
              </div>
              
              <div className="w-16 h-16 bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-xl font-bold text-white">
                  {user.displayName.charAt(0)}
                </span>
              </div>
              
              <h3 className="text-lg font-bold text-white mb-2">{user.displayName}</h3>
              <div className={`inline-block px-3 py-1 rounded-lg text-xs font-medium mb-3 ${getLevelColor(user.level)}`}>
                {getLevelLabel(user.level)}
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="text-gray-300">
                  スコア: <span className="text-white font-semibold">{user.totalScore.toLocaleString()}</span>
                </div>
                <div className="text-gray-300">
                  精度: <span className="text-green-400 font-semibold">{user.accuracy.toFixed(1)}%</span>
                </div>
                <div className="text-gray-300">
                  勝利: <span className="text-blue-400 font-semibold">{user.contestsWon}</span>
                </div>
              </div>
              
              {/* Badges */}
              <div className="flex flex-wrap justify-center gap-1 mt-4">
                {user.badges.slice(0, 2).map((badge, i) => (
                  <span key={i} className="text-xs px-2 py-1 bg-gray-800/50 rounded">
                    {badge}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Rankings Table */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800/50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">順位</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">ユーザー</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">スコア</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">予測精度</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">勝利/参加</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">勝率</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">連勝</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">最終ログイン</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {filteredRankings.slice(3).map((user, index) => (
                  <motion.tr
                    key={user.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: (index + 3) * 0.05 }}
                    className="hover:bg-gray-800/30 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className="text-lg font-semibold text-gray-400">
                          #{user.rank}
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center mr-3">
                          <span className="text-sm font-bold text-white">
                            {user.displayName.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium text-white">{user.displayName}</div>
                          <div className={`inline-block px-2 py-1 rounded text-xs ${getLevelColor(user.level)}`}>
                            {getLevelLabel(user.level)}
                          </div>
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <span className="text-white font-semibold">
                        {user.totalScore.toLocaleString()}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4">
                      <span className="text-green-400 font-semibold">
                        {user.accuracy.toFixed(1)}%
                      </span>
                    </td>
                    
                    <td className="px-6 py-4">
                      <span className="text-blue-400 font-semibold">
                        {user.contestsWon}/{user.contestsParticipated}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4">
                      <span className="text-purple-400 font-semibold">
                        {user.winRate.toFixed(1)}%
                      </span>
                    </td>
                    
                    <td className="px-6 py-4">
                      {user.streak > 0 && (
                        <div className="flex items-center">
                          <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
                          <span className="text-green-400 font-semibold">{user.streak}</span>
                        </div>
                      )}
                    </td>
                    
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {formatTimeAgo(user.lastActive)}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Load More Button */}
        <div className="text-center mt-8">
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            さらに読み込む
          </button>
        </div>
      </div>
    </div>
  );
}