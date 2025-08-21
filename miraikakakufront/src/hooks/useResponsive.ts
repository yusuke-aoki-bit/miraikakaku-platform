import { useState, useEffect } from 'react';

export type BreakpointKey = 'mobile' | 'tablet' | 'desktop' | 'ultrawide';

export interface ResponsiveBreakpoints {
  mobile: number;
  tablet: number;
  desktop: number;
  ultrawide: number;
}

// Financial-optimized breakpoints
export const FINANCIAL_BREAKPOINTS: ResponsiveBreakpoints = {
  mobile: 480,     // Primary trading interface
  tablet: 1024,    // Portrait/Landscape tablet
  desktop: 1200,   // Standard multi-column layout
  ultrawide: 1920  // Full screen real estate utilization
};

export interface ResponsiveState {
  width: number;
  height: number;
  breakpoint: BreakpointKey;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isUltrawide: boolean;
  orientation: 'portrait' | 'landscape';
  devicePixelRatio: number;
}

export function useResponsive(customBreakpoints?: Partial<ResponsiveBreakpoints>): ResponsiveState {
  const breakpoints = { ...FINANCIAL_BREAKPOINTS, ...customBreakpoints };
  
  const [state, setState] = useState<ResponsiveState>(() => {
    if (typeof window === 'undefined') {
      return {
        width: 1200,
        height: 800,
        breakpoint: 'desktop' as BreakpointKey,
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        isUltrawide: false,
        orientation: 'landscape' as const,
        devicePixelRatio: 1
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    
    return {
      width,
      height,
      breakpoint: getBreakpoint(width, breakpoints),
      isMobile: width < breakpoints.tablet,
      isTablet: width >= breakpoints.tablet && width < breakpoints.desktop,
      isDesktop: width >= breakpoints.desktop && width < breakpoints.ultrawide,
      isUltrawide: width >= breakpoints.ultrawide,
      orientation: width > height ? 'landscape' : 'portrait',
      devicePixelRatio: window.devicePixelRatio || 1
    };
  });

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleResize = () => {
      // Debounce resize events for performance
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        setState({
          width,
          height,
          breakpoint: getBreakpoint(width, breakpoints),
          isMobile: width < breakpoints.tablet,
          isTablet: width >= breakpoints.tablet && width < breakpoints.desktop,
          isDesktop: width >= breakpoints.desktop && width < breakpoints.ultrawide,
          isUltrawide: width >= breakpoints.ultrawide,
          orientation: width > height ? 'landscape' : 'portrait',
          devicePixelRatio: window.devicePixelRatio || 1
        });
      }, 150);
    };

    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  }, [breakpoints]);

  return state;
}

function getBreakpoint(width: number, breakpoints: ResponsiveBreakpoints): BreakpointKey {
  if (width < breakpoints.tablet) return 'mobile';
  if (width < breakpoints.desktop) return 'tablet';
  if (width < breakpoints.ultrawide) return 'desktop';
  return 'ultrawide';
}

// Hook for responsive grid columns
export function useResponsiveGridColumns(): {
  dashboardColumns: number;
  maxWidgetWidth: number;
  recommendedSizes: string[];
} {
  const { breakpoint } = useResponsive();
  
  switch (breakpoint) {
    case 'mobile':
      return {
        dashboardColumns: 6,
        maxWidgetWidth: 6,
        recommendedSizes: ['full', 'lg', 'md']
      };
    case 'tablet':
      return {
        dashboardColumns: 12,
        maxWidgetWidth: 12,
        recommendedSizes: ['xl', 'lg', 'md', 'sm']
      };
    case 'desktop':
      return {
        dashboardColumns: 18,
        maxWidgetWidth: 18,
        recommendedSizes: ['full', 'xl', 'lg', 'md', 'sm', 'xs']
      };
    case 'ultrawide':
      return {
        dashboardColumns: 24,
        maxWidgetWidth: 24,
        recommendedSizes: ['full', 'xl', 'lg', 'md', 'sm', 'xs']
      };
    default:
      return {
        dashboardColumns: 24,
        maxWidgetWidth: 24,
        recommendedSizes: ['full', 'xl', 'lg', 'md', 'sm', 'xs']
      };
  }
}

// Hook for responsive navigation
export function useResponsiveNavigation(): {
  sidebarMode: 'overlay' | 'push' | 'persistent';
  showTabNavigation: boolean;
  maxNavigationItems: number;
} {
  const { breakpoint } = useResponsive();
  
  switch (breakpoint) {
    case 'mobile':
      return {
        sidebarMode: 'overlay',
        showTabNavigation: true,
        maxNavigationItems: 4
      };
    case 'tablet':
      return {
        sidebarMode: 'overlay',
        showTabNavigation: true,
        maxNavigationItems: 6
      };
    case 'desktop':
      return {
        sidebarMode: 'push',
        showTabNavigation: false,
        maxNavigationItems: 8
      };
    case 'ultrawide':
      return {
        sidebarMode: 'persistent',
        showTabNavigation: false,
        maxNavigationItems: 12
      };
    default:
      return {
        sidebarMode: 'persistent',
        showTabNavigation: false,
        maxNavigationItems: 8
      };
  }
}

// Hook for responsive charts
export function useResponsiveCharts(): {
  defaultHeight: number;
  showToolbar: boolean;
  showLegend: boolean;
  touchOptimized: boolean;
} {
  const { breakpoint, isMobile } = useResponsive();
  
  return {
    defaultHeight: breakpoint === 'mobile' ? 250 : breakpoint === 'tablet' ? 350 : 400,
    showToolbar: !isMobile,
    showLegend: !isMobile,
    touchOptimized: isMobile
  };
}