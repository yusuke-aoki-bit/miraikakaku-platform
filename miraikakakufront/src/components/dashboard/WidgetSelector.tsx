'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDashboardStore } from '@/store/dashboardStore';
import { WidgetType } from '@/types/dashboard';
import { 
  X, 
  TrendingUp, 
  Table, 
  BarChart3, 
  Newspaper,
  PieChart,
  Briefcase,
  BookmarkCheck,
  Activity,
  Target,
  AlertTriangle,
  History,
  Bell,
  Search,
  Filter,
  Star
} from 'lucide-react';

interface WidgetSelectorProps {
  layoutId: string;
  onClose: () => void;
  userMode: 'light' | 'pro';
}

const WIDGET_CATALOG = [
  {
    type: 'price-prediction-chart' as WidgetType,
    name: 'AI価格予測チャート',
    description: '機械学習による株価予測と信頼区間を表示',
    icon: TrendingUp,
    category: 'charts',
    userLevel: ['intermediate', 'advanced'],
    tags: ['AI', '予測', 'チャート'],
    featured: true,
  },
  {
    type: 'market-overview' as WidgetType,
    name: 'マーケット概要',
    description: '主要指数と市場全体の動向',
    icon: PieChart,
    category: 'overview',
    userLevel: ['beginner', 'intermediate', 'advanced'],
    tags: ['市場', '概要', '指数'],
    featured: true,
  },
  {
    type: 'portfolio-summary' as WidgetType,
    name: 'ポートフォリオ概要',
    description: '資産配分とパフォーマンス概要',
    icon: Briefcase,
    category: 'portfolio',
    userLevel: ['beginner', 'intermediate', 'advanced'],
    tags: ['ポートフォリオ', '資産', 'パフォーマンス'],
    featured: true,
  },
  {
    type: 'watchlist' as WidgetType,
    name: 'ウォッチリスト',
    description: '関心銘柄の一覧と価格変動',
    icon: BookmarkCheck,
    category: 'portfolio',
    userLevel: ['beginner', 'intermediate', 'advanced'],
    tags: ['ウォッチリスト', '銘柄', '監視'],
    featured: false,
  },
  {
    type: 'real-time-prices' as WidgetType,
    name: 'リアルタイム価格',
    description: 'リアルタイムの株価と出来高',
    icon: Activity,
    category: 'data',
    userLevel: ['intermediate', 'advanced'],
    tags: ['リアルタイム', '価格', 'ライブ'],
    featured: false,
  },
  {
    type: 'technical-indicators' as WidgetType,
    name: 'テクニカル指標',
    description: 'RSI、MACD等のテクニカル分析',
    icon: Target,
    category: 'analysis',
    userLevel: ['intermediate', 'advanced'],
    tags: ['テクニカル', '分析', '指標'],
    featured: false,
  },
  {
    type: 'news-sentiment' as WidgetType,
    name: 'ニュース・センチメント',
    description: '市場ニュースと感情分析',
    icon: Newspaper,
    category: 'news',
    userLevel: ['beginner', 'intermediate', 'advanced'],
    tags: ['ニュース', 'センチメント', '感情分析'],
    featured: false,
  },
  {
    type: 'risk-analysis' as WidgetType,
    name: 'リスク分析',
    description: 'VaR、相関分析、リスク指標',
    icon: AlertTriangle,
    category: 'analysis',
    userLevel: ['advanced'],
    tags: ['リスク', 'VaR', '相関'],
    featured: false,
  },
  {
    type: 'kpi-scorecard' as WidgetType,
    name: 'KPIスコアカード',
    description: '重要指標の一覧表示',
    icon: BarChart3,
    category: 'data',
    userLevel: ['intermediate', 'advanced'],
    tags: ['KPI', '指標', 'メトリクス'],
    featured: false,
  },
  {
    type: 'data-table' as WidgetType,
    name: 'データテーブル',
    description: 'カスタマイズ可能なデータ表',
    icon: Table,
    category: 'data',
    userLevel: ['intermediate', 'advanced'],
    tags: ['データ', 'テーブル', '一覧'],
    featured: false,
  },
  {
    type: 'trading-history' as WidgetType,
    name: '取引履歴',
    description: '過去の取引記録と分析',
    icon: History,
    category: 'portfolio',
    userLevel: ['intermediate', 'advanced'],
    tags: ['取引', '履歴', '分析'],
    featured: false,
  },
  {
    type: 'alerts-panel' as WidgetType,
    name: 'アラートパネル',
    description: '価格アラートと通知設定',
    icon: Bell,
    category: 'alerts',
    userLevel: ['beginner', 'intermediate', 'advanced'],
    tags: ['アラート', '通知', 'アラーム'],
    featured: false,
  },
];

const CATEGORIES = [
  { id: 'all', name: 'すべて' },
  { id: 'overview', name: '概要' },
  { id: 'charts', name: 'チャート' },
  { id: 'portfolio', name: 'ポートフォリオ' },
  { id: 'data', name: 'データ' },
  { id: 'analysis', name: '分析' },
  { id: 'news', name: 'ニュース' },
  { id: 'alerts', name: 'アラート' },
];

export default function WidgetSelector({ layoutId, onClose, userMode }: WidgetSelectorProps) {
  const { addWidget } = useDashboardStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showAdvanced, setShowAdvanced] = useState(userMode === 'pro');

  const filteredWidgets = WIDGET_CATALOG.filter(widget => {
    // Filter by user level
    const levelMatch = showAdvanced || 
      widget.userLevel.includes('beginner') || 
      (userMode === 'pro' && widget.userLevel.includes('intermediate'));
    
    // Filter by category
    const categoryMatch = selectedCategory === 'all' || widget.category === selectedCategory;
    
    // Filter by search term
    const searchMatch = !searchTerm || 
      widget.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      widget.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      widget.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return levelMatch && categoryMatch && searchMatch;
  });

  const featuredWidgets = filteredWidgets.filter(w => w.featured);
  const regularWidgets = filteredWidgets.filter(w => !w.featured);

  const handleAddWidget = (type: WidgetType) => {
    const widgetId = addWidget(layoutId, type);
    if (widgetId) {
      onClose();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-surface-overlay backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-surface-card border border-border-default rounded-2xl w-full max-w-4xl h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border-default">
          <div>
            <h2 className="text-xl font-semibold text-text-primary">
              ウィジェットを追加
            </h2>
            <p className="text-text-secondary text-sm mt-1">
              ダッシュボードに追加するウィジェットを選択してください
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Search and Filters */}
        <div className="p-6 border-b border-border-default">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
              <input
                type="text"
                placeholder="ウィジェットを検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-base pl-10"
              />
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-base min-w-40"
            >
              {CATEGORIES.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>

            {/* Advanced Toggle */}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`
                px-4 py-2 rounded-lg border transition-colors
                ${showAdvanced 
                  ? 'bg-brand-primary text-white border-brand-primary' 
                  : 'bg-surface-elevated border-border-default text-text-secondary hover:text-text-primary'
                }
              `}
            >
              <Filter size={16} className="inline mr-2" />
              高度
            </button>
          </div>
        </div>

        {/* Widget Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Featured Widgets */}
          {featuredWidgets.length > 0 && (
            <div className="mb-8">
              <div className="flex items-center space-x-2 mb-4">
                <Star size={18} className="text-brand-primary" />
                <h3 className="font-semibold text-text-primary">おすすめ</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {featuredWidgets.map((widget) => (
                  <WidgetCard
                    key={widget.type}
                    widget={widget}
                    onAdd={handleAddWidget}
                    featured
                  />
                ))}
              </div>
            </div>
          )}

          {/* Regular Widgets */}
          {regularWidgets.length > 0 && (
            <div>
              <h3 className="font-semibold text-text-primary mb-4">
                その他のウィジェット
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {regularWidgets.map((widget) => (
                  <WidgetCard
                    key={widget.type}
                    widget={widget}
                    onAdd={handleAddWidget}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {filteredWidgets.length === 0 && (
            <div className="text-center py-12">
              <Search size={48} className="mx-auto mb-4 text-text-tertiary opacity-50" />
              <h3 className="text-lg font-medium text-text-primary mb-2">
                ウィジェットが見つかりません
              </h3>
              <p className="text-text-secondary">
                検索条件を変更してお試しください
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

interface WidgetCardProps {
  widget: typeof WIDGET_CATALOG[0];
  onAdd: (type: WidgetType) => void;
  featured?: boolean;
}

function WidgetCard({ widget, onAdd, featured = false }: WidgetCardProps) {
  const Icon = widget.icon;

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        p-4 rounded-xl border cursor-pointer transition-all
        ${featured 
          ? 'bg-gradient-to-br from-brand-primary/10 to-brand-primary-light/5 border-brand-primary/30 hover:border-brand-primary/50' 
          : 'bg-surface-elevated border-border-default hover:border-border-strong'
        }
        hover:shadow-lg group
      `}
      onClick={() => onAdd(widget.type)}
    >
      <div className="flex items-start space-x-3 mb-3">
        <div className={`
          p-2 rounded-lg 
          ${featured 
            ? 'bg-brand-primary/20 text-brand-primary' 
            : 'bg-surface-card text-text-secondary group-hover:text-brand-primary'
          }
        `}>
          <Icon size={20} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <h4 className="font-medium text-text-primary truncate">
              {widget.name}
            </h4>
            {featured && <Star size={14} className="text-brand-primary flex-shrink-0" />}
          </div>
          <p className="text-text-secondary text-sm mt-1 line-clamp-2">
            {widget.description}
          </p>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1">
        {widget.tags.slice(0, 3).map(tag => (
          <span 
            key={tag}
            className="px-2 py-1 bg-surface-card text-text-tertiary text-xs rounded-md"
          >
            {tag}
          </span>
        ))}
        {widget.tags.length > 3 && (
          <span className="px-2 py-1 bg-surface-card text-text-tertiary text-xs rounded-md">
            +{widget.tags.length - 3}
          </span>
        )}
      </div>
    </motion.div>
  );
}