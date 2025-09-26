'use client';

import React from 'react';
import { DollarSign, Shield, AlertCircle } from 'lucide-react';
import { StockDetails } from '../types';

interface FinancialAnalysisProps {
  details: StockDetails | null;
  financialAnalysis?: any;
  riskAnalysis?: any;
}

interface FinancialMetric {
  name: string;
  value: string | number;
  benchmark: string;
  status: 'excellent' | 'good' | 'fair' | 'poor';
  description: string;
}

interface RiskMetric {
  name: string;
  value: string;
  level: 'low' | 'medium' | 'high';
  description: string;
}

export default function FinancialAnalysis({ details, financialAnalysis, riskAnalysis }: FinancialAnalysisProps) {
  // Always show the component UI, even if data is not available
  // The individual sections will handle their own data availability checks

  // Calculate financial metrics
  const calculateFinancialMetrics = (): FinancialMetric[] => {
    const metrics: FinancialMetric[] = [];

    // Use new API data if available, fallback to old structure
    if (financialAnalysis?.metrics) {
      // P/E Ratio from new API
      if (financialAnalysis.metrics.pe_ratio) {
        const pe = financialAnalysis.metrics.pe_ratio;
        let status: 'excellent' | 'good' | 'fair' | 'poor';
        let benchmark: string;

        if (pe < 15) {
          status = 'excellent';
          benchmark = 'とても魅力的';
        } else if (pe < 20) {
          status = 'good';
          benchmark = '魅力的';
        } else if (pe < 30) {
          status = 'fair';
          benchmark = '標準的';
        } else {
          status = 'poor';
          benchmark = '割高の可能性';
        }

        metrics.push({
          name: 'P/E Ratio',
          value: pe.toFixed(1),
          benchmark,
          status,
          description: 'Price-to-Earnings Ratio - 株価収益率。低いほど割安とされる'
        });
      }

      // Market Cap from new API
      if (financialAnalysis.metrics.market_cap) {
        const marketCapB = financialAnalysis.metrics.market_cap / 1e9;
        let status: 'excellent' | 'good' | 'fair' | 'poor';
        let benchmark: string;

        if (marketCapB > 100) {
          status = 'excellent';
          benchmark = '超大型株';
        } else if (marketCapB > 10) {
          status = 'good';
          benchmark = '大型株';
        } else if (marketCapB > 2) {
          status = 'fair';
          benchmark = '中型株';
        } else {
          status = 'poor';
          benchmark = '小型株';
        }

        metrics.push({
          name: '時価総額',
          value: `${marketCapB.toFixed(1)}B`,
          benchmark,
          status,
          description: '企業の市場価値。大きいほど安定性が高い傾向'
        });
      }

      // Beta from new API
      if (financialAnalysis.metrics.beta) {
        const beta = financialAnalysis.metrics.beta;
        let status: 'excellent' | 'good' | 'fair' | 'poor';
        let benchmark: string;

        if (beta < 0.8) {
          status = 'excellent';
          benchmark = '低リスク';
        } else if (beta < 1.2) {
          status = 'good';
          benchmark = '標準リスク';
        } else if (beta < 1.5) {
          status = 'fair';
          benchmark = 'やや高リスク';
        } else {
          status = 'poor';
          benchmark = '高リスク';
        }

        metrics.push({
          name: 'ベータ値',
          value: beta.toFixed(2),
          benchmark,
          status,
          description: '市場との連動性。1.0が市場平均、高いほど変動が大きい'
        });
      }

      // Dividend Yield from new API
      if (financialAnalysis.metrics.dividend_yield) {
        const divYield = financialAnalysis.metrics.dividend_yield;
        let status: 'excellent' | 'good' | 'fair' | 'poor';
        let benchmark: string;

        if (divYield > 4) {
          status = 'excellent';
          benchmark = '高配当';
        } else if (divYield > 2) {
          status = 'good';
          benchmark = '魅力的な配当';
        } else if (divYield > 1) {
          status = 'fair';
          benchmark = '標準的配当';
        } else {
          status = 'poor';
          benchmark = '低配当/無配当';
        }

        metrics.push({
          name: '配当利回り',
          value: `${divYield.toFixed(1)}%`,
          benchmark,
          status,
          description: '年間配当金の株価に対する割合。インカムゲインの指標'
        })
      }

      return metrics;
    }

    // Fallback to old structure if new API data not available
    if (!details) return metrics;

    // P/E Ratio from old structure
    if (details.trailingPE) {
      const pe = details.trailingPE;
      let status: 'excellent' | 'good' | 'fair' | 'poor';
      let benchmark: string;

      if (pe < 15) {
        status = 'excellent';
        benchmark = 'とても魅力的';
      } else if (pe < 20) {
        status = 'good';
        benchmark = '魅力的';
      } else if (pe < 30) {
        status = 'fair';
        benchmark = '標準的';
      } else {
        status = 'poor';
        benchmark = '割高の可能性';
      }

      metrics.push({
        name: 'P/E Ratio',
        value: pe.toFixed(1),
        benchmark,
        status,
        description: 'Price-to-Earnings Ratio - 株価収益率。低いほど割安とされる'
      });
    }

    // Market Cap analysis
    if (details.marketCap) {
      const marketCapB = details.marketCap / 1e9;
      let status: 'excellent' | 'good' | 'fair' | 'poor';
      let benchmark: string;

      if (marketCapB > 100) {
        status = 'excellent';
        benchmark = '超大型株';
      } else if (marketCapB > 10) {
        status = 'good';
        benchmark = '大型株';
      } else if (marketCapB > 2) {
        status = 'fair';
        benchmark = '中型株';
      } else {
        status = 'poor';
        benchmark = '小型株';
      }

      metrics.push({
        name: '時価総額',
        value: `${marketCapB.toFixed(1)}B`,
        benchmark,
        status,
        description: '企業の市場価値。大きいほど安定性が高い傾向'
      });
    }

    // Beta analysis
    if (details.beta) {
      const beta = details.beta;
      let status: 'excellent' | 'good' | 'fair' | 'poor';
      let benchmark: string;

      if (beta < 0.8) {
        status = 'excellent';
        benchmark = '低リスク';
      } else if (beta < 1.2) {
        status = 'good';
        benchmark = '標準リスク';
      } else if (beta < 1.5) {
        status = 'fair';
        benchmark = 'やや高リスク';
      } else {
        status = 'poor';
        benchmark = '高リスク';
      }

      metrics.push({
        name: 'ベータ値',
        value: beta.toFixed(2),
        benchmark,
        status,
        description: '市場との連動性。1.0が市場平均、高いほど変動が大きい'
      });
    }

    // Dividend Yield
    if (details.dividendYield) {
      const divYield = details.dividendYield * 100;
      let status: 'excellent' | 'good' | 'fair' | 'poor';
      let benchmark: string;

      if (divYield > 4) {
        status = 'excellent';
        benchmark = '高配当';
      } else if (divYield > 2) {
        status = 'good';
        benchmark = '魅力的な配当';
      } else if (divYield > 1) {
        status = 'fair';
        benchmark = '標準的配当';
      } else {
        status = 'poor';
        benchmark = '低配当/無配当';
      }

      metrics.push({
        name: '配当利回り',
        value: `${divYield.toFixed(1)}%`,
        benchmark,
        status,
        description: '年間配当金の株価に対する割合。インカムゲインの指標'
      });
    }

    return metrics;
  };

  // Calculate risk metrics
  const calculateRiskMetrics = (): RiskMetric[] => {
    const risks: RiskMetric[] = [];

    // Use new API data if available
    if (riskAnalysis?.factors) {
      return riskAnalysis.factors.map((factor: any) => ({
        name: factor.name,
        value: typeof factor.value === 'number' ? factor.value.toFixed(1) : factor.value.toString(),
        level: factor.level === '高' ? 'high' : factor.level === '中' ? 'medium' : 'low',
        description: factor.description
      }));
    }

    // Fallback to old structure if new API data not available
    if (!details) return risks;

    // Beta risk assessment from old structure
    if (details.beta) {
      const beta = details.beta;
      let level: 'low' | 'medium' | 'high';
      let description: string;

      if (beta < 0.8) {
        level = 'low';
        description = '市場より安定した値動き、保守的な投資に適している';
      } else if (beta < 1.5) {
        level = 'medium';
        description = '市場と同程度またはやや高い変動性、バランス型投資';
      } else {
        level = 'high';
        description = '市場より大幅に高い変動性、積極的な投資家向け';
      }

      risks.push({
        name: 'ボラティリティリスク',
        value: beta.toFixed(2),
        level,
        description
      });
    }

    // Market cap risk
    if (details.marketCap) {
      const marketCapB = details.marketCap / 1e9;
      let level: 'low' | 'medium' | 'high';
      let description: string;

      if (marketCapB > 50) {
        level = 'low';
        description = '大型株として安定性が高く、流動性リスクは低い';
      } else if (marketCapB > 5) {
        level = 'medium';
        description = '中型株として適度な安定性、標準的な流動性';
      } else {
        level = 'high';
        description = '小型株として変動性が高く、流動性リスクに注意';
      }

      risks.push({
        name: '流動性リスク',
        value: `${marketCapB.toFixed(1)}B`,
        level,
        description
      });
    }

    // Valuation risk
    if (details.trailingPE) {
      const pe = details.trailingPE;
      let level: 'low' | 'medium' | 'high';
      let description: string;

      if (pe < 15) {
        level = 'low';
        description = '適正またはやや割安な水準、下落リスクは限定的';
      } else if (pe < 25) {
        level = 'medium';
        description = 'やや割高な可能性、市場調整時の影響に注意';
      } else {
        level = 'high';
        description = '割高な可能性が高く、大幅な調整リスクあり';
      }

      risks.push({
        name: 'バリュエーションリスク',
        value: pe.toFixed(1),
        level,
        description
      });
    }

    return risks;
  };

  const financialMetrics = calculateFinancialMetrics();
  const riskMetrics = calculateRiskMetrics();
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200';
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'fair': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'poor': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Financial Metrics */}
      <div className="rounded-lg shadow-md p-6" style={{
        backgroundColor: 'var(--yt-music-surface)',
        border: '1px solid var(--yt-music-border)'
      }}>
        <h2 className="text-2xl font-semibold mb-4 flex items-center" style={{ color: 'var(--yt-music-text-primary)' }}>
          <DollarSign className="w-6 h-6 mr-2" />
          財務分析
        </h2>

        {financialMetrics.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {financialMetrics.map((metric, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4" style={{
                backgroundColor: 'var(--yt-music-bg)'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium" style={{ color: 'var(--yt-music-text-primary)' }}>
                    {metric.name}
                  </h4>
                  <div className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(metric.status)}`}>
                    {metric.benchmark}
                  </div>
                </div>
                <div className="text-2xl font-bold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {metric.value}
                </div>
                <p className="text-sm" style={{ color: 'var(--yt-music-text-secondary)' }}>
                  {metric.description}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">財務指標データが不足しています</p>
        )}
      </div>

      {/* Risk Analysis */}
      <div className="rounded-lg shadow-md p-6" style={{
        backgroundColor: 'var(--yt-music-surface)',
        border: '1px solid var(--yt-music-border)'
      }}>
        <h2 className="text-2xl font-semibold mb-4 flex items-center" style={{ color: 'var(--yt-music-text-primary)' }}>
          <Shield className="w-6 h-6 mr-2" />
          リスク分析
        </h2>

        {riskMetrics.length > 0 ? (
          <div className="space-y-4">
            {riskMetrics.map((risk, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4" style={{
                backgroundColor: 'var(--yt-music-bg)'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium" style={{ color: 'var(--yt-music-text-primary)' }}>
                    {risk.name}
                  </h4>
                  <div className={`px-2 py-1 rounded text-xs font-medium border ${getRiskColor(risk.level)}`}>
                    {risk.level.toUpperCase()}
                  </div>
                </div>
                <div className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>
                  {risk.value}
                </div>
                <p className="text-sm" style={{ color: 'var(--yt-music-text-secondary)' }}>
                  {risk.description}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">リスク分析データが不足しています</p>
        )}

        {/* Investment Warning */}
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2 mt-0.5" />
            <div className="text-sm text-red-800">
              <strong>投資リスク警告:</strong> 投資には元本割れのリスクがあります。
              過去の実績は将来の成果を保証するものではありません。投資判断は自己責任で行ってください。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}