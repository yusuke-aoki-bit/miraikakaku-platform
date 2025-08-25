'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';
import SocialLogins from '@/components/auth/SocialLogins';

function LoginContent() {
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect');

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-background to-surface-elevated py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            ログイン
          </h1>
          <p className="text-text-secondary">
            アカウントにログインして続行
          </p>
        </div>

        <div className="bg-surface-elevated rounded-xl shadow-lg p-6 border border-border-primary">
          <LoginForm 
            redirectTo={redirectTo || undefined} 
          />
          
          <SocialLogins 
            mode="login"
            redirectTo={redirectTo || undefined}
          />
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-text-secondary">
            アカウントをお持ちでない方は{' '}
            <a 
              href={`/auth/register${redirectTo ? `?redirect=${encodeURIComponent(redirectTo)}` : ''}`}
              className="text-accent-primary hover:underline"
            >
              こちらから登録
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-surface-background to-surface-elevated flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}