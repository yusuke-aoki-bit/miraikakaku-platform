'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Search, Bell, Settings, User, Menu, X, Accessibility } from 'lucide-react';
import UserModeToggle from '@/components/common/UserModeToggle';
// import AccessibilitySettings from '@/components/accessibility/AccessibilitySettings';
// import { useAccessibilityContext } from '@/components/accessibility/AccessibilityProvider';

interface HeaderProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export default function Header({ sidebarOpen, setSidebarOpen }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  // const [showA11ySettings, setShowA11ySettings] = useState(false);
  // const { announce } = useAccessibilityContext();

  const handleSearch = async (query: string) => {
    if (query.length < 2) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/search?query=${encodeURIComponent(query)}`
      );
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
        setShowSearchResults(true);
      }
    } catch (error) {
      console.error('検索エラー:', error);
    }
  };

  const handleStockSelect = (symbol: string) => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
    // Navigate to the new unified stock page
    window.location.href = `/stock/${symbol}`;
  };

  return (
    <header className="youtube-glass px-4 md:px-6 py-4 flex items-center animate-fade-in">
      {/* Left Section */}
      <div className="flex items-center space-x-4 w-1/4">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="md:hidden text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <Link href="/" className="text-xl md:text-2xl font-bold bg-gradient-to-r from-base-blue-500 to-base-blue-400 bg-clip-text text-transparent whitespace-nowrap">
          Miraikakaku Dashboard
        </Link>
      </div>

      {/* Center Section - Search */}
      <div className="flex-1 flex justify-center px-4">
        <div className="relative w-full max-w-md" data-testid="stock-search">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              handleSearch(e.target.value);
            }}
            placeholder="株式コード、銘柄名で検索..."
            className="youtube-search pl-10 pr-4 py-2 w-full"
            data-testid="stock-search-input"
          />
          
          {showSearchResults && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 youtube-card max-h-60 overflow-y-auto z-50" data-testid="search-suggestions">
              {searchResults.map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => handleStockSelect(stock.symbol)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-800/50 border-b border-gray-700/50 last:border-b-0 transition-all duration-150"
                >
                  <div className="font-semibold text-white">{stock.symbol}</div>
                  <div className="text-sm text-gray-300 truncate">{stock.company_name}</div>
                  <div className="text-xs text-gray-500">
                    {stock.exchange} {stock.sector && `• ${stock.sector}`}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-2 md:space-x-4 w-1/4 justify-end">
        <UserModeToggle size="sm" showLabels={false} className="mr-2" />
        <button 
          onClick={() => {
            // Open notifications panel
            console.log('Open notifications');
          }}
          className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
          aria-label="通知"
        >
          <Bell size={20} />
        </button>
        <button
          onClick={() => {
            // Open accessibility settings
            console.log('Open accessibility settings');
          }}
          className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
          aria-label="アクセシビリティ設定"
          title="アクセシビリティ設定 (Alt + A)"
        >
          <Accessibility size={20} />
        </button>
        <Link 
          href="/settings" 
          className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
          aria-label="設定"
        >
          <Settings size={20} />
        </Link>
        <button 
          onClick={() => {
            // Open user menu
            console.log('Open user menu');
          }}
          className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
          aria-label="ユーザーメニュー"
        >
          <User size={20} />
        </button>
      </div>
    </header>
  );
}
