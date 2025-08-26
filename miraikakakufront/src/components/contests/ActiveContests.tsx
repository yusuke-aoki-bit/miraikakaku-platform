'use client';

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Trophy, 
  Users, 
  Target, 
  Zap, 
  Calendar,
  Award,
  TrendingUp,
  Timer
} from 'lucide-react';
import PredictionModal from '@/components/contests/PredictionModal';
import { apiClient } from '@/lib/api-client';

interface Contest {
  id: string;
  title: string;
  description: string;
  challenge: string;
  target_symbol: string;
  target_name: string;
  contest_type: 'weekly' | 'daily' | 'monthly' | 'special';
  start_date: string;
  end_date: string;
  submission_deadline: string;
  result_date: string;
  reward_description: string;
  prize_type: 'badge' | 'points' | 'title' | 'special';
  entry_fee: number;
  max_participants?: number;
  current_participants: number;
  status: 'upcoming' | 'active' | 'submission_closed' | 'completed';
  difficulty_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  user_participated: boolean;
  user_prediction?: number;
  estimated_result_value?: number;
}

interface ContestCardProps {
  contest: Contest;
  onParticipate: (contest: Contest) => void;
}

function ContestCard({ contest, onParticipate }: ContestCardProps) {
  const [timeLeft, setTimeLeft] = useState<string>('');

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date();
      const deadline = new Date(contest.submission_deadline);
      const diff = deadline.getTime() - now.getTime();

      if (diff <= 0) {
        setTimeLeft('締切');
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

      if (days > 0) {
        setTimeLeft(`${days}日${hours}時間`);
      } else if (hours > 0) {
        setTimeLeft(`${hours}時間${minutes}分`);
      } else {
        setTimeLeft(`${minutes}分`);
      }
    };

    calculateTimeLeft();
    const interval = setInterval(calculateTimeLeft, 60000);

    return () => clearInterval(interval);
  }, [contest.submission_deadline]);

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'text-green-400 bg-green-900/20';
      case 'intermediate': return 'text-blue-400 bg-blue-900/20';
      case 'advanced': return 'text-yellow-400 bg-yellow-900/20';
      case 'expert': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getDifficultyLabel = (level: string) => {
    switch (level) {
      case 'beginner': return '初級';
      case 'intermediate': return '中級';
      case 'advanced': return '上級';
      case 'expert': return 'エキスパート';
      default: return level;
    }
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

  const getPrizeIcon = (type: string) => {
    switch (type) {
      case 'badge': return Award;
      case 'points': return Zap;
      case 'title': return Trophy;
      case 'special': return Target;
      default: return Trophy;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isDeadlinePassed = () => {
    return new Date() > new Date(contest.submission_deadline);
  };

  const PrizeIcon = getPrizeIcon(contest.prize_type);

  return (
    <div className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl p-6 hover:border-purple-500/30 transition-all duration-300">
      {/* ヘッダー情報 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getContestTypeColor(contest.contest_type)}`}>
            {getContestTypeLabel(contest.contest_type)}
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(contest.difficulty_level)}`}>
            {getDifficultyLabel(contest.difficulty_level)}
          </div>
        </div>

        {contest.user_participated && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-green-900/20 text-green-400 rounded-full text-xs">
            <Target className="w-3 h-3" />
            <span>参加済み</span>
          </div>
        )}
      </div>

      {/* コンテストタイトル */}
      <h3 className="text-xl font-bold text-white mb-2">
        {contest.title}
      </h3>

      <p className="text-gray-300 text-sm mb-4 leading-relaxed">
        {contest.description}
      </p>

      {/* チャレンジ内容 */}
      <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 mb-4">
        <div className="flex items-center mb-2">
          <Target className="w-4 h-4 text-purple-400 mr-2" />
          <span className="text-sm font-medium text-purple-400">チャレンジ</span>
        </div>
        <p className="text-white font-medium">
          {contest.challenge}
        </p>
        <div className="flex items-center mt-2 text-sm text-gray-400">
          <span className="font-medium text-blue-400">{contest.target_symbol}</span>
          <span className="ml-2">({contest.target_name})</span>
        </div>
      </div>

      {/* 統計情報 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-800/30 rounded-lg">
          <div className="flex items-center justify-center mb-1">
            <Users className="w-4 h-4 text-blue-400 mr-1" />
            <span className="text-sm text-gray-400">参加者</span>
          </div>
          <div className="text-lg font-bold text-white">
            {contest.current_participants.toLocaleString()}
            {contest.max_participants && (
              <span className="text-sm text-gray-400">/{contest.max_participants.toLocaleString()}</span>
            )}
          </div>
        </div>

        <div className="text-center p-3 bg-gray-800/30 rounded-lg">
          <div className="flex items-center justify-center mb-1">
            <Timer className="w-4 h-4 text-yellow-400 mr-1" />
            <span className="text-sm text-gray-400">残り時間</span>
          </div>
          <div className={`text-lg font-bold ${
            timeLeft === '締切' ? 'text-red-400' : 'text-yellow-400'
          }`}>
            {timeLeft}
          </div>
        </div>
      </div>

      {/* 報酬情報 */}
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3 mb-4">
        <div className="flex items-center mb-2">
          <PrizeIcon className="w-4 h-4 text-yellow-400 mr-2" />
          <span className="text-sm font-medium text-yellow-400">報酬</span>
        </div>
        <p className="text-white text-sm">
          {contest.reward_description}
        </p>
      </div>

      {/* 重要日程 */}
      <div className="text-xs text-gray-500 mb-4 space-y-1">
        <div className="flex items-center">
          <Calendar className="w-3 h-3 mr-2" />
          <span>予測締切: {formatDate(contest.submission_deadline)}</span>
        </div>
        <div className="flex items-center">
          <TrendingUp className="w-3 h-3 mr-2" />
          <span>結果発表: {formatDate(contest.result_date)}</span>
        </div>
      </div>

      {/* アクションボタン */}
      <div className="flex items-center justify-between">
        {contest.user_participated && contest.user_prediction !== undefined ? (
          <div className="text-sm text-green-400">
            予測値: <span className="font-bold">{contest.user_prediction.toLocaleString()}</span>
          </div>
        ) : (
          <div></div>
        )}

        <button
          onClick={() => onParticipate(contest)}
          disabled={isDeadlinePassed() || contest.status === 'submission_closed'}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            isDeadlinePassed() || contest.status === 'submission_closed'
              ? 'bg-gray-600/50 text-gray-400 cursor-not-allowed'
              : contest.user_participated
              ? 'bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 border border-blue-500/30'
              : 'bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 border border-purple-500/30'
          }`}
        >
          {isDeadlinePassed() || contest.status === 'submission_closed'
            ? '締切済み'
            : contest.user_participated
            ? '予測を変更'
            : '予測を提出'
          }
        </button>
      </div>
    </div>
  );
}

export default function ActiveContests() {
  const [contests, setContests] = useState<Contest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContest, setSelectedContest] = useState<Contest | null>(null);
  const [showPredictionModal, setShowPredictionModal] = useState(false);

  useEffect(() => {
    fetchActiveContests();
  }, []);

  const fetchActiveContests = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getActiveContests();
      
      if (response.success && response.data) {
        setContests(response.data);
      } else {
        // Generate mock contests for development
        generateMockContests();
      }
    } catch (error) {
      console.error('Failed to fetch active contests:', error);
      generateMockContests();
    } finally {
      setLoading(false);
    }
  };

  const generateMockContests = () => {
    const mockContests: Contest[] = [
      {
        id: 'contest-001',
        title: '週間TOPIX予測チャレンジ',
        description: 'この週末のTOPIX終値を正確に予測しよう！市場動向を読み解く力が試されます。',
        challenge: '今週末のTOPIX終値を予測せよ！',
        target_symbol: '^TOPIX',
        target_name: '東証株価指数',
        contest_type: 'weekly',
        start_date: '2024-02-19T09:00:00Z',
        end_date: '2024-02-23T15:00:00Z',
        submission_deadline: '2024-02-23T14:00:00Z',
        result_date: '2024-02-23T16:00:00Z',
        reward_description: '上位10%に『ゴールドプレディクター』バッジを付与、1位には『週間チャンピオン』称号',
        prize_type: 'badge',
        entry_fee: 0,
        current_participants: 1247,
        max_participants: 5000,
        status: 'active',
        difficulty_level: 'intermediate',
        user_participated: false,
      },
      {
        id: 'contest-002',
        title: 'ドル円デイリー予測',
        description: '明日のドル円終値を予測！為替市場のプロフェッショナルを目指そう。',
        challenge: '明日17:00時点のUSD/JPY終値を予測',
        target_symbol: 'USDJPY',
        target_name: '米ドル/円',
        contest_type: 'daily',
        start_date: '2024-02-20T17:00:00Z',
        end_date: '2024-02-21T17:00:00Z',
        submission_deadline: '2024-02-21T16:00:00Z',
        result_date: '2024-02-21T17:30:00Z',
        reward_description: '上位5位以内に500ポイント、1位には1000ポイント付与',
        prize_type: 'points',
        entry_fee: 0,
        current_participants: 892,
        status: 'active',
        difficulty_level: 'beginner',
        user_participated: true,
        user_prediction: 149.85,
      },
      {
        id: 'contest-003',
        title: 'ビットコイン月間予測',
        description: '今月末のビットコイン価格を予測！暗号資産市場の動向を読み解こう。',
        challenge: '月末最終営業日のBTC価格(USD)を予測',
        target_symbol: 'BTCUSD',
        target_name: 'ビットコイン',
        contest_type: 'monthly',
        start_date: '2024-02-01T00:00:00Z',
        end_date: '2024-02-29T23:59:59Z',
        submission_deadline: '2024-02-28T23:59:59Z',
        result_date: '2024-03-01T10:00:00Z',
        reward_description: '上位1%に『暗号資産マスター』称号、トップ10に特別NFTバッジ',
        prize_type: 'special',
        entry_fee: 0,
        current_participants: 3421,
        status: 'active',
        difficulty_level: 'advanced',
        user_participated: false,
      },
      {
        id: 'contest-004',
        title: '日経225スペシャル',
        description: '決算シーズン特別企画！複数の重要指標を同時に予測する上級者向けチャレンジ。',
        challenge: '来週金曜日の日経225平均とその日の最高値・最安値を予測',
        target_symbol: '^N225',
        target_name: '日経平均株価',
        contest_type: 'special',
        start_date: '2024-02-19T00:00:00Z',
        end_date: '2024-02-26T15:00:00Z',
        submission_deadline: '2024-02-26T09:00:00Z',
        result_date: '2024-02-26T16:00:00Z',
        reward_description: '完璧予測者に『レジェンダリープレディクター』称号、上位5%に限定バッジ',
        prize_type: 'title',
        entry_fee: 100, // ポイント消費
        current_participants: 567,
        max_participants: 1000,
        status: 'active',
        difficulty_level: 'expert',
        user_participated: false,
      }
    ];

    setContests(mockContests);
  };

  const handleParticipate = (contest: Contest) => {
    setSelectedContest(contest);
    setShowPredictionModal(true);
  };

  const handlePredictionSubmit = async (prediction: number) => {
    if (!selectedContest) return;

    try {
      const response = await apiClient.submitPrediction(selectedContest.id, prediction);
      
      if (response.success) {
        // Update the contest in the local state
        setContests(prevContests => 
          prevContests.map(contest => 
            contest.id === selectedContest.id 
              ? { 
                  ...contest, 
                  user_participated: true, 
                  user_prediction: prediction,
                  current_participants: contest.user_participated 
                    ? contest.current_participants 
                    : contest.current_participants + 1
                }
              : contest
          )
        );
        
        setShowPredictionModal(false);
        setSelectedContest(null);
      }
    } catch (error) {
      console.error('Failed to submit prediction:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {contests.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {contests.map((contest) => (
            <ContestCard
              key={contest.id}
              contest={contest}
              onParticipate={handleParticipate}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <Trophy className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            開催中のコンテストがありません
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            新しいコンテストが開催されるまで<br />
            しばらくお待ちください。
          </p>
        </div>
      )}

      {/* 予測提出モーダル */}
      <PredictionModal
        contest={selectedContest}
        isOpen={showPredictionModal}
        onClose={() => {
          setShowPredictionModal(false);
          setSelectedContest(null);
        }}
        onSubmit={handlePredictionSubmit}
      />
    </div>
  );
}