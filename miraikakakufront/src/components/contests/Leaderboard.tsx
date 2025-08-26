'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Crown,
  Trophy,
  Medal,
  Star,
  Users,
  Target,
  TrendingUp,
  Award,
  Eye,
  Filter,
  Calendar,
  Zap
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  nickname: string;
  avatar_url?: string;
  title?: string;
  badges: string[];
  total_points: number;
  contests_participated: number;
  contests_won: number;
  average_accuracy: number;
  best_rank: number;
  recent_streak: number;
  last_activity: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond';
  is_current_user?: boolean;
}

interface LeaderboardProps {
  timeFrame?: 'all_time' | 'monthly' | 'weekly';
}

export default function Leaderboard({ timeFrame = 'all_time' }: LeaderboardProps) {
  const router = useRouter();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeFrame, setSelectedTimeFrame] = useState<'all_time' | 'monthly' | 'weekly'>(timeFrame);
  const [filterTier, setFilterTier] = useState<string>('all');

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedTimeFrame]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getLeaderboard(selectedTimeFrame);
      
      if (response.success && response.data) {
        setLeaderboard(response.data);
      } else {
        // Generate mock leaderboard for development
        generateMockLeaderboard();
      }
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      generateMockLeaderboard();
    } finally {
      setLoading(false);
    }
  };

  const generateMockLeaderboard = () => {
    const tiers: ('bronze' | 'silver' | 'gold' | 'platinum' | 'diamond')[] = ['bronze', 'silver', 'gold', 'platinum', 'diamond'];
    const titles = [
      'レジェンダリープレディクター',
      'グランドマスター',
      'プラチナオラクル',
      'ゴールドプレディクター',
      'シルバーエキスパート',
      'ブロンズアナリスト',
      '新人予測師',
      '市場の賢者',
      '予測マスター',
      'トレンドハンター'
    ];

    const nicknames = [
      'MarketMaster', 'TradingKing', 'PredictorPro', 'ForexGuru', 'StockSage',
      'CryptoOracle', 'TrendHunter', 'ChartWizard', 'DataDriven', 'AlphaSeer',
      'BullEye', 'BearTamer', 'GoldenRatio', 'PivoPoint', 'WaveRider',
      'MarketMover', 'PriceAction', 'VolatilityViper', 'MomentumKing', 'SwingMaster'
    ];

    const badges = [
      'ウィークリーチャンピオン', 'デイリーキング', 'マンスリーマスター', 
      '連勝記録', '高精度予測', '新人王', 'ベテラン', '市場分析家',
      '為替エキスパート', '株式プロ', '暗号資産マスター', 'コミュニティリーダー'
    ];

    const mockData: LeaderboardEntry[] = Array.from({ length: 50 }, (_, index) => {
      const rank = index + 1;
      const isTopTier = rank <= 5;
      const tier = isTopTier ? tiers[Math.floor(Math.random() * 2) + 3] : tiers[Math.floor(Math.random() * tiers.length)];
      const contestsParticipated = Math.floor(Math.random() * 50) + 10;
      const contestsWon = Math.floor(contestsParticipated * Math.random() * 0.3);
      
      return {
        rank,
        user_id: `user-${rank}`,
        nickname: nicknames[Math.floor(Math.random() * nicknames.length)] + (rank > 10 ? rank : ''),
        avatar_url: Math.random() > 0.7 ? `/avatars/user-${rank}.png` : undefined,
        title: isTopTier || Math.random() > 0.7 ? titles[Math.floor(Math.random() * titles.length)] : undefined,
        badges: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => 
          badges[Math.floor(Math.random() * badges.length)]
        ),
        total_points: Math.floor(Math.random() * 10000) + 1000 - (rank * 100),
        contests_participated: contestsParticipated,
        contests_won: contestsWon,
        average_accuracy: Math.random() * 30 + 70, // 70-100%
        best_rank: Math.floor(Math.random() * Math.min(rank, 10)) + 1,
        recent_streak: Math.floor(Math.random() * 10),
        last_activity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        tier,
        is_current_user: rank === 23 // Mock current user
      };
    });

    setLeaderboard(mockData);
  };

  const handleViewProfile = (userId: string) => {
    router.push(`/users/${userId}`);
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return Crown;
    if (rank === 2 || rank === 3) return Trophy;
    if (rank <= 10) return Medal;
    return Star;
  };

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-400';
    if (rank === 2) return 'text-gray-300';
    if (rank === 3) return 'text-orange-400';
    if (rank <= 10) return 'text-blue-400';
    return 'text-gray-400';
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'diamond': return 'text-cyan-400 bg-cyan-900/20';
      case 'platinum': return 'text-gray-300 bg-gray-800/50';
      case 'gold': return 'text-yellow-400 bg-yellow-900/20';
      case 'silver': return 'text-gray-400 bg-gray-700/50';
      case 'bronze': return 'text-orange-400 bg-orange-900/20';
      default: return 'text-gray-400 bg-gray-800/50';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'diamond': return 'ダイヤモンド';
      case 'platinum': return 'プラチナ';
      case 'gold': return 'ゴールド';
      case 'silver': return 'シルバー';
      case 'bronze': return 'ブロンズ';
      default: return tier;
    }
  };

  const formatLastActivity = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffDays > 0) {
      return `${diffDays}日前`;
    } else if (diffHours > 0) {
      return `${diffHours}時間前`;
    } else {
      return '1時間以内';
    }
  };

  const getTimeFrameLabel = (frame: string) => {
    switch (frame) {
      case 'weekly': return '今週';
      case 'monthly': return '今月';
      case 'all_time': return '全期間';
      default: return frame;
    }
  };

  // フィルタリング
  const filteredLeaderboard = leaderboard.filter(entry => {
    if (filterTier === 'all') return true;
    return entry.tier === filterTier;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* コントロール */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center space-x-4">
          {/* 期間選択 */}
          <select
            value={selectedTimeFrame}
            onChange={(e) => setSelectedTimeFrame(e.target.value as any)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
          >
            <option value="all_time">全期間</option>
            <option value="monthly">今月</option>
            <option value="weekly">今週</option>
          </select>

          {/* ティアフィルタ */}
          <select
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
          >
            <option value="all">全ティア</option>
            <option value="diamond">ダイヤモンド</option>
            <option value="platinum">プラチナ</option>
            <option value="gold">ゴールド</option>
            <option value="silver">シルバー</option>
            <option value="bronze">ブロンズ</option>
          </select>
        </div>

        <div className="text-sm text-gray-400">
          {getTimeFrameLabel(selectedTimeFrame)}のランキング - {filteredLeaderboard.length}人
        </div>
      </div>

      {/* トップ3の特別表示 */}
      {filteredLeaderboard.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {filteredLeaderboard.slice(0, 3).map((entry) => {
            const RankIcon = getRankIcon(entry.rank);
            return (
              <div
                key={entry.user_id}
                className={`bg-gradient-to-br ${
                  entry.rank === 1 
                    ? 'from-yellow-900/30 to-yellow-800/20 border-yellow-500/50' 
                    : entry.rank === 2
                    ? 'from-gray-800/30 to-gray-700/20 border-gray-400/50'
                    : 'from-orange-900/30 to-orange-800/20 border-orange-500/50'
                } border rounded-xl p-6 text-center hover:scale-105 transition-transform cursor-pointer`}
                onClick={() => handleViewProfile(entry.user_id)}
              >
                <div className={`w-16 h-16 mx-auto mb-3 rounded-full bg-gray-800 flex items-center justify-center ${getRankColor(entry.rank)}`}>
                  <RankIcon className="w-8 h-8" />
                </div>
                <div className="text-2xl font-bold text-white mb-1">#{entry.rank}</div>
                <div className="font-medium text-white mb-2">{entry.nickname}</div>
                {entry.title && (
                  <div className="text-xs text-gray-300 mb-2">{entry.title}</div>
                )}
                <div className="text-lg font-bold text-yellow-400 mb-2">
                  {entry.total_points.toLocaleString()}pt
                </div>
                <div className="text-sm text-gray-400">
                  平均的中率: {entry.average_accuracy.toFixed(1)}%
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* リーダーボードテーブル */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800/50 border-b border-gray-700/50">
              <tr className="text-sm text-gray-300">
                <th className="text-left p-4 w-16">順位</th>
                <th className="text-left p-4">ユーザー</th>
                <th className="text-center p-4">ティア</th>
                <th className="text-right p-4">総合ポイント</th>
                <th className="text-center p-4">平均的中率</th>
                <th className="text-center p-4">参加回数</th>
                <th className="text-center p-4">最高順位</th>
                <th className="text-center p-4">最終活動</th>
                <th className="text-center p-4">アクション</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {filteredLeaderboard.map((entry) => {
                const RankIcon = getRankIcon(entry.rank);
                
                return (
                  <tr 
                    key={entry.user_id}
                    className={`hover:bg-gray-800/20 transition-colors ${
                      entry.is_current_user ? 'bg-purple-900/20 border border-purple-500/30' : ''
                    }`}
                  >
                    {/* 順位 */}
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <RankIcon className={`w-4 h-4 ${getRankColor(entry.rank)}`} />
                        <span className={`font-bold ${getRankColor(entry.rank)}`}>
                          {entry.rank}
                        </span>
                      </div>
                    </td>

                    {/* ユーザー */}
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                          {entry.avatar_url ? (
                            <img 
                              src={entry.avatar_url} 
                              alt={entry.nickname}
                              className="w-10 h-10 rounded-full"
                            />
                          ) : (
                            <Users className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <div className="font-medium text-white flex items-center space-x-2">
                            <span>{entry.nickname}</span>
                            {entry.is_current_user && (
                              <span className="text-xs bg-purple-600/20 text-purple-400 px-1 py-0.5 rounded">
                                あなた
                              </span>
                            )}
                          </div>
                          {entry.title && (
                            <div className="text-xs text-gray-400">{entry.title}</div>
                          )}
                          {entry.badges.length > 0 && (
                            <div className="flex items-center space-x-1 mt-1">
                              <Award className="w-3 h-3 text-yellow-400" />
                              <span className="text-xs text-gray-500">
                                {entry.badges.length}個のバッジ
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* ティア */}
                    <td className="p-4 text-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTierColor(entry.tier)}`}>
                        {getTierLabel(entry.tier)}
                      </span>
                    </td>

                    {/* 総合ポイント */}
                    <td className="p-4 text-right">
                      <div className="font-bold text-white text-lg">
                        {entry.total_points.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-400">pt</div>
                    </td>

                    {/* 平均的中率 */}
                    <td className="p-4 text-center">
                      <div className="font-medium text-white">
                        {entry.average_accuracy.toFixed(1)}%
                      </div>
                      {entry.recent_streak > 0 && (
                        <div className="text-xs text-green-400">
                          {entry.recent_streak}連続的中
                        </div>
                      )}
                    </td>

                    {/* 参加回数 */}
                    <td className="p-4 text-center">
                      <div className="text-white">
                        {entry.contests_participated}回
                      </div>
                      <div className="text-xs text-gray-400">
                        勝利: {entry.contests_won}回
                      </div>
                    </td>

                    {/* 最高順位 */}
                    <td className="p-4 text-center">
                      <div className={`font-medium ${getRankColor(entry.best_rank)}`}>
                        {entry.best_rank}位
                      </div>
                    </td>

                    {/* 最終活動 */}
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center space-x-1 text-sm text-gray-400">
                        <Calendar className="w-3 h-3" />
                        <span>{formatLastActivity(entry.last_activity)}</span>
                      </div>
                    </td>

                    {/* アクション */}
                    <td className="p-4 text-center">
                      <button
                        onClick={() => handleViewProfile(entry.user_id)}
                        className="text-purple-400 hover:text-purple-300 transition-colors"
                        title="プロフィールを見る"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 現在のユーザーの位置表示 */}
      {leaderboard.find(entry => entry.is_current_user) && (
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Target className="w-5 h-5 text-purple-400" />
              <span className="text-white font-medium">あなたの現在の順位</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-purple-400">
                #{leaderboard.find(entry => entry.is_current_user)?.rank}
              </div>
              <div className="text-sm text-gray-400">
                {leaderboard.find(entry => entry.is_current_user)?.total_points.toLocaleString()}pt
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}