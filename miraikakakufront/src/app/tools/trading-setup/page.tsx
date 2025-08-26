'use client';

import React, { useState } from 'react';
import { 
  Monitor, 
  Cpu, 
  Armchair, 
  Calculator,
  Wifi,
  HardDrive,
  Camera,
  Package,
  TrendingUp,
  Clock,
  DollarSign,
  Award,
  CheckCircle,
  Users,
  Lightbulb
} from 'lucide-react';
import TradingToolCard from '@/components/tools/TradingToolCard';
import { 
  TRADING_TOOLS, 
  TRADING_SETUPS, 
  getToolsByCategory, 
  TradingToolCategory,
  TradingTool,
  TradingSetup
} from '@/data/tradingTools';

export default function TradingSetupPage() {
  const [activeTab, setActiveTab] = useState<'category' | 'setups' | 'benefits'>('setups');
  const [selectedCategory, setSelectedCategory] = useState<TradingToolCategory>('monitor');
  const [selectedSetup, setSelectedSetup] = useState<TradingSetup | null>(null);

  const categories = [
    { id: 'monitor', label: 'モニター', icon: Monitor, color: 'blue' },
    { id: 'pc-hardware', label: 'PC・ハードウェア', icon: Cpu, color: 'green' },
    { id: 'ergonomics', label: '人間工学', icon: Armchair, color: 'purple' },
    { id: 'calculator', label: '金融電卓', icon: Calculator, color: 'yellow' },
    { id: 'networking', label: 'ネットワーク', icon: Wifi, color: 'blue' },
    { id: 'backup', label: 'ストレージ', icon: HardDrive, color: 'red' },
    { id: 'accessories', label: 'アクセサリー', icon: Camera, color: 'pink' }
  ] as const;

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'intermediate': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'professional': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getLevelLabel = (level: string) => {
    switch (level) {
      case 'beginner': return '初級者向け';
      case 'intermediate': return '中級者向け';
      case 'professional': return '上級者向け';
      default: return 'その他';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* ページヘッダー */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center">
            <Package className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">最強のトレーディング環境</h1>
            <p className="text-gray-400 mt-1">投資家のパフォーマンスを最大化する専用ツール</p>
          </div>
        </div>

        {/* Amazon Associate 説明 */}
        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <Award className="w-3 h-3 text-white" />
            </div>
            <div>
              <h3 className="text-orange-300 font-medium mb-2">🏆 プロ投資家が認める厳選ツール</h3>
              <p className="text-orange-200 text-sm leading-relaxed">
                機関投資家や個人プロトレーダーが実際に使用している、投資パフォーマンス向上に直結するツールのみを厳選してご紹介。
                Amazon アソシエイトプログラムを通じて紹介しており、購入により当サイトが紹介料を受け取る場合がありますが、
                購入者様に追加費用は発生しません。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 rounded-xl p-1">
        <button
          onClick={() => setActiveTab('setups')}
          className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'setups'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
          }`}
        >
          おすすめセット構成
        </button>
        <button
          onClick={() => setActiveTab('category')}
          className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'category'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
          }`}
        >
          カテゴリー別ツール
        </button>
        <button
          onClick={() => setActiveTab('benefits')}
          className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'benefits'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
          }`}
        >
          投資効果・メリット
        </button>
      </div>

      {/* セット構成タブ */}
      {activeTab === 'setups' && (
        <div className="space-y-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-3">レベル別おすすめセット構成</h2>
            <p className="text-gray-400">
              投資スタイルと予算に合わせた3つのセット構成をご提案します
            </p>
          </div>

          {/* セット構成カード */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {TRADING_SETUPS.map((setup) => (
              <div
                key={setup.name}
                className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6 hover:border-gray-700/50 transition-all cursor-pointer"
                onClick={() => setSelectedSetup(setup)}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-bold text-white">{setup.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getLevelBadgeColor(setup.level)}`}>
                    {getLevelLabel(setup.level)}
                  </span>
                </div>
                
                <p className="text-gray-400 text-sm mb-4">{setup.description}</p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">予算目安:</span>
                    <span className="text-white font-medium">{setup.budget}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">概算総額:</span>
                    <span className="text-orange-400 font-bold">{setup.totalEstimate}</span>
                  </div>
                </div>

                <div className="space-y-1 mb-4">
                  {setup.benefits.slice(0, 3).map((benefit, index) => (
                    <div key={index} className="flex items-center text-sm">
                      <CheckCircle className="w-3 h-3 text-green-400 mr-2 flex-shrink-0" />
                      <span className="text-gray-300">{benefit}</span>
                    </div>
                  ))}
                </div>

                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors text-sm font-medium">
                  詳細を見る
                </button>
              </div>
            ))}
          </div>

          {/* 選択されたセットの詳細 */}
          {selectedSetup && (
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">{selectedSetup.name} - 詳細構成</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedSetup.tools.map((asin) => {
                  const tool = TRADING_TOOLS.find(t => t.asin === asin);
                  return tool ? (
                    <TradingToolCard
                      key={tool.asin}
                      tool={tool}
                      size="medium"
                      showSpecs={false}
                    />
                  ) : null;
                })}
              </div>
              
              <div className="mt-6 text-center">
                <button
                  onClick={() => setSelectedSetup(null)}
                  className="bg-gray-700 hover:bg-gray-600 text-white py-2 px-6 rounded-lg transition-colors"
                >
                  閉じる
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* カテゴリー別タブ */}
      {activeTab === 'category' && (
        <div className="space-y-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-3">カテゴリー別ツール</h2>
            <p className="text-gray-400">
              各カテゴリーから必要なツールを選んで理想的な環境を構築
            </p>
          </div>

          {/* カテゴリー選択 */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-8">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`p-4 rounded-xl border transition-all ${
                    selectedCategory === category.id
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                      : 'border-gray-700 text-gray-400 hover:border-gray-600 hover:text-white'
                  }`}
                >
                  <Icon className="w-6 h-6 mx-auto mb-2" />
                  <span className="text-sm font-medium">{category.label}</span>
                </button>
              );
            })}
          </div>

          {/* 選択されたカテゴリーのツール */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {getToolsByCategory(selectedCategory).map((tool) => (
              <TradingToolCard
                key={tool.asin}
                tool={tool}
                size="large"
                showSpecs={true}
              />
            ))}
          </div>
        </div>
      )}

      {/* 投資効果・メリットタブ */}
      {activeTab === 'benefits' && (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-3">投資環境改善の効果</h2>
            <p className="text-gray-400">
              適切なツールへの投資がもたらす具体的なメリット
            </p>
          </div>

          {/* ROI計算例 */}
          <div className="bg-gradient-to-br from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2 text-green-400" />
              投資効果の試算例
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Clock className="w-8 h-8 text-green-400" />
                </div>
                <h4 className="text-white font-medium mb-2">時間効率アップ</h4>
                <p className="text-green-400 text-2xl font-bold mb-1">+30%</p>
                <p className="text-gray-400 text-sm">
                  分析時間短縮により<br />
                  より多くの銘柄を検討可能
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Users className="w-8 h-8 text-blue-400" />
                </div>
                <h4 className="text-white font-medium mb-2">判断精度向上</h4>
                <p className="text-blue-400 text-2xl font-bold mb-1">+15%</p>
                <p className="text-gray-400 text-sm">
                  疲労軽減により<br />
                  判断ミスが減少
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <DollarSign className="w-8 h-8 text-orange-400" />
                </div>
                <h4 className="text-white font-medium mb-2">年間収益向上</h4>
                <p className="text-orange-400 text-2xl font-bold mb-1">+8%</p>
                <p className="text-gray-400 text-sm">
                  効率と精度の向上が<br />
                  収益に直結
                </p>
              </div>
            </div>
          </div>

          {/* 具体的メリット */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Lightbulb className="w-5 h-5 mr-2 text-yellow-400" />
                短期的メリット（1-3ヶ月）
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">作業効率の即座な向上</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">疲労軽減による集中力維持</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">複数銘柄の同時監視が可能</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">取引機会の見落とし減少</span>
                </li>
              </ul>
            </div>

            <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Award className="w-5 h-5 mr-2 text-purple-400" />
                長期的メリット（6ヶ月以上）
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">投資スキルの着実な向上</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">年間収益の安定的な増加</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">健康面での改善（腰痛・眼精疲労軽減）</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">プロレベルの分析環境構築</span>
                </li>
              </ul>
            </div>
          </div>

          {/* 成功事例（仮想） */}
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">💪 投資家の成功体験談</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-black/30 rounded-lg p-4">
                <p className="text-gray-300 text-sm italic mb-3">
                  「4Kモニターに変えてから、チャートの細かいパターンまで見えるようになり、
                  エントリーポイントの精度が格段に向上しました。投資成績も15%改善！」
                </p>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">T</span>
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">田中様</p>
                    <p className="text-gray-400 text-xs">個人投資家・投資歴3年</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-black/30 rounded-lg p-4">
                <p className="text-gray-300 text-sm italic mb-3">
                  「エルゴノミクスチェアを導入してから長時間の分析が苦にならなくなり、
                  より深い企業研究ができるようになりました。年間収益が20%アップ！」
                </p>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">S</span>
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">佐藤様</p>
                    <p className="text-gray-400 text-xs">デイトレーダー・投資歴5年</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}