'use client';

/**
 * Add Portfolio Holding Page
 * Phase 5-2: Frontend Implementation
 *
 * Features:
 * - Form to add new holding
 * - Symbol validation
 * - Form validation
 * - Success redirect to portfolio page
 */

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { addPortfolioHolding } from '@/app/lib/portfolio-api';
import type { AddHoldingRequest } from '@/app/types/portfolio';

export default function AddHoldingPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<AddHoldingRequest>({
    user_id: 'demo_user', // Hardcoded for demo
    symbol: '',
    quantity: 0,
    purchase_price: 0,
    purchase_date: new Date().toISOString().split('T')[0], // Today's date
    notes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.symbol.trim()) {
      newErrors.symbol = 'シンボルを入力してください';
    } else if (!/^[A-Z0-9.]+$/.test(formData.symbol)) {
      newErrors.symbol = '有効なシンボルを入力してください（例: AAPL, 7203.T）';
    }

    if (formData.quantity <= 0) {
      newErrors.quantity = '数量は0より大きい値を入力してください';
    }

    if (formData.purchase_price <= 0) {
      newErrors.purchase_price = '購入単価は0より大きい値を入力してください';
    }

    if (!formData.purchase_date) {
      newErrors.purchase_date = '購入日を入力してください';
    } else {
      const purchaseDate = new Date(formData.purchase_date);
      const today = new Date();
      if (purchaseDate > today) {
        newErrors.purchase_date = '購入日は今日以前の日付を入力してください';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      setSubmitting(true);
      setErrors({});

      // Convert symbol to uppercase
      const requestData = {
        ...formData,
        symbol: formData.symbol.toUpperCase(),
      };

      await addPortfolioHolding(requestData);

      // Success! Redirect to portfolio page
      router.push('/portfolio');
    } catch (err) {
      console.error('Error adding holding:', err);
      setErrors({
        submit: err instanceof Error ? err.message : '保有銘柄の追加に失敗しました',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/portfolio"
            className="text-blue-600 hover:underline mb-4 inline-block"
          >
            ← ポートフォリオに戻る
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">銘柄を追加</h1>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {/* Submit Error */}
          {errors.submit && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{errors.submit}</p>
            </div>
          )}

          {/* Symbol */}
          <div className="mb-6">
            <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-2">
              シンボル <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="symbol"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              placeholder="例: AAPL, 7203.T"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.symbol ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.symbol && <p className="mt-1 text-sm text-red-600">{errors.symbol}</p>}
            <p className="mt-1 text-sm text-gray-500">
              米国株: AAPL, MSFT など / 日本株: 7203.T, 9984.T など
            </p>
          </div>

          {/* Quantity */}
          <div className="mb-6">
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
              数量 <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="quantity"
              step="0.0001"
              min="0"
              value={formData.quantity || ''}
              onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 0 })}
              placeholder="10"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.quantity ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.quantity && <p className="mt-1 text-sm text-red-600">{errors.quantity}</p>}
          </div>

          {/* Purchase Price */}
          <div className="mb-6">
            <label htmlFor="purchase_price" className="block text-sm font-medium text-gray-700 mb-2">
              購入単価 <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="purchase_price"
              step="0.01"
              min="0"
              value={formData.purchase_price || ''}
              onChange={(e) => setFormData({ ...formData, purchase_price: parseFloat(e.target.value) || 0 })}
              placeholder="150.00"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.purchase_price ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.purchase_price && <p className="mt-1 text-sm text-red-600">{errors.purchase_price}</p>}
            <p className="mt-1 text-sm text-gray-500">
              1株あたりの購入価格を入力してください
            </p>
          </div>

          {/* Purchase Date */}
          <div className="mb-6">
            <label htmlFor="purchase_date" className="block text-sm font-medium text-gray-700 mb-2">
              購入日 <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="purchase_date"
              value={formData.purchase_date}
              onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
              max={new Date().toISOString().split('T')[0]}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.purchase_date ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.purchase_date && <p className="mt-1 text-sm text-red-600">{errors.purchase_date}</p>}
          </div>

          {/* Notes */}
          <div className="mb-6">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              メモ（任意）
            </label>
            <textarea
              id="notes"
              rows={3}
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="購入理由や注意点などを記録できます"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Cost Preview */}
          {formData.quantity > 0 && formData.purchase_price > 0 && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-sm text-gray-700 mb-1">取得原価</div>
              <div className="text-2xl font-bold text-gray-900">
                {new Intl.NumberFormat('ja-JP', {
                  style: 'currency',
                  currency: 'JPY',
                  minimumFractionDigits: 0,
                }).format(formData.quantity * formData.purchase_price)}
              </div>
              <div className="text-xs text-gray-600 mt-1">
                {formData.quantity} 株 × {formData.purchase_price.toLocaleString()} 円
              </div>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {submitting ? '追加中...' : '追加'}
            </button>
            <Link
              href="/portfolio"
              className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 text-center transition"
            >
              キャンセル
            </Link>
          </div>
        </form>

        {/* Help Text */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="font-semibold text-yellow-900 mb-2">💡 ヒント</h3>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• シンボルは大文字で入力してください（自動で変換されます）</li>
            <li>• 日本株の場合は「.T」を付けてください（例: 7203.T）</li>
            <li>• 現在価格は自動的に最新データから取得されます</li>
            <li>• 評価損益はポートフォリオページで確認できます</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
