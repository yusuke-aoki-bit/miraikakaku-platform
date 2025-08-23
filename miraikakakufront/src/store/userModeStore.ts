import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserMode, UserModeConfig, UserBehaviorMetrics, PRO_MODE_CONFIG } from '@/types/user-modes';

interface UserModeStore {
  config: UserModeConfig;
  metrics: UserBehaviorMetrics;
  isTransitioning: boolean;
  
  // Actions
  setMode: (mode: UserMode) => void;
  toggleMode: () => void;
  updateConfig: (updates: Partial<UserModeConfig>) => void;
  updateMetrics: (updates: Partial<UserBehaviorMetrics>) => void;
  trackFeatureUsage: (feature: string) => void;
  shouldSuggestModeSwitch: () => boolean;
  startModeTransition: () => void;
  completeModeTransition: () => void;
  resetToDefaults: () => void;
}

const INITIAL_METRICS: UserBehaviorMetrics = {
  sessionsCount: 0,
  averageSessionDuration: 0,
  advancedFeaturesUsed: [],
  tradingFrequency: 0,
  lastModeSwitch: null,
  preferredFeatures: [],
};

export const useUserModeStore = create<UserModeStore>()(
  persist(
    (set, get) => ({
      config: PRO_MODE_CONFIG,
      metrics: INITIAL_METRICS,
      isTransitioning: false,

      setMode: (mode: UserMode) => {
        console.log('Setting mode to:', mode);
        // Always use PRO mode
        set((state) => ({
          config: { ...PRO_MODE_CONFIG, mode: 'pro' },
          metrics: {
            ...state.metrics,
            lastModeSwitch: new Date(),
          },
        }));
      },

      toggleMode: () => {
        // Mode switching disabled - always stay in PRO mode
        get().setMode('pro');
      },

      updateConfig: (updates: Partial<UserModeConfig>) => {
        set((state) => ({
          config: { ...state.config, ...updates },
        }));
      },

      updateMetrics: (updates: Partial<UserBehaviorMetrics>) => {
        set((state) => ({
          metrics: { ...state.metrics, ...updates },
        }));
      },

      trackFeatureUsage: (feature: string) => {
        set((state) => {
          const advancedFeatures = [
            'technical-indicators',
            'algorithm-trading',
            'advanced-charts',
            'risk-management',
            'api-access',
            'multi-panel-layout',
            'hotkeys',
            'custom-indicators',
          ];

          const isAdvancedFeature = advancedFeatures.includes(feature);
          const updatedAdvancedFeatures = isAdvancedFeature
            ? [...new Set([...state.metrics.advancedFeaturesUsed, feature])]
            : state.metrics.advancedFeaturesUsed;

          const updatedPreferredFeatures = [...state.metrics.preferredFeatures, feature];
          
          return {
            metrics: {
              ...state.metrics,
              advancedFeaturesUsed: updatedAdvancedFeatures,
              preferredFeatures: updatedPreferredFeatures.slice(-20), // Keep last 20 features
            },
          };
        });
      },

      shouldSuggestModeSwitch: (): boolean => {
        const { config, metrics } = get();
        
        if (!config.autoSuggestModeSwitch) return false;
        
        // Suggest switching to Pro mode if user is in Light mode
        if (config.mode === 'light') {
          const advancedFeatureThreshold = 3;
          const sessionThreshold = 5;
          const avgSessionDurationThreshold = 300; // 5 minutes
          
          return (
            metrics.advancedFeaturesUsed.length >= advancedFeatureThreshold ||
            metrics.sessionsCount >= sessionThreshold ||
            metrics.averageSessionDuration >= avgSessionDurationThreshold
          );
        }
        
        // Suggest switching to Light mode if user rarely uses advanced features
        if (config.mode === 'pro') {
          const recentAdvancedUsage = metrics.preferredFeatures
            .slice(-10)
            .filter(feature => metrics.advancedFeaturesUsed.includes(feature));
          
          return recentAdvancedUsage.length < 2 && metrics.sessionsCount > 10;
        }
        
        return false;
      },

      startModeTransition: () => {
        set({ isTransitioning: true });
      },

      completeModeTransition: () => {
        set({ isTransitioning: false });
      },

      resetToDefaults: () => {
        set({
          config: PRO_MODE_CONFIG,
          metrics: INITIAL_METRICS,
          isTransitioning: false,
        });
      },
    }),
    {
      name: 'user-mode-storage',
      partialize: (state) => ({
        config: state.config,
        metrics: state.metrics,
      }),
    }
  )
);