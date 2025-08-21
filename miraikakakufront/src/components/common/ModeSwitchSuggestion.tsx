'use client';

import { useState, useEffect } from 'react';
import { useUserModeStore } from '@/store/userModeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  X, 
  ArrowRight, 
  BookOpen, 
  Zap,
  Monitor,
  Smartphone,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface ModeSwitchSuggestionProps {
  className?: string;
}

export default function ModeSwitchSuggestion({ className = '' }: ModeSwitchSuggestionProps) {
  const { 
    config, 
    metrics, 
    shouldSuggestModeSwitch, 
    setMode, 
    updateConfig 
  } = useUserModeStore();
  
  const [showSuggestion, setShowSuggestion] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);

  useEffect(() => {
    if (!dismissed && shouldSuggestModeSwitch()) {
      const timer = setTimeout(() => {
        setShowSuggestion(true);
      }, 2000); // Show after 2 seconds delay

      return () => clearTimeout(timer);
    }
  }, [dismissed, shouldSuggestModeSwitch]);

  const handleAccept = async () => {
    setIsAccepting(true);
    
    // Smooth transition
    setTimeout(() => {
      const newMode = config.mode === 'light' ? 'pro' : 'light';
      setMode(newMode);
      setShowSuggestion(false);
      setDismissed(true);
      setIsAccepting(false);
    }, 500);
  };

  const handleDismiss = () => {
    setShowSuggestion(false);
    setDismissed(true);
  };

  const handleNeverShow = () => {
    updateConfig({ autoSuggestModeSwitch: false });
    setShowSuggestion(false);
    setDismissed(true);
  };

  const getSuggestionContent = () => {
    if (config.mode === 'light') {
      return {
        title: 'プロモードをお試しください',
        description: 'あなたの使用パターンから、より高度な機能がお役に立てそうです',
        benefits: [
          { icon: TrendingUp, text: 'リアルタイム高度分析' },
          { icon: Zap, text: 'キーボードショートカット' },
          { icon: Monitor, text: 'マルチパネルレイアウト' },
        ],
        reason: getProModeReason(),
        buttonText: 'プロモードに切り替え',
        icon: Monitor,
        gradient: 'from-brand-primary to-brand-primary-light'
      };
    } else {
      return {
        title: 'ライトモードをお試しください',
        description: 'シンプルなインターフェースで、より快適にご利用いただけます',
        benefits: [
          { icon: Smartphone, text: 'シンプルなUI' },
          { icon: BookOpen, text: '学習支援機能' },
          { icon: CheckCircle, text: '使いやすい操作' },
        ],
        reason: 'より直感的なインターフェースで効率的にお使いいただけます',
        buttonText: 'ライトモードに切り替え',
        icon: Smartphone,
        gradient: 'from-status-success to-status-success-light'
      };
    }
  };

  const getProModeReason = () => {
    if (metrics.advancedFeaturesUsed.length >= 3) {
      return `${metrics.advancedFeaturesUsed.length}個の高度な機能をご利用されています`;
    }
    if (metrics.sessionsCount >= 5) {
      return `${metrics.sessionsCount}回以上のご利用実績があります`;
    }
    if (metrics.averageSessionDuration >= 300) {
      return '長時間のセッションでのご利用が多くなっています';
    }
    return 'ご利用パターンから判断しました';
  };

  if (!showSuggestion) return null;

  const content = getSuggestionContent();
  const IconComponent = content.icon;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: -20 }}
        className={`fixed bottom-6 right-6 z-50 ${className}`}
      >
        <div className="bg-surface-card border border-border-default rounded-2xl shadow-2xl p-6 max-w-sm backdrop-blur-lg">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className={`p-2 rounded-xl bg-gradient-to-r ${content.gradient} bg-opacity-10`}>
              <IconComponent 
                size={24} 
                className={`bg-gradient-to-r ${content.gradient} bg-clip-text text-transparent`}
              />
            </div>
            <button
              onClick={handleDismiss}
              className="text-text-tertiary hover:text-text-primary transition-colors p-1"
            >
              <X size={16} />
            </button>
          </div>

          {/* Content */}
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-text-primary text-lg mb-2">
                {content.title}
              </h3>
              <p className="text-text-secondary text-sm leading-relaxed">
                {content.description}
              </p>
              <div className="flex items-center space-x-1 mt-2">
                <AlertCircle size={14} className="text-brand-primary" />
                <span className="text-xs text-text-tertiary">
                  {content.reason}
                </span>
              </div>
            </div>

            {/* Benefits */}
            <div className="space-y-2">
              {content.benefits.map((benefit, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center space-x-3"
                >
                  <benefit.icon size={16} className="text-brand-primary flex-shrink-0" />
                  <span className="text-text-secondary text-sm">
                    {benefit.text}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex space-x-2 pt-2">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleAccept}
                disabled={isAccepting}
                className={`
                  flex-1 flex items-center justify-center space-x-2 py-3 px-4 
                  bg-gradient-to-r ${content.gradient} text-white font-medium rounded-xl
                  transition-all duration-200 hover:shadow-lg
                  ${isAccepting ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                {isAccepting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span className="text-sm">{content.buttonText}</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </motion.button>
            </div>

            {/* Dismiss Options */}
            <div className="flex justify-between pt-2 border-t border-border-default">
              <button
                onClick={handleNeverShow}
                className="text-xs text-text-tertiary hover:text-text-secondary transition-colors"
              >
                今後表示しない
              </button>
              <button
                onClick={handleDismiss}
                className="text-xs text-text-tertiary hover:text-text-secondary transition-colors"
              >
                後で決める
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}