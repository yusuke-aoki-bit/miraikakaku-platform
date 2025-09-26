'use client';

import React from 'react';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
  fullScreen?: boolean;
  className?: string;
}

export default function Loading({
  size = 'medium',
  text = '読み込み中...',
  fullScreen = false,
  className = ''
}: LoadingProps) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  const textSizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  const containerClasses = fullScreen
    ? 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50'
    : 'flex items-center justify-center p-4';

  return (
    <div
      className={`${containerClasses} ${className}`}
      data-testid="loading"
      role="status"
      aria-label={text}
    >
      <div className="flex flex-col items-center space-y-3">
        <div className={`${sizeClasses[size]} relative`}>
          <div className="absolute inset-0 rounded-full border-2 border-cyan-200"></div>
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-500 animate-spin"></div>
        </div>
        {text && (
          <p className={`${textSizeClasses[size]} text-white/80 font-medium animate-pulse`}>
            {text}
          </p>
        )}
      </div>
    </div>
  );
}

// Inline loading spinner for buttons
export function InlineLoading({ size = 'small' }: { size?: 'small' | 'medium' }) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6'
  };

  return (
    <div
      className={`${sizeClasses[size]} relative`}
      data-testid="inline-loading"
      role="status"
      aria-label="処理中"
    >
      <div className="absolute inset-0 rounded-full border-2 border-white/30"></div>
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-white animate-spin"></div>
    </div>
  );
}

// Loading skeleton for content placeholders
export function LoadingSkeleton({
  lines = 3,
  className = ''
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-3 ${className}`} data-testid="loading-skeleton">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="animate-pulse bg-white/10 rounded-md h-4"
          style={{
            width: `${90 + Math.random() * 10}%`
          }}
        />
      ))}
    </div>
  );
}