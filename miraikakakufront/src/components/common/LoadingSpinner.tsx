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
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-spin opacity-75"></div>
          <div className="relative bg-black rounded-full p-2">
            <Brain className={`${sizeClasses[size]} text-purple-400 animate-pulse`} />
          </div>
        </div>
      );
    }
    
    if (type === 'chart') {
      return (
        <div className="relative">
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-red-500 to-pink-500 animate-spin opacity-75"></div>
          <div className="relative bg-black rounded-full p-2">
            <TrendingUp className={`${sizeClasses[size]} text-red-400 animate-pulse`} />
          </div>
        </div>
      );
    }

    return (
      <div className="relative">
        <div className="absolute inset-0 rounded-full border-2 border-gray-700"></div>
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-red-500 animate-spin"></div>
        <div className={`${sizeClasses[size]} rounded-full bg-gradient-to-r from-red-500/20 to-pink-500/20`}></div>
      </div>
    );
  };

  return (
    <div className={`flex flex-col items-center justify-center ${containerClasses[size]} animate-fade-in`}>
      {renderSpinner()}
      {message && (
        <p className="mt-4 text-gray-300 text-center animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}