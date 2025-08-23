'use client';

import { createContext, useContext, useEffect } from 'react';
import { useAccessibility, AccessibilityPreferences } from '@/hooks/useAccessibility';

interface AccessibilityContextType {
  preferences: AccessibilityPreferences;
  updatePreferences: (prefs: Partial<AccessibilityPreferences>) => void;
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  announcement: string;
  getFontSizeClass: () => string;
  getMotionClass: () => string;
  getContrastClass: () => string;
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

export function AccessibilityProvider({ children }: { children: React.ReactNode }) {
  const accessibility = useAccessibility();

  // Apply accessibility preferences to document
  useEffect(() => {
    if (typeof document === 'undefined') return;

    const { preferences } = accessibility;
    
    // Apply font size
    document.documentElement.style.setProperty(
      '--base-font-size', 
      preferences.fontSize === 'small' ? '14px' :
      preferences.fontSize === 'large' ? '18px' :
      preferences.fontSize === 'xl' ? '20px' : '16px'
    );

    // Apply motion preference
    document.documentElement.setAttribute(
      'data-motion-preference',
      preferences.prefersReducedMotion ? 'reduce' : 'auto'
    );

    // Apply contrast preference
    document.documentElement.setAttribute(
      'data-contrast-preference',
      preferences.prefersHighContrast ? 'high' : 'normal'
    );

    // Apply color scheme preference
    if (preferences.prefersColorScheme !== 'no-preference') {
      document.documentElement.setAttribute(
        'data-color-scheme',
        preferences.prefersColorScheme
      );
    }

    // Apply focus visible preference
    if (preferences.focusVisible) {
      document.documentElement.classList.add('focus-visible-enabled');
    } else {
      document.documentElement.classList.remove('focus-visible-enabled');
    }

  }, [accessibility, accessibility.preferences]);

  return (
    <AccessibilityContext.Provider value={accessibility}>
      {children}
      
      {/* Screen Reader Announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {accessibility.announcement}
      </div>
      
      {/* Skip to main content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-brand-primary text-white px-4 py-2 rounded-lg font-medium"
      >
        メインコンテンツにスキップ
      </a>
    </AccessibilityContext.Provider>
  );
}

export function useAccessibilityContext() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibilityContext must be used within AccessibilityProvider');
  }
  return context;
}