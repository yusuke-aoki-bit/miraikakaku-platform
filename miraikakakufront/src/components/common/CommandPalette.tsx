'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Home, BarChart3, Brain, Star, Trophy, SlidersHorizontal, Calculator, Settings, X, Folder, History } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface CommandItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  action?: () => void;
  keywords: string[];
  category: string;
}

const allCommands: CommandItem[] = [
  { id: 'home', label: 'ホーム', icon: <Home />, href: '/', keywords: ['home', 'ダッシュボード', 'トップ'], category: 'Navigation' },
  { id: 'realtime', label: 'リアルタイム', icon: <BarChart3 />, href: '/realtime', keywords: ['realtime', 'リアルタイム', '市場', 'トレンド'], category: 'Explore' },
  { id: 'rankings', label: 'ランキング', icon: <Trophy />, href: '/rankings', keywords: ['ranking', 'ランキング', '順位'], category: 'Explore' },
  { id: 'analysis', label: '分析', icon: <Brain />, href: '/analysis', keywords: ['analysis', '分析', '発見', 'おすすめ'], category: 'Explore' },
  { id: 'watchlist', label: 'ウォッチリスト', icon: <Star />, href: '/watchlist', keywords: ['watchlist', 'ウォッチ', 'お気に入り'], category: 'Portfolio' },
  { id: 'dashboard', label: 'ダッシュボード', icon: <Folder />, href: '/dashboard', keywords: ['dashboard', 'ダッシュボード', 'ポートフォリオ'], category: 'Portfolio' },
  { id: 'history', label: '取引履歴', icon: <History />, href: '/history', keywords: ['history', '履歴', '取引'], category: 'Portfolio' },
  { id: 'predictions', label: 'AI予測', icon: <SlidersHorizontal />, href: '/predictions', keywords: ['predictions', '予測', 'AI', '分析'], category: 'Tools' },
  { id: 'tools', label: '分析ツール', icon: <Calculator />, href: '/tools', keywords: ['tools', 'ツール', '計算機', '分析'], category: 'Tools' },
  { id: 'management', label: '管理', icon: <Settings />, href: '/management', keywords: ['management', '管理', 'アカウント'], category: 'Settings' },
  // Add more commands as needed, including stock search results
];

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [filteredCommands, setFilteredCommands] = useState<CommandItem[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setFilteredCommands(allCommands);
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    // Close palette if route changes
    onClose();
  }, [pathname, onClose]);

  const handleSearch = useCallback(async (searchQuery: string) => {
    setQuery(searchQuery);
    if (searchQuery.length < 1) {
      setFilteredCommands(allCommands);
      setSelectedIndex(0);
      return;
    }

    const lowerCaseQuery = searchQuery.toLowerCase();
    let results: CommandItem[] = [];

    // Filter commands by label or keywords
    const commandMatches = allCommands.filter(cmd => 
      cmd.label.toLowerCase().includes(lowerCaseQuery) || 
      cmd.keywords.some(keyword => keyword.includes(lowerCaseQuery))
    );
    results.push(...commandMatches);

    // --- Stock Search Integration ---
    // This part would ideally be debounced and fetched from the API
    // For demonstration, we'll simulate it or use a simplified version
    if (searchQuery.length >= 2) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/search?query=${encodeURIComponent(searchQuery)}`
        );
        if (response.ok) {
          const stockData = await response.json();
          const stockCommands: CommandItem[] = stockData.map((stock: any) => ({
            id: `stock-${stock.symbol}`,
            label: `${stock.symbol} - ${stock.company_name}`,
            icon: <BarChart3 />, // Or a specific stock icon
            href: `/stock/${stock.symbol}`, // Assuming a unified stock detail page
            keywords: [stock.symbol.toLowerCase(), stock.company_name.toLowerCase()],
            category: 'Stocks',
          }));
          results.push(...stockCommands);
        }
      } catch (error) {
        console.error('Stock search error in command palette:', error);
      }
    }
    // --- End Stock Search Integration ---

    // Deduplicate and sort results (e.g., exact matches first, then partial, then category)
    const uniqueResults = Array.from(new Set(results.map(cmd => cmd.id)))
      .map(id => results.find(cmd => cmd.id === id)!);

    setFilteredCommands(uniqueResults);
    setSelectedIndex(0);
  }, []);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prevIndex) => (prevIndex + 1) % filteredCommands.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prevIndex) => (prevIndex - 1 + filteredCommands.length) % filteredCommands.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        const command = filteredCommands[selectedIndex];
        if (command.href) {
          window.location.href = command.href;
        } else if (command.action) {
          command.action();
        }
        onClose();
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  }, [filteredCommands, selectedIndex, onClose]);

  useEffect(() => {
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    } else {
      window.removeEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, handleKeyDown]);

  const variants = {
    hidden: { opacity: 0, scale: 0.95, y: -20 },
    visible: { opacity: 1, scale: 1, y: 0 },
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial="hidden"
          animate="visible"
          exit="hidden"
          variants={variants}
          className="fixed inset-0 z-[9999] flex items-start justify-center p-4 md:p-16 backdrop-blur-sm bg-black/50"
          onClick={onClose} // Close when clicking outside
        >
          <motion.div
            className="bg-dark-card rounded-lg shadow-2xl w-full max-w-xl flex flex-col overflow-hidden border border-dark-border"
            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
          >
            <div className="relative flex items-center p-4 border-b border-dark-border">
              <Search className="w-5 h-5 text-text-medium mr-3" />
              <input
                ref={inputRef}
                type="text"
                placeholder="コマンドまたは銘柄を検索..."
                className="flex-1 bg-transparent text-text-light outline-none placeholder-text-medium"
                value={query}
                onChange={(e) => handleSearch(e.target.value)}
              />
              <button onClick={onClose} className="text-text-medium hover:text-text-light p-1 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto max-h-[50vh]">
              {filteredCommands.length === 0 && query.length > 0 ? (
                <div className="p-4 text-text-medium text-center">一致するコマンドや銘柄は見つかりませんでした。</div>
              ) : (
                filteredCommands.map((command, index) => (
                  <Link
                    key={command.id}
                    href={command.href || '#'}
                    onClick={() => { command.action?.(); onClose(); }}
                    className={`flex items-center p-4 hover:bg-dark-border transition-colors
                      ${index === selectedIndex ? 'bg-dark-border' : ''}
                    `}
                  >
                    <div className="mr-3 text-text-medium">{command.icon}</div>
                    <div className="flex-1">
                      <div className="text-text-light font-medium">{command.label}</div>
                      <div className="text-xs text-text-dark">{command.category}</div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
