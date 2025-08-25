'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import RegistrationForm from '@/components/auth/RegistrationForm';
import SocialLogins from '@/components/auth/SocialLogins';

function RegisterContent() {
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect');

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-background to-surface-elevated py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            無料で始める
          </h1>
          <p className="text-text-secondary">
            アカウントを作成して、すべての機能をご利用ください
          </p>
        </div>

        <div className="bg-surface-elevated rounded-xl shadow-lg p-6 border border-border-primary">
          <RegistrationForm 
            redirectTo={redirectTo || undefined} 
          />
          
          <SocialLogins 
            mode="register"
            redirectTo={redirectTo || undefined}
          />
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-text-secondary">
            登録することで、より詳細な市場分析、
            <br />
            個人向けポートフォリオ管理、AI予測などの
            <br />
            プレミアム機能をご利用いただけます。
          </p>
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-surface-background to-surface-elevated flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
      </div>
    }>
      <RegisterContent />
    </Suspense>
  );
}