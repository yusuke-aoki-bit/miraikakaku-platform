'use client';

import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
  className?: string;
}

export default function ErrorMessage({ error, onRetry, className = '' }: ErrorMessageProps) {
  const { t } = useTranslation('common'
  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-center text-center">
        <div>
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            {t('errors.somethingWentWrong', 'エラーが発生しました')}
          </h3>
          <p className="text-red-700 mb-4">
            {error}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              {t('errors.tryAgain', '再試行')}
            </button>
          )}
        </div>
      </div>
    </div>
}

export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  const { t } = useTranslation('common'
  return (
    <ErrorMessage
      error={t('errors.networkError', 'サーバーに接続できません。インターネット接続を確認して再度お試しください。')}
      onRetry={onRetry}
    />
}

export function NotFoundError({ stockSymbol }: { stockSymbol: string }) {
  const { t } = useTranslation('common'
  return (
    <ErrorMessage
      error={t('errors.stockNotFound', '株式「{{symbol}}」が見つかりません。シンボルを確認して再度お試しください。', { symbol: stockSymbol })}
    />
}