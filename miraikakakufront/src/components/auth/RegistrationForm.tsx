'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

interface RegistrationFormProps {
  redirectTo?: string;
  onSuccess?: () => void;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
}

export default function RegistrationForm({ redirectTo, onSuccess }: RegistrationFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // パスワード強度チェック
  const checkPasswordStrength = (password: string): PasswordStrength => {
    let score = 0;
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>?]/.test(password),
    };

    score = Object.values(checks).filter(Boolean).length;

    if (score === 0) return { score: 0, label: '', color: '' };
    if (score <= 2) return { score, label: '弱い', color: 'text-red-500' };
    if (score <= 3) return { score, label: '普通', color: 'text-yellow-500' };
    if (score <= 4) return { score, label: '強い', color: 'text-green-500' };
    return { score, label: '非常に強い', color: 'text-green-600' };
  };

  const passwordStrength = checkPasswordStrength(formData.password);

  // フォームバリデーション
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'メールアドレスを入力してください';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '有効なメールアドレスを入力してください';
    }

    if (!formData.password) {
      newErrors.password = 'パスワードを入力してください';
    } else if (passwordStrength.score < 3) {
      newErrors.password = 'パスワードが弱すぎます。8文字以上で大文字、小文字、数字を含めてください';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'パスワード（確認用）を入力してください';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'パスワードが一致しません';
    }

    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = '利用規約とプライバシーポリシーに同意してください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      // TODO: 実際のAPI呼び出しを実装
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      if (response.ok) {
        // 登録成功
        // ローカルストレージからゲストデータを取得して移行
        await migrateGuestData();
        
        if (onSuccess) {
          onSuccess();
        } else {
          router.push(redirectTo || '/');
        }
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.message || '登録に失敗しました' });
      }
    } catch (error) {
      setErrors({ submit: 'ネットワークエラーが発生しました' });
    } finally {
      setIsLoading(false);
    }
  };

  const migrateGuestData = async () => {
    try {
      // ゲストのウォッチリストデータを取得
      const guestWatchlist = localStorage.getItem('guestWatchlist');
      const guestSettings = localStorage.getItem('guestSettings');

      if (guestWatchlist || guestSettings) {
        // TODO: ユーザーアカウントにデータを移行
        await fetch('/api/user/migrate-guest-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            watchlist: guestWatchlist ? JSON.parse(guestWatchlist) : null,
            settings: guestSettings ? JSON.parse(guestSettings) : null,
          }),
        });

        // 移行後、ゲストデータをクリア
        localStorage.removeItem('guestWatchlist');
        localStorage.removeItem('guestSettings');
      }
    } catch (error) {
      console.error('Guest data migration failed:', error);
      // エラーでも登録は成功として扱う
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    // エラーをクリア
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const isFormValid = formData.email && 
                     formData.password && 
                     formData.confirmPassword && 
                     formData.agreeToTerms && 
                     passwordStrength.score >= 3 && 
                     formData.password === formData.confirmPassword;

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* メールアドレス */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
            メールアドレス
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className={`w-full px-4 py-3 rounded-lg border transition-colors ${
              errors.email 
                ? 'border-red-500 focus:border-red-500' 
                : 'border-border-primary focus:border-accent-primary'
            } bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20`}
            placeholder="your.email@example.com"
          />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
        </div>

        {/* パスワード */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
            パスワード
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 pr-12 rounded-lg border transition-colors ${
                errors.password 
                  ? 'border-red-500 focus:border-red-500' 
                  : 'border-border-primary focus:border-accent-primary'
              } bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20`}
              placeholder="パスワードを入力"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
            >
              {showPassword ? (
                <EyeSlashIcon className="w-5 h-5" />
              ) : (
                <EyeIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          
          {/* パスワード強度インジケーター */}
          {formData.password && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-text-secondary">パスワード強度</span>
                <span className={passwordStrength.color}>{passwordStrength.label}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div 
                  className={`h-1 rounded-full transition-all duration-300 ${
                    passwordStrength.score <= 2 ? 'bg-red-500' :
                    passwordStrength.score <= 3 ? 'bg-yellow-500' :
                    passwordStrength.score <= 4 ? 'bg-green-500' : 'bg-green-600'
                  }`}
                  style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* パスワード要件 */}
          <div className="mt-2 text-xs text-text-secondary">
            <p>パスワード要件:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li className={formData.password.length >= 8 ? 'text-green-500' : ''}>
                8文字以上
              </li>
              <li className={/[A-Z]/.test(formData.password) ? 'text-green-500' : ''}>
                英大文字を含む
              </li>
              <li className={/[a-z]/.test(formData.password) ? 'text-green-500' : ''}>
                英小文字を含む
              </li>
              <li className={/[0-9]/.test(formData.password) ? 'text-green-500' : ''}>
                数字を含む
              </li>
            </ul>
          </div>

          {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
        </div>

        {/* パスワード確認 */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
            パスワード（確認用）
          </label>
          <div className="relative">
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 pr-12 rounded-lg border transition-colors ${
                errors.confirmPassword 
                  ? 'border-red-500 focus:border-red-500' 
                  : 'border-border-primary focus:border-accent-primary'
              } bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20`}
              placeholder="パスワードを再入力"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
            >
              {showConfirmPassword ? (
                <EyeSlashIcon className="w-5 h-5" />
              ) : (
                <EyeIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
        </div>

        {/* 利用規約同意 */}
        <div>
          <label className="flex items-start space-x-3">
            <input
              type="checkbox"
              name="agreeToTerms"
              checked={formData.agreeToTerms}
              onChange={handleInputChange}
              className="mt-1 rounded border-border-primary text-accent-primary focus:ring-accent-primary"
            />
            <span className="text-sm text-text-secondary">
              <a href="/terms" className="text-accent-primary hover:underline" target="_blank">
                利用規約
              </a>
              と
              <a href="/privacy" className="text-accent-primary hover:underline" target="_blank">
                プライバシーポリシー
              </a>
              に同意します
            </span>
          </label>
          {errors.agreeToTerms && <p className="text-red-500 text-sm mt-1">{errors.agreeToTerms}</p>}
        </div>

        {/* 送信エラー */}
        {errors.submit && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-500 text-sm">{errors.submit}</p>
          </div>
        )}

        {/* 登録ボタン */}
        <button
          type="submit"
          disabled={!isFormValid || isLoading}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all ${
            isFormValid && !isLoading
              ? 'bg-accent-primary hover:bg-accent-primary/90 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isLoading ? '登録中...' : '無料で登録する'}
        </button>

        {/* ログイン画面への導線 */}
        <div className="text-center">
          <p className="text-text-secondary text-sm">
            すでにアカウントをお持ちですか？{' '}
            <a href="/auth/login" className="text-accent-primary hover:underline">
              ログイン
            </a>
          </p>
        </div>
      </form>
    </div>
  );
}