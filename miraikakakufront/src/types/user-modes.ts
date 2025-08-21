export type UserMode = 'light' | 'pro';

export interface UserModeConfig {
  mode: UserMode;
  showAdvancedFeatures: boolean;
  enableHotkeys: boolean;
  multiPanelLayout: boolean;
  showEducationalTooltips: boolean;
  autoSuggestModeSwitch: boolean;
  experienceLevel: 'beginner' | 'intermediate' | 'advanced';
}

export interface UserBehaviorMetrics {
  sessionsCount: number;
  averageSessionDuration: number;
  advancedFeaturesUsed: string[];
  tradingFrequency: number;
  lastModeSwitch: Date | null;
  preferredFeatures: string[];
}

export const DEFAULT_USER_MODE_CONFIG: UserModeConfig = {
  mode: 'light',
  showAdvancedFeatures: false,
  enableHotkeys: false,
  multiPanelLayout: false,
  showEducationalTooltips: true,
  autoSuggestModeSwitch: true,
  experienceLevel: 'beginner',
};

export const PRO_MODE_CONFIG: UserModeConfig = {
  mode: 'pro',
  showAdvancedFeatures: true,
  enableHotkeys: true,
  multiPanelLayout: true,
  showEducationalTooltips: false,
  autoSuggestModeSwitch: true,
  experienceLevel: 'advanced',
};