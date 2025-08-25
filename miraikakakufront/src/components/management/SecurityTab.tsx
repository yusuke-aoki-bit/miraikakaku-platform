'use client';

import { useState } from 'react';
import { EyeIcon, EyeSlashIcon, ShieldCheckIcon, ComputerDesktopIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline';

interface LoginHistoryItem {
  id: string;
  ip_address: string;
  location: string;
  device: string;
  browser: string;
  login_time: string;
  is_current: boolean;
}

export default function SecurityTab() {
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const [loginHistory] = useState<LoginHistoryItem[]>([
    {
      id: '1',
      ip_address: '192.168.1.100',
      location: '東京都, 日本',
      device: 'Windows PC',
      browser: 'Chrome 128',
      login_time: '2024-08-24T10:30:00Z',
      is_current: true,
    },
    {
      id: '2',
      ip_address: '192.168.1.101',
      location: '東京都, 日本',
      device: 'iPhone',
      browser: 'Safari',
      login_time: '2024-08-23T14:20:00Z',
      is_current: false,
    },
    {
      id: '3',
      ip_address: '203.0.113.50',
      location: '大阪府, 日本',
      device: 'Android',
      browser: 'Chrome Mobile',
      login_time: '2024-08-22T09:15:00Z',
      is_current: false,
    },
  ]);

  const validatePasswordForm = () => {
    const newErrors: Record<string, string> = {};

    if (!passwordForm.currentPassword) {
      newErrors.currentPassword = '現在のパスワードを入力してください';
    }

    if (!passwordForm.newPassword) {
      newErrors.newPassword = '新しいパスワードを入力してください';
    } else if (passwordForm.newPassword.length < 8) {
      newErrors.newPassword = 'パスワードは8文字以上で入力してください';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwordForm.newPassword)) {
      newErrors.newPassword = 'パスワードには大文字、小文字、数字を含めてください';
    }

    if (!passwordForm.confirmPassword) {
      newErrors.confirmPassword = 'パスワード（確認用）を入力してください';
    } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      newErrors.confirmPassword = 'パスワードが一致しません';
    }

    if (passwordForm.currentPassword === passwordForm.newPassword) {
      newErrors.newPassword = '新しいパスワードは現在のパスワードと異なるものにしてください';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) return;

    setIsLoading(true);
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          current_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword,
        }),
      });

      if (response.ok) {
        alert('パスワードが正常に変更されました');
        setPasswordForm({
          currentPassword: '',
          newPassword: '',
          confirmPassword: '',
        });
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.message || 'パスワードの変更に失敗しました' });
      }
    } catch (error) {
      setErrors({ submit: 'ネットワークエラーが発生しました' });
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FAToggle = async () => {
    if (!is2FAEnabled) {
      setShow2FASetup(true);
    } else {
      // 無効化確認
      if (window.confirm('二要素認証を無効にしますか？アカウントのセキュリティが低下します。')) {
        setIsLoading(true);
        try {
          // TODO: API呼び出し
          const response = await fetch('/api/user/2fa/disable', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          });

          if (response.ok) {
            setIs2FAEnabled(false);
            alert('二要素認証が無効になりました');
          } else {
            alert('二要素認証の無効化に失敗しました');
          }
        } catch (error) {
          alert('ネットワークエラーが発生しました');
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  const getDeviceIcon = (device: string) => {
    if (device.toLowerCase().includes('iphone') || device.toLowerCase().includes('android')) {
      return <DevicePhoneMobileIcon className="w-5 h-5" />;
    }
    return <ComputerDesktopIcon className="w-5 h-5" />;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-text-primary">セキュリティ</h2>
        <p className="text-sm text-text-secondary mt-1">
          アカウントの安全性を管理します
        </p>
      </div>

      <div className="space-y-8">
        {/* パスワード変更 */}
        <div className="border-b border-border-primary pb-6">
          <h3 className="text-lg font-medium text-text-primary mb-4">パスワードの変更</h3>
          
          <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                現在のパスワード
              </label>
              <div className="relative">
                <input
                  type={showPasswords.current ? 'text' : 'password'}
                  value={passwordForm.currentPassword}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                  className={`w-full px-3 py-2 pr-10 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.currentPassword ? 'border-red-500' : 'border-border-primary'
                  }`}
                  placeholder="現在のパスワード"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
                >
                  {showPasswords.current ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.currentPassword && <p className="text-red-500 text-sm mt-1">{errors.currentPassword}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                新しいパスワード
              </label>
              <div className="relative">
                <input
                  type={showPasswords.new ? 'text' : 'password'}
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                  className={`w-full px-3 py-2 pr-10 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.newPassword ? 'border-red-500' : 'border-border-primary'
                  }`}
                  placeholder="新しいパスワード"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
                >
                  {showPasswords.new ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.newPassword && <p className="text-red-500 text-sm mt-1">{errors.newPassword}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                新しいパスワード（確認用）
              </label>
              <div className="relative">
                <input
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  className={`w-full px-3 py-2 pr-10 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary ${
                    errors.confirmPassword ? 'border-red-500' : 'border-border-primary'
                  }`}
                  placeholder="パスワードを再入力"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
                >
                  {showPasswords.confirm ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
            </div>

            {errors.submit && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-500 text-sm">{errors.submit}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="bg-accent-primary hover:bg-accent-primary/90 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'パスワード変更中...' : 'パスワードを変更'}
            </button>
          </form>
        </div>

        {/* 二要素認証 */}
        <div className="border-b border-border-primary pb-6">
          <h3 className="text-lg font-medium text-text-primary mb-4">二要素認証 (2FA)</h3>
          
          <div className="flex items-center justify-between p-4 bg-surface-background rounded-lg border border-border-primary">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${is2FAEnabled ? 'bg-green-500/10' : 'bg-gray-500/10'}`}>
                <ShieldCheckIcon className={`w-6 h-6 ${is2FAEnabled ? 'text-green-500' : 'text-gray-500'}`} />
              </div>
              <div>
                <h4 className="font-medium text-text-primary">
                  二要素認証{is2FAEnabled ? '有効' : '無効'}
                </h4>
                <p className="text-sm text-text-secondary">
                  {is2FAEnabled ? 'アカウントは追加のセキュリティで保護されています' : 'セキュリティを強化するために二要素認証を有効にしてください'}
                </p>
              </div>
            </div>
            <button
              onClick={handle2FAToggle}
              disabled={isLoading}
              className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 ${
                is2FAEnabled
                  ? 'border border-red-500 text-red-500 hover:bg-red-500/10'
                  : 'bg-accent-primary hover:bg-accent-primary/90 text-white'
              }`}
            >
              {is2FAEnabled ? '無効にする' : '有効にする'}
            </button>
          </div>

          {is2FAEnabled && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h5 className="font-medium text-green-800 mb-2">バックアップコード</h5>
              <p className="text-sm text-green-700 mb-3">
                認証デバイスにアクセスできない場合に使用します
              </p>
              <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                バックアップコードを表示
              </button>
            </div>
          )}
        </div>

        {/* ログイン履歴 */}
        <div>
          <h3 className="text-lg font-medium text-text-primary mb-4">ログイン履歴</h3>
          
          <div className="bg-surface-background rounded-lg border border-border-primary overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-border-primary">
                  <tr>
                    <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">デバイス</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">場所</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">IPアドレス</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">ログイン日時</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-text-secondary">状態</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-primary">
                  {loginHistory.map((item) => (
                    <tr key={item.id} className="hover:bg-surface-elevated/50">
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <div className="text-text-secondary">
                            {getDeviceIcon(item.device)}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-text-primary">{item.device}</div>
                            <div className="text-xs text-text-secondary">{item.browser}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-text-primary">{item.location}</td>
                      <td className="px-4 py-3 text-sm font-mono text-text-secondary">{item.ip_address}</td>
                      <td className="px-4 py-3 text-sm text-text-primary">
                        {new Date(item.login_time).toLocaleString('ja-JP')}
                      </td>
                      <td className="px-4 py-3">
                        {item.is_current ? (
                          <span className="inline-flex px-2 py-1 text-xs font-medium bg-green-500/10 text-green-600 rounded-full">
                            現在のセッション
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 text-xs font-medium bg-gray-500/10 text-gray-600 rounded-full">
                            終了済み
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              💡 不審なログインを発見した場合は、すぐにパスワードを変更し、二要素認証を有効にしてください。
            </p>
          </div>
        </div>
      </div>

      {/* 2FA設定モーダル */}
      {show2FASetup && (
        <TwoFactorSetupModal 
          onClose={() => setShow2FASetup(false)}
          onSuccess={() => {
            setIs2FAEnabled(true);
            setShow2FASetup(false);
          }}
        />
      )}
    </div>
  );
}

interface TwoFactorSetupModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

function TwoFactorSetupModal({ onClose, onSuccess }: TwoFactorSetupModalProps) {
  const [step, setStep] = useState(1);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [qrCode] = useState('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzMzMzMzMyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmaWxsPSJ3aGl0ZSIgZm9udC1zaXplPSIxNHB4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+UVLjgrPjg7zjg4njgaj0Y6Y</text></svg>');

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      alert('6桁の認証コードを入力してください');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/2fa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          code: verificationCode,
        }),
      });

      if (response.ok) {
        onSuccess();
        alert('二要素認証が正常に有効になりました');
      } else {
        alert('認証コードが正しくありません');
      }
    } catch (error) {
      alert('ネットワークエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-lg shadow-xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            二要素認証の設定
          </h3>
          
          {step === 1 ? (
            <div className="space-y-4">
              <p className="text-text-secondary">
                認証アプリ（Google Authenticator、Authyなど）でQRコードをスキャンしてください。
              </p>
              
              <div className="flex justify-center">
                <img src={qrCode} alt="QRコード" className="w-48 h-48 border border-border-primary rounded-lg" />
              </div>
              
              <div className="bg-surface-background p-3 rounded-lg">
                <p className="text-sm font-medium text-text-primary mb-1">手動設定用キー:</p>
                <code className="text-xs font-mono text-text-secondary break-all">
                  JBSWY3DPEHPK3PXP
                </code>
              </div>
              
              <button
                onClick={() => setStep(2)}
                className="w-full bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                次へ
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-text-secondary">
                認証アプリに表示された6桁のコードを入力してください。
              </p>
              
              <div>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary text-center text-xl font-mono focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
                  placeholder="000000"
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
                >
                  戻る
                </button>
                <button
                  onClick={handleVerify}
                  disabled={isLoading || verificationCode.length !== 6}
                  className="flex-1 bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '確認中...' : '確認'}
                </button>
              </div>
            </div>
          )}
          
          <button
            onClick={onClose}
            className="mt-4 w-full text-text-secondary hover:text-text-primary text-sm transition-colors"
          >
            キャンセル
          </button>
        </div>
      </div>
    </div>
  );
}