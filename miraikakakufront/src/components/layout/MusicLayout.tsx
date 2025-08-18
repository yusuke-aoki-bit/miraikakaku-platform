'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Home, TrendingUp, BarChart3, Brain, Activity, Settings, User, Bell, Star, History, Calculator, Menu, X, Trophy } from 'lucide-react';

interface StockMusicLayoutProps {
  children: React.ReactNode;
}

export default function StockMusicLayout({ children }: StockMusicLayoutProps) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

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
    window.location.href = `/?symbol=${symbol}`;
  };

  return (
    <div className="h-screen bg-black text-white flex flex-col">
      {/* Header Bar with frosted glass effect */}
      <div className="youtube-glass px-4 md:px-6 py-4 flex items-center animate-fade-in">
        {/* Left Section */}
        <div className="flex items-center space-x-4 w-1/4">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent whitespace-nowrap">
            Miraikakaku
          </h1>
        </div>

        {/* Center Section - Search */}
        <div className="flex-1 flex justify-center px-4">
          <div className="relative w-full max-w-md">
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
            />
            
            {/* 検索結果ドロップダウン */}
            {showSearchResults && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 youtube-card max-h-60 overflow-y-auto z-50">
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
          <button className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all">
            <Bell size={20} />
          </button>
          <button className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all">
            <Settings size={20} />
          </button>
          <button className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800/50 transition-all">
            <User size={20} />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div 
            className="md:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Sidebar */}
        <div className={`w-64 bg-black/95 border-r border-gray-800/50 flex flex-col backdrop-blur-sm transform transition-transform duration-300 ease-in-out z-50 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 md:relative md:z-auto fixed inset-y-0 left-0`}>
          <nav className="flex-1 px-4 py-6 space-y-2 animate-slide-up">
            <Link 
              href="/"
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                pathname === '/' 
                  ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <Home className="w-5 h-5 mr-3" />
              ダッシュボード
            </Link>
            
            <Link 
              href="/analysis"
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                pathname === '/analysis' 
                  ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <BarChart3 className="w-5 h-5 mr-3" />
              市場分析
            </Link>
            
            <Link 
              href="/predictions"
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                pathname === '/predictions' 
                  ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <Brain className="w-5 h-5 mr-3" />
              AI予測
            </Link>
            
            <Link 
              href="/watchlist"
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                pathname === '/watchlist' 
                  ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <Star className="w-5 h-5 mr-3" />
              ウォッチリスト
            </Link>
            
            <Link 
              href="/rankings"
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                pathname === '/rankings' 
                  ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                  : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <Trophy className="w-5 h-5 mr-3" />
              ランキング
            </Link>
            
            <div className="pt-6">
              <h3 className="px-4 text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
                ツール
              </h3>
              <div className="space-y-2">
                <Link 
                  href="/tools"
                  className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                    pathname === '/tools' 
                      ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <Calculator className="w-5 h-5 mr-3" />
                  投資計算機
                </Link>
                
                <Link 
                  href="/history"
                  className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                    pathname === '/history' 
                      ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <History className="w-5 h-5 mr-3" />
                  履歴
                </Link>
                
                <Link 
                  href="/realtime"
                  className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
                    pathname === '/realtime' 
                      ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
                      : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <Activity className="w-5 h-5 mr-3" />
                  リアルタイム
                </Link>
              </div>
            </div>
          </nav>
        </div>

        {/* Main Content with gradient background */}
        <main className="flex-1 bg-gradient-to-br from-black via-gray-900 to-black overflow-auto">
          <div className="min-h-full bg-gradient-to-b from-transparent via-black/50 to-black animate-fade-in">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile Search Bar */}
      <div className="sm:hidden bg-gray-900/80 backdrop-blur-md border-t border-gray-800/50 px-4 py-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input 
            type="text" 
            placeholder="株式検索..."
            className="youtube-search pl-10 pr-4 py-2 w-full"
          />
        </div>
      </div>

      {/* Bottom Status Bar (replacing music player) */}
      <div className="youtube-glass px-4 md:px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Market Status */}
          <div className="flex items-center space-x-3 md:space-x-4 min-w-0 flex-1 md:w-1/3">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse-slow flex-shrink-0"></div>
            <div className="min-w-0">
              <p className="text-white text-xs md:text-sm font-medium truncate">市場オープン</p>
              <p className="text-gray-400 text-xs truncate">東京証券取引所</p>
            </div>
          </div>

          {/* Market Indices */}
          <div className="hidden md:flex items-center space-x-8 w-1/3 justify-center">
            <div className="text-center">
              <p className="text-xs text-gray-400">日経225</p>
              <p className="text-white font-medium">29,850.45</p>
              <p className="text-green-400 text-xs">+125.30 (+0.42%)</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">TOPIX</p>
              <p className="text-white font-medium">2,125.67</p>
              <p className="text-red-400 text-xs">-15.20 (-0.71%)</p>
            </div>
          </div>

          {/* AI Status */}
          <div className="flex items-center space-x-2 md:space-x-4 flex-1 md:w-1/3 justify-end">
            <div className="flex items-center space-x-2">
              <Brain className="w-4 h-4 text-purple-400 animate-pulse-slow" />
              <span className="text-xs md:text-sm text-gray-300 hidden sm:inline">AI予測アクティブ</span>
            </div>
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    </div>
  );
}