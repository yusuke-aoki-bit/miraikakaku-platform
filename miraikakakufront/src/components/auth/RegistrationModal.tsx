'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { XMarkIcon, StarIcon, ChartBarIcon, BellIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import RegistrationForm from './RegistrationForm';
import SocialLogins from './SocialLogins';

interface RegistrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  trigger?: 'watchlist' | 'alert' | 'portfolio' | 'advanced_analysis' | 'export' | 'ai_insights';
  currentAction?: string;
}

const triggerMessages = {
  watchlist: {
    icon: StarIcon,
    title: 'ウォッチリストに追加',
    description: 'お気に入りの銘柄を追加して、リアルタイムで価格変動を追跡しましょう。',
    benefits: ['無制限のウォッチリスト作成', 'リアルタイム価格アラート', 'ポートフォリオ分析']
  },
  alert: {
    icon: BellIcon,
    title: '価格アラート設定',
    description: '指定した価格に達したときに通知を受け取り、投資機会を逃しません。',
    benefits: ['カスタムアラート設定', 'メール・プッシュ通知', '複数条件での通知']
  },
  portfolio: {
    icon: ChartBarIcon,
    title: 'ポートフォリオ管理',
    description: '投資パフォーマンスを詳細に分析し、最適な資産配分を実現しましょう。',
    benefits: ['詳細なパフォーマンス分析', '資産配分の最適化提案', 'リスク分析レポート']
  },
  advanced_analysis: {
    icon: ChartBarIcon,
    title: '高度な分析機能',
    description: 'プロレベルのテクニカル分析ツールで、より精度の高い投資判断を。',
    benefits: ['30種類以上のテクニカル指標', 'カスタムチャート作成', 'バックテスト機能']
  },
  export: {
    icon: ShieldCheckIcon,
    title: 'データエクスポート',
    description: '分析結果やポートフォリオデータをエクスポートして、さらに活用しましょう。',
    benefits: ['CSV・Excel形式でエクスポート', 'カスタムレポート生成', 'API連携']
  },
  ai_insights: {
    icon: StarIcon,
    title: 'AI投資洞察',
    description: 'AIが市場データを分析し、個人向けの投資アドバイスを提供します。',
    benefits: ['パーソナライズされた推奨銘柄', 'リスクレベル診断', '市場トレンド予測']
  }
};

export default function RegistrationModal({ isOpen, onClose, trigger = 'watchlist', currentAction }: RegistrationModalProps) {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const triggerData = triggerMessages[trigger];
  const IconComponent = triggerData.icon;

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      setShowForm(false);
      setIsClosing(false);
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      onClose();
    }, 150);
  };

  const handleRegistrationSuccess = () => {
    handleClose();
  };

  const handleLoginRedirect = () => {
    const redirectUrl = currentAction ? `/auth/login?redirect=${encodeURIComponent(currentAction)}` : '/auth/login';
    router.push(redirectUrl);
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${isClosing ? 'animate-fade-out' : 'animate-fade-in'}`}>
      {/* オーバーレイ */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* モーダルコンテンツ */}
      <div className={`relative bg-surface-elevated rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border border-border-primary ${isClosing ? 'animate-scale-out' : 'animate-scale-in'}`}>
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b border-border-primary">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-accent-primary/10 rounded-lg">
              <IconComponent className="w-6 h-6 text-accent-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {triggerData.title}
              </h3>
              <p className="text-sm text-text-secondary">
                ログインが必要です
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1 text-text-secondary hover:text-text-primary transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* メインコンテンツ */}
        <div className="p-6">
          {!showForm ? (
            <>
              {/* 機能説明 */}
              <div className="text-center mb-6">
                <p className="text-text-secondary mb-4">
                  {triggerData.description}
                </p>
                
                {/* メリット一覧 */}
                <div className="bg-accent-primary/5 rounded-lg p-4 mb-6">
                  <h4 className="text-sm font-medium text-text-primary mb-3">
                    登録すると利用できる機能：
                  </h4>
                  <ul className="space-y-2">
                    {triggerData.benefits.map((benefit, index) => (
                      <li key={index} className="flex items-center text-sm text-text-secondary">
                        <div className="w-1.5 h-1.5 bg-accent-primary rounded-full mr-3 flex-shrink-0" />
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* アクションボタン */}
              <div className="space-y-3">
                <button
                  onClick={() => setShowForm(true)}
                  className="w-full bg-accent-primary hover:bg-accent-primary/90 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  無料で登録して続行
                </button>
                
                <button
                  onClick={handleLoginRedirect}
                  className="w-full border border-border-primary hover:bg-surface-background text-text-primary py-3 px-4 rounded-lg font-medium transition-colors"
                >
                  すでにアカウントをお持ちの方
                </button>
              </div>

              {/* 注意書き */}
              <div className="mt-4 text-center">
                <p className="text-xs text-text-secondary">
                  登録は完全無料です。クレジットカード不要。
                </p>
              </div>
            </>
          ) : (
            <>
              {/* 戻るボタン */}
              <div className="mb-4">
                <button
                  onClick={() => setShowForm(false)}
                  className="text-sm text-accent-primary hover:text-accent-primary/80 transition-colors"
                >
                  ← 戻る
                </button>
              </div>

              {/* 登録フォーム */}
              <div className="space-y-6">
                <div className="text-center">
                  <h4 className="text-lg font-semibold text-text-primary mb-2">
                    アカウント作成
                  </h4>
                  <p className="text-sm text-text-secondary">
                    30秒で完了します
                  </p>
                </div>

                <RegistrationForm
                  redirectTo={currentAction}
                  onSuccess={handleRegistrationSuccess}
                />
                
                <SocialLogins
                  mode="register"
                  redirectTo={currentAction}
                  onSuccess={handleRegistrationSuccess}
                />
              </div>
            </>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes fade-out {
          from { opacity: 1; }
          to { opacity: 0; }
        }
        
        @keyframes scale-in {
          from { 
            opacity: 0;
            transform: scale(0.95) translateY(10px);
          }
          to { 
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        
        @keyframes scale-out {
          from { 
            opacity: 1;
            transform: scale(1) translateY(0);
          }
          to { 
            opacity: 0;
            transform: scale(0.95) translateY(10px);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }
        
        .animate-fade-out {
          animation: fade-out 0.15s ease-in;
        }
        
        .animate-scale-in {
          animation: scale-in 0.2s ease-out;
        }
        
        .animate-scale-out {
          animation: scale-out 0.15s ease-in;
        }
      `}</style>
    </div>
  );
}