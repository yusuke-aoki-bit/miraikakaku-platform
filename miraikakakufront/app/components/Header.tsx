'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { TrendingUp, Activity, User, LogIn } from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { NotificationSystem } from './NotificationSystem';
import { AuthModal } from './AuthModal';

// Static translations to avoid i18n dependency
const translations = {
  'hero.title': '未来価格'
};

const t = (key: string) => translations[key] || key;

interface UserData {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_premium: boolean;
}

interface HeaderProps {
  onUserAuthenticated?: (user: UserData) => void;
  currentUser?: UserData | null;
}

export default function Header({ onUserAuthenticated, currentUser }: HeaderProps) {
  const router = useRouter(
  const [showAuthModal, setShowAuthModal] = useState(false
  const [user, setUser] = useState<UserData | null>(currentUser || null
  useEffect(() => {
    // Check for existing user session
    const token = localStorage.getItem('auth_token'
    const userData = localStorage.getItem('user_data'
    if (token && userData && !user) {
      try {
        const parsedUser = JSON.parse(userData
        setUser(parsedUser
        onUserAuthenticated?.(parsedUser
      } catch (error) {
        localStorage.removeItem('auth_token'
        localStorage.removeItem('user_data'
      }
    }
  }, [user, onUserAuthenticated]
  const handleAuthSuccess = (userData: UserData) => {
    setUser(userData
    onUserAuthenticated?.(userData
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token'
    localStorage.removeItem('user_data'
    setUser(null
    router.push('/'
  };

  const openDashboard = () => {
    router.push('/dashboard'
  };

  return (
    <>
      <header className="sticky top-0 z-50 shadow-sm" style={{
        backgroundColor: 'rgb(var(--theme-bg-secondary))'
        borderBottom: '1px solid rgb(var(--theme-border))'
      }}>
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <button
              onClick={() => router.push('/')}
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <TrendingUp className="w-8 h-8" style={{ color: 'rgb(var(--theme-primary))' }} />
              <span className="theme-heading-sm text-xl">
                {t('hero.title')}
              </span>
            </button>

            {/* Navigation & User Section */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/monitoring')}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors hover:bg-gray-100"
                title="システム監視"
              >
                <Activity className="w-5 h-5" style={{ color: 'rgb(var(--theme-primary))' }} />
                <span className="hidden md:inline text-sm font-medium">監視</span>
              </button>

              <NotificationSystem />

              {/* User Authentication */}
              {user ? (
                <div className="flex items-center space-x-3">
                  <button
                    onClick={openDashboard}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors hover:bg-gray-100"
                    title="ダッシュボード"
                  >
                    <User className="w-5 h-5" style={{ color: 'rgb(var(--theme-primary))' }} />
                    <span className="hidden md:inline text-sm font-medium">
                      {user.full_name || user.username}
                    </span>
                    {user.is_premium && (
                      <span className="bg-yellow-100 text-yellow-800 text-xs px-1 py-0.5 rounded">
                        Premium
                      </span>
                    )}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <LogIn className="w-5 h-5" />
                  <span className="text-sm font-medium">ログイン</span>
                </button>
              )}

              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </header>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </>
}