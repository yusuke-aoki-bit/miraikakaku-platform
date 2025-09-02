
'use client';

import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import { useEffect, useState } from 'react';
import SearchBar from './components/SearchBar';
import LoadingSpinner from './components/LoadingSpinner';
import { TrendingUp, Brain, BarChart3, Calendar } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { t, ready, i18n } = useTranslation();
  const [isFullyReady, setIsFullyReady] = useState(false);

  const handleSelectStock = (symbol: string) => {
    console.log('Home handleSelectStock called with:', symbol);
    console.log('Navigating to:', `/details/${symbol}`);
    router.push(`/details/${symbol}`);
  };

  // Ensure i18n is fully loaded
  useEffect(() => {
    if (ready && i18n.isInitialized) {
      // Check if translations are available
      const testTranslation = t('hero.title');
      if (testTranslation && testTranslation !== 'hero.title') {
        setIsFullyReady(true);
      } else {
        // Force ready after short delay to prevent infinite waiting
        setTimeout(() => setIsFullyReady(true), 500);
      }
    } else if (ready) {
      // If ready but not initialized, still proceed after delay
      setTimeout(() => setIsFullyReady(true), 1000);
    }
  }, [ready, i18n.isInitialized, t]);

  // Fallback: force ready after 3 seconds to prevent infinite loading
  useEffect(() => {
    const fallbackTimer = setTimeout(() => {
      setIsFullyReady(true);
    }, 3000);

    return () => clearTimeout(fallbackTimer);
  }, []);

  // Wait for translation to be fully ready
  if (!isFullyReady) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: 'var(--yt-music-bg)' }}>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen" style={{ backgroundColor: 'var(--yt-music-bg)' }} data-testid="homepage-loaded">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center px-4 py-16 md:py-24">
        <div className="w-full max-w-6xl text-center">
          {/* Logo and Title */}
          <div className="mb-12">
            <div className="flex items-center justify-center mb-6">
              <TrendingUp className="w-16 h-16 mr-4" style={{ color: 'var(--yt-music-primary)' }} />
              <h1 className="text-5xl md:text-7xl font-bold" style={{ color: 'var(--yt-music-text-primary)' }}>
                <span style={{ color: 'var(--yt-music-primary)' }}>{t('hero.title')}</span>
              </h1>
            </div>
            <p className="text-2xl md:text-3xl mb-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              {t('hero.title')}
            </p>
            <p className="text-lg max-w-3xl mx-auto" style={{ color: 'var(--yt-music-text-secondary)' }}>
              {t('hero.description')}
            </p>
          </div>

          {/* Search Section */}
          <div className="mb-20">
            <SearchBar 
              onSelectStock={handleSelectStock}
              className="max-w-3xl mx-auto"
              placeholder={t('search.placeholder')}
            />
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            <div className="rounded-xl p-8 hover:scale-105 transition-all duration-300 glass-effect">
              <Brain className="w-16 h-16 mx-auto mb-6" style={{ color: 'var(--yt-music-accent)' }} />
              <h3 className="text-2xl font-semibold mb-4" style={{ color: 'var(--yt-music-text-primary)' }}>
                {t('hero.features.ai.title')}
              </h3>
              <p style={{ color: 'var(--yt-music-text-secondary)' }}>
                {t('hero.features.ai.description')}
              </p>
            </div>
            
            <div className="rounded-xl p-8 hover:scale-105 transition-all duration-300 glass-effect">
              <BarChart3 className="w-16 h-16 mx-auto mb-6" style={{ color: '#10b981' }} />
              <h3 className="text-2xl font-semibold mb-4" style={{ color: 'var(--yt-music-text-primary)' }}>
                {t('hero.features.visual.title')}
              </h3>
              <p style={{ color: 'var(--yt-music-text-secondary)' }}>
                {t('hero.features.visual.description')}
              </p>
            </div>
            
            <div className="rounded-xl p-8 hover:scale-105 transition-all duration-300 glass-effect">
              <Calendar className="w-16 h-16 mx-auto mb-6" style={{ color: '#8b5cf6' }} />
              <h3 className="text-2xl font-semibold mb-4" style={{ color: 'var(--yt-music-text-primary)' }}>
                {t('hero.features.factors.title')}
              </h3>
              <p style={{ color: 'var(--yt-music-text-secondary)' }}>
                {t('hero.features.factors.description')}
              </p>
            </div>
          </div>

          {/* Popular Stocks */}
          <div className="rounded-xl p-8 mb-12 glass-effect" data-testid="popular-stocks">
            <h3 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>
              {t('hero.popularStocks')}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'].map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => handleSelectStock(symbol)}
                  className="px-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
                  style={{ 
                    backgroundColor: 'var(--yt-music-surface-variant)',
                    color: 'var(--yt-music-text-primary)',
                    border: '1px solid var(--yt-music-border)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                    e.currentTarget.style.color = 'var(--yt-music-primary)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                    e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                  }}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {/* Search Keywords */}
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* First Column */}
            <div className="space-y-8">
              {/* Sectors */}
              <div className="rounded-xl p-8 glass-effect" data-testid="sectors">
                <h3 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {t('hero.sectors.title')}
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'technology', icon: '💻' },
                    { key: 'healthcare', icon: '🏥' },
                    { key: 'finance', icon: '🏦' },
                    { key: 'energy', icon: '⚡' },
                    { key: 'consumer', icon: '🛒' },
                    { key: 'industrial', icon: '🏭' }
                  ].map((sector) => (
                    <button
                      key={sector.key}
                      onClick={() => handleSelectStock(sector.key)}
                      className="px-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 text-left"
                      style={{ 
                        backgroundColor: 'var(--yt-music-surface-variant)',
                        color: 'var(--yt-music-text-primary)',
                        border: '1px solid var(--yt-music-border)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                        e.currentTarget.style.color = 'var(--yt-music-accent)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                        e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                      }}
                    >
                      <span className="mr-2">{sector.icon}</span>
                      {t(`hero.sectors.${sector.key}`)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Categories */}
              <div className="rounded-xl p-8 glass-effect" data-testid="categories">
                <h3 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {t('hero.categories.title')}
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'growth', icon: '📈' },
                    { key: 'dividend', icon: '💰' },
                    { key: 'value', icon: '💎' },
                    { key: 'small', icon: '🔸' },
                    { key: 'large', icon: '🔷' },
                    { key: 'emerging', icon: '🌟' }
                  ].map((category) => (
                    <button
                      key={category.key}
                      onClick={() => handleSelectStock(category.key)}
                      className="px-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 text-left"
                      style={{ 
                        backgroundColor: 'var(--yt-music-surface-variant)',
                        color: 'var(--yt-music-text-primary)',
                        border: '1px solid var(--yt-music-border)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                        e.currentTarget.style.color = 'var(--yt-music-accent)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                        e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                      }}
                    >
                      <span className="mr-2">{category.icon}</span>
                      {t(`hero.categories.${category.key}`)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Second Column */}
            <div className="space-y-8">
              {/* Rankings */}
              <div className="rounded-xl p-8 glass-effect" data-testid="rankings">
                <h3 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {t('hero.rankings.title')}
                </h3>
                <div className="grid grid-cols-1 gap-3">
                  {[
                    { key: 'gainers', icon: '🔥' },
                    { key: 'losers', icon: '❄️' },
                    { key: 'volume', icon: '📊' },
                    { key: 'marketcap', icon: '🏆' },
                    { key: 'momentum', icon: '🚀' },
                    { key: 'performance', icon: '⭐' }
                  ].map((ranking) => (
                    <button
                      key={ranking.key}
                      onClick={() => handleSelectStock(ranking.key)}
                      className="px-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 text-left"
                      style={{ 
                        backgroundColor: 'var(--yt-music-surface-variant)',
                        color: 'var(--yt-music-text-primary)',
                        border: '1px solid var(--yt-music-border)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                        e.currentTarget.style.color = 'var(--yt-music-primary)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                        e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                      }}
                    >
                      <span className="mr-2">{ranking.icon}</span>
                      {t(`hero.rankings.${ranking.key}`)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Company Names */}
              <div className="rounded-xl p-8 glass-effect" data-testid="company-search">
                <h3 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {t('hero.companySearch.title')}
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'apple', symbol: 'AAPL', icon: '🍎' },
                    { key: 'microsoft', symbol: 'MSFT', icon: '🪟' },
                    { key: 'google', symbol: 'GOOGL', icon: '🔍' },
                    { key: 'amazon', symbol: 'AMZN', icon: '📦' },
                    { key: 'tesla', symbol: 'TSLA', icon: '🚗' },
                    { key: 'nvidia', symbol: 'NVDA', icon: '🎮' },
                    { key: 'meta', symbol: 'META', icon: '📱' },
                    { key: 'netflix', symbol: 'NFLX', icon: '🎬' },
                    { key: 'toyota', symbol: '7203.T', icon: '🚙' },
                    { key: 'sony', symbol: '6758.T', icon: '🎵' }
                  ].map((company) => (
                    <button
                      key={company.key}
                      onClick={() => handleSelectStock(company.symbol)}
                      className="px-3 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 text-left"
                      style={{ 
                        backgroundColor: 'var(--yt-music-surface-variant)',
                        color: 'var(--yt-music-text-primary)',
                        border: '1px solid var(--yt-music-border)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                        e.currentTarget.style.color = 'var(--yt-music-accent)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
                        e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                      }}
                    >
                      <div className="flex items-center">
                        <span className="mr-2">{company.icon}</span>
                        <div>
                          <div className="text-sm font-semibold">{t(`hero.companySearch.${company.key}`)}</div>
                          <div className="text-xs opacity-70">{company.symbol}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 px-4 border-t" style={{ 
        backgroundColor: 'var(--yt-music-surface)', 
        borderColor: 'var(--yt-music-border)'
      }}>
        <div className="max-w-6xl mx-auto text-center">
          <p className="mb-2" style={{ color: 'var(--yt-music-text-secondary)' }}>
            {t('footer.copyright')}
          </p>
          <p className="text-sm" style={{ color: 'var(--yt-music-text-disabled)' }}>
            {t('footer.disclaimer')}
          </p>
        </div>
      </footer>
    </main>
  );
}
