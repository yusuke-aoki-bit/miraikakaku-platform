'use client';

import { useState } from 'react';

interface SocialLoginsProps {
  mode: 'register' | 'login';
  redirectTo?: string;
  onSuccess?: () => void;
}

export default function SocialLogins({ mode, redirectTo, onSuccess }: SocialLoginsProps) {
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const actionText = mode === 'register' ? '登録' : 'ログイン';

  const handleSocialAuth = async (provider: string) => {
    setIsLoading(provider);
    try {
      // TODO: 実際のソーシャルログイン実装
      // 例: OAuth2フローを開始
      const authUrl = `/api/auth/${provider}${redirectTo ? `?redirect=${encodeURIComponent(redirectTo)}` : ''}`;
      window.location.href = authUrl;
    } catch (error) {
      console.error(`${provider} auth failed:`, error);
      setIsLoading(null);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* 区切り線 */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border-primary"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-surface-background text-text-secondary">または</span>
        </div>
      </div>

      {/* ソーシャルログインボタン */}
      <div className="space-y-3">
        {/* Google */}
        <button
          onClick={() => handleSocialAuth('google')}
          disabled={isLoading !== null}
          className="w-full flex items-center justify-center px-4 py-3 border border-border-primary rounded-lg bg-white hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading === 'google' ? (
            <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin mr-3" />
          ) : (
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
          )}
          <span className="text-gray-700 font-medium">
            Googleで{actionText}
          </span>
        </button>

        {/* Twitter/X */}
        <button
          onClick={() => handleSocialAuth('twitter')}
          disabled={isLoading !== null}
          className="w-full flex items-center justify-center px-4 py-3 border border-border-primary rounded-lg bg-black hover:bg-gray-900 transition-colors text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading === 'twitter' ? (
            <div className="w-5 h-5 border-2 border-gray-300 border-t-white rounded-full animate-spin mr-3" />
          ) : (
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          )}
          <span className="font-medium">
            X (旧Twitter)で{actionText}
          </span>
        </button>

        {/* LINE (日本向け) */}
        <button
          onClick={() => handleSocialAuth('line')}
          disabled={isLoading !== null}
          className="w-full flex items-center justify-center px-4 py-3 border border-border-primary rounded-lg bg-green-500 hover:bg-green-600 transition-colors text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading === 'line' ? (
            <div className="w-5 h-5 border-2 border-gray-300 border-t-white rounded-full animate-spin mr-3" />
          ) : (
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.477 2 2 5.64 2 10.24c0 4.01 3.589 7.36 8.4 8.04l-1.58 5.76L15.6 19.2c4.811-.68 8.4-4.03 8.4-8.04C24 5.64 19.523 2 12 2zm-5.6 11.2h-1.6v-4.8h1.6v4.8zm2.4 0h-1.6v-4.8h1.6v4.8zm2.4 0h-1.6v-4.8h1.6v4.8zm4-1.6h-2.4v1.6h-1.6v-4.8h4v3.2z"/>
            </svg>
          )}
          <span className="font-medium">
            LINEで{actionText}
          </span>
        </button>
      </div>

      {/* 注意書き */}
      <div className="mt-4 text-center">
        <p className="text-xs text-text-secondary">
          ソーシャル{actionText}を使用すると、
          <a href="/terms" className="text-accent-primary hover:underline" target="_blank">
            利用規約
          </a>
          と
          <a href="/privacy" className="text-accent-primary hover:underline" target="_blank">
            プライバシーポリシー
          </a>
          に同意したものとみなされます。
        </p>
      </div>
    </div>
  );
}