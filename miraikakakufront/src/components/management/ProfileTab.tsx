'use client';

import { useState, useRef, useEffect } from 'react';
import { CameraIcon, PencilIcon } from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api-client';

interface UserProfile {
  id: string;
  email: string;
  nickname: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export default function ProfileTab() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    nickname: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showEmailChangeModal, setShowEmailChangeModal] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // プロファイル情報をロード
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setProfileLoading(true);
        const response = await apiClient.getUserProfile();
        
        if (response.success && response.data) {
          const userProfile = response.data as UserProfile;
          setProfile(userProfile);
          setEditForm({ nickname: userProfile.nickname || '' });
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setProfileLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleSaveChanges = async () => {
    if (!profile) return;
    
    if (!editForm.nickname.trim()) {
      alert('ニックネームを入力してください');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          nickname: editForm.nickname,
        }),
      });

      if (response.ok) {
        if (profile) {
          setProfile(prev => prev ? ({
            ...prev,
            nickname: editForm.nickname,
            updated_at: new Date().toISOString(),
          }) : null);
        }
        setIsEditing(false);
      } else {
        throw new Error('プロフィールの更新に失敗しました');
      }
    } catch (error) {
      console.error('Profile update error:', error);
      alert('プロフィールの更新に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAvatarChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // ファイルサイズチェック (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('ファイルサイズは5MB以下にしてください');
      return;
    }

    // ファイル形式チェック
    if (!file.type.startsWith('image/')) {
      alert('画像ファイルを選択してください');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('avatar', file);

      // TODO: API呼び出し
      const response = await fetch('/api/user/avatar', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (profile) {
          setProfile(prev => prev ? ({
            ...prev,
            avatar_url: data.avatar_url,
            updated_at: new Date().toISOString(),
          }) : null);
        }
      } else {
        throw new Error('アバターのアップロードに失敗しました');
      }
    } catch (error) {
      console.error('Avatar upload error:', error);
      alert('アバターのアップロードに失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  if (profileLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-accent-primary border-t-transparent"></div>
          <span className="ml-3 text-text-secondary">プロフィール読み込み中...</span>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <h3 className="text-text-primary font-semibold mb-2">プロフィール情報が見つかりません</h3>
          <p className="text-text-secondary">しばらく経ってから再度お試しください。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-text-primary">プロフィール</h2>
        <p className="text-sm text-text-secondary mt-1">
          基本的なユーザー情報を管理します
        </p>
      </div>

      <div className="space-y-6">
        {/* アバター画像 */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold overflow-hidden">
              {profile.avatar_url ? (
                <img 
                  src={profile.avatar_url} 
                  alt="アバター" 
                  className="w-full h-full object-cover"
                />
              ) : (
                profile.nickname.charAt(0).toUpperCase()
              )}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="absolute -bottom-1 -right-1 bg-accent-primary hover:bg-accent-primary/90 text-white p-1.5 rounded-full transition-colors disabled:opacity-50"
            >
              <CameraIcon className="w-4 h-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              className="hidden"
            />
          </div>
          <div>
            <h3 className="font-medium text-text-primary">{profile.nickname}</h3>
            <p className="text-sm text-text-secondary">
              クリックして画像を変更 (最大5MB)
            </p>
          </div>
        </div>

        {/* ニックネーム */}
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            ニックネーム
          </label>
          {isEditing ? (
            <input
              type="text"
              value={editForm.nickname}
              onChange={(e) => setEditForm(prev => ({ ...prev, nickname: e.target.value }))}
              className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
              placeholder="ニックネームを入力"
            />
          ) : (
            <div className="flex items-center justify-between p-3 bg-surface-background rounded-lg border border-border-primary">
              <span className="text-text-primary">{profile.nickname}</span>
              <button
                onClick={() => setIsEditing(true)}
                className="text-accent-primary hover:text-accent-primary/80 p-1"
              >
                <PencilIcon className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* メールアドレス */}
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            メールアドレス
          </label>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-border-primary">
            <span className="text-text-secondary">{profile.email}</span>
            <button
              onClick={() => setShowEmailChangeModal(true)}
              className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium"
            >
              変更
            </button>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            セキュリティ上の理由により、メール変更時はパスワード確認が必要です
          </p>
        </div>

        {/* アカウント情報 */}
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            アカウント情報
          </label>
          <div className="bg-surface-background rounded-lg border border-border-primary p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">ユーザーID:</span>
              <span className="text-text-primary font-mono">{profile.id}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">登録日:</span>
              <span className="text-text-primary">
                {new Date(profile.created_at).toLocaleDateString('ja-JP')}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">最終更新:</span>
              <span className="text-text-primary">
                {new Date(profile.updated_at).toLocaleDateString('ja-JP')}
              </span>
            </div>
          </div>
        </div>

        {/* 操作ボタン */}
        {isEditing && (
          <div className="flex space-x-3 pt-4 border-t border-border-primary">
            <button
              onClick={handleSaveChanges}
              disabled={isLoading}
              className="bg-accent-primary hover:bg-accent-primary/90 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '保存中...' : '変更を保存'}
            </button>
            <button
              onClick={() => {
                setIsEditing(false);
                setEditForm({ nickname: profile.nickname });
              }}
              disabled={isLoading}
              className="border border-border-primary text-text-primary px-4 py-2 rounded-lg font-medium hover:bg-surface-background transition-colors"
            >
              キャンセル
            </button>
          </div>
        )}
      </div>

      {/* メール変更モーダル */}
      {showEmailChangeModal && (
        <EmailChangeModal 
          currentEmail={profile.email}
          onClose={() => setShowEmailChangeModal(false)}
          onSuccess={(newEmail: string) => {
            if (profile) {
              setProfile(prev => prev ? ({ ...prev, email: newEmail }) : null);
            }
            setShowEmailChangeModal(false);
          }}
        />
      )}
    </div>
  );
}

interface EmailChangeModalProps {
  currentEmail: string;
  onClose: () => void;
  onSuccess: (newEmail: string) => void;
}

function EmailChangeModal({ currentEmail, onClose, onSuccess }: EmailChangeModalProps) {
  const [formData, setFormData] = useState({
    newEmail: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.newEmail || !formData.password) {
      setError('すべての項目を入力してください');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.newEmail)) {
      setError('有効なメールアドレスを入力してください');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/email', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          new_email: formData.newEmail,
          password: formData.password,
        }),
      });

      if (response.ok) {
        onSuccess(formData.newEmail);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'メールアドレスの変更に失敗しました');
      }
    } catch (error) {
      setError('ネットワークエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-lg shadow-xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            メールアドレスの変更
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                現在のメールアドレス
              </label>
              <input
                type="email"
                value={currentEmail}
                disabled
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-gray-50 text-text-secondary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                新しいメールアドレス
              </label>
              <input
                type="email"
                value={formData.newEmail}
                onChange={(e) => setFormData(prev => ({ ...prev, newEmail: e.target.value }))}
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
                placeholder="新しいメールアドレスを入力"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                パスワード確認
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-3 py-2 border border-border-primary rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
                placeholder="現在のパスワードを入力"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-500 text-sm">{error}</p>
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-accent-primary hover:bg-accent-primary/90 text-white py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '変更中...' : 'メールアドレスを変更'}
              </button>
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1 border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                キャンセル
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}