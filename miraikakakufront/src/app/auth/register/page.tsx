'use client';

import React, { useState } from 'react';
import { Eye, EyeOff, UserPlus, ArrowRight, Check } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    displayName: '',
    agreeToTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('パスワードが一致しません');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('パスワードは8文字以上で入力してください');
      setLoading(false);
      return;
    }

    if (!formData.agreeToTerms) {
      setError('利用規約に同意してください');
      setLoading(false);
      return;
    }

    try {
      const response = await apiClient.register({
        email: formData.email,
        password: formData.password,
        displayName: formData.displayName
      });

      if (response.success) {
        // Redirect to dashboard after successful registration
        router.push('/dashboard');
      } else {
        setError(response.error || '登録に失敗しました');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('登録に失敗しました。再度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full space-y-8"
      >
        {/* Header */}
        <div className="text-center">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="flex justify-center mb-6"
          >
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <UserPlus className="w-8 h-8 text-white" />
            </div>
          </motion.div>
          <h2 className="text-3xl font-bold text-white">
            無料で始める
          </h2>
          <p className="mt-2 text-gray-400">
            アカウントを作成して、すべての機能をご利用ください
          </p>
        </div>

        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-900/50 border border-gray-800 rounded-xl p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-900/30 border border-red-800 rounded-lg p-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="displayName" className="block text-sm font-medium text-gray-300 mb-2">
                表示名
              </label>
              <input
                id="displayName"
                name="displayName"
                type="text"
                value={formData.displayName}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="あなたの表示名"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                メールアドレス
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="your.email@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                パスワード
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 pr-12"
                  placeholder="8文字以上のパスワード"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                8文字以上の英数字を組み合わせてください
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                パスワード確認
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 pr-12"
                  placeholder="パスワードを再度入力"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center">
              <input
                id="agreeToTerms"
                name="agreeToTerms"
                type="checkbox"
                checked={formData.agreeToTerms}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-600 rounded bg-gray-800"
                required
              />
              <label htmlFor="agreeToTerms" className="ml-2 block text-sm text-gray-300">
                <Link href="/terms" className="text-blue-400 hover:text-blue-300 hover:underline">
                  利用規約
                </Link>
                {' '}および{' '}
                <Link href="/privacy" className="text-blue-400 hover:text-blue-300 hover:underline">
                  プライバシーポリシー
                </Link>
                に同意します
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  無料でアカウントを作成
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* Benefits */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">登録すると利用可能な機能</h3>
          <div className="space-y-3">
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-400 mr-3" />
              <span className="text-gray-300 text-sm">AI予測とポートフォリオ管理</span>
            </div>
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-400 mr-3" />
              <span className="text-gray-300 text-sm">パーソナライズされた投資分析</span>
            </div>
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-400 mr-3" />
              <span className="text-gray-300 text-sm">リアルタイム市場データ</span>
            </div>
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-400 mr-3" />
              <span className="text-gray-300 text-sm">投資コンテストへの参加</span>
            </div>
          </div>
        </motion.div>

        {/* Login Link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <p className="text-gray-400">
            すでにアカウントをお持ちの方は{' '}
            <Link
              href="/auth/login"
              className="text-blue-400 hover:text-blue-300 hover:underline font-medium"
            >
              こちらからログイン
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}