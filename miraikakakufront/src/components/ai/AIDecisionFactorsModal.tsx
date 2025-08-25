'use client';

import React, { useState, useEffect } from 'react';
import { X, TrendingUp, TrendingDown, Info, ChevronRight, Brain } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface AIFactor {
  id: string;
  factor_name: string;
  factor_category: 'technical' | 'fundamental' | 'market' | 'sentiment' | 'pattern';
  impact_score: number; // -100 to +100
  impact_direction: 'positive' | 'negative' | 'neutral';
  explanation: string;
  confidence: number; // 0 to 1
  data_points?: {
    name: string;
    value: string | number;
  }[];
}

interface AIDecisionFactorsModalProps {
  predictionId: string;
  symbol: string;
  companyName: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function AIDecisionFactorsModal({
  predictionId,
  symbol,
  companyName,
  isOpen,
  onClose
}: AIDecisionFactorsModalProps) {
  const [factors, setFactors] = useState<AIFactor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [overallSummary, setOverallSummary] = useState<string>('');

  useEffect(() => {
    if (isOpen && predictionId) {
      fetchAIFactors();
    }
  }, [isOpen, predictionId]);

  const fetchAIFactors = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getAIDecisionFactors(predictionId);
      
      if (response.status === 'success' && response.data) {
        setFactors(response.data.factors);
        generateSummary(response.data.factors);
      }
    } catch (err) {
      setError('AI判断根拠の取得に失敗しました');
      console.error('Error fetching AI factors:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = (factorsList: AIFactor[]) => {
    const positiveCount = factorsList.filter(f => f.impact_direction === 'positive').length;
    const negativeCount = factorsList.filter(f => f.impact_direction === 'negative').length;
    const totalCount = factorsList.length;
    
    const sentiment = positiveCount > negativeCount ? '強気' : 
                     positiveCount < negativeCount ? '弱気' : '中立';
    
    setOverallSummary(
      `分析した${totalCount}の要因のうち、${positiveCount}つがポジティブ、${negativeCount}つがネガティブに作用し、総合的に${sentiment}のシグナルと判断しました。`
    );
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'technical': return 'text-blue-600 bg-blue-50';
      case 'fundamental': return 'text-green-600 bg-green-50';
      case 'market': return 'text-purple-600 bg-purple-50';
      case 'sentiment': return 'text-orange-600 bg-orange-50';
      case 'pattern': return 'text-pink-600 bg-pink-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'technical': return 'テクニカル指標';
      case 'fundamental': return 'ファンダメンタル';
      case 'market': return '市場環境';
      case 'sentiment': return 'センチメント';
      case 'pattern': return 'パターン認識';
      default: return category;
    }
  };

  const renderImpactBar = (score: number, direction: string) => {
    const absScore = Math.abs(score);
    const segments = 5;
    const filledSegments = Math.ceil((absScore / 100) * segments);
    
    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: segments }, (_, i) => (
          <div
            key={i}
            className={`h-2 w-6 rounded-sm ${
              i < filledSegments
                ? direction === 'positive'
                  ? 'bg-green-500'
                  : direction === 'negative'
                  ? 'bg-red-500'
                  : 'bg-gray-400'
                : 'bg-gray-200'
            }`}
          />
        ))}
        <span className="ml-2 text-sm font-medium">
          {direction === 'positive' ? '+' : direction === 'negative' ? '-' : ''}
          {absScore}%
        </span>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Brain className="w-6 h-6" />
                AIの判断根拠
              </h2>
              <p className="mt-1 text-blue-100">
                {companyName} ({symbol})
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
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          ) : (
            <>
              {/* Summary */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">総合評価</h3>
                    <p className="text-gray-700">{overallSummary}</p>
                  </div>
                </div>
              </div>

              {/* Factors List */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  影響要因（インパクトの大きい順）
                </h3>
                
                {factors.map((factor, index) => (
                  <div
                    key={factor.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {factor.impact_direction === 'positive' ? (
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : factor.impact_direction === 'negative' ? (
                          <TrendingDown className="w-5 h-5 text-red-600" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        )}
                        <div>
                          <h4 className="font-semibold text-gray-900">
                            {index + 1}. {factor.factor_name}
                          </h4>
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 ${getCategoryColor(factor.factor_category)}`}>
                            {getCategoryLabel(factor.factor_category)}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500 mb-1">影響度</div>
                        {renderImpactBar(factor.impact_score, factor.impact_direction)}
                      </div>
                    </div>

                    <p className="text-gray-700 text-sm leading-relaxed mb-3">
                      {factor.explanation}
                    </p>

                    {factor.data_points && factor.data_points.length > 0 && (
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-600 mb-2">関連データ</div>
                        <div className="flex flex-wrap gap-3">
                          {factor.data_points.map((point, idx) => (
                            <div key={idx} className="bg-white rounded px-2 py-1 text-xs">
                              <span className="text-gray-600">{point.name}: </span>
                              <span className="font-medium text-gray-900">{point.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                      <span className="text-xs text-gray-500">
                        信頼度: {Math.round(factor.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Link to detailed documentation */}
              <div className="mt-8 p-4 bg-gray-50 rounded-lg text-center">
                <a
                  href="/ai-methodology"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm inline-flex items-center gap-1"
                >
                  AIモデルの仕組みと全要因一覧
                  <ChevronRight className="w-4 h-4" />
                </a>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}