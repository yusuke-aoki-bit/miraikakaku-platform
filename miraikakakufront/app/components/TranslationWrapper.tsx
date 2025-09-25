'use client';

import { useTranslation } from 'react-i18next';
import LoadingSpinner from './LoadingSpinner';

interface TranslationWrapperProps {
  children: React.ReactNode;
}

export default function TranslationWrapper({ children }: TranslationWrapperProps) {
  const { ready } = useTranslation(
  if (!ready) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: 'var(--yt-music-bg)' }}>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </div>
  }

  return <>{children}</>;
}