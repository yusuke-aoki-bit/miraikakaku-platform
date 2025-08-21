'use client';

import { useState, useEffect } from 'react';
import { useUserModeStore } from '@/store/userModeStore';
import { UserMode } from '@/types/user-modes';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Zap, 
  Settings, 
  TrendingUp, 
  BookOpen, 
  Monitor,
  Smartphone,
  Gauge
} from 'lucide-react';

interface UserModeToggleProps {
  className?: string;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function UserModeToggle({ 
  className = '', 
  showLabels = true,
  size = 'md' 
}: UserModeToggleProps) {
  const { config, toggleMode, startModeTransition, completeModeTransition, isTransitioning } = useUserModeStore();
  const [showTooltip, setShowTooltip] = useState(false);

  const handleToggle = async () => {
    startModeTransition();
    
    // Add a slight delay for smooth transition effect
    setTimeout(() => {
      toggleMode();
      setTimeout(() => {
        completeModeTransition();
      }, 300);
    }, 150);
  };

  const sizeClasses = {
    sm: 'h-8 w-16',
    md: 'h-10 w-20',
    lg: 'h-12 w-24'
  };

  const iconSizes = {
    sm: 12,
    md: 16,
    lg: 20
  };

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className={`relative ${className}`}>
      {/* Mode Toggle Switch */}
      <div className="flex items-center space-x-3">
        {showLabels && (
          <div className={`flex items-center space-x-2 ${textSizes[size]}`}>
            <User size={iconSizes[size]} className="text-text-secondary" />
            <span className="text-text-secondary font-medium">
              {config.mode === 'light' ? 'ライト' : 'プロ'}モード
            </span>
          </div>
        )}

        {/* Toggle Switch */}
        <button
          onClick={handleToggle}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          disabled={isTransitioning}
          className={`
            relative ${sizeClasses[size]} bg-surface-card border-2 border-border-default 
            rounded-full transition-all duration-300 ease-in-out
            hover:border-brand-primary-light focus:outline-none focus:ring-2 
            focus:ring-brand-primary focus:ring-offset-2 focus:ring-offset-surface-background
            ${isTransitioning ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${config.mode === 'pro' ? 'bg-gradient-to-r from-brand-primary to-brand-primary-light' : ''}
          `}
          aria-label={`現在のモード: ${config.mode === 'light' ? 'ライト' : 'プロ'}モード。クリックで切り替え`}
        >
          <motion.div
            layout
            className={`
              absolute top-0.5 left-0.5 w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10
              bg-white rounded-full shadow-lg flex items-center justify-center
              ${config.mode === 'pro' ? 'bg-surface-background' : 'bg-white'}
            `}
            animate={{
              x: config.mode === 'pro' ? (size === 'sm' ? 28 : size === 'md' ? 36 : 44) : 0,
            }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          >
            <AnimatePresence mode="wait">
              {config.mode === 'light' ? (
                <motion.div
                  key="light"
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 180 }}
                  transition={{ duration: 0.2 }}
                >
                  <Smartphone 
                    size={iconSizes[size]} 
                    className="text-brand-primary" 
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="pro"
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 180 }}
                  transition={{ duration: 0.2 }}
                >
                  <Monitor 
                    size={iconSizes[size]} 
                    className="text-white" 
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Loading overlay during transition */}
          <AnimatePresence>
            {isTransitioning && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-surface-background/80 rounded-full flex items-center justify-center"
              >
                <div className="w-4 h-4 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
              </motion.div>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.8 }}
            className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 z-50"
          >
            <div className="bg-surface-elevated border border-border-default rounded-lg p-3 shadow-lg max-w-xs">
              <div className="space-y-2">
                <div className="font-medium text-text-primary text-sm">
                  {config.mode === 'light' ? 'ライトモード' : 'プロモード'}
                </div>
                
                {config.mode === 'light' ? (
                  <div className="text-text-secondary text-xs space-y-1">
                    <div className="flex items-center space-x-2">
                      <BookOpen size={12} />
                      <span>学習支援ツールチップ表示</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Smartphone size={12} />
                      <span>シンプルなインターフェース</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-text-secondary text-xs space-y-1">
                    <div className="flex items-center space-x-2">
                      <TrendingUp size={12} />
                      <span>高度な分析ツール</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Gauge size={12} />
                      <span>マルチパネルレイアウト</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Zap size={12} />
                      <span>ホットキー対応</span>
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-text-tertiary border-t border-border-default pt-2">
                  クリックで{config.mode === 'light' ? 'プロ' : 'ライト'}モードに切り替え
                </div>
              </div>
              
              {/* Tooltip Arrow */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2">
                <div className="w-2 h-2 bg-surface-elevated border-r border-b border-border-default transform rotate-45" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}