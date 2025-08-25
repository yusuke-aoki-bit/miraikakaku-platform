'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Calendar,
  Trophy,
  Target,
  Users,
  TrendingUp,
  TrendingDown,
  Award,
  Eye,
  Medal,
  ExternalLink,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface PastContest {
  id: string;
  title: string;
  description: string;
  challenge: string;
  target_symbol: string;
  target_name: string;
  contest_type: 'weekly' | 'daily' | 'monthly' | 'special';
  end_date: string;
  result_date: string;
  actual_result: number;
  winning_prediction: number;
  winning_user: {
    id: string;
    nickname: string;
    avatar_url?: string;
  };
  total_participants: number;
  reward_description: string;
  user_participation?: {
    participated: boolean;
    prediction?: number;
    rank?: number;
    points_earned?: number;
    badge_earned?: string;
    accuracy_percent?: number;
  };
  status: 'completed' | 'cancelled';
}

interface PastContestCardProps {
  contest: PastContest;
  onViewDetails: (contestId: string) => void;
}

function PastContestCard({ contest, onViewDetails }: PastContestCardProps) {
  const router = useRouter();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatValue = (value: number, symbol: string) => {
    if (symbol === 'USDJPY') {
      return `¥${value.toFixed(2)}`;
    }
    if (symbol === 'BTCUSD') {
      return `$${value.toLocaleString()}`;
    }
    if (symbol.includes('TOPIX') || symbol.includes('N225')) {
      return value.toLocaleString();
    }
    return value.toLocaleString();
  };

  const getAccuracyColor = (accuracy?: number) => {
    if (!accuracy) return 'text-gray-400';
    if (accuracy >= 95) return 'text-green-400';
    if (accuracy >= 90) return 'text-blue-400';
    if (accuracy >= 80) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRankColor = (rank?: number) => {
    if (!rank) return 'text-gray-400';
    if (rank === 1) return 'text-yellow-400';
    if (rank <= 3) return 'text-gray-300';
    if (rank <= 10) return 'text-blue-400';
    return 'text-gray-400';
  };

  const getRankIcon = (rank?: number) => {
    if (rank === 1) return Trophy;
    if (rank === 2 || rank === 3) return Medal;
    return Target;
  };

  const getContestTypeColor = (type: string) => {
    switch (type) {
      case 'daily': return 'text-orange-400 bg-orange-900/20';
      case 'weekly': return 'text-blue-400 bg-blue-900/20';
      case 'monthly': return 'text-purple-400 bg-purple-900/20';
      case 'special': return 'text-pink-400 bg-pink-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getContestTypeLabel = (type: string) => {
    switch (type) {
      case 'daily': return 'デイリー';
      case 'weekly': return 'ウィークリー';
      case 'monthly': return 'マンスリー';
      case 'special': return 'スペシャル';
      default: return type;
    }
  };

  const calculateAccuracy = (prediction: number, actual: number) => {
    const error = Math.abs(prediction - actual);
    const errorPercent = (error / actual) * 100;
    return Math.max(0, 100 - errorPercent);
  };

  const userParticipated = contest.user_participation?.participated;
  const userRank = contest.user_participation?.rank;
  const userPrediction = contest.user_participation?.prediction;
  const userAccuracy = userPrediction 
    ? calculateAccuracy(userPrediction, contest.actual_result)
    : contest.user_participation?.accuracy_percent;

  const RankIcon = userRank ? getRankIcon(userRank) : Target;

  return (
    <div className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl p-6 hover:border-gray-600/50 transition-all duration-300">
      {/* ヘッダー */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getContestTypeColor(contest.contest_type)}`}>
            {getContestTypeLabel(contest.contest_type)}
          </div>
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Calendar className="w-3 h-3" />
            <span>{formatDate(contest.end_date)}</span>
          </div>
        </div>

        {contest.status === 'completed' ? (
          <div className="flex items-center space-x-1 text-green-400 text-sm">
            <CheckCircle className="w-4 h-4" />
            <span>完了</span>
          </div>
        ) : (
          <div className="flex items-center space-x-1 text-red-400 text-sm">
            <XCircle className="w-4 h-4" />
            <span>キャンセル</span>
          </div>
        )}
      </div>

      {/* コンテスト情報 */}
      <h3 className="text-xl font-bold text-white mb-2">
        {contest.title}
      </h3>

      <p className="text-gray-300 text-sm mb-4 leading-relaxed">
        {contest.challenge}
      </p>

      {/* 結果セクション */}
      {contest.status === 'completed' && (
        <div className="bg-gray-800/30 rounded-lg p-4 mb-4">
          <h4 className="font-semibold text-white mb-3 flex items-center">
            <Trophy className="w-4 h-4 text-yellow-400 mr-2" />
            コンテスト結果
          </h4>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-400 mb-1">実際の結果</div>
              <div className="text-white font-bold text-lg">
                {formatValue(contest.actual_result, contest.target_symbol)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">優勝予測</div>
              <div className="text-yellow-400 font-bold text-lg">
                {formatValue(contest.winning_prediction, contest.target_symbol)}
              </div>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-gray-700/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                  <Trophy className="w-3 h-3 text-gray-900" />
                </div>
                <span className="text-white font-medium">{contest.winning_user.nickname}</span>
              </div>
              <div className="text-xs text-gray-500">
                {contest.total_participants.toLocaleString()}人参加
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ユーザーの成績 */}
      {userParticipated && (
        <div className={`rounded-lg p-4 mb-4 ${
          userRank && userRank <= 10 
            ? 'bg-green-900/20 border border-green-500/30' 
            : 'bg-blue-900/20 border border-blue-500/30'
        }`}>
          <h4 className="font-semibold text-white mb-3 flex items-center">
            <RankIcon className={`w-4 h-4 mr-2 ${getRankColor(userRank)}`} />
            あなたの成績
          </h4>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-400 mb-1">順位</div>
              <div className={`font-bold text-lg ${getRankColor(userRank)}`}>
                {userRank ? `${userRank}位` : '未発表'}
              </div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">予測値</div>
              <div className="text-white font-bold text-lg">
                {userPrediction ? formatValue(userPrediction, contest.target_symbol) : '---'}
              </div>
            </div>
          </div>

          {userAccuracy !== undefined && (
            <div className="mt-3 pt-3 border-t border-gray-600/50">
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">的中率</span>
                <span className={`font-bold ${getAccuracyColor(userAccuracy)}`}>
                  {userAccuracy.toFixed(1)}%
                </span>
              </div>
            </div>
          )}

          {contest.user_participation?.badge_earned && (
            <div className="mt-2 pt-2 border-t border-gray-600/50">
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-yellow-400" />
                <span className="text-yellow-400 text-sm font-medium">
                  {contest.user_participation.badge_earned}
                </span>
              </div>
            </div>
          )}

          {contest.user_participation?.points_earned && contest.user_participation.points_earned > 0 && (
            <div className="mt-2">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-blue-400" />
                <span className="text-blue-400 text-sm">
                  +{contest.user_participation.points_earned}ポイント獲得
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 参加していない場合の表示 */}
      {!userParticipated && (
        <div className="bg-gray-800/30 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-2 text-gray-400 text-sm">
            <Clock className="w-4 h-4" />
            <span>このコンテストには参加していません</span>
          </div>
        </div>
      )}

      {/* アクションボタン */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <div className="flex items-center space-x-1">
            <Users className="w-3 h-3" />
            <span>{contest.total_participants.toLocaleString()}人</span>
          </div>
          <div className="flex items-center space-x-1">
            <Target className="w-3 h-3" />
            <span>{contest.target_symbol}</span>
          </div>
        </div>

        <button
          onClick={() => onViewDetails(contest.id)}
          className="flex items-center space-x-1 px-4 py-2 bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 rounded-lg transition-colors text-sm border border-purple-500/30"
        >
          <Eye className="w-4 h-4" />
          <span>詳細結果</span>
        </button>
      </div>
    </div>
  );
}

export default function PastContests() {
  const router = useRouter();
  const [contests, setContests] = useState<PastContest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'participated' | 'won'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'accuracy' | 'rank'>('date');

  useEffect(() => {
    fetchPastContests();
  }, []);

  const fetchPastContests = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getPastContests();
      
      if (response.success && response.data) {
        setContests(response.data);
      } else {
        // Generate mock past contests for development
        generateMockPastContests();
      }
    } catch (error) {
      console.error('Failed to fetch past contests:', error);
      generateMockPastContests();
    } finally {
      setLoading(false);
    }
  };

  const generateMockPastContests = () => {
    const mockContests: PastContest[] = [
      {
        id: 'past-001',
        title: '先週のTOPIX予測チャレンジ',
        description: '先週末のTOPIX終値を予測するウィークリーチャレンジでした。',
        challenge: '2月16日のTOPIX終値を予測',
        target_symbol: '^TOPIX',
        target_name: '東証株価指数',
        contest_type: 'weekly',
        end_date: '2024-02-16T15:00:00Z',
        result_date: '2024-02-16T16:00:00Z',
        actual_result: 2741.8,
        winning_prediction: 2742.1,
        winning_user: {
          id: 'user-123',
          nickname: 'MarketMaster',
          avatar_url: '/avatars/market-master.png'
        },
        total_participants: 1834,
        reward_description: '上位10%に『ゴールドプレディクター』バッジを付与',
        user_participation: {
          participated: true,
          prediction: 2739.5,
          rank: 47,
          points_earned: 150,
          badge_earned: undefined,
          accuracy_percent: 99.2
        },
        status: 'completed'
      },
      {
        id: 'past-002',
        title: 'ドル円デイリー予測 2/15',
        description: '2月15日のドル円終値予測でした。',
        challenge: '2月15日17:00時点のUSD/JPY終値を予測',
        target_symbol: 'USDJPY',
        target_name: '米ドル/円',
        contest_type: 'daily',
        end_date: '2024-02-15T17:00:00Z',
        result_date: '2024-02-15T17:30:00Z',
        actual_result: 149.73,
        winning_prediction: 149.74,
        winning_user: {
          id: 'user-456',
          nickname: 'ForexKing',
        },
        total_participants: 967,
        reward_description: '上位5位以内に500ポイント付与',
        user_participation: {
          participated: true,
          prediction: 149.85,
          rank: 2,
          points_earned: 500,
          badge_earned: 'シルバープレディクター',
          accuracy_percent: 99.9
        },
        status: 'completed'
      },
      {
        id: 'past-003',
        title: '1月末ビットコイン予測',
        description: '1月最終営業日のビットコイン価格を予測する月間チャレンジでした。',
        challenge: '1月31日のBTC価格(USD)を予測',
        target_symbol: 'BTCUSD',
        target_name: 'ビットコイン',
        contest_type: 'monthly',
        end_date: '2024-01-31T23:59:59Z',
        result_date: '2024-02-01T10:00:00Z',
        actual_result: 43127.50,
        winning_prediction: 43089.00,
        winning_user: {
          id: 'user-789',
          nickname: 'CryptoSage',
        },
        total_participants: 2456,
        reward_description: '上位1%に『暗号資産マスター』称号',
        user_participation: {
          participated: false
        },
        status: 'completed'
      },
      {
        id: 'past-004',
        title: '日経225新年予測',
        description: '新年最初の営業日の日経平均を予測する特別企画でした。',
        challenge: '1月4日の日経225終値を予測',
        target_symbol: '^N225',
        target_name: '日経平均株価',
        contest_type: 'special',
        end_date: '2024-01-04T15:00:00Z',
        result_date: '2024-01-04T16:00:00Z',
        actual_result: 33288.47,
        winning_prediction: 33291.20,
        winning_user: {
          id: 'user-101',
          nickname: 'NewYearOracle',
        },
        total_participants: 3721,
        reward_description: '完璧予測者に『レジェンダリープレディクター』称号',
        user_participation: {
          participated: true,
          prediction: 33150.00,
          rank: 156,
          points_earned: 50,
          accuracy_percent: 99.6
        },
        status: 'completed'
      }
    ];

    setContests(mockContests);
  };

  const handleViewDetails = (contestId: string) => {
    router.push(`/contests/${contestId}`);
  };

  // フィルタリングとソート
  const filteredContests = contests.filter(contest => {
    if (filter === 'participated') {
      return contest.user_participation?.participated;
    }
    if (filter === 'won') {
      return contest.user_participation?.rank && contest.user_participation.rank <= 3;
    }
    return true;
  });

  const sortedContests = [...filteredContests].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.end_date).getTime() - new Date(a.end_date).getTime();
      case 'accuracy':
        const aAccuracy = a.user_participation?.accuracy_percent || 0;
        const bAccuracy = b.user_participation?.accuracy_percent || 0;
        return bAccuracy - aAccuracy;
      case 'rank':
        const aRank = a.user_participation?.rank || 999999;
        const bRank = b.user_participation?.rank || 999999;
        return aRank - bRank;
      default:
        return 0;
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* フィルタとソート */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
          >
            <option value="all">全てのコンテスト</option>
            <option value="participated">参加したコンテスト</option>
            <option value="won">上位入賞したコンテスト</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-purple-500"
          >
            <option value="date">開催日順</option>
            <option value="accuracy">的中率順</option>
            <option value="rank">順位順</option>
          </select>
        </div>

        <div className="text-sm text-gray-400">
          {sortedContests.length}件のコンテスト
        </div>
      </div>

      {/* コンテストリスト */}
      {sortedContests.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sortedContests.map((contest) => (
            <PastContestCard
              key={contest.id}
              contest={contest}
              onViewDetails={handleViewDetails}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <Trophy className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            {filter === 'participated' 
              ? '参加したコンテストがありません' 
              : filter === 'won'
              ? '入賞したコンテストがありません'
              : '過去のコンテストがありません'
            }
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            {filter === 'participated' 
              ? '積極的にコンテストに参加して、予測スキルを磨きましょう！'
              : filter === 'won'
              ? '上位入賞を目指して、予測の精度を高めていきましょう！'
              : 'コンテストの履歴がここに表示されます。'
            }
          </p>
        </div>
      )}
    </div>
  );
}