'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2'
    md: 'w-8 h-8 border-2'
    lg: 'w-12 h-12 border-3'
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div
        className={`${sizeClasses[size]} rounded-full animate-spin`}
        style={{
          borderColor: 'rgb(var(--theme-border))'
          borderTopColor: 'rgb(var(--theme-primary))'
        }}
      ></div>
    </div>
}

export function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <LoadingSpinner size="lg" />
      <p className="theme-text-secondary">株式データを読み込み中...</p>
    </div>
}

export function ChartLoader() {
  return (
    <div className="h-96 w-full rounded-lg flex items-center justify-center theme-card">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="theme-text-secondary">チャートを読み込み中...</p>
      </div>
    </div>
}