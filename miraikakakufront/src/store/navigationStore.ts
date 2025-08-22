import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { NavigationItem, TabNavigationItem, CommandItem } from '@/types/navigation';
import { 
  Home,
  TrendingUp,
  PieChart,
  Brain,
  Briefcase,
  BookmarkCheck,
  History,
  Calculator,
  Settings,
  BarChart3,
  Trophy,
  Activity,
  Search,
  Star,
  Target,
  AlertTriangle,
  Bell,
  User,
  Layout,
  Grid3X3,
  Edit,
  Save,
  Plus,
  Download,
  Upload,
  RefreshCw,
  HelpCircle,
  DollarSign,
  Globe
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
  getPrimaryNavigation: (userMode: 'light' | 'pro') => NavigationItem[];
  getTabNavigation: () => TabNavigationItem[];
  getCommandItems: (userMode: 'light' | 'pro') => CommandItem[];
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

      getPrimaryNavigation: (userMode: 'light' | 'pro'): NavigationItem[] => {
        const baseNavigation: NavigationItem[] = [
          {
            id: 'dashboard',
            label: 'ダッシュボード',
            href: '/dashboard',
            icon: Layout,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+1',
            description: 'カスタマイズ可能なダッシュボード'
          },
          {
            id: 'market',
            label: 'マーケット',
            icon: PieChart,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            children: [
              {
                id: 'realtime',
                label: 'リアルタイム',
                href: '/realtime',
                icon: Activity,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                hotkey: '⌘+R'
              },
              {
                id: 'rankings',
                label: 'ランキング',
                href: '/rankings',
                icon: Trophy,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced']
              },
              {
                id: 'analysis',
                label: '分析',
                href: '/analysis',
                icon: Brain,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced']
              },
              {
                id: 'volume',
                label: '出来高分析',
                href: '/volume',
                icon: BarChart3,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                description: '出来高の実測値・過去予測・未来予測'
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
            id: 'portfolio',
            label: 'ポートフォリオ',
            icon: Briefcase,
            category: 'primary',
            userLevel: ['beginner', 'intermediate', 'advanced'],
            children: [
              {
                id: 'watchlist',
                label: 'ウォッチリスト',
                href: '/watchlist',
                icon: BookmarkCheck,
                category: 'secondary',
                userLevel: ['beginner', 'intermediate', 'advanced'],
                hotkey: '⌘+W'
              },
              {
                id: 'history',
                label: '取引履歴',
                href: '/history',
                icon: History,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced']
              }
            ]
          }
        ];

        // Add advanced navigation for pro mode
        if (userMode === 'pro') {
          baseNavigation.push({
            id: 'analysis-tools',
            label: '分析ツール',
            icon: Calculator,
            category: 'primary',
            userLevel: ['intermediate', 'advanced'],
            children: [
              {
                id: 'predictions',
                label: 'AI予測',
                href: '/predictions',
                icon: Brain,
                category: 'secondary',
                userLevel: ['intermediate', 'advanced'],
                hotkey: '⌘+P'
              },
              {
                id: 'tools',
                label: '分析ツール',
                href: '/tools',
                icon: Target,
                category: 'secondary',
                userLevel: ['advanced']
              },
              {
                id: 'risk-analysis',
                label: 'リスク分析',
                href: '/risk',
                icon: AlertTriangle,
                category: 'secondary',
                userLevel: ['advanced']
              }
            ]
          });
        }

        baseNavigation.push({
          id: 'settings',
          label: '設定',
          href: '/management',
          icon: Settings,
          category: 'primary',
          userLevel: ['beginner', 'intermediate', 'advanced'],
          hotkey: '⌘+,'
        });

        return baseNavigation;
      },

      getTabNavigation: (): TabNavigationItem[] => [
        {
          id: 'dashboard',
          label: 'ダッシュボード',
          href: '/dashboard',
          icon: Layout,
          hotkey: '⌘+1'
        },
        {
          id: 'predictions',
          label: '予測',
          href: '/predictions',
          icon: Brain,
          hotkey: '⌘+2'
        },
        {
          id: 'portfolio',
          label: 'ポートフォリオ',
          href: '/watchlist',
          icon: Briefcase,
          hotkey: '⌘+3'
        },
        {
          id: 'analysis',
          label: '分析',
          href: '/analysis',
          icon: BarChart3,
          hotkey: '⌘+4'
        },
        {
          id: 'market',
          label: 'マーケット',
          href: '/realtime',
          icon: TrendingUp,
          hotkey: '⌘+5'
        },
        {
          id: 'tools',
          label: 'ツール',
          href: '/tools',
          icon: Calculator,
          hotkey: '⌘+6'
        }
      ],

      getCommandItems: (userMode: 'light' | 'pro'): CommandItem[] => {
        const baseCommands: CommandItem[] = [
          // Navigation commands
          {
            id: 'go-dashboard',
            label: 'ダッシュボードに移動',
            description: 'メインダッシュボードを表示',
            icon: Layout,
            action: () => window.location.href = '/dashboard',
            category: 'navigation',
            keywords: ['dashboard', 'ダッシュボード', 'メイン'],
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+1'
          },
          {
            id: 'go-predictions',
            label: 'AI予測に移動',
            description: '株価予測ページを表示',
            icon: Brain,
            action: () => window.location.href = '/predictions',
            category: 'navigation',
            keywords: ['predictions', '予測', 'AI', '株価'],
            userLevel: ['intermediate', 'advanced'],
            hotkey: '⌘+2'
          },
          {
            id: 'go-watchlist',
            label: 'ウォッチリストに移動',
            description: 'お気に入りの銘柄リストを表示',
            icon: BookmarkCheck,
            action: () => window.location.href = '/watchlist',
            category: 'navigation',
            keywords: ['watchlist', 'ウォッチリスト', 'お気に入り', '銘柄'],
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+W'
          },
          {
            id: 'go-realtime',
            label: 'リアルタイムデータに移動',
            description: 'リアルタイム株価を表示',
            icon: Activity,
            action: () => window.location.href = '/realtime',
            category: 'navigation',
            keywords: ['realtime', 'リアルタイム', '株価', 'ライブ'],
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+R'
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
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+K'
          },
          {
            id: 'refresh-data',
            label: 'データ更新',
            description: '最新データを取得',
            icon: RefreshCw,
            action: () => window.location.reload(),
            category: 'action',
            keywords: ['refresh', '更新', 'データ', '最新'],
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+⇧+R'
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
            userLevel: ['beginner', 'intermediate', 'advanced'],
            hotkey: '⌘+\\'
          }
        ];

        // Add pro mode specific commands
        if (userMode === 'pro') {
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
              userLevel: ['intermediate', 'advanced'],
              hotkey: '⌘+E'
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
              userLevel: ['intermediate', 'advanced'],
              hotkey: '⌘+⇧+A'
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
        }

        baseCommands.push({
          id: 'help',
          label: 'ヘルプ',
          description: 'ヘルプとサポート情報を表示',
          icon: HelpCircle,
          action: () => console.log('Show help'),
          category: 'action',
          keywords: ['help', 'ヘルプ', 'サポート', '使い方'],
          userLevel: ['beginner', 'intermediate', 'advanced'],
          hotkey: '⌘+?'
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