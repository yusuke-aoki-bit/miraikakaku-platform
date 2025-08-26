'use client';

import { useState } from 'react';
import { EyeIcon, EyeSlashIcon, ExclamationCircleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api-client';

interface ResetPasswordFormProps {
  token: string;
  onPasswordReset: () => void;
}

interface PasswordValidation {
  minLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSymbol: boolean;
}

export default function ResetPasswordForm({ token, onPasswordReset }: ResetPasswordFormProps) {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const validatePassword = (password: string): PasswordValidation => {
    return {
      minLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSymbol: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
  };

  const validation = validatePassword(formData.password);
  const isPasswordValid = Object.values(validation).every(Boolean);
  const passwordsMatch = formData.password === formData.confirmPassword;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.password) {
      setError('新しいパスワードを入力してください。');
      return;
    }

    if (!isPasswordValid) {
      setError('パスワードが要件を満たしていません。');
      return;
    }

    if (!formData.confirmPassword) {
      setError('パスワード確認を入力してください。');
      return;
    }

    if (!passwordsMatch) {
      setError('パスワードが一致しません。');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await apiClient.resetPassword(token, formData.password);
      
      if (response.success) {
        onPasswordReset();
      } else {
        setError(response.message || 'パスワードの再設定に失敗しました。');
      }
    } catch (error) {
      console.error('Password reset failed:', error);
      setError('ネットワークエラーが発生しました。インターネット接続をご確認の上、再度お試しください。');
    } finally {
      setIsSubmitting(false);
    }
  };

  const ValidationItem = ({ isValid, children }: { isValid: boolean; children: React.ReactNode }) => (
    <div className={`flex items-center space-x-2 ${isValid ? 'text-green-600' : 'text-text-secondary'}`}>
      {isValid ? (
        <CheckCircleIcon className="h-4 w-4 text-green-500" />
      ) : (
        <div className="w-4 h-4 rounded-full border border-current" />
      )}
      <span className="text-xs">{children}</span>
    </div>
  );

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 新しいパスワード */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
            新しいパスワード <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleInputChange}
              placeholder="新しいパスワードを入力"
              className="w-full pr-10 pl-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              disabled={isSubmitting}
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-secondary hover:text-text-primary transition-colors"
              disabled={isSubmitting}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* パスワード要件 */}
          {formData.password && (
            <div className="mt-2 p-3 bg-gray-500/5 border border-gray-500/10 rounded-lg space-y-2">
              <h4 className="text-xs font-medium text-text-primary">パスワード要件</h4>
              <div className="space-y-1">
                <ValidationItem isValid={validation.minLength}>
                  8文字以上
                </ValidationItem>
                <ValidationItem isValid={validation.hasUppercase}>
                  大文字を含む (A-Z)
                </ValidationItem>
                <ValidationItem isValid={validation.hasLowercase}>
                  小文字を含む (a-z)
                </ValidationItem>
                <ValidationItem isValid={validation.hasNumber}>
                  数字を含む (0-9)
                </ValidationItem>
                <ValidationItem isValid={validation.hasSymbol}>
                  記号を含む (!@#$%^&*など)
                </ValidationItem>
              </div>
            </div>
          )}
        </div>

        {/* パスワード確認 */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
            パスワード確認 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="パスワードを再度入力"
              className="w-full pr-10 pl-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              disabled={isSubmitting}
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-secondary hover:text-text-primary transition-colors"
              disabled={isSubmitting}
            >
              {showConfirmPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* パスワード一致チェック */}
          {formData.confirmPassword && (
            <div className={`mt-2 flex items-center space-x-2 ${
              passwordsMatch ? 'text-green-600' : 'text-red-600'
            }`}>
              {passwordsMatch ? (
                <CheckCircleIcon className="h-4 w-4" />
              ) : (
                <ExclamationCircleIcon className="h-4 w-4" />
              )}
              <span className="text-xs">
                {passwordsMatch ? 'パスワードが一致しています' : 'パスワードが一致しません'}
              </span>
            </div>
          )}
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className="flex items-start space-x-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* 設定ボタン */}
        <button
          type="submit"
          disabled={isSubmitting || !isPasswordValid || !passwordsMatch || !formData.password || !formData.confirmPassword}
          className="w-full bg-accent-primary hover:bg-accent-primary/90 disabled:bg-accent-primary/50 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              設定中...
            </>
          ) : (
            'パスワードを設定'
          )}
        </button>

        {/* セキュリティ情報 */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-600 mb-2">セキュリティのために</h3>
          <ul className="text-xs text-blue-700 space-y-1">
            <li>• 他のサービスで使用していないパスワードを設定してください</li>
            <li>• 定期的なパスワード変更をおすすめします</li>
            <li>• パスワードは第三者に教えないでください</li>
            <li>• 二要素認証の設定もご検討ください</li>
          </ul>
        </div>

        <div className="text-center text-xs text-text-secondary">
          <p>このページはSSL暗号化により保護されています</p>
        </div>
      </form>
    </div>
  );
}