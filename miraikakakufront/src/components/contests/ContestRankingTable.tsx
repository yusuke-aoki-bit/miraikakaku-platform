'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Trophy,
  Medal,
  Star,
  Crown,
  Target,
  Users,
  Award,
  Eye,
  ChevronUp,
  ChevronDown,
  Filter
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface RankingEntry {
  rank: number;
  user_id: string;
  nickname: string;
  avatar_url?: string;
  prediction: number;
  actual_result: number;
  accuracy: number;
  error_abs: number;
  points_earned: number;
  badge_earned?: string;
  is_current_user?: boolean;
}

interface ContestRankingTableProps {
  contestId: string;
}

type SortField = 'rank' | 'accuracy' | 'error_abs' | 'points_earned';
type SortOrder = 'asc' | 'desc';

export default function ContestRankingTable({ contestId }: ContestRankingTableProps) {
  const router = useRouter();
  const [rankings, setRankings] = useState<RankingEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField>('rank');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [filterTop, setFilterTop] = useState<number>(100); // Top N users to show
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchContestRanking();
  }, [contestId]);

  const fetchContestRanking = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getContestRanking(contestId);
      
      if (response.success && response.data) {
        setRankings(response.data);
      } else {
        // Generate mock ranking data for development
        generateMockRanking();
      }
    } catch (error) {
      console.error('Failed to fetch contest ranking:', error);
      generateMockRanking();
    } finally {
      setLoading(false);
    }
  };

  const generateMockRanking = () => {
    const actualResult = 2741.8;
    const nicknames = [
      'MarketMaster', 'TradingKing', 'PredictorPro', 'ForexGuru', 'StockSage',
      'CryptoOracle', 'TrendHunter', 'ChartWizard', 'DataDriven', 'AlphaSeer',
      'BullEye', 'BearTamer', 'GoldenRatio', 'PivotPoint', 'WaveRider',
      'MarketMover', 'PriceAction', 'VolatilityViper', 'MomentumKing', 'SwingMaster'
    ];

    const badges = [
      '週間チャンピオン', 'ゴールドプレディクター', 'シルバーエキスパート',
      '高精度予測', '連勝記録', '新人王', 'ベテラン予測師'
    ];

    const mockData: RankingEntry[] = Array.from({ length: 1834 }, (_, index) => {
      const rank = index + 1;
      
      // 順位に基づく予測精度の設定（上位ほど正確）
      const baseError = rank <= 10 ? 0.1 + Math.random() * 0.5 : 
                       rank <= 50 ? 0.5 + Math.random() * 2 :
                       rank <= 100 ? 2 + Math.random() * 5 :
                       5 + Math.random() * 20;
      
      const errorDirection = Math.random() > 0.5 ? 1 : -1;
      const prediction = actualResult + (baseError * errorDirection);
      const errorAbs = Math.abs(prediction - actualResult);
      const accuracy = Math.max(0, 100 - (errorAbs / actualResult) * 100);
      
      // ポイント計算
      let pointsEarned = 0;
      if (rank === 1) pointsEarned = 1000;
      else if (rank <= 3) pointsEarned = 750;
      else if (rank <= 10) pointsEarned = 500;
      else if (rank <= 50) pointsEarned = 200;
      else if (rank <= 100) pointsEarned = 100;
      else if (rank <= 500) pointsEarned = 50;

      // バッジ付与
      let badgeEarned: string | undefined;
      if (rank === 1) badgeEarned = '週間チャンピオン';
      else if (rank <= 3) badgeEarned = 'ゴールドプレディクター';
      else if (rank <= 10) badgeEarned = 'シルバーエキスパート';
      else if (rank <= 50 && Math.random() > 0.7) badgeEarned = '高精度予測';

      return {
        rank,
        user_id: `user-${rank}`,
        nickname: nicknames[Math.floor(Math.random() * nicknames.length)] + (rank > 20 ? rank : ''),
        avatar_url: Math.random() > 0.8 ? `/avatars/user-${rank}.png` : undefined,
        prediction,
        actual_result: actualResult,
        accuracy,
        error_abs: errorAbs,
        points_earned: pointsEarned,
        badge_earned: badgeEarned,
        is_current_user: rank === 47 // Mock current user
      };
    });

    setRankings(mockData);
  };

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder(field === 'rank' ? 'asc' : 'desc');
    }
  };

  const handleViewProfile = (userId: string) => {
    router.push(`/users/${userId}`);
  };

  // フィルタリングとソート
  const filteredRankings = rankings.filter(entry => {
    const matchesSearch = entry.nickname.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTopFilter = entry.rank <= filterTop;
    return matchesSearch && matchesTopFilter;
  });

  const sortedRankings = [...filteredRankings].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    }

    return 0;
  });

  // ページネーション
  const totalPages = Math.ceil(sortedRankings.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedRankings = sortedRankings.slice(startIndex, startIndex + itemsPerPage);

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

  const formatValue = (value: number) => {
    return value.toFixed(1);
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-left hover:text-yellow-400 transition-colors group"
    >
      <span>{children}</span>
      <div className="flex flex-col">
        <ChevronUp 
          className={`w-3 h-3 ${
            sortField === field && sortOrder === 'asc' 
              ? 'text-yellow-400' 
              : 'text-gray-600 group-hover:text-gray-400'
          }`} 
        />
        <ChevronDown 
          className={`w-3 h-3 -mt-1 ${
            sortField === field && sortOrder === 'desc' 
              ? 'text-yellow-400' 
              : 'text-gray-600 group-hover:text-gray-400'
          }`} 
        />
      </div>
    </button>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* コントロール */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center space-x-4">
          {/* 検索 */}
          <div className="relative">
            <input
              type="text"
              placeholder="ユーザー名で検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500"
            />
            <Users className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          {/* トップN表示フィルタ */}
          <select
            value={filterTop}
            onChange={(e) => setFilterTop(Number(e.target.value))}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
          >
            <option value={50}>トップ50</option>
            <option value={100}>トップ100</option>
            <option value={500}>トップ500</option>
            <option value={1000}>トップ1000</option>
            <option value={rankings.length}>全参加者</option>
          </select>
        </div>

        <div className="text-sm text-gray-400">
          {sortedRankings.length.toLocaleString()}人中 {startIndex + 1}-{Math.min(startIndex + itemsPerPage, sortedRankings.length)}人を表示
        </div>
      </div>

      {/* ランキングテーブル */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800/50 border-b border-gray-700/50">
              <tr className="text-sm text-gray-300">
                <th className="text-left p-4 w-20">
                  <SortButton field="rank">順位</SortButton>
                </th>
                <th className="text-left p-4">ユーザー</th>
                <th className="text-right p-4">予測値</th>
                <th className="text-center p-4">
                  <SortButton field="accuracy">的中率</SortButton>
                </th>
                <th className="text-center p-4">
                  <SortButton field="error_abs">誤差</SortButton>
                </th>
                <th className="text-right p-4">
                  <SortButton field="points_earned">獲得ポイント</SortButton>
                </th>
                <th className="text-center p-4">バッジ</th>
                <th className="text-center p-4">アクション</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {paginatedRankings.map((entry) => {
                const RankIcon = getRankIcon(entry.rank);
                
                return (
                  <tr 
                    key={entry.user_id}
                    className={`hover:bg-gray-800/20 transition-colors ${
                      entry.is_current_user ? 'bg-purple-900/20 border-l-4 border-purple-500' : ''
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
                        <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                          {entry.avatar_url ? (
                            <img 
                              src={entry.avatar_url} 
                              alt={entry.nickname}
                              className="w-8 h-8 rounded-full"
                            />
                          ) : (
                            <Users className="w-4 h-4 text-gray-400" />
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
                        </div>
                      </div>
                    </td>

                    {/* 予測値 */}
                    <td className="p-4 text-right">
                      <div className="font-medium text-white">
                        {formatValue(entry.prediction)}
                      </div>
                    </td>

                    {/* 的中率 */}
                    <td className="p-4 text-center">
                      <div className="font-bold text-green-400">
                        {entry.accuracy.toFixed(2)}%
                      </div>
                    </td>

                    {/* 誤差 */}
                    <td className="p-4 text-center">
                      <div className="font-medium text-red-400">
                        ±{entry.error_abs.toFixed(1)}
                      </div>
                    </td>

                    {/* 獲得ポイント */}
                    <td className="p-4 text-right">
                      <div className="font-bold text-blue-400">
                        {entry.points_earned.toLocaleString()}pt
                      </div>
                    </td>

                    {/* バッジ */}
                    <td className="p-4 text-center">
                      {entry.badge_earned ? (
                        <div className="flex items-center justify-center space-x-1">
                          <Award className="w-4 h-4 text-yellow-400" />
                          <span className="text-xs text-yellow-400">
                            {entry.badge_earned}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
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

        {/* ページネーション */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-gray-700/50">
            <div className="text-sm text-gray-400">
              ページ {currentPage} / {totalPages}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
              >
                前へ
              </button>
              
              {/* ページ番号 */}
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                if (pageNum <= totalPages) {
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-1 rounded transition-colors ${
                        currentPage === pageNum
                          ? 'bg-yellow-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                }
                return null;
              })}

              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
              >
                次へ
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 現在のユーザーハイライト */}
      {rankings.find(entry => entry.is_current_user) && (
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Target className="w-5 h-5 text-purple-400" />
              <span className="text-white font-medium">あなたの成績</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-purple-400">
                #{rankings.find(entry => entry.is_current_user)?.rank}位
              </div>
              <div className="text-sm text-gray-400">
                的中率: {rankings.find(entry => entry.is_current_user)?.accuracy.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}