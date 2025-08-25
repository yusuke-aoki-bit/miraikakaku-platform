import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { NavigationItem, TabNavigationItem, CommandItem } from '@/types/navigation';
import { 
  PieChart,
  Brain,
  BookmarkCheck,
  Calculator,
  BarChart3,
  Trophy,
  Activity,
  Search,
  Target,
  Layout,
  Edit,
  Plus,
  Download,
  Upload,
  RefreshCw,
  HelpCircle,
  DollarSign,
  User,
  Settings,
  TrendingUp,
  Lightbulb,
  Newspaper,
  Users,
  Crown
} from 'lucide-react';

interface NavigationStore {
  sidebarCollapsed: boolean;
  activeTabId: string;
  recentPages: string[];
  favoritePages: string[];
  
  // Actions
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  setActiveTab: (tabId: string) => void;
  addRecentPage: (href: string) => void;
  toggleFavoritePage: (href: string) => void;
  
  // Navigation items
  getPrimaryNavigation: () => NavigationItem[];
  getTabNavigation: () => TabNavigationItem[];
  getCommandItems: () => CommandItem[];
}

export const useNavigationStore = create<NavigationStore>()(
  persist(
    (set, get) => ({
      sidebarCollapsed: false,
      activeTabId: 'dashboard',
      recentPages: [],
      favoritePages: [],

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      setActiveTab: (tabId: string) => {
        set({ activeTabId: tabId });
      },

      addRecentPage: (href: string) => {
        set((state) => {
          const recentPages = [href, ...state.recentPages.filter(p => p !== href)].slice(0, 10);
          return { recentPages };
        });
      },

      toggleFavoritePage: (href: string) => {
        set((state) => {
          const favoritePages = state.favoritePages.includes(href)
            ? state.favoritePages.filter(p => p !== href)
            : [...state.favoritePages, href];
          return { favoritePages };
        });
      },

      getPrimaryNavigation: (): NavigationItem[] => {
        const baseNavigation: NavigationItem[] = [
          {
            id: 'dashboard',
            label: 'ダッシュボード',
            href: '/',
            icon: Layout,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            description: 'メインダッシュボード・市場概況'
          },
          {
            id: 'market',
            label: 'マーケット',
            icon: TrendingUp,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            children: [
              {
                id: 'rankings',
                label: 'ランキング',
                href: '/rankings',
                icon: Trophy,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: '値上がり・値下がり・出来高ランキング'
              },
              {
                id: 'themes',
                label: 'テーマ別分析',
                href: '/themes',
                icon: Lightbulb,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: 'テーマ・関連銘柄の分析'
              },
              {
                id: 'sectors',
                label: 'セクター分析',
                href: '/sectors',
                icon: PieChart,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '業種別パフォーマンス分析'
              },
              {
                id: 'search',
                label: '銘柄検索',
                href: '/search',
                icon: Search,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: 'キーワードや条件で銘柄を検索'
              },
              {
                id: 'news',
                label: 'マーケットニュース',
                href: '/news',
                icon: Newspaper,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: '最新の市場ニュース・分析'
              }
            ]
          },
          {
            id: 'ai-analysis',
            label: 'AI分析',
            icon: Brain,
            category: 'primary',
            userLevel: ['intermediate', 'advanced'],
            children: [
              {
                id: 'predictions',
                label: '個別銘柄予測',
                href: '/predictions',
                icon: Target,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '個別銘柄のAI予測'
              },
              {
                id: 'volume',
                label: '出来高予測',
                href: '/volume',
                icon: BarChart3,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '出来高のAI予測分析'
              },
              {
                id: 'currency',
                label: '為替予測',
                href: '/currency',
                icon: DollarSign,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '主要通貨ペアのAI予測'
              }
            ]
          },
          {
            id: 'community',
            label: 'コミュニティ',
            icon: Users,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            children: [
              {
                id: 'contests',
                label: '予測コロシアム',
                href: '/contests',
                icon: Crown,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '予測コンテストとランキング'
              },
              {
                id: 'user-rankings',
                label: 'ユーザーランキング',
                href: '/user-rankings',
                icon: Trophy,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: 'ユーザー別パフォーマンスランキング'
              }
            ]
          },
          {
            id: 'mypage',
            label: 'マイページ',
            icon: User,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            children: [
              {
                id: 'portfolio',
                label: 'ポートフォリオ',
                href: '/portfolio',
                icon: PieChart,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '保有資産の管理・分析'
              },
              {
                id: 'watchlist',
                label: 'ウォッチリスト',
                href: '/watchlist',
                icon: BookmarkCheck,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: 'お気に入り銘柄の管理'
              },
              {
                id: 'management',
                label: 'アカウント設定',
                href: '/management',
                icon: Settings,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                description: 'ユーザー設定・通知管理'
              }
            ]
          }
        ];

        return baseNavigation;
      },

      getTabNavigation: (): TabNavigationItem[] => [
        {
          id: 'dashboard',
          label: 'ダッシュボード',
          href: '/',
          icon: Layout
        },
        {
          id: 'rankings',
          label: 'ランキング',
          href: '/rankings',
          icon: Trophy
        },
        {
          id: 'themes',
          label: 'テーマ分析',
          href: '/themes',
          icon: Lightbulb
        },
        {
          id: 'predictions',
          label: 'AI予測',
          href: '/predictions',
          icon: Brain
        },
        {
          id: 'volume',
          label: '出来高予測',
          href: '/volume',
          icon: BarChart3
        },
        {
          id: 'currency',
          label: '為替予測',
          href: '/currency',
          icon: DollarSign
        },
        {
          id: 'contests',
          label: 'コロシアム',
          href: '/contests',
          icon: Crown
        },
        {
          id: 'watchlist',
          label: 'ウォッチリスト',
          href: '/watchlist',
          icon: BookmarkCheck
        },
        {
          id: 'portfolio',
          label: 'ポートフォリオ',
          href: '/portfolio',
          icon: PieChart
        }
      ],

      getCommandItems: (): CommandItem[] => {
        const baseCommands: CommandItem[] = [
          // Navigation commands
          {
            id: 'go-dashboard',
            label: 'ダッシュボードに移動',
            description: 'メインダッシュボードを表示',
            icon: Layout,
            action: () => window.location.href = '/',
            category: 'navigation',
            keywords: ['dashboard', 'ダッシュボード', 'メイン'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          },
          {
            id: 'go-rankings',
            label: 'ランキングに移動',
            description: '値上がり・値下がりランキングを表示',
            icon: Trophy,
            action: () => window.location.href = '/rankings',
            category: 'navigation',
            keywords: ['rankings', 'ランキング', '値上がり', '値下がり'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          },
          {
            id: 'go-themes',
            label: 'テーマ分析に移動',
            description: 'テーマ別銘柄分析を表示',
            icon: Lightbulb,
            action: () => window.location.href = '/themes',
            category: 'navigation',
            keywords: ['themes', 'テーマ', '分析', '銘柄'],
            userLevel: ['intermediate', 'advanced']
          },
          {
            id: 'go-predictions',
            label: 'AI予測に移動',
            description: '個別銘柄のAI予測を表示',
            icon: Brain,
            action: () => window.location.href = '/predictions',
            category: 'navigation',
            keywords: ['predictions', '予測', 'AI', '株価'],
            userLevel: ['intermediate', 'advanced']
          },
          {
            id: 'go-contests',
            label: '予測コロシアムに移動',
            description: '予測コンテストに参加',
            icon: Crown,
            action: () => window.location.href = '/contests',
            category: 'navigation',
            keywords: ['contests', 'コロシアム', '予測', 'コンテスト'],
            userLevel: ['intermediate', 'advanced']
          },
          {
            id: 'go-watchlist',
            label: 'ウォッチリストに移動',
            description: 'お気に入りの銘柄リストを表示',
            icon: BookmarkCheck,
            action: () => window.location.href = '/watchlist',
            category: 'navigation',
            keywords: ['watchlist', 'ウォッチリスト', 'お気に入り', '銘柄'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          },
          {
            id: 'go-portfolio',
            label: 'ポートフォリオに移動',
            description: '保有資産の管理・分析を表示',
            icon: PieChart,
            action: () => window.location.href = '/portfolio',
            category: 'navigation',
            keywords: ['portfolio', 'ポートフォリオ', '資産', '管理'],
            userLevel: ['intermediate', 'advanced']
          },
          
          // Action commands
          {
            id: 'search-stocks',
            label: '銘柄検索',
            description: '株式を検索して詳細を表示',
            icon: Search,
            action: () => {
              // Focus on search input
              const searchInput = document.querySelector('[data-testid="stock-search-input"]') as HTMLInputElement;
              if (searchInput) searchInput.focus();
            },
            category: 'search',
            keywords: ['search', '検索', '銘柄', '株式', 'stock'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          },
          {
            id: 'refresh-data',
            label: 'データ更新',
            description: '最新データを取得',
            icon: RefreshCw,
            action: () => window.location.reload(),
            category: 'action',
            keywords: ['refresh', '更新', 'データ', '最新'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          },
          
          // Layout commands
          {
            id: 'toggle-sidebar',
            label: 'サイドバー切り替え',
            description: 'サイドバーの表示/非表示を切り替え',
            icon: Layout,
            action: () => get().toggleSidebar(),
            category: 'layout',
            keywords: ['sidebar', 'サイドバー', '表示', '非表示'],
            userLevel: ['beginner', 'intermediate', 'advanced']
          }
        ];

        // Add dashboard management commands
        baseCommands.push(
          {
            id: 'edit-dashboard',
            label: 'ダッシュボード編集',
            description: 'ダッシュボードを編集モードに切り替え',
            icon: Edit,
            action: () => {
              // This would trigger dashboard edit mode
              console.log('Toggle dashboard edit mode');
            },
            category: 'action',
            keywords: ['edit', '編集', 'ダッシュボード', 'レイアウト'],
            userLevel: ['intermediate', 'advanced']
          },
          {
            id: 'add-widget',
            label: 'ウィジェット追加',
            description: 'ダッシュボードにウィジェットを追加',
            icon: Plus,
            action: () => {
              console.log('Add widget to dashboard');
            },
            category: 'widget',
            keywords: ['widget', 'ウィジェット', '追加', 'add'],
            userLevel: ['intermediate', 'advanced']
          },
          {
            id: 'export-layout',
            label: 'レイアウト出力',
            description: 'ダッシュボードレイアウトをエクスポート',
            icon: Download,
            action: () => {
              console.log('Export dashboard layout');
            },
            category: 'layout',
            keywords: ['export', '出力', 'レイアウト', 'ダウンロード'],
            userLevel: ['advanced']
          },
          {
            id: 'import-layout',
            label: 'レイアウト読み込み',
            description: 'ダッシュボードレイアウトをインポート',
            icon: Upload,
            action: () => {
              console.log('Import dashboard layout');
            },
            category: 'layout',
            keywords: ['import', '読み込み', 'レイアウト', 'アップロード'],
            userLevel: ['advanced']
          }
        );

        baseCommands.push({
          id: 'help',
          label: 'ヘルプ',
          description: 'ヘルプとサポート情報を表示',
          icon: HelpCircle,
          action: () => console.log('Show help'),
          category: 'action',
          keywords: ['help', 'ヘルプ', 'サポート', '使い方'],
          userLevel: ['beginner', 'intermediate', 'advanced']
        });

        return baseCommands;
      }
    }),
    {
      name: 'navigation-storage',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        activeTabId: state.activeTabId,
        recentPages: state.recentPages,
        favoritePages: state.favoritePages,
      }),
    }
  )
);