'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp
  TrendingDown
  BarChart3
  PieChart
  Target
  AlertTriangle
  CheckCircle
  XCircle
  Activity
  Zap
  DollarSign
  Calendar
  Percent
} from 'lucide-react';

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: 'buy' | 'sell' | 'hold';
  strength: number; // 0-100
  description: string;
}

interface RiskMetrics {
  volatility: number;
  beta: number;
  sharpeRatio: number;
  maxDrawdown: number;
  var95: number; // Value at Risk 95%
}

interface FundamentalAnalysis {
  peRatio: number;
  pegRatio: number;
  priceToBook: number;
  debtToEquity: number;
  roe: number;
  roa: number;
  profitMargin: number;
  revenueGrowth: number;
}

interface MarketSentiment {
  analystRating: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  priceTarget: number;
  upside: number;
  newsScore: number; // -1 to 1
  socialScore: number; // -1 to 1
  optionsFlow: 'bullish' | 'bearish' | 'neutral';
}

interface AdvancedAnalysisProps {
  symbol: string;
  currentPrice: number;
  className?: string;
}

export const AdvancedAnalysis: React.FC<AdvancedAnalysisProps> = ({
  symbol
  currentPrice
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'technical' | 'fundamental' | 'risk' | 'sentiment'>('technical'
  const [loading, setLoading] = useState(false
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicator[]>([]
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null
  const [fundamentalData, setFundamentalData] = useState<FundamentalAnalysis | null>(null
  const [marketSentiment, setMarketSentiment] = useState<MarketSentiment | null>(null
  useEffect(() => {
    if (symbol) {
      fetchAdvancedAnalysis(
    }
  }, [symbol]
  const fetchAdvancedAnalysis = async () => {
    setLoading(true
    try {
      // This would normally fetch from your backend API
      // For now, we'll simulate realistic data

      // Simulate technical indicators
      const mockTechnical: TechnicalIndicator[] = [
        {
          name: 'RSI (14)'
          value: 65.8
          signal: 'buy'
          strength: 75
          description: 'Relative Strength Index showing moderate overbought conditions'
        }
        {
          name: 'MACD'
          value: 2.34
          signal: 'buy'
          strength: 85
          description: 'MACD line above signal line indicating bullish momentum'
        }
        {
          name: 'Moving Average (50)'
          value: currentPrice * 0.98
          signal: 'buy'
          strength: 70
          description: 'Price trading above 50-day moving average'
        }
        {
          name: 'Bollinger Bands'
          value: 0.78
          signal: 'hold'
          strength: 60
          description: 'Price in middle of Bollinger Bands, neutral signal'
        }
        {
          name: 'Volume Trend'
          value: 1.25
          signal: 'buy'
          strength: 80
          description: 'Above average volume supporting price movement'
        }
      ];

      // Simulate risk metrics
      const mockRisk: RiskMetrics = {
        volatility: 24.5
        beta: 1.15
        sharpeRatio: 1.8
        maxDrawdown: -18.2
        var95: -12.8
      };

      // Simulate fundamental data
      const mockFundamental: FundamentalAnalysis = {
        peRatio: 22.5
        pegRatio: 1.8
        priceToBook: 3.2
        debtToEquity: 0.45
        roe: 18.5
        roa: 12.3
        profitMargin: 15.2
        revenueGrowth: 12.8
      };

      // Simulate market sentiment
      const mockSentiment: MarketSentiment = {
        analystRating: 'buy'
        priceTarget: currentPrice * 1.15
        upside: 15.0
        newsScore: 0.3
        socialScore: 0.2
        optionsFlow: 'bullish'
      };

      setTechnicalIndicators(mockTechnical
      setRiskMetrics(mockRisk
      setFundamentalData(mockFundamental
      setMarketSentiment(mockSentiment
    } catch (error) {
      } finally {
      setLoading(false
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy'
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'sell'
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default
        return <Activity className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy'
        return 'text-green-600 bg-green-50 border-green-200';
      case 'sell'
        return 'text-red-600 bg-red-50 border-red-200';
      default
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  const getStrengthBar = (strength: number) => (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full ${
          strength >= 70 ? 'bg-green-500'
          strength >= 40 ? 'bg-yellow-500' : 'bg-red-500'
        }`}
        style={{ width: `${strength}%` }}
      />
    </div>
  const renderTechnicalAnalysis = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Technical Indicators */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            テクニカル指標
          </h3>
          {technicalIndicators.map((indicator, index) => (
            <div key={index} className="bg-white border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getSignalIcon(indicator.signal)}
                  <span className="font-medium text-gray-900">{indicator.name}</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSignalColor(indicator.signal)}`}>
                  {indicator.signal.toUpperCase()}
                </span>
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {indicator.value.toFixed(2)}
              </div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-sm text-gray-600">強度:</span>
                {getStrengthBar(indicator.strength)}
                <span className="text-sm font-medium">{indicator.strength}%</span>
              </div>
              <p className="text-sm text-gray-600">{indicator.description}</p>
            </div>
          ))}
        </div>

        {/* Signal Summary */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Target className="w-5 h-5 mr-2" />
            シグナル総合評価
          </h3>

          {/* Overall Signal */}
          <div className="bg-white border rounded-lg p-6">
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                <TrendingUp className="w-12 h-12 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-green-600 mb-2">買いシグナル</h4>
              <p className="text-gray-600 mb-4">
                複数の指標が強気を示しています
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="text-sm text-green-700">
                  信頼度: <span className="font-bold">78%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Signal Distribution */}
          <div className="bg-white border rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-3">シグナル分布</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">買い</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '60%' }} />
                  </div>
                  <span className="text-sm font-medium">3</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">ホールド</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '20%' }} />
                  </div>
                  <span className="text-sm font-medium">1</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">売り</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }} />
                  </div>
                  <span className="text-sm font-medium">1</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  const renderFundamentalAnalysis = () => (
    <div className="space-y-6">
      {fundamentalData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">PER</span>
              <DollarSign className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{fundamentalData.peRatio}</div>
            <p className="text-xs text-gray-500">株価収益率</p>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">PEG</span>
              <Percent className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{fundamentalData.pegRatio}</div>
            <p className="text-xs text-gray-500">成長調整PER</p>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">ROE</span>
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{fundamentalData.roe}%</div>
            <p className="text-xs text-gray-500">自己資本利益率</p>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">成長率</span>
              <Activity className="w-4 h-4 text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-green-600">+{fundamentalData.revenueGrowth}%</div>
            <p className="text-xs text-gray-500">売上成長率</p>
          </div>
        </div>
      )}
    </div>
  const renderRiskAnalysis = () => (
    <div className="space-y-6">
      {riskMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              リスク指標
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ボラティリティ</span>
                <span className="font-semibold">{riskMetrics.volatility}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ベータ値</span>
                <span className="font-semibold">{riskMetrics.beta}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">シャープレシオ</span>
                <span className="font-semibold text-green-600">{riskMetrics.sharpeRatio}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">最大ドローダウン</span>
                <span className="font-semibold text-red-600">{riskMetrics.maxDrawdown}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">VaR (95%)</span>
                <span className="font-semibold text-orange-600">{riskMetrics.var95}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">リスク評価</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-sm">適度なボラティリティ</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-sm">優秀なシャープレシオ</span>
              </div>
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <span className="text-sm">市場より高いベータ</span>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
                <p className="text-sm text-blue-700">
                  <strong>総合評価:</strong> 中程度のリスクで良好なリターンが期待できます。
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  const renderMarketSentiment = () => (
    <div className="space-y-6">
      {marketSentiment && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <PieChart className="w-5 h-5 mr-2" />
              アナリスト評価
            </h3>
            <div className="text-center mb-4">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {marketSentiment.analystRating.replace('_', ' ').toUpperCase()}
              </div>
              <div className="text-gray-600">
                目標価格: <span className="font-semibold">${marketSentiment.priceTarget.toFixed(2)}</span>
              </div>
              <div className="text-green-600 font-semibold">
                上昇余地: +{marketSentiment.upside.toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">センチメント指標</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">ニューススコア</span>
                  <span className="text-sm font-medium text-green-600">+{(marketSentiment.newsScore * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${((marketSentiment.newsScore + 1) / 2) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">ソーシャルスコア</span>
                  <span className="text-sm font-medium text-green-600">+{(marketSentiment.socialScore * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${((marketSentiment.socialScore + 1) / 2) * 100}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-600">オプションフロー</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  marketSentiment.optionsFlow === 'bullish' ? 'bg-green-100 text-green-800'
                  marketSentiment.optionsFlow === 'bearish' ? 'bg-red-100 text-red-800'
                  'bg-gray-100 text-gray-800'
                }`}>
                  {marketSentiment.optionsFlow.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  return (
    <div className={`bg-gray-50 rounded-lg p-6 ${className}`}>
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
        <Zap className="w-6 h-6 mr-2" />
        高度な投資分析
      </h2>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
        {[
          { key: 'technical', label: 'テクニカル', icon: BarChart3 }
          { key: 'fundamental', label: 'ファンダメンタル', icon: DollarSign }
          { key: 'risk', label: 'リスク', icon: AlertTriangle }
          { key: 'sentiment', label: 'センチメント', icon: PieChart }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
              activeTab === key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span className="font-medium">{label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'technical' && renderTechnicalAnalysis()}
          {activeTab === 'fundamental' && renderFundamentalAnalysis()}
          {activeTab === 'risk' && renderRiskAnalysis()}
          {activeTab === 'sentiment' && renderMarketSentiment()}
        </>
      )}
    </div>
};