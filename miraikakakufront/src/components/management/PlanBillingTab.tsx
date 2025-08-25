'use client';

import { useState } from 'react';
import { CreditCardIcon, DocumentArrowDownIcon, StarIcon, CheckIcon } from '@heroicons/react/24/outline';

interface Subscription {
  plan: 'free' | 'pro';
  status: 'active' | 'cancelled' | 'past_due';
  next_billing_date?: string;
  amount?: number;
  currency: string;
}

interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
}

interface BillingHistory {
  id: string;
  date: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed';
  invoice_url?: string;
  description: string;
}

export default function PlanBillingTab() {
  const [subscription] = useState<Subscription>({
    plan: 'free',
    status: 'active',
    currency: 'JPY',
  });

  const [paymentMethods] = useState<PaymentMethod[]>([
    {
      id: 'pm_1',
      brand: 'visa',
      last4: '4242',
      exp_month: 12,
      exp_year: 2025,
      is_default: true,
    },
  ]);

  const [billingHistory] = useState<BillingHistory[]>([
    {
      id: 'inv_1',
      date: '2024-07-24T00:00:00Z',
      amount: 2980,
      currency: 'JPY',
      status: 'paid',
      invoice_url: '#',
      description: 'Miraikakaku Pro プラン - 月額',
    },
    {
      id: 'inv_2',
      date: '2024-06-24T00:00:00Z',
      amount: 2980,
      currency: 'JPY',
      status: 'paid',
      invoice_url: '#',
      description: 'Miraikakaku Pro プラン - 月額',
    },
  ]);

  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleUpgrade = async () => {
    setIsProcessing(true);
    try {
      // TODO: Stripe Checkoutへリダイレクト
      const response = await fetch('/api/user/upgrade', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (response.ok) {
        const { checkout_url } = await response.json();
        window.location.href = checkout_url;
      } else {
        alert('アップグレードの処理に失敗しました');
      }
    } catch (error) {
      console.error('Upgrade error:', error);
      alert('ネットワークエラーが発生しました');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      // TODO: Stripe顧客ポータルへリダイレクト
      const response = await fetch('/api/user/billing-portal', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (response.ok) {
        const { portal_url } = await response.json();
        window.open(portal_url, '_blank');
      } else {
        alert('支払い管理画面を開けませんでした');
      }
    } catch (error) {
      console.error('Portal error:', error);
      alert('ネットワークエラーが発生しました');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <span className="inline-flex px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">支払済み</span>;
      case 'pending':
        return <span className="inline-flex px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">保留中</span>;
      case 'failed':
        return <span className="inline-flex px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">失敗</span>;
      default:
        return <span className="inline-flex px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">{status}</span>;
    }
  };

  const getCardBrand = (brand: string) => {
    switch (brand.toLowerCase()) {
      case 'visa':
        return 'Visa';
      case 'mastercard':
        return 'Mastercard';
      case 'amex':
        return 'American Express';
      case 'jcb':
        return 'JCB';
      default:
        return brand.toUpperCase();
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-text-primary">プランと請求</h2>
        <p className="text-sm text-text-secondary mt-1">
          サブスクリプションプランと支払い履歴を管理します
        </p>
      </div>

      <div className="space-y-8">
        {/* 現在のプラン */}
        <div>
          <h3 className="text-lg font-medium text-text-primary mb-4">現在のプラン</h3>
          
          {subscription.plan === 'free' ? (
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 border border-border-primary rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-xl font-bold text-text-primary">無料プラン</h4>
                  <p className="text-text-secondary">基本機能をご利用いただけます</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-text-primary">¥0</div>
                  <div className="text-sm text-text-secondary">/月</div>
                </div>
              </div>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  基本的な株価チャート表示
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  10銘柄までのウォッチリスト
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  基本的な市場データ
                </div>
              </div>

              <button
                onClick={() => setShowUpgradeModal(true)}
                className="w-full bg-gradient-to-r from-accent-primary to-purple-600 hover:from-accent-primary/90 hover:to-purple-600/90 text-white py-3 px-6 rounded-lg font-medium transition-all transform hover:scale-[1.02]"
              >
                <div className="flex items-center justify-center space-x-2">
                  <StarIcon className="w-5 h-5" />
                  <span>プロプランにアップグレード</span>
                </div>
              </button>
            </div>
          ) : (
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-accent-primary rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-xl font-bold text-text-primary flex items-center">
                    <StarIcon className="w-6 h-6 text-accent-primary mr-2" />
                    プロプラン
                  </h4>
                  <p className="text-text-secondary">すべての機能を無制限でご利用いただけます</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-text-primary">¥{subscription.amount?.toLocaleString()}</div>
                  <div className="text-sm text-text-secondary">/月</div>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  無制限のウォッチリスト
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  AI株価予測機能
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  高度なテクニカル分析
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  リアルタイム価格アラート
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                  <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
                  ポートフォリオ分析
                </div>
              </div>

              {subscription.next_billing_date && (
                <div className="mb-4 p-3 bg-white/50 rounded-lg">
                  <p className="text-sm text-text-secondary">
                    次回更新日: {new Date(subscription.next_billing_date).toLocaleDateString('ja-JP')}
                  </p>
                </div>
              )}

              <button
                onClick={handleManageSubscription}
                className="w-full border border-accent-primary text-accent-primary py-2 px-4 rounded-lg font-medium hover:bg-accent-primary/5 transition-colors"
              >
                サブスクリプションを管理
              </button>
            </div>
          )}
        </div>

        {/* 支払い方法 */}
        {subscription.plan === 'pro' && (
          <div className="border-b border-border-primary pb-6">
            <h3 className="text-lg font-medium text-text-primary mb-4">お支払い方法</h3>
            
            {paymentMethods.length > 0 ? (
              <div className="space-y-3">
                {paymentMethods.map((method) => (
                  <div key={method.id} className="flex items-center justify-between p-4 bg-surface-background rounded-lg border border-border-primary">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <CreditCardIcon className="w-5 h-5 text-gray-600" />
                      </div>
                      <div>
                        <div className="font-medium text-text-primary">
                          {getCardBrand(method.brand)} •••• {method.last4}
                        </div>
                        <div className="text-sm text-text-secondary">
                          有効期限: {method.exp_month.toString().padStart(2, '0')}/{method.exp_year}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {method.is_default && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          デフォルト
                        </span>
                      )}
                      <button className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium">
                        編集
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <CreditCardIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-text-secondary">支払い方法が登録されていません</p>
              </div>
            )}

            <div className="mt-4">
              <button
                onClick={handleManageSubscription}
                className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium"
              >
                + 支払い方法を追加
              </button>
            </div>
          </div>
        )}

        {/* 請求履歴 */}
        {subscription.plan === 'pro' && billingHistory.length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-text-primary mb-4">請求履歴</h3>
            
            <div className="bg-surface-background rounded-lg border border-border-primary overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-border-primary">
                    <tr>
                      <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">日付</th>
                      <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">内容</th>
                      <th className="text-right px-4 py-3 text-sm font-medium text-text-secondary">金額</th>
                      <th className="text-center px-4 py-3 text-sm font-medium text-text-secondary">状態</th>
                      <th className="text-center px-4 py-3 text-sm font-medium text-text-secondary">請求書</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-primary">
                    {billingHistory.map((item) => (
                      <tr key={item.id} className="hover:bg-surface-elevated/50">
                        <td className="px-4 py-3 text-sm text-text-primary">
                          {new Date(item.date).toLocaleDateString('ja-JP')}
                        </td>
                        <td className="px-4 py-3 text-sm text-text-primary">
                          {item.description}
                        </td>
                        <td className="px-4 py-3 text-sm text-text-primary text-right font-mono">
                          ¥{item.amount.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-center">
                          {getStatusBadge(item.status)}
                        </td>
                        <td className="px-4 py-3 text-center">
                          {item.invoice_url && (
                            <button
                              onClick={() => window.open(item.invoice_url, '_blank')}
                              className="text-accent-primary hover:text-accent-primary/80 p-1"
                              title="請求書をダウンロード"
                            >
                              <DocumentArrowDownIcon className="w-4 h-4" />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-4 text-center">
              <button
                onClick={handleManageSubscription}
                className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium"
              >
                すべての請求履歴を見る
              </button>
            </div>
          </div>
        )}
      </div>

      {/* アップグレードモーダル */}
      {showUpgradeModal && (
        <UpgradeModal 
          onClose={() => setShowUpgradeModal(false)}
          onUpgrade={handleUpgrade}
          isProcessing={isProcessing}
        />
      )}
    </div>
  );
}

interface UpgradeModalProps {
  onClose: () => void;
  onUpgrade: () => void;
  isProcessing: boolean;
}

function UpgradeModal({ onClose, onUpgrade, isProcessing }: UpgradeModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-xl shadow-2xl max-w-lg w-full border border-border-primary">
        <div className="p-6">
          <div className="text-center mb-6">
            <div className="p-3 bg-gradient-to-r from-accent-primary/10 to-purple-600/10 rounded-full inline-flex mb-4">
              <StarIcon className="w-8 h-8 text-accent-primary" />
            </div>
            <h3 className="text-2xl font-bold text-text-primary mb-2">
              プロプランにアップグレード
            </h3>
            <p className="text-text-secondary">
              すべての機能を解放して、投資分析を次のレベルへ
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
            <div className="text-center mb-4">
              <div className="text-3xl font-bold text-text-primary">¥2,980</div>
              <div className="text-text-secondary">月額（税込）</div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">無制限のウォッチリスト</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">AI株価予測＆分析レポート</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">リアルタイム価格アラート</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">高度なテクニカル分析ツール</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">ポートフォリオ管理＆最適化</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckIcon className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-text-primary">データエクスポート機能</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={onUpgrade}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-accent-primary to-purple-600 hover:from-accent-primary/90 hover:to-purple-600/90 text-white py-3 px-6 rounded-lg font-medium transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isProcessing ? 'アップグレード中...' : '今すぐアップグレード'}
            </button>
            
            <button
              onClick={onClose}
              disabled={isProcessing}
              className="w-full border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
            >
              後で決める
            </button>
          </div>

          <div className="mt-4 text-center">
            <p className="text-xs text-text-secondary">
              いつでもキャンセル可能 • 初回7日間返金保証
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}