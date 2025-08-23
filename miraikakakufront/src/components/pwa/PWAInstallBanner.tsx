'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePWAInstallBanner } from '@/hooks/usePWA';
import { Download, X, Smartphone, Monitor } from 'lucide-react';
import { useResponsive } from '@/hooks/useResponsive';

export default function PWAInstallBanner() {
  const { showBanner, handleInstall, handleDismiss } = usePWAInstallBanner();
  const { isMobile } = useResponsive();

  if (!showBanner) return null;

  const deviceIcon = isMobile ? Smartphone : Monitor;
  const DeviceIcon = deviceIcon;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50"
      >
        <div className="bg-surface-card border border-border-default rounded-2xl shadow-2xl backdrop-blur-lg overflow-hidden">
          {/* Header */}
          <div className="relative">
            <div className="bg-gradient-to-r from-brand-primary to-brand-primary-light p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <DeviceIcon size={24} className="text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">
                      Miraikakaku をインストール
                    </h3>
                    <p className="text-white/80 text-sm">
                      {isMobile ? 'ホーム画面に追加' : 'デスクトップアプリとして使用'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleDismiss}
                  className="p-2 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <div className="space-y-3 mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-status-success/20 rounded-lg flex items-center justify-center">
                  <span className="text-status-success text-lg">⚡</span>
                </div>
                <div>
                  <h4 className="font-medium text-text-primary text-sm">高速アクセス</h4>
                  <p className="text-text-secondary text-xs">オフラインでもデータにアクセス可能</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-brand-primary/20 rounded-lg flex items-center justify-center">
                  <span className="text-brand-primary text-lg">🔔</span>
                </div>
                <div>
                  <h4 className="font-medium text-text-primary text-sm">リアルタイム通知</h4>
                  <p className="text-text-secondary text-xs">重要な市場変動をお知らせ</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-status-warning/20 rounded-lg flex items-center justify-center">
                  <span className="text-status-warning text-lg">🏠</span>
                </div>
                <div>
                  <h4 className="font-medium text-text-primary text-sm">ネイティブ体験</h4>
                  <p className="text-text-secondary text-xs">
                    {isMobile ? 'アプリのような操作感' : 'デスクトップアプリとして起動'}
                  </p>
                </div>
              </div>
            </div>

            {/* Install Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleInstall}
              className="w-full flex items-center justify-center space-x-2 bg-brand-primary text-white py-3 px-4 rounded-xl font-medium hover:bg-brand-primary-hover transition-colors"
            >
              <Download size={18} />
              <span>今すぐインストール</span>
            </motion.button>

            {/* Dismiss Link */}
            <div className="text-center mt-3">
              <button
                onClick={handleDismiss}
                className="text-text-tertiary text-xs hover:text-text-secondary transition-colors"
              >
                後で通知する
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

// Install prompt for desktop
export function PWAInstallPrompt() {
  const { showBanner, handleInstall, handleDismiss } = usePWAInstallBanner();
  const { isDesktop, isUltrawide } = useResponsive();

  if (!showBanner || (!isDesktop && !isUltrawide)) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="fixed inset-0 bg-surface-overlay backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ y: 20 }}
          animate={{ y: 0 }}
          className="bg-surface-card border border-border-default rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-brand-primary to-brand-primary-light p-6 text-center">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Monitor size={32} className="text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Miraikakaku をインストール
            </h2>
            <p className="text-white/80">
              デスクトップアプリとしてより快適にご利用いただけます
            </p>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="space-y-4 mb-6">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-status-success/20 rounded-xl flex items-center justify-center">
                  <span className="text-status-success text-xl">⚡</span>
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">高速起動</h3>
                  <p className="text-text-secondary text-sm">ブラウザより高速にアクセス</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-brand-primary/20 rounded-xl flex items-center justify-center">
                  <span className="text-brand-primary text-xl">🔒</span>
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">セキュア</h3>
                  <p className="text-text-secondary text-sm">独立したアプリ環境で安全</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-status-warning/20 rounded-xl flex items-center justify-center">
                  <span className="text-status-warning text-xl">📊</span>
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">オフライン対応</h3>
                  <p className="text-text-secondary text-sm">ネット接続なしでもデータ閲覧可能</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleInstall}
                className="flex-1 flex items-center justify-center space-x-2 bg-brand-primary text-white py-3 px-4 rounded-xl font-medium hover:bg-brand-primary-hover transition-colors"
              >
                <Download size={18} />
                <span>インストール</span>
              </motion.button>

              <button
                onClick={handleDismiss}
                className="px-6 py-3 border border-border-default text-text-secondary rounded-xl font-medium hover:text-text-primary hover:border-border-strong transition-colors"
              >
                後で
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}