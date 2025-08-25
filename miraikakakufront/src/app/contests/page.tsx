'use client';

import React, { useState, useEffect } from 'react';
import { Trophy, Target, Medal, Users, Zap, Crown } from 'lucide-react';
import ActiveContests from '@/components/contests/ActiveContests';
import PastContests from '@/components/contests/PastContests';
import Leaderboard from '@/components/contests/Leaderboard';
import { apiClient } from '@/lib/api-client';

type TabType = 'active' | 'past' | 'leaderboard';

interface ContestStats {
  total_contests: number;
  active_contests: number;
  total_participants: number;
  user_rank?: number;
  user_points?: number;
  user_badges?: number;
}

export default function ContestsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('active');
  const [stats, setStats] = useState<ContestStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContestStats();
  }, []);

  const fetchContestStats = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getContestStats();
      
      if (response.status === 'success' && response.data) {
        setStats(response.data);
      } else {
        // Generate mock stats for development
        generateMockStats();
      }
    } catch (error) {
      console.error('Failed to fetch contest stats:', error);
      generateMockStats();
    } finally {
      setLoading(false);
    }
  };

  const generateMockStats = () => {
    const mockStats: ContestStats = {
      total_contests: 47,
      active_contests: 5,
      total_participants: 2847,
      user_rank: 156,
      user_points: 2450,
      user_badges: 7
    };
    setStats(mockStats);
  };

  const getTabIcon = (tab: TabType) => {
    switch (tab) {
      case 'active':
        return Zap;
      case 'past':
        return Target;
      case 'leaderboard':
        return Crown;
      default:
        return Trophy;
    }
  };

  const getTabLabel = (tab: TabType) => {
    switch (tab) {
      case 'active':
        return '開催中';
      case 'past':
        return '過去の結果';
      case 'leaderboard':
        return 'ランキング';
      default:
        return tab;
    }
  };

  const getTabCount = (tab: TabType) => {
    if (!stats) return null;
    switch (tab) {
      case 'active':
        return stats.active_contests;
      case 'past':
        return stats.total_contests - stats.active_contests;
      case 'leaderboard':
        return null; // Don't show count for leaderboard
      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Trophy className="w-8 h-8 mr-3 text-yellow-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">予測コロシアム</h1>
            <p className="text-sm text-gray-400 mt-1">
              予測スキルを競い合い、上位を目指そう
            </p>
          </div>
        </div>

        {/* ユーザー成績サマリー */}
        {stats && stats.user_rank && (
          <div className="text-right">
            <div className="text-sm text-gray-400">あなたの順位</div>
            <div className="text-2xl font-bold text-yellow-400">
              #{stats.user_rank}
            </div>
            <div className="text-sm text-gray-300">
              {stats.user_points?.toLocaleString()}pt
            </div>
          </div>
        )}
      </div>

      {/* 機能説明パネル */}
      <div className="bg-gradient-to-r from-purple-900/20 to-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start space-x-4">
          <Trophy className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">
              予測コロシアムの特徴
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-300">
              <div>
                <div className="flex items-center mb-2">
                  <Target className="w-4 h-4 text-green-400 mr-2" />
                  <span className="font-medium">予測チャレンジ</span>
                </div>
                <p>株価指数、個別銘柄、為替レートなど様々な金融商品の値動きを予測。精度を競い合います</p>
              </div>
              <div>
                <div className="flex items-center mb-2">
                  <Medal className="w-4 h-4 text-blue-400 mr-2" />
                  <span className="font-medium">称号とバッジ</span>
                </div>
                <p>優秀な成績を収めることで特別な称号やバッジを獲得。レア称号は真の予測マスターの証です</p>
              </div>
              <div>
                <div className="flex items-center mb-2">
                  <Users className="w-4 h-4 text-purple-400 mr-2" />
                  <span className="font-medium">コミュニティ</span>
                </div>
                <p>全国の投資家とスキルを競い合い、リーダーボードで実力を証明。成長し続ける投資コミュニティ</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 統計サマリー */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800/30 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.active_contests}</div>
            <div className="text-sm text-gray-400">開催中のコンテスト</div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.total_participants.toLocaleString()}</div>
            <div className="text-sm text-gray-400">総参加者数</div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-400">{stats.total_contests}</div>
            <div className="text-sm text-gray-400">総開催回数</div>
          </div>
          <div className="bg-gray-800/30 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.user_badges || 0}</div>
            <div className="text-sm text-gray-400">獲得バッジ数</div>
          </div>
        </div>
      )}

      {/* タブナビゲーション */}
      <div className="border-b border-gray-700/50">
        <nav className="flex space-x-8">
          {(['active', 'past', 'leaderboard'] as TabType[]).map((tab) => {
            const TabIcon = getTabIcon(tab);
            const count = getTabCount(tab);
            const isActive = activeTab === tab;

            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  isActive
                    ? 'border-yellow-400 text-yellow-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                }`}
              >
                <TabIcon className="w-5 h-5" />
                <span>{getTabLabel(tab)}</span>
                {count !== null && (
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    isActive 
                      ? 'bg-yellow-400/20 text-yellow-400' 
                      : 'bg-gray-700 text-gray-300'
                  }`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* タブコンテンツ */}
      <div className="min-h-96">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
          </div>
        ) : (
          <>
            {activeTab === 'active' && <ActiveContests />}
            {activeTab === 'past' && <PastContests />}
            {activeTab === 'leaderboard' && <Leaderboard />}
          </>
        )}
      </div>

      {/* フッター注意事項 */}
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Trophy className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-400 mb-2">予測コロシアムについて</h4>
            <div className="text-sm text-gray-300 space-y-2">
              <p>
                • 予測コロシアムは教育・エンターテイメント目的のゲーミフィケーション機能です。実際の投資判断とは異なります。
              </p>
              <p>
                • 予測の精度は過去の実績を示すものであり、将来の投資成果を保証するものではありません。
              </p>
              <p>
                • 健全なコミュニティ環境維持のため、不適切な行為は禁止されています。利用規約をご確認ください。
              </p>
              <p>
                • 個人情報の保護に配慮し、ニックネームでの参加を推奨しています。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}