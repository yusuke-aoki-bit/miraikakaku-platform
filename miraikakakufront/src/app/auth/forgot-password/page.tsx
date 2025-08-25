'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm';

export default function ForgotPasswordPage() {
  const [emailSent, setEmailSent] = useState(false);
  const [sentEmail, setSentEmail] = useState('');

  const handleEmailSent = (email: string) => {
    setEmailSent(true);
    setSentEmail(email);
  };

  const handleBackToForm = () => {
    setEmailSent(false);
    setSentEmail('');
  };

  return (
    <div className="min-h-screen bg-surface-background flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        {/* ヘッダー */}
        <div className="text-center">
          <Link 
            href="/auth/login"
            className="inline-flex items-center text-accent-primary hover:text-accent-primary/80 transition-colors mb-6"
          >
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            ログインに戻る
          </Link>
          <h1 className="text-2xl font-bold text-text-primary mb-2">
            パスワードを忘れた場合
          </h1>
          <p className="text-text-secondary">
            {emailSent 
              ? 'パスワード再設定のご案内を送信しました' 
              : 'ご登録のメールアドレスにパスワード再設定のご案内を送信します'
            }
          </p>
        </div>

        {emailSent ? (
          /* 送信完了画面 */
          <div className="bg-surface-elevated rounded-lg border border-border-primary p-6 text-center space-y-4">
            <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-lg font-semibold text-text-primary">
                送信完了
              </h2>
              <p className="text-text-secondary text-sm">
                <span className="font-medium text-accent-primary">{sentEmail}</span>
                <br />
                にパスワード再設定のご案内を送信しました。
              </p>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 text-left">
              <h3 className="text-sm font-medium text-blue-600 mb-2">次のステップ</h3>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• メールボックスをご確認ください</li>
                <li>• 迷惑メールフォルダもご確認ください</li>
                <li>• メール内のリンクをクリックしてパスワードを再設定してください</li>
                <li>• リンクの有効期限は24時間です</li>
              </ul>
            </div>

            <div className="space-y-3">
              <button
                onClick={handleBackToForm}
                className="w-full text-accent-primary hover:text-accent-primary/80 transition-colors text-sm"
              >
                別のメールアドレスで再送信する
              </button>
              
              <Link
                href="/auth/login"
                className="block w-full text-center border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                ログインページに戻る
              </Link>
            </div>

            <div className="text-xs text-text-secondary">
              <p>メールが届かない場合は、</p>
              <Link href="/contact" className="text-accent-primary hover:underline">
                サポートまでお問い合わせ
              </Link>
              <span>ください。</span>
            </div>
          </div>
        ) : (
          /* パスワード再設定申請フォーム */
          <ForgotPasswordForm onEmailSent={handleEmailSent} />
        )}
      </div>
    </div>
  );
}