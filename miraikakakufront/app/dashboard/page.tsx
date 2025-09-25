'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { UserDashboard } from '../components/UserDashboard';
import LoadingSpinner from '../components/LoadingSpinner';

interface UserData {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  bio?: string;
  investment_experience?: string;
  risk_tolerance?: string;
  is_premium: boolean;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter(
  const [user, setUser] = useState<UserData | null>(null
  const [loading, setLoading] = useState(true
  useEffect(() => {
    checkAuthentication(
  }, []
  const checkAuthentication = async () => {
    const token = localStorage.getItem('auth_token'
    const userData = localStorage.getItem('user_data'
    if (!token || !userData) {
      router.push('/'
      return;
    }

    try {
      // Verify token is still valid by fetching user profile
      const response = await fetch('http://localhost:8080/api/auth/me', {
        headers: {
          'Authorization'
          'Content-Type': 'application/json'
        }
      }
      if (response.ok) {
        const userProfile = await response.json(
        setUser(userProfile
      } else {
        // Token is invalid, redirect to login
        localStorage.removeItem('auth_token'
        localStorage.removeItem('user_data'
        router.push('/'
      }
    } catch (error) {
      // Fallback to stored user data if server is unreachable
      try {
        const parsedUser = JSON.parse(userData
        setUser(parsedUser
      } catch (parseError) {
        localStorage.removeItem('auth_token'
        localStorage.removeItem('user_data'
        router.push('/'
      }
    } finally {
      setLoading(false
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token'
    localStorage.removeItem('user_data'
    router.push('/'
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">認証が必要です</h1>
          <p className="text-gray-600 mb-6">ダッシュボードにアクセスするにはログインしてください。</p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            ホームページに戻る
          </button>
        </div>
      </div>
  }

  return <UserDashboard user={user} onLogout={handleLogout} />;
}