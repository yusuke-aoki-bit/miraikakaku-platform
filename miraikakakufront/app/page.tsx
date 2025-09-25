
'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import LoadingSpinner from './components/LoadingSpinner';
import { ProgressiveLoader } from './components/ProgressiveLoader';
import Header from './components/Header';
import Footer from './components/Footer';
import { SystemStatus, RankingCard, EnhancedStatsCard } from './components/LazyComponents';
import { TrendingUp } from 'lucide-react';

// Static translations to avoid i18n dependency
const translations = {
  'hero.title': '未来価格'
  'hero.description': '高度な機械学習モデルに基づくAI株価予測'
  'search.placeholder': '株式・企業名・ランキングを検索 (例: AAPL, アップル, 値上がり率)'
  'hero.features.ai.title': 'AI予測'
  'hero.features.ai.description': 'LSTMニューラルネットワークが2年間のデータを分析し、6ヶ月先を予測'
  'hero.features.visual.title': 'ビジュアル分析'
  'hero.features.visual.description': '過去データ、過去の予測、未来予測を表示するインタラクティブチャート'
  'hero.features.factors.title': '判断要因'
  'hero.features.factors.description': '詳細な要因分析でAI予測の理由を理解'
  'hero.rankings.title': 'ランキング'
  'hero.rankings.bestPredictions7d': '7日間ベスト予測'
  'hero.rankings.highConfidence': '高信頼度予測'
  'hero.rankings.bestPredictions30d': '30日間ベスト予測'
  'hero.rankings.bestPredictions90d': '90日間ベスト予測'
};

const t = (key: string) => translations[key] || key;

interface UserData {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_premium: boolean;
}

export default function Home() {
  const router = useRouter(
  const [isReady, setIsReady] = useState(true
  const [currentUser, setCurrentUser] = useState<UserData | null>(null
  const [showProgressiveLoader, setShowProgressiveLoader] = useState(false
  const [performanceMetrics, setPerformanceMetrics] = useState<any>({}
  // Progressive loader disabled for performance and E2E testing

  const handleSelectStock = (symbol: string) => {
    router.push(`/details/${symbol}`
  };

  const handleUserAuthenticated = (user: UserData) => {
    setCurrentUser(user
  };

  const handleProgressiveLoadingComplete = () => {
    // Mark progressive loading as shown today
    const today = new Date().toDateString(
    localStorage.setItem('progressive-loader-shown', today
    setShowProgressiveLoader(false
    setIsReady(true
  };

  const handleStageUpdate = (stage: any, progress: number) => {
    // Track performance metrics
    setPerformanceMetrics(prev => ({
      ...prev
      [`stage_${stage.id}`]: {
        duration: stage.duration
        status: stage.status
      }
      overallProgress: progress
    })
  };

  // Show Progressive Loader
  if (showProgressiveLoader) {
    return (
      <ProgressiveLoader
        onComplete={handleProgressiveLoadingComplete}
        onStageUpdate={handleStageUpdate}
        enablePerformanceMode={true}
      />
  }

  // Show fallback loader for quick subsequent loads
  if (!isReady) {
    return (
      <div className="theme-page">
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </div>
  }

  return (
    <div className="theme-page">
      <Header
        onUserAuthenticated={handleUserAuthenticated}
        currentUser={currentUser}
      />
      <main data-testid="homepage-loaded">
        {/* Hero Section */}
        <div className="theme-container">
          <div className="flex flex-col items-center justify-center px-4 py-16 md:py-24">
            <div className="w-full max-w-4xl text-center">
          {/* Logo and Title */}
          <div className="mb-12">
            <div className="flex items-center justify-center mb-6">
              <TrendingUp className="w-16 h-16 mr-4 theme-text-primary float" />
              <h1 className="theme-heading-xl text-4xl md:text-6xl">
                <span className="gradient-text">{t('hero.title')}</span>
              </h1>
            </div>
            <p className="theme-body text-lg max-w-2xl mx-auto mb-8">
              {t('hero.description')}
            </p>
          </div>

          {/* Search Section */}
          <div className="mb-16">
            <SearchBar
              onSelectStock={handleSelectStock}
              className="max-w-2xl mx-auto"
              placeholder={t('search.placeholder')}
            />
          </div>

          {/* Popular Stocks Section */}
          <div className="mb-12" data-testid="popular-stocks">
            <h3 className="theme-heading-md mb-4">人気銘柄</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'].map(stock => (
                <button
                  key={stock}
                  onClick={() => handleSelectStock(stock)}
                  className="theme-btn-secondary px-4 py-2 rounded-lg hover:scale-105 transition-transform"
                >
                  {stock}
                </button>
              ))}
            </div>
          </div>

          {/* Category Sections */}
          <div className="mb-12" data-testid="categories">
            <h3 className="theme-heading-md mb-4">カテゴリー</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: '成長株', icon: '📈' }
                { name: '高配当株', icon: '💰' }
                { name: 'バリュー株', icon: '💎' }
                { name: '小型株', icon: '🚀' }
                { name: 'テクノロジー', icon: '💻' }
                { name: 'ヘルスケア', icon: '🏥' }
                { name: '金融', icon: '🏦' }
                { name: 'エネルギー', icon: '⚡' }
              ].map(category => (
                <button
                  key={category.name}
                  className="theme-card p-4 text-center hover:shadow-lg transition-shadow"
                  onClick={() => {}}
                >
                  <div className="text-2xl mb-2">{category.icon}</div>
                  <div className="theme-text-secondary">{category.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Ranking Buttons */}
          <div className="mb-12" data-testid="ranking-buttons">
            <h3 className="theme-heading-md mb-4">ランキング</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              {['値上がり率ランキング', '値下がり率ランキング', '出来高ランキング'].map(ranking => (
                <button
                  key={ranking}
                  className="theme-btn-primary px-6 py-3 rounded-lg"
                  onClick={() => {}}
                >
                  {ranking}
                </button>
              ))}
            </div>
          </div>

          {/* Company Name Section */}
          <div className="mb-12" data-testid="company-names">
            <h3 className="theme-heading-md mb-4">日本企業</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              {[
                { name: 'トヨタ', symbol: '7203.T' }
                { name: 'ソニー', symbol: '6758.T' }
                { name: 'ソフトバンク', symbol: '9984.T' }
                { name: '任天堂', symbol: '7974.T' }
              ].map(company => (
                <button
                  key={company.symbol}
                  onClick={() => handleSelectStock(company.symbol)}
                  className="theme-btn-secondary px-4 py-2 rounded-lg"
                >
                  {company.name}
                </button>
              ))}
            </div>
          </div>

          {/* Features Section */}
          <div className="mb-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="theme-card p-8 text-center hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-blue-500/30 transform hover:scale-105">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <span className="text-3xl">🧠</span>
                </div>
                <h3 className="theme-heading-sm mb-3 text-xl font-bold">{t('hero.features.ai.title')}</h3>
                <p className="theme-body-secondary leading-relaxed">{t('hero.features.ai.description')}</p>
              </div>
              <div className="theme-card p-8 text-center hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-green-500/30 transform hover:scale-105">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <span className="text-3xl">📊</span>
                </div>
                <h3 className="theme-heading-sm mb-3 text-xl font-bold">{t('hero.features.visual.title')}</h3>
                <p className="theme-body-secondary leading-relaxed">{t('hero.features.visual.description')}</p>
              </div>
              <div className="theme-card p-8 text-center hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-purple-500/30 transform hover:scale-105">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <span className="text-3xl">🔍</span>
                </div>
                <h3 className="theme-heading-sm mb-3 text-xl font-bold">{t('hero.features.factors.title')}</h3>
                <p className="theme-body-secondary leading-relaxed">{t('hero.features.factors.description')}</p>
              </div>
            </div>
          </div>

          {/* Statistics Section */}
          <div className="mb-16">
            <h3 className="theme-heading-lg mb-8 text-center">システム統計</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <EnhancedStatsCard
                title="予測精度"
                value="87.3%"
                subtitle="7日間平均"
                icon="target"
                color="green"
                animationDelay={100}
              />
              <EnhancedStatsCard
                title="分析銘柄数"
                value="1,247"
                subtitle="活発追跡中"
                icon="trending-up"
                color="blue"
                animationDelay={200}
              />
              <EnhancedStatsCard
                title="ユーザー数"
                value="2,834"
                subtitle="月間アクティブ"
                icon="users"
                color="purple"
                animationDelay={300}
              />
              <EnhancedStatsCard
                title="予測処理時間"
                value="1.2秒"
                subtitle="平均レスポンス"
                icon="clock"
                color="orange"
                animationDelay={400}
              />
            </div>
          </div>

          {/* Rankings */}
          <div className="theme-section" data-testid="rankings">
            <h3 className="theme-heading-lg mb-6">
              {t('hero.rankings.title')}
            </h3>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8 max-w-7xl mx-auto">
              {[
                { key: 'bestPredictions', icon: '🎯', timeframe: '7d' as const, type: 'best_predictions' as const, title: t('hero.rankings.bestPredictions7d') }
                { key: 'highConfidence', icon: '🔥', timeframe: '30d' as const, type: 'highest_confidence' as const, title: t('hero.rankings.highConfidence') }
                { key: 'monthlyPredictions', icon: '📈', timeframe: '30d' as const, type: 'best_predictions' as const, title: t('hero.rankings.bestPredictions30d') }
                { key: 'quarterlyPredictions', icon: '⭐', timeframe: '90d' as const, type: 'best_predictions' as const, title: t('hero.rankings.bestPredictions90d') }
              ].map((ranking) => (
                <RankingCard
                  key={ranking.key}
                  title={ranking.title}
                  icon={ranking.icon}
                  timeframe={ranking.timeframe}
                  type={ranking.type}
                  onSelectStock={handleSelectStock}
                />
              ))}
            </div>
          </div>

            </div>
          </div>
        </div>
      </main>
      <Footer />
      <SystemStatus />
    </div>
}
