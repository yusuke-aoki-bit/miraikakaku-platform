'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Target, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Calendar,
  Zap,
  Info
} from 'lucide-react';

interface Contest {
  id: string;
  title: string;
  description: string;
  challenge: string;
  target_symbol: string;
  target_name: string;
  contest_type: 'weekly' | 'daily' | 'monthly' | 'special';
  submission_deadline: string;
  result_date: string;
  reward_description: string;
  entry_fee: number;
  current_participants: number;
  user_participated: boolean;
  user_prediction?: number;
  estimated_result_value?: number;
}

interface PredictionModalProps {
  contest: Contest | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (prediction: number) => void;
}

export default function PredictionModal({ contest, isOpen, onClose, onSubmit }: PredictionModalProps) {
  const [prediction, setPrediction] = useState<string>('');
  const [confidence, setConfidence] = useState<number>(50);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (contest && contest.user_prediction !== undefined) {
      setPrediction(contest.user_prediction.toString());
    } else {
      setPrediction('');
    }
    setConfidence(50);
    setError('');
    setIsSubmitting(false);
  }, [contest, isOpen]);

  const handleSubmit = async () => {
    if (!contest || !prediction) return;

    const numericPrediction = parseFloat(prediction);
    if (isNaN(numericPrediction)) {
      setError('有効な数値を入力してください');
      return;
    }

    if (numericPrediction <= 0) {
      setError('正の数値を入力してください');
      return;
    }

    // Validation based on target symbol
    if (contest.target_symbol === 'USDJPY' && (numericPrediction < 100 || numericPrediction > 200)) {
      setError('USD/JPYの予測値は100-200の範囲で入力してください');
      return;
    }

    if (contest.target_symbol === '^TOPIX' && (numericPrediction < 1000 || numericPrediction > 3000)) {
      setError('TOPIXの予測値は1000-3000の範囲で入力してください');
      return;
    }

    if (contest.target_symbol === '^N225' && (numericPrediction < 20000 || numericPrediction > 50000)) {
      setError('日経225の予測値は20000-50000の範囲で入力してください');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      
      await onSubmit(numericPrediction);
    } catch (err) {
      setError('予測の提出に失敗しました。もう一度お試しください。');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTimeLeft = (deadline: string) => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diff = deadlineDate.getTime() - now.getTime();

    if (diff <= 0) return '締切';

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (days > 0) {
      return `${days}日${hours}時間`;
    } else if (hours > 0) {
      return `${hours}時間${minutes}分`;
    } else {
      return `${minutes}分`;
    }
  };

  const getSymbolHint = (symbol: string) => {
    switch (symbol) {
      case 'USDJPY':
        return {
          hint: '例: 149.50 (小数点第2位まで)',
          current: '現在値: 149.25円',
          range: '通常範囲: 100-200円'
        };
      case '^TOPIX':
        return {
          hint: '例: 2750.5 (小数点第1位まで)',
          current: '現在値: 2734.2',
          range: '通常範囲: 1000-3000'
        };
      case '^N225':
        return {
          hint: '例: 39500 (整数値)',
          current: '現在値: 39,128円',
          range: '通常範囲: 20,000-50,000円'
        };
      case 'BTCUSD':
        return {
          hint: '例: 51200.50 (ドル単位)',
          current: '現在値: $50,847',
          range: '通常範囲: $20,000-$100,000'
        };
      default:
        return {
          hint: '数値を入力してください',
          current: '',
          range: ''
        };
    }
  };

  const getConfidenceColor = (conf: number) => {
    if (conf >= 80) return 'text-green-400';
    if (conf >= 60) return 'text-blue-400';
    if (conf >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 80) return '非常に高い';
    if (conf >= 60) return '高い';
    if (conf >= 40) return '普通';
    return '低い';
  };

  if (!isOpen || !contest) return null;

  const symbolHint = getSymbolHint(contest.target_symbol);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Target className="w-6 h-6" />
                予測を提出
              </h2>
              <p className="mt-1 text-blue-100">
                {contest.title}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Contest Details */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
            <div className="flex items-center mb-3">
              <Target className="w-5 h-5 text-purple-400 mr-2" />
              <h3 className="font-semibold text-white">チャレンジ内容</h3>
            </div>
            <p className="text-gray-300 mb-3">{contest.challenge}</p>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center text-blue-400">
                <span className="font-medium">{contest.target_symbol}</span>
                <span className="ml-2 text-gray-400">({contest.target_name})</span>
              </div>
              <div className="flex items-center text-yellow-400">
                <Calendar className="w-4 h-4 mr-1" />
                <span>締切まで: {formatTimeLeft(contest.submission_deadline)}</span>
              </div>
            </div>
          </div>

          {/* Current Market Info */}
          {symbolHint.current && (
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <TrendingUp className="w-4 h-4 text-blue-400 mr-2" />
                <span className="text-sm font-medium text-blue-400">市場情報</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-gray-300">
                  {symbolHint.current}
                </div>
                <div className="text-gray-400">
                  {symbolHint.range}
                </div>
              </div>
            </div>
          )}

          {/* Prediction Input */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                予測値
              </label>
              <input
                type="number"
                step="any"
                value={prediction}
                onChange={(e) => setPrediction(e.target.value)}
                placeholder={symbolHint.hint}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
              />
              {symbolHint.hint && (
                <p className="mt-1 text-xs text-gray-400">{symbolHint.hint}</p>
              )}
            </div>

            {/* Confidence Slider */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                予測への信頼度
              </label>
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={confidence}
                  onChange={(e) => setConfidence(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">0%</span>
                  <span className={`font-medium ${getConfidenceColor(confidence)}`}>
                    {confidence}% ({getConfidenceLabel(confidence)})
                  </span>
                  <span className="text-gray-400">100%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Reward Info */}
          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <Zap className="w-4 h-4 text-yellow-400 mr-2" />
              <span className="text-sm font-medium text-yellow-400">獲得可能報酬</span>
            </div>
            <p className="text-gray-300 text-sm">{contest.reward_description}</p>
            {contest.entry_fee > 0 && (
              <p className="text-red-400 text-xs mt-2">
                参加費: {contest.entry_fee}ポイント
              </p>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
              <div className="flex items-center">
                <AlertTriangle className="w-4 h-4 text-red-400 mr-2" />
                <span className="text-red-400 text-sm">{error}</span>
              </div>
            </div>
          )}

          {/* Previous Prediction Notice */}
          {contest.user_participated && contest.user_prediction !== undefined && (
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3">
              <div className="flex items-center">
                <Info className="w-4 h-4 text-green-400 mr-2" />
                <span className="text-green-400 text-sm">
                  前回の予測: {contest.user_prediction.toLocaleString()} 
                  {contest.user_participated && ' (変更されます)'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-800/50 px-6 py-4 border-t border-gray-700/50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              参加者数: {contest.current_participants.toLocaleString()}人
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={handleSubmit}
                disabled={!prediction || isSubmitting}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? '提出中...' : contest.user_participated ? '予測を更新' : '予測を提出'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}