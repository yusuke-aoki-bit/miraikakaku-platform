'use client';

import { useState } from 'react';
import { EnvelopeIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api-client';

interface ForgotPasswordFormProps {
  onEmailSent: (email: string) => void;
}

export default function ForgotPasswordForm({ onEmailSent }: ForgotPasswordFormProps) {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('メールアドレスを入力してください。');
      return;
    }

    if (!validateEmail(email)) {
      setError('有効なメールアドレスを入力してください。');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await apiClient.sendPasswordResetLink(email);
      
      if (response.status === 'success') {
        onEmailSent(email);
      } else {
        setError(response.message || 'エラーが発生しました。しばらく時間を置いてから再度お試しください。');
      }
    } catch (error) {
      console.error('Password reset request failed:', error);
      setError('ネットワークエラーが発生しました。インターネット接続をご確認の上、再度お試しください。');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* メールアドレス入力 */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
            メールアドレス <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <EnvelopeIcon className="h-5 w-5 text-text-secondary" />
            </div>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="example@email.com"
              className="w-full pl-10 pr-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              disabled={isSubmitting}
              autoComplete="email"
            />
          </div>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className="flex items-start space-x-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* 送信ボタン */}
        <button
          type="submit"
          disabled={isSubmitting || !email.trim()}
          className="w-full bg-accent-primary hover:bg-accent-primary/90 disabled:bg-accent-primary/50 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              送信中...
            </>
          ) : (
            'パスワード再設定のご案内を送信'
          )}
        </button>

        {/* 注意事項 */}
        <div className="bg-gray-500/5 border border-gray-500/10 rounded-lg p-4">
          <h3 className="text-sm font-medium text-text-primary mb-2">ご注意事項</h3>
          <ul className="text-xs text-text-secondary space-y-1">
            <li>• ご登録のメールアドレスにパスワード再設定用のリンクを送信します</li>
            <li>• リンクの有効期限は24時間です</li>
            <li>• メールが届かない場合は迷惑メールフォルダもご確認ください</li>
            <li>• 存在しないメールアドレスでもセキュリティ上、同様の画面が表示されます</li>
          </ul>
        </div>

        {/* セキュリティ情報 */}
        <div className="text-center text-xs text-text-secondary">
          <p>このページはSSL暗号化により保護されています</p>
        </div>
      </form>
    </div>
  );
}