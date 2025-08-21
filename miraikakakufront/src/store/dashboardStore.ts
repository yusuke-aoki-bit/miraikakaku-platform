import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  Widget, 
  DashboardLayout, 
  WidgetPosition, 
  WidgetSize, 
  WidgetType,
  DEFAULT_GRID_CONFIG,
  GridConfig,
  WIDGET_SIZES 
} from '@/types/dashboard';
import { v4 as uuidv4 } from 'uuid';

interface DashboardStore {
  layouts: DashboardLayout[];
  activeLayoutId: string | null;
  gridConfig: GridConfig;
  isEditMode: boolean;
  isDragging: boolean;
  selectedWidgetId: string | null;
  
  // Actions
  createLayout: (name: string, userMode: 'light' | 'pro') => string;
  deleteLayout: (layoutId: string) => void;
  duplicateLayout: (layoutId: string, newName: string) => string;
  setActiveLayout: (layoutId: string) => void;
  updateLayoutName: (layoutId: string, name: string) => void;
  
  // Widget actions
  addWidget: (layoutId: string, type: WidgetType, position?: WidgetPosition) => string;
  removeWidget: (layoutId: string, widgetId: string) => void;
  updateWidget: (layoutId: string, widgetId: string, updates: Partial<Widget>) => void;
  moveWidget: (layoutId: string, widgetId: string, position: WidgetPosition) => void;
  resizeWidget: (layoutId: string, widgetId: string, size: WidgetSize) => void;
  toggleWidgetVisibility: (layoutId: string, widgetId: string) => void;
  lockWidget: (layoutId: string, widgetId: string, locked: boolean) => void;
  
  // Layout management
  toggleEditMode: () => void;
  setDragging: (isDragging: boolean) => void;
  selectWidget: (widgetId: string | null) => void;
  autoArrangeWidgets: (layoutId: string) => void;
  resetLayout: (layoutId: string) => void;
  
  // Grid management
  updateGridConfig: (config: Partial<GridConfig>) => void;
  getOptimalPosition: (layoutId: string, size: WidgetSize) => WidgetPosition | null;
  checkCollision: (layoutId: string, widgetId: string, position: WidgetPosition, size: WidgetSize) => boolean;
  
  // Utility
  getActiveLayout: () => DashboardLayout | null;
  exportLayout: (layoutId: string) => string;
  importLayout: (layoutData: string) => void;
}

// Default widgets for different modes
const createDefaultLightModeWidgets = (): Widget[] => [
  {
    id: uuidv4(),
    type: 'portfolio-summary',
    title: 'ポートフォリオ概要',
    size: WIDGET_SIZES.lg,
    position: { x: 0, y: 0 },
    config: { showTitle: true, refreshInterval: 60000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'beginner',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'market-overview',
    title: 'マーケット概要',
    size: WIDGET_SIZES.lg,
    position: { x: 12, y: 0 },
    config: { showTitle: true, refreshInterval: 30000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'beginner',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'watchlist',
    title: 'ウォッチリスト',
    size: WIDGET_SIZES.md,
    position: { x: 0, y: 8 },
    config: { showTitle: true, refreshInterval: 15000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'beginner',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'news-sentiment',
    title: 'ニュース・センチメント',
    size: WIDGET_SIZES.md,
    position: { x: 9, y: 8 },
    config: { showTitle: true, refreshInterval: 120000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'beginner',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

const createDefaultProModeWidgets = (): Widget[] => [
  {
    id: uuidv4(),
    type: 'price-prediction-chart',
    title: 'AI価格予測チャート',
    size: { width: 16, height: 10 },
    position: { x: 0, y: 0 },
    config: { showTitle: true, refreshInterval: 30000, allowFullscreen: true },
    isVisible: true,
    isLocked: false,
    userLevel: 'advanced',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'technical-indicators',
    title: 'テクニカル指標',
    size: WIDGET_SIZES.sidebar,
    position: { x: 18, y: 0 },
    config: { showTitle: true, refreshInterval: 15000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'intermediate',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'real-time-prices',
    title: 'リアルタイム価格',
    size: { width: 8, height: 8 },
    position: { x: 0, y: 10 },
    config: { showTitle: true, refreshInterval: 1000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'advanced',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: uuidv4(),
    type: 'risk-analysis',
    title: 'リスク分析',
    size: { width: 8, height: 8 },
    position: { x: 8, y: 10 },
    config: { showTitle: true, refreshInterval: 300000 },
    isVisible: true,
    isLocked: false,
    userLevel: 'advanced',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

export const useDashboardStore = create<DashboardStore>()(
  persist(
    (set, get) => ({
      layouts: [],
      activeLayoutId: null,
      gridConfig: DEFAULT_GRID_CONFIG,
      isEditMode: false,
      isDragging: false,
      selectedWidgetId: null,

      createLayout: (name: string, userMode: 'light' | 'pro') => {
        const layoutId = uuidv4();
        const defaultWidgets = userMode === 'pro' 
          ? createDefaultProModeWidgets() 
          : createDefaultLightModeWidgets();

        const newLayout: DashboardLayout = {
          id: layoutId,
          name,
          widgets: defaultWidgets,
          gridColumns: DEFAULT_GRID_CONFIG.columns,
          gridRows: DEFAULT_GRID_CONFIG.rows,
          isDefault: false,
          userMode,
          tags: [userMode],
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        set((state) => ({
          layouts: [...state.layouts, newLayout],
          activeLayoutId: layoutId,
        }));

        return layoutId;
      },

      deleteLayout: (layoutId: string) => {
        set((state) => {
          const newLayouts = state.layouts.filter(layout => layout.id !== layoutId);
          const newActiveId = state.activeLayoutId === layoutId 
            ? (newLayouts.length > 0 ? newLayouts[0].id : null)
            : state.activeLayoutId;

          return {
            layouts: newLayouts,
            activeLayoutId: newActiveId,
          };
        });
      },

      duplicateLayout: (layoutId: string, newName: string) => {
        const layout = get().layouts.find(l => l.id === layoutId);
        if (!layout) return '';

        const newLayoutId = uuidv4();
        const duplicatedLayout: DashboardLayout = {
          ...layout,
          id: newLayoutId,
          name: newName,
          isDefault: false,
          widgets: layout.widgets.map(widget => ({
            ...widget,
            id: uuidv4(),
            createdAt: new Date(),
            updatedAt: new Date(),
          })),
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        set((state) => ({
          layouts: [...state.layouts, duplicatedLayout],
        }));

        return newLayoutId;
      },

      setActiveLayout: (layoutId: string) => {
        set({ activeLayoutId: layoutId });
      },

      updateLayoutName: (layoutId: string, name: string) => {
        set((state) => ({
          layouts: state.layouts.map(layout =>
            layout.id === layoutId
              ? { ...layout, name, updatedAt: new Date() }
              : layout
          ),
        }));
      },

      addWidget: (layoutId: string, type: WidgetType, position?: WidgetPosition) => {
        const widgetId = uuidv4();
        const defaultSize = WIDGET_SIZES.md;
        const optimalPosition = position || get().getOptimalPosition(layoutId, defaultSize);

        if (!optimalPosition) return '';

        const newWidget: Widget = {
          id: widgetId,
          type,
          title: getWidgetDefaultTitle(type),
          size: defaultSize,
          position: optimalPosition,
          config: { showTitle: true, refreshInterval: 60000 },
          isVisible: true,
          isLocked: false,
          userLevel: 'intermediate',
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        set((state) => ({
          layouts: state.layouts.map(layout =>
            layout.id === layoutId
              ? { 
                  ...layout, 
                  widgets: [...layout.widgets, newWidget],
                  updatedAt: new Date()
                }
              : layout
          ),
        }));

        return widgetId;
      },

      removeWidget: (layoutId: string, widgetId: string) => {
        set((state) => ({
          layouts: state.layouts.map(layout =>
            layout.id === layoutId
              ? {
                  ...layout,
                  widgets: layout.widgets.filter(w => w.id !== widgetId),
                  updatedAt: new Date()
                }
              : layout
          ),
          selectedWidgetId: state.selectedWidgetId === widgetId ? null : state.selectedWidgetId,
        }));
      },

      updateWidget: (layoutId: string, widgetId: string, updates: Partial<Widget>) => {
        set((state) => ({
          layouts: state.layouts.map(layout =>
            layout.id === layoutId
              ? {
                  ...layout,
                  widgets: layout.widgets.map(widget =>
                    widget.id === widgetId
                      ? { ...widget, ...updates, updatedAt: new Date() }
                      : widget
                  ),
                  updatedAt: new Date()
                }
              : layout
          ),
        }));
      },

      moveWidget: (layoutId: string, widgetId: string, position: WidgetPosition) => {
        get().updateWidget(layoutId, widgetId, { position });
      },

      resizeWidget: (layoutId: string, widgetId: string, size: WidgetSize) => {
        get().updateWidget(layoutId, widgetId, { size });
      },

      toggleWidgetVisibility: (layoutId: string, widgetId: string) => {
        const layout = get().layouts.find(l => l.id === layoutId);
        const widget = layout?.widgets.find(w => w.id === widgetId);
        
        if (widget) {
          get().updateWidget(layoutId, widgetId, { isVisible: !widget.isVisible });
        }
      },

      lockWidget: (layoutId: string, widgetId: string, locked: boolean) => {
        get().updateWidget(layoutId, widgetId, { isLocked: locked });
      },

      toggleEditMode: () => {
        set((state) => ({ 
          isEditMode: !state.isEditMode,
          selectedWidgetId: null 
        }));
      },

      setDragging: (isDragging: boolean) => {
        set({ isDragging });
      },

      selectWidget: (widgetId: string | null) => {
        set({ selectedWidgetId: widgetId });
      },

      autoArrangeWidgets: (layoutId: string) => {
        const layout = get().layouts.find(l => l.id === layoutId);
        if (!layout) return;

        const arrangedWidgets = layout.widgets.map((widget, index) => {
          const cols = Math.floor(24 / widget.size.width);
          const x = (index % cols) * widget.size.width;
          const y = Math.floor(index / cols) * widget.size.height;

          return {
            ...widget,
            position: { x: Math.min(x, 24 - widget.size.width), y },
            updatedAt: new Date(),
          };
        });

        set((state) => ({
          layouts: state.layouts.map(l =>
            l.id === layoutId
              ? { ...l, widgets: arrangedWidgets, updatedAt: new Date() }
              : l
          ),
        }));
      },

      resetLayout: (layoutId: string) => {
        const layout = get().layouts.find(l => l.id === layoutId);
        if (!layout) return;

        const defaultWidgets = layout.userMode === 'pro'
          ? createDefaultProModeWidgets()
          : createDefaultLightModeWidgets();

        set((state) => ({
          layouts: state.layouts.map(l =>
            l.id === layoutId
              ? { ...l, widgets: defaultWidgets, updatedAt: new Date() }
              : l
          ),
        }));
      },

      updateGridConfig: (config: Partial<GridConfig>) => {
        set((state) => ({
          gridConfig: { ...state.gridConfig, ...config },
        }));
      },

      getOptimalPosition: (layoutId: string, size: WidgetSize): WidgetPosition | null => {
        const layout = get().layouts.find(l => l.id === layoutId);
        if (!layout) return null;

        const { gridColumns, gridRows } = layout;
        const occupiedPositions = new Set<string>();

        layout.widgets.forEach(widget => {
          for (let x = widget.position.x; x < widget.position.x + widget.size.width; x++) {
            for (let y = widget.position.y; y < widget.position.y + widget.size.height; y++) {
              occupiedPositions.add(`${x},${y}`);
            }
          }
        });

        for (let y = 0; y <= gridRows - size.height; y++) {
          for (let x = 0; x <= gridColumns - size.width; x++) {
            let canPlace = true;
            
            for (let dx = 0; dx < size.width; dx++) {
              for (let dy = 0; dy < size.height; dy++) {
                if (occupiedPositions.has(`${x + dx},${y + dy}`)) {
                  canPlace = false;
                  break;
                }
              }
              if (!canPlace) break;
            }
            
            if (canPlace) {
              return { x, y };
            }
          }
        }

        return null;
      },

      checkCollision: (layoutId: string, widgetId: string, position: WidgetPosition, size: WidgetSize): boolean => {
        const layout = get().layouts.find(l => l.id === layoutId);
        if (!layout) return false;

        const otherWidgets = layout.widgets.filter(w => w.id !== widgetId);

        for (const widget of otherWidgets) {
          const widget1 = {
            x1: position.x,
            x2: position.x + size.width,
            y1: position.y,
            y2: position.y + size.height,
          };

          const widget2 = {
            x1: widget.position.x,
            x2: widget.position.x + widget.size.width,
            y1: widget.position.y,
            y2: widget.position.y + widget.size.height,
          };

          if (widget1.x1 < widget2.x2 && widget1.x2 > widget2.x1 &&
              widget1.y1 < widget2.y2 && widget1.y2 > widget2.y1) {
            return true;
          }
        }

        return false;
      },

      getActiveLayout: () => {
        const { layouts, activeLayoutId } = get();
        return layouts.find(layout => layout.id === activeLayoutId) || null;
      },

      exportLayout: (layoutId: string) => {
        const layout = get().layouts.find(l => l.id === layoutId);
        return layout ? JSON.stringify(layout, null, 2) : '';
      },

      importLayout: (layoutData: string) => {
        try {
          const layout: DashboardLayout = JSON.parse(layoutData);
          layout.id = uuidv4();
          layout.createdAt = new Date();
          layout.updatedAt = new Date();
          layout.widgets = layout.widgets.map(widget => ({
            ...widget,
            id: uuidv4(),
            createdAt: new Date(),
            updatedAt: new Date(),
          }));

          set((state) => ({
            layouts: [...state.layouts, layout],
          }));
        } catch (error) {
          console.error('Failed to import layout:', error);
        }
      },
    }),
    {
      name: 'dashboard-storage',
      partialize: (state) => ({
        layouts: state.layouts,
        activeLayoutId: state.activeLayoutId,
        gridConfig: state.gridConfig,
      }),
    }
  )
);

// Helper function to get default widget titles
function getWidgetDefaultTitle(type: WidgetType): string {
  const titles: Record<WidgetType, string> = {
    'price-prediction-chart': 'AI価格予測チャート',
    'data-table': 'データテーブル',
    'kpi-scorecard': 'KPIスコアカード',
    'news-sentiment': 'ニュース・センチメント',
    'market-overview': 'マーケット概要',
    'portfolio-summary': 'ポートフォリオ概要',
    'watchlist': 'ウォッチリスト',
    'real-time-prices': 'リアルタイム価格',
    'technical-indicators': 'テクニカル指標',
    'risk-analysis': 'リスク分析',
    'trading-history': '取引履歴',
    'alerts-panel': 'アラートパネル',
  };

  return titles[type] || type;
}