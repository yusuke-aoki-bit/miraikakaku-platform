'use client';

import { Brain, TrendingUp } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  type?: 'default' | 'ai' | 'chart';
}

export default function LoadingSpinner({
  message = "読み込み中...",
  size = 'md',
  type = 'default'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const containerClasses = {
    sm: 'p-4',
    md: 'p-8',
    lg: 'p-12'
  };

  const renderSpinner = () => {
    if (type === 'ai') {
      return (
        <div className="relative">
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-brand-accent to-brand-secondary animate-spin opacity-75"></div>
          <div className="relative bg-dark-card rounded-full p-2">
            <Brain className={`${sizeClasses[size]} text-brand-accent animate-pulse`} />
          </div>
        </div>
      );
    }
    
    if (type === 'chart') {
      return (
        <div className="relative">
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-brand-primary to-brand-secondary animate-spin opacity-75"></div>
          <div className="relative bg-dark-card rounded-full p-2">
            <TrendingUp className={`${sizeClasses[size]} text-brand-primary animate-pulse`} />
          </div>
        </div>
      );
    }

    return (
      <div className="relative">
        {/* Outer spinning ring with brand colors */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-brand-primary border-r-brand-secondary animate-spin"></div>
        {/* Inner pulsing circle */}
        <div className={`absolute inset-1 rounded-full bg-dark-card animate-pulse-slow`}></div>
        {/* Central icon or logo placeholder if needed */}
        <div className={`${sizeClasses[size]} rounded-full flex items-center justify-center`}>
          {/* Optional: Add a small brand logo or icon here */}
        </div>
      </div>
    );
  };

  return (
    <div className={`flex flex-col items-center justify-center ${containerClasses[size]} animate-fade-in`}>
      {renderSpinner()}
      {message && (
        <p className="mt-4 text-text-medium text-center animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}
