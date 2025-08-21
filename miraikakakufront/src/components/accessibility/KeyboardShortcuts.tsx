'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Keyboard, X } from 'lucide-react';
import { useAccessibilityContext } from './AccessibilityProvider';

interface KeyboardShortcut {
  key: string;
  description: string;
  category: string;
  action?: () => void;
}

const KEYBOARD_SHORTCUTS: KeyboardShortcut[] = [
  // Navigation
  { key: 'Alt + H', description: 'ホームページに移動', category: 'ナビゲーション' },
  { key: 'Alt + D', description: 'ダッシュボードに移動', category: 'ナビゲーション' },
  { key: 'Alt + P', description: '予測ページに移動', category: 'ナビゲーション' },
  { key: 'Alt + W', description: 'ウォッチリストに移動', category: 'ナビゲーション' },
  { key: 'Alt + R', description: 'リアルタイムデータに移動', category: 'ナビゲーション' },
  
  // Search and Commands
  { key: 'Ctrl + K', description: 'コマンドパレットを開く', category: '検索・コマンド' },
  { key: 'Ctrl + /', description: '銘柄検索を開く', category: '検索・コマンド' },
  { key: 'Esc', description: 'モーダル・メニューを閉じる', category: '検索・コマンド' },
  
  // Accessibility
  { key: 'Alt + A', description: 'アクセシビリティ設定を開く', category: 'アクセシビリティ' },
  { key: 'Alt + ?', description: 'キーボードショートカット一覧を表示', category: 'アクセシビリティ' },
  { key: 'Tab', description: '次の要素に移動', category: 'アクセシビリティ' },
  { key: 'Shift + Tab', description: '前の要素に移動', category: 'アクセシビリティ' },
  
  // Data Actions
  { key: 'F5', description: 'データを更新', category: 'データ操作' },
  { key: 'Ctrl + R', description: 'ページを再読み込み', category: 'データ操作' },
  
  // Chart Controls
  { key: '1', description: '1日チャートに切り替え', category: 'チャート' },
  { key: '7', description: '1週間チャートに切り替え', category: 'チャート' },
  { key: '30', description: '1ヶ月チャートに切り替え', category: 'チャート' },
  { key: '+', description: 'チャートズームイン', category: 'チャート' },
  { key: '-', description: 'チャートズームアウト', category: 'チャート' }
];

export default function KeyboardShortcuts() {
  const [isOpen, setIsOpen] = useState(false);
  const { announce } = useAccessibilityContext();

  const handleKeyPress = useCallback((e: KeyboardEvent) => {
    // Alt + ? to open shortcuts
    if (e.altKey && e.key === '?') {
      e.preventDefault();
      setIsOpen(true);
      announce('キーボードショートカット一覧を開きました');
    }
    
    // Escape to close
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      setIsOpen(false);
      announce('キーボードショートカット一覧を閉じました');
    }
  }, [isOpen, announce]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  const groupedShortcuts = KEYBOARD_SHORTCUTS.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, KeyboardShortcut[]>);

  const closeModal = () => {
    setIsOpen(false);
    announce('キーボードショートカット一覧を閉じました');
  };

  return (
    <>
      {/* Help button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 w-12 h-12 bg-brand-primary text-white rounded-full shadow-lg hover:bg-brand-primary-hover transition-colors z-fixed flex items-center justify-center"
        aria-label="キーボードショートカット一覧を表示"
        title="キーボードショートカット (Alt + ?)"
      >
        <Keyboard size={20} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-surface-overlay backdrop-blur-sm z-modal flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-surface-card border border-border-default rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-modal="true"
              aria-labelledby="shortcuts-title"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-brand-primary to-brand-primary-light p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                      <Keyboard size={24} className="text-white" />
                    </div>
                    <div>
                      <h2 id="shortcuts-title" className="text-2xl font-bold text-white">
                        キーボードショートカット
                      </h2>
                      <p className="text-white/80">
                        効率的な操作のためのキーボードショートカット一覧
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={closeModal}
                    className="p-2 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                    aria-label="キーボードショートカット一覧を閉じる"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {Object.entries(groupedShortcuts).map(([category, shortcuts]) => (
                    <section key={category}>
                      <h3 className="text-lg font-semibold text-text-primary mb-4 pb-2 border-b border-border-default">
                        {category}
                      </h3>
                      <div className="space-y-3">
                        {shortcuts.map((shortcut, index) => (
                          <div 
                            key={index}
                            className="flex items-center justify-between p-3 bg-surface-hover rounded-lg"
                          >
                            <span className="text-text-primary">
                              {shortcut.description}
                            </span>
                            <kbd className="px-3 py-1 bg-surface-card border border-border-default rounded-md text-sm font-mono text-text-secondary">
                              {shortcut.key}
                            </kbd>
                          </div>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>

                {/* Tips */}
                <div className="mt-8 p-4 bg-brand-primary/10 rounded-xl">
                  <h4 className="font-semibold text-text-primary mb-2">
                    💡 使用方法のヒント
                  </h4>
                  <ul className="text-sm text-text-secondary space-y-1">
                    <li>• Tabキーで要素間を移動できます</li>
                    <li>• Enterキーまたはスペースキーでボタンを押せます</li>
                    <li>• 矢印キーでメニューやオプション間を移動できます</li>
                    <li>• Escキーでモーダルやメニューを閉じることができます</li>
                  </ul>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-border-default bg-surface-hover">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-text-secondary">
                    Alt + ? でいつでもこの一覧を表示できます
                  </p>
                  <button
                    onClick={closeModal}
                    className="px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-primary-hover transition-colors"
                  >
                    閉じる
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// Hook for keyboard shortcut management
export function useKeyboardShortcuts() {
  const handleGlobalShortcuts = useCallback((e: KeyboardEvent) => {
    // Navigation shortcuts
    if (e.altKey) {
      switch (e.key.toLowerCase()) {
        case 'h':
          e.preventDefault();
          window.location.href = '/';
          break;
        case 'd':
          e.preventDefault();
          window.location.href = '/dashboard';
          break;
        case 'p':
          e.preventDefault();
          window.location.href = '/predictions';
          break;
        case 'w':
          e.preventDefault();
          window.location.href = '/watchlist';
          break;
        case 'r':
          e.preventDefault();
          window.location.href = '/realtime';
          break;
      }
    }
    
    // Refresh shortcuts
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
      // Allow default browser refresh behavior
      return;
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleGlobalShortcuts);
    return () => document.removeEventListener('keydown', handleGlobalShortcuts);
  }, [handleGlobalShortcuts]);

  return { handleGlobalShortcuts };
}