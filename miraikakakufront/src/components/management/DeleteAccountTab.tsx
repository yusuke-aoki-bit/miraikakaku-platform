'use client';

import { useState } from 'react';
import { ExclamationTriangleIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function DeleteAccountTab() {
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-text-primary">アカウント削除</h2>
        <p className="text-sm text-text-secondary mt-1">
          アカウントを完全に削除します
        </p>
      </div>

      <div className="space-y-6">
        {/* 警告メッセージ */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-800 mb-3">
                注意: この操作は元に戻せません
              </h3>
              <div className="space-y-2 text-sm text-red-700">
                <p>• アカウントを削除すると、すべてのデータが完全に削除されます</p>
                <p>• ウォッチリスト、ポートフォリオ、設定などのすべての情報が失われます</p>
                <p>• 過去の取引履歴や分析レポートにアクセスできなくなります</p>
                <p>• サブスクリプションがある場合は自動的にキャンセルされます</p>
                <p>• 削除後は同じメールアドレスでの再登録に制限がかかる場合があります</p>
              </div>
            </div>
          </div>
        </div>

        {/* データ削除の詳細 */}
        <div className="bg-surface-background rounded-lg border border-border-primary p-6">
          <h4 className="text-lg font-medium text-text-primary mb-4">削除されるデータ</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">プロフィール情報</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">ウォッチリスト</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">価格アラート設定</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">通知設定</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">ポートフォリオデータ</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">分析レポート履歴</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">支払い履歴</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                <span className="text-text-primary">ログイン履歴</span>
              </div>
            </div>
          </div>
        </div>

        {/* アカウント削除前の選択肢 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="text-lg font-medium text-blue-800 mb-3">
            アカウント削除の前に検討してください
          </h4>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h5 className="font-medium text-blue-800">一時的な利用停止</h5>
                <p className="text-sm text-blue-700">
                  アカウントを無効化して、後で再開することができます
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h5 className="font-medium text-blue-800">データエクスポート</h5>
                <p className="text-sm text-blue-700">
                  削除前にウォッチリストやポートフォリオデータをダウンロードできます
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <h5 className="font-medium text-blue-800">プランのダウングレード</h5>
                <p className="text-sm text-blue-700">
                  プロプランから無料プランに変更して利用を続けることができます
                </p>
              </div>
            </div>
          </div>
          
          <div className="mt-4 space-y-2">
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium block">
              → データをエクスポートする
            </button>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium block">
              → アカウントを一時停止する
            </button>
            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium block">
              → 無料プランに変更する
            </button>
          </div>
        </div>

        {/* サポート情報 */}
        <div className="bg-surface-background rounded-lg border border-border-primary p-6">
          <h4 className="text-lg font-medium text-text-primary mb-3">
            問題がございますか？
          </h4>
          <p className="text-sm text-text-secondary mb-4">
            アカウント削除を検討される理由があれば、サポートチームにお気軽にご相談ください。
            問題解決のお手伝いをいたします。
          </p>
          <div className="space-y-2">
            <button className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium block">
              → サポートに問い合わせる
            </button>
            <button className="text-accent-primary hover:text-accent-primary/80 text-sm font-medium block">
              → よくある質問を見る
            </button>
          </div>
        </div>

        {/* 削除ボタン */}
        <div className="pt-6 border-t border-border-primary">
          <button
            onClick={() => setShowConfirmModal(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <TrashIcon className="w-5 h-5" />
            <span>アカウントを削除する</span>
          </button>
          <p className="text-xs text-text-secondary mt-2">
            この操作により、すべてのデータが完全に削除されます
          </p>
        </div>
      </div>

      {/* 確認モーダル */}
      {showConfirmModal && (
        <DeleteConfirmModal 
          onClose={() => setShowConfirmModal(false)}
          onConfirm={() => {
            // TODO: 削除処理
            setShowConfirmModal(false);
          }}
        />
      )}
    </div>
  );
}

interface DeleteConfirmModalProps {
  onClose: () => void;
  onConfirm: () => void;
}

function DeleteConfirmModal({ onClose, onConfirm }: DeleteConfirmModalProps) {
  const [password, setPassword] = useState('');
  const [confirmText, setConfirmText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const requiredText = 'アカウントを削除します';

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!password) {
      newErrors.password = 'パスワードを入力してください';
    }

    if (confirmText !== requiredText) {
      newErrors.confirmText = `正確に「${requiredText}」と入力してください`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      // TODO: API呼び出し
      const response = await fetch('/api/user/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          password: password,
          confirmation: confirmText,
        }),
      });

      if (response.ok) {
        alert('アカウントが削除されました。ご利用ありがとうございました。');
        localStorage.clear();
        window.location.href = '/';
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.message || 'アカウントの削除に失敗しました' });
      }
    } catch (error) {
      setErrors({ submit: 'ネットワークエラーが発生しました' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-elevated rounded-xl shadow-2xl max-w-md w-full border border-border-primary">
        <div className="p-6">
          <div className="text-center mb-6">
            <div className="p-3 bg-red-100 rounded-full inline-flex mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-2">
              本当に削除しますか？
            </h3>
            <p className="text-text-secondary text-sm">
              この操作は取り消すことができません。
              すべてのデータが完全に削除されます。
            </p>
          </div>

          <form onSubmit={handleDelete} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                パスワードを入力してください
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 ${
                  errors.password ? 'border-red-500' : 'border-border-primary'
                }`}
                placeholder="現在のパスワード"
              />
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                以下のテキストを正確に入力してください:
                <br />
                <span className="font-mono text-red-600">「{requiredText}」</span>
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 ${
                  errors.confirmText ? 'border-red-500' : 'border-border-primary'
                }`}
                placeholder={requiredText}
              />
              {errors.confirmText && <p className="text-red-500 text-sm mt-1">{errors.confirmText}</p>}
            </div>

            {errors.submit && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-500 text-sm">{errors.submit}</p>
              </div>
            )}

            <div className="space-y-3 pt-4">
              <button
                type="submit"
                disabled={isLoading || !password || confirmText !== requiredText}
                className="w-full bg-red-600 hover:bg-red-700 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'アカウント削除中...' : 'アカウントを削除する'}
              </button>
              
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="w-full border border-border-primary text-text-primary py-2 px-4 rounded-lg font-medium hover:bg-surface-background transition-colors"
              >
                キャンセル
              </button>
            </div>
          </form>

          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              最後のチャンス：削除の代わりに、アカウントの一時停止や
              データのエクスポートを検討してみませんか？
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}