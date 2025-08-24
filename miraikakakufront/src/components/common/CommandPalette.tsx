'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Clock, Hash, ArrowRight } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { useNavigationStore } from '@/store/navigationStore';
import { CommandItem } from '@/types/navigation';

interface StockResult {
  id: string;
  label: string;
  description: string;
  symbol: string;
  company_name: string;
  href: string;
}

interface RecentItem {
  id: string;
  label: string;
  href: string;
  timestamp: Date;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [filteredCommands, setFilteredCommands] = useState<CommandItem[]>([]);
  const [stockResults, setStockResults] = useState<StockResult[]>([]);
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const pathname = usePathname();
  
  const { getCommandItems, recentPages, addRecentPage } = useNavigationStore();
  
  const allCommands = getCommandItems();

  // Initialize recent items from navigation store
  useEffect(() => {
    const recent = recentPages.map((href, index) => ({
      id: `recent-${index}`,
      label: getPageTitle(href),
      href,
      timestamp: new Date(Date.now() - index * 60000) // Mock timestamps
    }));
    setRecentItems(recent);
  }, [recentPages]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setFilteredCommands([]);
      setStockResults([]);
      setSelectedIndex(0);
    }
  }, [isOpen, trackFeatureUsage]);

  useEffect(() => {
    // Close palette if route changes
    onClose();
  }, [pathname, onClose]);

  // Helper function to get page title from href
  const getPageTitle = (href: string): string => {
    const pathMap: Record<string, string> = {
      '/': 'ホーム',
      '/dashboard': 'ダッシュボード',
      '/predictions': 'AI予測',
      '/watchlist': 'ウォッチリスト',
      '/realtime': 'リアルタイム',
      '/rankings': 'ランキング',
      '/analysis': '分析',
      '/tools': '分析ツール',
      '/history': '取引履歴',
      '/management': '管理'
    };
    return pathMap[href] || href;
  };

  const handleSearch = useCallback(async (searchQuery: string) => {
    setQuery(searchQuery);
    
    if (searchQuery.length < 1) {
      setFilteredCommands([]);
      setStockResults([]);
      setSelectedIndex(0);
      return;
    }

    setIsLoading(true);
    const lowerCaseQuery = searchQuery.toLowerCase();

    // Filter commands by label or keywords
    const commandMatches = allCommands.filter(cmd => 
      cmd.label.toLowerCase().includes(lowerCaseQuery) || 
      cmd.keywords.some(keyword => keyword.toLowerCase().includes(lowerCaseQuery))
    );

    setFilteredCommands(commandMatches);

    // Stock search integration
    if (searchQuery.length >= 2) {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/search?query=${encodeURIComponent(searchQuery)}`
        );
        if (response.ok) {
          const stockData = await response.json();
          const stockResults: StockResult[] = stockData.slice(0, 5).map((stock: any) => ({
            id: `stock-${stock.symbol}`,
            label: `${stock.symbol}`,
            description: stock.company_name,
            symbol: stock.symbol,
            company_name: stock.company_name,
            href: `/stock/${stock.symbol}`,
          }));
          setStockResults(stockResults);
        }
      } catch (error) {
        console.error('Stock search error:', error);
      }
    } else {
      setStockResults([]);
    }

    setIsLoading(false);
    setSelectedIndex(0);
  }, [allCommands]);

  const getTotalResults = () => {
    const totalCommands = filteredCommands.length;
    const totalStocks = stockResults.length;
    const totalRecent = query.length === 0 ? recentItems.length : 0;
    return totalCommands + totalStocks + totalRecent;
  };

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const totalResults = getTotalResults();
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      e.stopPropagation();
      setSelectedIndex((prevIndex) => (prevIndex + 1) % Math.max(totalResults, 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      e.stopPropagation();
      setSelectedIndex((prevIndex) => (prevIndex - 1 + Math.max(totalResults, 1)) % Math.max(totalResults, 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      handleSelection(selectedIndex);
    } else if (e.key === 'Escape' && !e.altKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      e.stopPropagation();
      onClose();
    }
  }, [filteredCommands, stockResults, recentItems, selectedIndex, query.length, onClose]);

  const handleSelection = (index: number) => {
    let currentIndex = 0;
    
    // Check if it's a command
    if (index < filteredCommands.length) {
      const command = filteredCommands[index];
      command.action();
      onClose();
      return;
    }
    currentIndex += filteredCommands.length;
    
    // Check if it's a stock result
    if (index < currentIndex + stockResults.length) {
      const stockIndex = index - currentIndex;
      const stock = stockResults[stockIndex];
      addRecentPage(stock.href);
      window.location.href = stock.href;
      onClose();
      return;
    }
    currentIndex += stockResults.length;
    
    // Check if it's a recent item (only when no query)
    if (query.length === 0 && index < currentIndex + recentItems.length) {
      const recentIndex = index - currentIndex;
      const recent = recentItems[recentIndex];
      window.location.href = recent.href;
      onClose();
      return;
    }
  };

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

  const renderResults = () => {
    let currentIndex = 0;
    const results = [];

    // Render commands
    if (filteredCommands.length > 0) {
      results.push(
        <div key="commands" className="p-2">
          <div className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2">
            コマンド
          </div>
          {filteredCommands.map((command, index) => {
            const Icon = command.icon;
            const isSelected = currentIndex + index === selectedIndex;
            return (
              <motion.button
                key={command.id}
                onClick={() => handleSelection(currentIndex + index)}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className={`
                  w-full flex items-center p-3 rounded-lg transition-all duration-150
                  ${isSelected 
                    ? 'bg-brand-primary text-white' 
                    : 'text-text-primary hover:bg-surface-elevated'
                  }
                `}
              >
                <Icon size={18} className="mr-3 flex-shrink-0" />
                <div className="flex-1 text-left">
                  <div className="font-medium">{command.label}</div>
                  {command.description && (
                    <div className={`text-sm ${isSelected ? 'text-white/70' : 'text-text-secondary'}`}>
                      {command.description}
                    </div>
                  )}
                </div>
                {command.hotkey && (
                  <div className={`text-xs font-mono px-2 py-1 rounded ${
                    isSelected 
                      ? 'bg-white/20 text-white/70' 
                      : 'bg-surface-card text-text-tertiary'
                  }`}>
                    {command.hotkey}
                  </div>
                )}
              </motion.button>
            );
          })}
        </div>
      );
      currentIndex += filteredCommands.length;
    }

    // Render stock results
    if (stockResults.length > 0) {
      results.push(
        <div key="stocks" className="p-2">
          <div className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2 flex items-center">
            <Hash size={12} className="mr-1" />
            銘柄
          </div>
          {stockResults.map((stock, index) => {
            const isSelected = currentIndex + index === selectedIndex;
            return (
              <motion.button
                key={stock.id}
                onClick={() => handleSelection(currentIndex + index)}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className={`
                  w-full flex items-center p-3 rounded-lg transition-all duration-150
                  ${isSelected 
                    ? 'bg-brand-primary text-white' 
                    : 'text-text-primary hover:bg-surface-elevated'
                  }
                `}
              >
                <div className={`w-8 h-8 rounded-md flex items-center justify-center mr-3 font-mono text-sm font-bold ${
                  isSelected ? 'bg-white/20' : 'bg-surface-card'
                }`}>
                  {stock.symbol.slice(0, 2)}
                </div>
                <div className="flex-1 text-left">
                  <div className="font-medium">{stock.symbol}</div>
                  <div className={`text-sm truncate ${isSelected ? 'text-white/70' : 'text-text-secondary'}`}>
                    {stock.company_name}
                  </div>
                </div>
                <ArrowRight size={16} className="opacity-50" />
              </motion.button>
            );
          })}
        </div>
      );
      currentIndex += stockResults.length;
    }

    // Render recent items (only when no query)
    if (query.length === 0 && recentItems.length > 0) {
      results.push(
        <div key="recent" className="p-2">
          <div className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2 flex items-center">
            <Clock size={12} className="mr-1" />
            最近のページ
          </div>
          {recentItems.slice(0, 5).map((recent, index) => {
            const isSelected = currentIndex + index === selectedIndex;
            return (
              <motion.button
                key={recent.id}
                onClick={() => handleSelection(currentIndex + index)}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className={`
                  w-full flex items-center p-3 rounded-lg transition-all duration-150
                  ${isSelected 
                    ? 'bg-brand-primary text-white' 
                    : 'text-text-primary hover:bg-surface-elevated'
                  }
                `}
              >
                <Clock size={16} className="mr-3 flex-shrink-0 opacity-50" />
                <div className="flex-1 text-left">
                  <div className="font-medium">{recent.label}</div>
                  <div className={`text-sm ${isSelected ? 'text-white/70' : 'text-text-secondary'}`}>
                    {recent.href}
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      );
    }

    return results;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial="hidden"
          animate="visible"
          exit="hidden"
          variants={variants}
          className="fixed inset-0 z-[9999] flex items-start justify-center p-4 md:p-16 backdrop-blur-sm bg-surface-overlay"
          onClick={onClose}
        >
          <motion.div
            className="bg-surface-card border border-border-default rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center p-4 border-b border-border-default bg-surface-elevated/50">
              <Search className="w-5 h-5 text-text-secondary mr-3" />
              <input
                ref={inputRef}
                type="text"
                placeholder="コマンドや銘柄を検索... (Ctrl+K)"
                className="flex-1 bg-transparent text-text-primary outline-none placeholder-text-secondary"
                value={query}
                onChange={(e) => handleSearch(e.target.value)}
              />
              {isLoading && (
                <div className="w-4 h-4 border-2 border-brand-primary border-t-transparent rounded-full animate-spin mr-2" />
              )}
              <button 
                onClick={onClose} 
                className="p-2 text-text-secondary hover:text-text-primary hover:bg-surface-elevated rounded-lg transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Results */}
            <div className="flex-1 overflow-y-auto max-h-[60vh]">
              {query.length === 0 && filteredCommands.length === 0 && stockResults.length === 0 ? (
                <div className="p-8 text-center">
                  <Search size={48} className="mx-auto mb-4 text-text-tertiary opacity-50" />
                  <h3 className="font-medium text-text-primary mb-2">
                    コマンドパレット
                  </h3>
                  <p className="text-text-secondary text-sm mb-4">
                    コマンドの実行や銘柄の検索ができます
                  </p>
                  <div className="text-xs text-text-tertiary">
                    ↑↓ 選択 • Enter 実行 • Esc 閉じる
                  </div>
                </div>
              ) : getTotalResults() === 0 && query.length > 0 ? (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-4">🔍</div>
                  <h3 className="font-medium text-text-primary mb-2">
                    結果が見つかりません
                  </h3>
                  <p className="text-text-secondary text-sm">
                    「{query}」に一致するコマンドや銘柄はありません
                  </p>
                </div>
              ) : (
                <div className="py-2">
                  {renderResults()}
                </div>
              )}
            </div>

            {/* Footer */}
            {getTotalResults() > 0 && (
              <div className="px-4 py-2 border-t border-border-default bg-surface-elevated/30">
                <div className="text-xs text-text-tertiary flex items-center justify-between">
                  <span>{getTotalResults()} 件の結果</span>
                  <div className="flex items-center space-x-4">
                    <span>↑↓ 選択</span>
                    <span>Enter 実行</span>
                    <span>Esc 閉じる</span>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
