'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

/**
 * キーボードショートカットシステム
 * パワーユーザー向けの高速ナビゲーション機能
 */

interface ShortcutItem {
  key: string;
  description: string;
  action: () => void;
  modifiers?: {
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
  };
}

export function useKeyboardShortcuts() {
  const router = useRouter();
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const shortcuts: ShortcutItem[] = [
    {
      key: '/',
      description: '検索バーにフォーカス',
      action: () => {
        const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
        } else {
          router.push('/search');
        }
      },
    },
    {
      key: 'h',
      description: 'ホームページへ移動',
      action: () => router.push('/'),
    },
    {
      key: 'r',
      description: 'ランキングページへ移動',
      action: () => router.push('/rankings'),
    },
    {
      key: 's',
      description: '検索ページへ移動',
      action: () => router.push('/search'),
    },
    {
      key: 'c',
      description: '銘柄比較ページへ移動',
      action: () => router.push('/compare'),
    },
    {
      key: 'a',
      description: '精度ダッシュボードへ移動',
      action: () => router.push('/accuracy'),
    },
    {
      key: 'm',
      description: 'マイページへ移動',
      action: () => router.push('/mypage'),
    },
    {
      key: 'd',
      description: 'ダークモード切り替え',
      action: () => {
        const isDark = document.documentElement.classList.contains('dark');
        if (isDark) {
          document.documentElement.classList.remove('dark');
          localStorage.setItem('theme', 'light');
        } else {
          document.documentElement.classList.add('dark');
          localStorage.setItem('theme', 'dark');
        }
      },
    },
    {
      key: '?',
      description: 'ショートカット一覧を表示',
      action: () => setIsHelpOpen(true),
    },
    {
      key: 'Escape',
      description: 'モーダルを閉じる',
      action: () => setIsHelpOpen(false),
    },
  ];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 入力フィールドにフォーカスがある場合は無効化（/とEscapeを除く）
      const isInputFocused =
        document.activeElement instanceof HTMLInputElement ||
        document.activeElement instanceof HTMLTextAreaElement;

      if (isInputFocused && e.key !== '/' && e.key !== 'Escape') {
        return;
      }

      // ショートカットを検索
      const shortcut = shortcuts.find(s => {
        const keyMatches = s.key === e.key;
        const ctrlMatches = s.modifiers?.ctrl ? e.ctrlKey : !e.ctrlKey;
        const altMatches = s.modifiers?.alt ? e.altKey : !e.altKey;
        const shiftMatches = s.modifiers?.shift ? e.shiftKey : !e.shiftKey;

        return keyMatches && ctrlMatches && altMatches && shiftMatches;
      });

      if (shortcut) {
        e.preventDefault();
        shortcut.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return { isHelpOpen, setIsHelpOpen, shortcuts };
}

/**
 * キーボードショートカットヘルプモーダル
 */
export function KeyboardShortcutsHelp() {
  const { isHelpOpen, setIsHelpOpen, shortcuts } = useKeyboardShortcuts();

  if (!isHelpOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={() => setIsHelpOpen(false)}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            キーボードショートカット
          </h2>
          <button
            onClick={() => setIsHelpOpen(false)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="閉じる"
          >
            <svg className="w-6 h-6 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            以下のキーボードショートカットを使用して、より効率的にナビゲートできます。
          </p>

          <div className="space-y-3">
            {shortcuts.filter(s => s.key !== 'Escape').map((shortcut) => (
              <div
                key={shortcut.key}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="text-gray-700 dark:text-gray-300">
                  {shortcut.description}
                </span>
                <kbd className="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-sm font-mono font-semibold text-gray-900 dark:text-white shadow-sm">
                  {shortcut.modifiers?.ctrl && 'Ctrl + '}
                  {shortcut.modifiers?.alt && 'Alt + '}
                  {shortcut.modifiers?.shift && 'Shift + '}
                  {shortcut.key === '/' ? '/' : shortcut.key.toUpperCase()}
                </kbd>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>ヒント:</strong> 入力フィールドにフォーカスしている場合、ショートカットは無効になります。
              <kbd className="mx-1 px-2 py-0.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-xs font-mono">Escape</kbd>
              キーでフォーカスを解除できます。
            </p>
          </div>
        </div>

        <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button
            onClick={() => setIsHelpOpen(false)}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * ショートカットインジケーター（右下に表示）
 */
export function KeyboardShortcutIndicator() {
  const { setIsHelpOpen } = useKeyboardShortcuts();

  return (
    <button
      onClick={() => setIsHelpOpen(true)}
      className="fixed bottom-6 right-6 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg transition-all hover:scale-110 z-40"
      aria-label="キーボードショートカットを表示"
      title="キーボードショートカット (?)"
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
      </svg>
    </button>
  );
}

/**
 * グローバルキーボードショートカットシステム
 * layout.tsxに追加して使用
 */
export default function KeyboardShortcutsProvider() {
  useKeyboardShortcuts();

  return (
    <>
      <KeyboardShortcutsHelp />
      <KeyboardShortcutIndicator />
    </>
  );
}
