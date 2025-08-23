'use client';

import React from 'react';
import { 
  Settings, 
  Eye, 
  Volume2, 
  Keyboard, 
  MousePointer,
  Type,
  Contrast,
  RotateCcw
} from 'lucide-react';
import { useAccessibilityContext } from './AccessibilityProvider';

export default function AccessibilitySettings({ 
  isOpen, 
  onClose 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
}) {
  const { 
    preferences, 
    updatePreferences, 
    announce 
  } = useAccessibilityContext();

  const handleToggle = (key: keyof typeof preferences, value: boolean | number | string) => {
    updatePreferences({ [key]: value });
    announce(`${key}が${value}に設定されました`);
  };

  const resetToDefaults = () => {
    updatePreferences({
      fontSize: 'medium',
      screenReaderAnnouncements: true,
      keyboardNavigation: true,
      focusVisible: true
    });
    announce('アクセシビリティ設定がリセットされました');
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-surface-overlay backdrop-blur-sm z-modal flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-surface-card border border-border-default rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="a11y-settings-title"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-brand-primary to-brand-primary-light p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <Settings size={24} className="text-white" />
              </div>
              <div>
                <h2 id="a11y-settings-title" className="text-2xl font-bold text-white">
                  アクセシビリティ設定
                </h2>
                <p className="text-white/80">
                  ユーザビリティとアクセシビリティを向上させます
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
              aria-label="設定を閉じる"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          <div className="space-y-8">
            {/* Display Settings */}
            <section>
              <div className="flex items-center space-x-3 mb-4">
                <Eye size={20} className="text-brand-primary" />
                <h3 className="text-lg font-semibold text-text-primary">
                  表示設定
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Font Size */}
                <div className="flex items-center justify-between p-4 bg-surface-hover rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Type size={18} className="text-text-secondary" />
                    <div>
                      <label className="font-medium text-text-primary">
                        フォントサイズ
                      </label>
                      <p className="text-sm text-text-secondary">
                        テキストの大きさを調整
                      </p>
                    </div>
                  </div>
                  <select
                    value={preferences.fontSize}
                    onChange={(e) => handleToggle('fontSize', e.target.value)}
                    className="bg-surface-card border border-border-default rounded-lg px-3 py-2 text-text-primary focus:ring-2 focus:ring-brand-primary focus:border-transparent"
                    aria-label="フォントサイズを選択"
                  >
                    <option value="small">小</option>
                    <option value="medium">中</option>
                    <option value="large">大</option>
                    <option value="xl">特大</option>
                  </select>
                </div>

                {/* High Contrast */}
                <div className="flex items-center justify-between p-4 bg-surface-hover rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Contrast size={18} className="text-text-secondary" />
                    <div>
                      <label className="font-medium text-text-primary">
                        ハイコントラスト
                      </label>
                      <p className="text-sm text-text-secondary">
                        {preferences.prefersHighContrast ? '有効' : '無効'}
                        （システム設定に依存）
                      </p>
                    </div>
                  </div>
                  <div className="px-3 py-1 bg-brand-primary/20 text-brand-primary rounded-lg text-sm">
                    自動検出
                  </div>
                </div>
              </div>
            </section>

            {/* Navigation Settings */}
            <section>
              <div className="flex items-center space-x-3 mb-4">
                <Keyboard size={20} className="text-brand-primary" />
                <h3 className="text-lg font-semibold text-text-primary">
                  ナビゲーション設定
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Keyboard Navigation */}
                <div className="flex items-center justify-between p-4 bg-surface-hover rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Keyboard size={18} className="text-text-secondary" />
                    <div>
                      <label className="font-medium text-text-primary">
                        キーボードナビゲーション
                      </label>
                      <p className="text-sm text-text-secondary">
                        矢印キーでの要素移動を有効化
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggle('keyboardNavigation', !preferences.keyboardNavigation)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      preferences.keyboardNavigation ? 'bg-brand-primary' : 'bg-surface-border'
                    }`}
                    aria-label={`キーボードナビゲーション ${preferences.keyboardNavigation ? '無効にする' : '有効にする'}`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      preferences.keyboardNavigation ? 'translate-x-6' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>

                {/* Focus Visible */}
                <div className="flex items-center justify-between p-4 bg-surface-hover rounded-xl">
                  <div className="flex items-center space-x-3">
                    <MousePointer size={18} className="text-text-secondary" />
                    <div>
                      <label className="font-medium text-text-primary">
                        フォーカス表示
                      </label>
                      <p className="text-sm text-text-secondary">
                        フォーカスされた要素のハイライト表示
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggle('focusVisible', !preferences.focusVisible)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      preferences.focusVisible ? 'bg-brand-primary' : 'bg-surface-border'
                    }`}
                    aria-label={`フォーカス表示 ${preferences.focusVisible ? '無効にする' : '有効にする'}`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      preferences.focusVisible ? 'translate-x-6' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>
              </div>
            </section>

            {/* Screen Reader Settings */}
            <section>
              <div className="flex items-center space-x-3 mb-4">
                <Volume2 size={20} className="text-brand-primary" />
                <h3 className="text-lg font-semibold text-text-primary">
                  スクリーンリーダー設定
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Screen Reader Announcements */}
                <div className="flex items-center justify-between p-4 bg-surface-hover rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Volume2 size={18} className="text-text-secondary" />
                    <div>
                      <label className="font-medium text-text-primary">
                        音声アナウンス
                      </label>
                      <p className="text-sm text-text-secondary">
                        スクリーンリーダーでの状態変更アナウンス
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggle('screenReaderAnnouncements', !preferences.screenReaderAnnouncements)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      preferences.screenReaderAnnouncements ? 'bg-brand-primary' : 'bg-surface-border'
                    }`}
                    aria-label={`音声アナウンス ${preferences.screenReaderAnnouncements ? '無効にする' : '有効にする'}`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      preferences.screenReaderAnnouncements ? 'translate-x-6' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>
              </div>
            </section>

            {/* Motion Settings */}
            <section>
              <div className="p-4 bg-surface-hover rounded-xl">
                <div className="flex items-center space-x-3 mb-2">
                  <RotateCcw size={18} className="text-text-secondary" />
                  <label className="font-medium text-text-primary">
                    モーション設定
                  </label>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  アニメーションの動作: {preferences.prefersReducedMotion ? '軽減' : '通常'}
                </p>
                <div className="px-3 py-1 bg-brand-primary/20 text-brand-primary rounded-lg text-sm inline-block">
                  システム設定に依存
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border-default bg-surface-hover">
          <div className="flex justify-between items-center">
            <p className="text-sm text-text-secondary">
              これらの設定は自動的に保存されます
            </p>
            <button
              onClick={resetToDefaults}
              className="flex items-center space-x-2 px-4 py-2 border border-border-default text-text-secondary rounded-lg hover:text-text-primary hover:border-border-strong transition-colors"
            >
              <RotateCcw size={16} />
              <span>リセット</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}