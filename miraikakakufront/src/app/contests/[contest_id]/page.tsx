'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ArrowLeft, 
  Trophy, 
  Target, 
  BarChart3,
  Award,
  Medal,
  Crown,
  Info
} from 'lucide-react';
import ContestResultChart from '@/components/contests/ContestResultChart';
import ContestRankingTable from '@/components/contests/ContestRankingTable';
import { apiClient } from '@/lib/api-client';

interface ContestDetail {
  id: string;
  title: string;
  description: string;
  challenge: string;
  target_symbol: string;
  target_name: string;
  contest_type: 'weekly' | 'daily' | 'monthly' | 'special';
  start_date: string;
  end_date: string;
  result_date: string;
  actual_result: number;
  total_participants: number;
  status: 'completed' | 'cancelled';
  reward_description: string;
  user_participation?: {
    participated: boolean;
    prediction?: number;
    rank?: number;
    points_earned?: number;
    badge_earned?: string;
    accuracy_percent?: number;
  };
  statistics: {
    average_prediction: number;
    median_prediction: number;
    closest_prediction: number;
    furthest_prediction: number;
    standard_deviation: number;
  };
  top_performers: Array<{
    rank: number;
    user_id: string;
    nickname: string;
    prediction: number;
    accuracy: number;
    points_earned: number;
    badge_earned?: string;
  }>;
}

interface PredictionDistribution {
  range: string;
  count: number;
  percentage: number;
}

export default function ContestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const contestId = params.contest_id as string;

  const [contest, setContest] = useState<ContestDetail | null>(null);
  const [distribution, setDistribution] = useState<PredictionDistribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'ranking' | 'analysis'>('overview');

  const setDefaultContestData = useCallback(() => {
    setContest(null);
    setDistribution([]);
    setError('コンテストデータが見つかりませんでした');
  }, []);

  const fetchContestDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getContestDetails(contestId);
      
      if (response.success && response.data) {
        setContest(response.data.contest);
        setDistribution(response.data.distribution);
      } else {
        setDefaultContestData();
      }
    } catch (err) {
      console.error('Failed to fetch contest details:', err);
      setDefaultContestData();
    } finally {
      setLoading(false);
    }
  }, [contestId, setDefaultContestData]);

  useEffect(() => {
    if (contestId) {
      fetchContestDetails();
    }
  }, [contestId, fetchContestDetails]);

  const formatValue = (value: number, symbol: string) => {
    if (symbol === 'USDJPY') {
      return `¥${value.toFixed(2)}`;
    }
    if (symbol === 'BTCUSD') {
      return `$${value.toLocaleString()}`;
    }
    if (symbol.includes('TOPIX') || symbol.includes('N225')) {
      return value.toFixed(1);
    }
    return value.toLocaleString();
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-400';
    if (rank === 2) return 'text-gray-300';
    if (rank === 3) return 'text-orange-400';
    if (rank <= 10) return 'text-blue-400';
    return 'text-gray-400';
  };

  const handleBackToContests = () => {
    router.push('/contests');
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
        </div>
      </div>
    );
  }

  if (error || !contest) {
    return (
      <div className="p-6 space-y-6">
        <button
          onClick={handleBackToContests}
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>コンテスト一覧に戻る</span>
        </button>
        
        <div className="text-center py-20">
          <Trophy className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            コンテストが見つかりません
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            指定されたコンテストは存在しないか、<br />
            一時的にアクセスできません。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 戻るボタン */}
      <button
        onClick={handleBackToContests}
        className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>コンテスト一覧に戻る</span>
      </button>

      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border border-purple-500/30 rounded-xl p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getContestTypeColor(contest.contest_type)}`}>
                {getContestTypeLabel(contest.contest_type)}
              </div>
              <div className="text-sm text-gray-400">
                {formatDate(contest.end_date)}
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              {contest.title}
            </h1>
            <p className="text-gray-300">{contest.description}</p>
          </div>

          <div className="text-right">
            <div className="text-sm text-gray-400">参加者数</div>
            <div className="text-2xl font-bold text-blue-400">
              {contest.total_participants.toLocaleString()}人
            </div>
          </div>
        </div>

        {/* チャレンジ内容 */}
        <div className="bg-gray-800/30 rounded-lg p-4 mb-4">
          <div className="flex items-center mb-2">
            <Target className="w-4 h-4 text-purple-400 mr-2" />
            <span className="text-sm font-medium text-purple-400">チャレンジ内容</span>
          </div>
          <p className="text-white font-medium mb-2">{contest.challenge}</p>
          <div className="text-sm text-gray-400">
            対象: <span className="text-blue-400 font-medium">{contest.target_symbol}</span> ({contest.target_name})
          </div>
        </div>

        {/* 結果サマリー */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800/30 rounded-lg p-3 text-center">
            <div className="text-sm text-gray-400 mb-1">実際の結果</div>
            <div className="text-lg font-bold text-green-400">
              {formatValue(contest.actual_result, contest.target_symbol)}
            </div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-3 text-center">
            <div className="text-sm text-gray-400 mb-1">平均予測</div>
            <div className="text-lg font-bold text-white">
              {formatValue(contest.statistics.average_prediction, contest.target_symbol)}
            </div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-3 text-center">
            <div className="text-sm text-gray-400 mb-1">最高精度</div>
            <div className="text-lg font-bold text-yellow-400">
              {formatValue(contest.statistics.closest_prediction, contest.target_symbol)}
            </div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-3 text-center">
            <div className="text-sm text-gray-400 mb-1">標準偏差</div>
            <div className="text-lg font-bold text-purple-400">
              {contest.statistics.standard_deviation.toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      {/* ユーザーの成績 */}
      {contest.user_participation?.participated && (
        <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Medal className="w-6 h-6 mr-2 text-green-400" />
            あなたの成績
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">順位</div>
              <div className={`text-2xl font-bold ${getRankColor(contest.user_participation.rank || 999)}`}>
                {contest.user_participation.rank ? `${contest.user_participation.rank}位` : '未発表'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">予測値</div>
              <div className="text-2xl font-bold text-white">
                {contest.user_participation.prediction 
                  ? formatValue(contest.user_participation.prediction, contest.target_symbol)
                  : '---'
                }
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">的中率</div>
              <div className="text-2xl font-bold text-green-400">
                {contest.user_participation.accuracy_percent?.toFixed(1) || '---'}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">獲得ポイント</div>
              <div className="text-2xl font-bold text-blue-400">
                {contest.user_participation.points_earned || 0}pt
              </div>
            </div>
          </div>

          {contest.user_participation.badge_earned && (
            <div className="mt-4 pt-4 border-t border-gray-700/50">
              <div className="flex items-center justify-center space-x-2">
                <Award className="w-5 h-5 text-yellow-400" />
                <span className="text-yellow-400 font-medium">
                  {contest.user_participation.badge_earned} を獲得！
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* タブナビゲーション */}
      <div className="border-b border-gray-700/50">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: '概要', icon: Info },
            { id: 'ranking', label: 'ランキング', icon: Trophy },
            { id: 'analysis', label: '分析', icon: BarChart3 }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'overview' | 'ranking' | 'analysis')}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  isActive
                    ? 'border-yellow-400 text-yellow-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* タブコンテンツ */}
      <div>
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* トップパフォーマー */}
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Crown className="w-5 h-5 mr-2 text-yellow-400" />
                トップパフォーマー
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {contest.top_performers.slice(0, 3).map((performer) => (
                  <div 
                    key={performer.user_id}
                    className={`p-4 rounded-lg border ${
                      performer.rank === 1 
                        ? 'bg-yellow-900/20 border-yellow-500/50' 
                        : performer.rank === 2
                        ? 'bg-gray-800/50 border-gray-500/50'
                        : 'bg-orange-900/20 border-orange-500/50'
                    }`}
                  >
                    <div className="text-center">
                      <div className={`text-2xl font-bold mb-2 ${getRankColor(performer.rank)}`}>
                        #{performer.rank}
                      </div>
                      <div className="font-medium text-white mb-1">
                        {performer.nickname}
                      </div>
                      <div className="text-sm text-gray-300 mb-2">
                        予測: {formatValue(performer.prediction, contest.target_symbol)}
                      </div>
                      <div className="text-sm text-green-400">
                        的中率: {performer.accuracy.toFixed(2)}%
                      </div>
                      {performer.badge_earned && (
                        <div className="mt-2 text-xs text-yellow-400">
                          {performer.badge_earned}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 報酬情報 */}
            <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center">
                <Award className="w-5 h-5 mr-2 text-yellow-400" />
                報酬について
              </h3>
              <p className="text-gray-300">{contest.reward_description}</p>
            </div>
          </div>
        )}

        {activeTab === 'ranking' && (
          <ContestRankingTable contestId={contest.id} />
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <ContestResultChart
              actualResult={contest.actual_result}
              distribution={distribution}
              userPrediction={contest.user_participation?.prediction}
            />
            
            {/* 統計情報詳細 */}
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">統計分析</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <div className="text-sm text-gray-400 mb-1">中央値</div>
                  <div className="text-lg font-bold text-white">
                    {formatValue(contest.statistics.median_prediction, contest.target_symbol)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">最大予測</div>
                  <div className="text-lg font-bold text-red-400">
                    {formatValue(contest.statistics.furthest_prediction, contest.target_symbol)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">最小予測</div>
                  <div className="text-lg font-bold text-green-400">
                    {formatValue(Math.min(...contest.top_performers.map(p => p.prediction)), contest.target_symbol)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">予測範囲</div>
                  <div className="text-lg font-bold text-purple-400">
                    ±{((contest.statistics.furthest_prediction - contest.statistics.closest_prediction) / 2).toFixed(1)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}