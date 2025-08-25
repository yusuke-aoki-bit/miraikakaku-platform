'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeftIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import ResetPasswordForm from '@/components/auth/ResetPasswordForm';
import { apiClient } from '@/lib/api-client';

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(true);
  const [validationError, setValidationError] = useState('');
  const [resetComplete, setResetComplete] = useState(false);

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    
    if (!tokenParam) {
      setValidationError('無効なリンクです。パスワード再設定のご案内メールから正しいリンクをクリックしてください。');
      setIsValidating(false);
      return;
    }

    validateToken(tokenParam);
  }, [searchParams]);

  const validateToken = async (tokenParam: string) => {
    try {
      const response = await apiClient.validatePasswordResetToken(tokenParam);
      
      if (response.success) {
        setToken(tokenParam);
      } else {
        setValidationError(response.message || 'パスワード再設定トークンが無効または期限切れです。');
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      setValidationError('サーバーエラーが発生しました。しばらく時間を置いてから再度お試しください。');
    } finally {
      setIsValidating(false);
    }
  };

  const handlePasswordReset = () => {
    setResetComplete(true);
    setTimeout(() => {
      router.push('/auth/login');
    }, 3000);
  };

  if (isValidating) {
    return (
      <div className="min-h-screen bg-surface-background flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary mx-auto mb-4"></div>
            <p className="text-text-primary">リンクを確認しています...</p>
          </div>
        </div>
      </div>
    );
  }

  if (validationError) {
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
              パスワード再設定
            </h1>
          </div>

          {/* エラー表示 */}
          <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
            <div className="flex items-start space-x-3">
              <ExclamationCircleIcon className="h-6 w-6 text-red-500 flex-shrink-0 mt-1" />
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-red-600">
                  リンクが無効です
                </h2>
                <p className="text-text-secondary text-sm">
                  {validationError}
                </p>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <Link
                href="/auth/forgot-password"
                className="block w-full text-center bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                パスワード再設定を再申請
              </Link>
              
              <Link
                href="/auth/login"
                className="block w-full text-center border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                ログインページに戻る
              </Link>
            </div>

            <div className="mt-4 text-xs text-text-secondary">
              <p>問題が解決しない場合は、</p>
              <Link href="/contact" className="text-accent-primary hover:underline">
                サポートまでお問い合わせ
              </Link>
              <span>ください。</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (resetComplete) {
    return (
      <div className="min-h-screen bg-surface-background flex items-center justify-center p-4">
        <div className="max-w-md w-full space-y-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              パスワード再設定完了
            </h1>
          </div>

          <div className="bg-surface-elevated rounded-lg border border-border-primary p-6 text-center space-y-4">
            <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-lg font-semibold text-text-primary">
                設定完了
              </h2>
              <p className="text-text-secondary text-sm">
                パスワードの再設定が完了しました。
                <br />
                新しいパスワードでログインしてください。
              </p>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <p className="text-sm text-blue-600">
                3秒後に自動的にログインページへ移動します...
              </p>
            </div>

            <Link
              href="/auth/login"
              className="block w-full bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors"
            >
              今すぐログインページへ
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
            新しいパスワードを設定
          </h1>
          <p className="text-text-secondary">
            新しいパスワードを入力してください。
          </p>
        </div>

        {/* パスワード再設定フォーム */}
        {token && (
          <ResetPasswordForm 
            token={token} 
            onPasswordReset={handlePasswordReset} 
          />
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-surface-background flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"></div>
      </div>
    }>
      <ResetPasswordContent />
    </Suspense>
  );
}