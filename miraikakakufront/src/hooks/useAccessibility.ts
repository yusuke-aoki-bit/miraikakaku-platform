import { useState, useEffect, useCallback, useRef } from 'react';

// Accessibility preferences interface
export interface AccessibilityPreferences {
  prefersReducedMotion: boolean;
  prefersHighContrast: boolean;
  prefersColorScheme: 'light' | 'dark' | 'no-preference';
  fontSize: 'small' | 'medium' | 'large' | 'xl';
  screenReaderAnnouncements: boolean;
  keyboardNavigation: boolean;
  focusVisible: boolean;
}

// Default accessibility preferences
const DEFAULT_A11Y_PREFERENCES: AccessibilityPreferences = {
  prefersReducedMotion: false,
  prefersHighContrast: false,
  prefersColorScheme: 'no-preference',
  fontSize: 'medium',
  screenReaderAnnouncements: true,
  keyboardNavigation: true,
  focusVisible: true
};

export function useAccessibility() {
  const [preferences, setPreferences] = useState<AccessibilityPreferences>(DEFAULT_A11Y_PREFERENCES);
  const [announcement, setAnnouncement] = useState<string>('');
  const announcementTimeoutRef = useRef<NodeJS.Timeout>();

  // Detect system preferences
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updatePreferences = () => {
      const newPreferences: AccessibilityPreferences = {
        ...preferences,
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        prefersHighContrast: window.matchMedia('(prefers-contrast: high)').matches,
        prefersColorScheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 
                          window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'no-preference'
      };
      setPreferences(newPreferences);
    };

    // Initial check
    updatePreferences();

    // Set up media query listeners
    const reducedMotionMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
    const highContrastMQ = window.matchMedia('(prefers-contrast: high)');
    const darkModeMQ = window.matchMedia('(prefers-color-scheme: dark)');
    const lightModeMQ = window.matchMedia('(prefers-color-scheme: light)');

    reducedMotionMQ.addEventListener('change', updatePreferences);
    highContrastMQ.addEventListener('change', updatePreferences);
    darkModeMQ.addEventListener('change', updatePreferences);
    lightModeMQ.addEventListener('change', updatePreferences);

    return () => {
      reducedMotionMQ.removeEventListener('change', updatePreferences);
      highContrastMQ.removeEventListener('change', updatePreferences);
      darkModeMQ.removeEventListener('change', updatePreferences);
      lightModeMQ.removeEventListener('change', updatePreferences);
    };
  }, []);

  // Load saved preferences
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const savedPreferences = localStorage.getItem('accessibility-preferences');
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        setPreferences(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Failed to parse accessibility preferences:', error);
      }
    }
  }, []);

  // Save preferences when they change
  const updatePreferences = useCallback((newPreferences: Partial<AccessibilityPreferences>) => {
    setPreferences(prev => {
      const updated = { ...prev, ...newPreferences };
      
      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('accessibility-preferences', JSON.stringify(updated));
      }
      
      return updated;
    });
  }, []);

  // Screen reader announcements
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!preferences.screenReaderAnnouncements) return;

    // Clear previous announcement
    if (announcementTimeoutRef.current) {
      clearTimeout(announcementTimeoutRef.current);
    }

    setAnnouncement(message);

    // Clear announcement after delay
    announcementTimeoutRef.current = setTimeout(() => {
      setAnnouncement('');
    }, priority === 'assertive' ? 5000 : 3000);
  }, [preferences.screenReaderAnnouncements]);

  // Get font size class
  const getFontSizeClass = useCallback(() => {
    switch (preferences.fontSize) {
      case 'small': return 'text-sm';
      case 'large': return 'text-lg';
      case 'xl': return 'text-xl';
      default: return 'text-base';
    }
  }, [preferences.fontSize]);

  // Get motion class
  const getMotionClass = useCallback(() => {
    return preferences.prefersReducedMotion ? 'motion-reduce' : 'motion-safe';
  }, [preferences.prefersReducedMotion]);

  // Get contrast class
  const getContrastClass = useCallback(() => {
    return preferences.prefersHighContrast ? 'contrast-high' : 'contrast-normal';
  }, [preferences.prefersHighContrast]);

  return {
    preferences,
    updatePreferences,
    announce,
    announcement,
    getFontSizeClass,
    getMotionClass,
    getContrastClass
  };
}

// Hook for managing focus
export function useFocusManagement() {
  const [focusedElement, setFocusedElement] = useState<HTMLElement | null>(null);
  const focusHistoryRef = useRef<HTMLElement[]>([]);

  // Focus trap utility
  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    return () => container.removeEventListener('keydown', handleTabKey);
  }, []);

  // Restore focus to previous element
  const restoreFocus = useCallback(() => {
    const previousElement = focusHistoryRef.current.pop();
    if (previousElement && document.contains(previousElement)) {
      previousElement.focus();
    }
  }, []);

  // Set focus and remember previous
  const setFocus = useCallback((element: HTMLElement) => {
    if (document.activeElement instanceof HTMLElement) {
      focusHistoryRef.current.push(document.activeElement);
    }
    element.focus();
    setFocusedElement(element);
  }, []);

  return {
    focusedElement,
    trapFocus,
    restoreFocus,
    setFocus
  };
}

// Hook for keyboard navigation
export function useKeyboardNavigation() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const itemsRef = useRef<HTMLElement[]>([]);

  const registerItem = useCallback((element: HTMLElement | null) => {
    if (element && !itemsRef.current.includes(element)) {
      itemsRef.current.push(element);
    }
  }, []);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const items = itemsRef.current.filter(item => document.contains(item));
    
    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        setCurrentIndex(prev => {
          const newIndex = (prev + 1) % items.length;
          items[newIndex]?.focus();
          return newIndex;
        });
        break;
        
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        setCurrentIndex(prev => {
          const newIndex = prev === 0 ? items.length - 1 : prev - 1;
          items[newIndex]?.focus();
          return newIndex;
        });
        break;
        
      case 'Home':
        e.preventDefault();
        setCurrentIndex(0);
        items[0]?.focus();
        break;
        
      case 'End':
        e.preventDefault();
        const lastIndex = items.length - 1;
        setCurrentIndex(lastIndex);
        items[lastIndex]?.focus();
        break;
    }
  }, []);

  const reset = useCallback(() => {
    setCurrentIndex(0);
    itemsRef.current = [];
  }, []);

  return {
    currentIndex,
    registerItem,
    handleKeyDown,
    reset
  };
}

// Hook for ARIA live regions
export function useAriaLiveRegion() {
  const [liveRegionMessage, setLiveRegionMessage] = useState('');
  const timeoutRef = useRef<NodeJS.Timeout>();

  const announceToScreenReader = useCallback((
    message: string, 
    priority: 'polite' | 'assertive' = 'polite',
    delay: number = 100
  ) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Clear previous message first
    setLiveRegionMessage('');

    // Set new message after short delay to ensure it's announced
    timeoutRef.current = setTimeout(() => {
      setLiveRegionMessage(message);
      
      // Clear message after announcement
      setTimeout(() => {
        setLiveRegionMessage('');
      }, priority === 'assertive' ? 5000 : 3000);
    }, delay);
  }, []);

  return {
    liveRegionMessage,
    announceToScreenReader
  };
}