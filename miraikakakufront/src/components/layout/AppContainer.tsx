'use client';

import { useState, useEffect } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { ToastContainer } from '@/components/common/ToastNotification';
import CommandPalette from '@/components/common/CommandPalette';
import ModeSwitchSuggestion from '@/components/common/ModeSwitchSuggestion';
import TabNavigation, { MobileBottomTabBar } from '@/components/navigation/TabNavigation';
import { useResponsive, useResponsiveNavigation } from '@/hooks/useResponsive';
import ResponsiveContainer from './ResponsiveContainer';

interface AppContainerProps {
  children: React.ReactNode;
}

export default function AppContainer({ children }: AppContainerProps) {
  const { isMobile, isTablet, isDesktop, isUltrawide } = useResponsive();
  const { sidebarMode, showTabNavigation } = useResponsiveNavigation();
  
  // Initialize sidebar state based on screen size
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return true; // SSR default
    return isDesktop || isUltrawide; // Open by default on desktop+
  });
  const [isCommandPaletteOpen, setCommandPaletteOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check if we're in an input field, text area, or contenteditable element
      const target = event.target as HTMLElement;
      const isInputField = target.tagName === 'INPUT' || 
                          target.tagName === 'TEXTAREA' || 
                          target.isContentEditable;
      
      // Command palette shortcut: Ctrl+K or Cmd+K
      if ((event.metaKey || event.ctrlKey) && event.key === 'k' && !event.altKey && !event.shiftKey) {
        // Don't interfere with browser shortcuts in input fields
        if (!isInputField) {
          event.preventDefault();
          event.stopPropagation();
          setCommandPaletteOpen((prev) => !prev);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Auto-manage sidebar state based on screen size
  useEffect(() => {
    if (isMobile || isTablet) {
      setSidebarOpen(false);
    } else if (isDesktop || isUltrawide) {
      setSidebarOpen(true);
    }
  }, [isMobile, isTablet, isDesktop, isUltrawide]);

  return (
    <div className="h-screen bg-surface-background text-text-primary flex flex-col overflow-hidden">
      {/* Header - always visible */}
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Tab Navigation - mobile/tablet only */}
      <TabNavigation />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Overlay - mobile/tablet */}
        {(sidebarMode === 'overlay') && sidebarOpen && (
          <div 
            className="fixed inset-0 bg-surface-overlay backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Sidebar */}
        {sidebarMode === 'persistent' ? (
          // Always visible sidebar (ultrawide)
          <div className="relative z-auto h-full">
            <Sidebar />
          </div>
        ) : sidebarMode === 'push' ? (
          // Push sidebar (desktop) - shows/hides based on sidebarOpen state
          <div className={`transform transition-transform duration-300 ease-in-out ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } relative z-auto h-full`}>
            <Sidebar />
          </div>
        ) : (
          // Overlay sidebar (mobile/tablet)
          <div className={`transform transition-transform duration-300 ease-in-out z-50 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } fixed left-0`}
          style={{ 
            top: 'var(--header-height)', 
            bottom: 0,
            height: 'calc(100vh - var(--header-height))'
          }}>
            <Sidebar />
          </div>
        )}

        {/* Main Content */}
        <main className="flex-1 bg-gradient-to-br from-surface-background via-surface-background to-surface-elevated overflow-auto">
          <ResponsiveContainer>
            <div className={`min-h-full ${isMobile ? 'pb-20' : ''}`}>
              {children}
            </div>
          </ResponsiveContainer>
        </main>
      </div>

      {/* Footer - desktop only */}
      {!isMobile && <Footer />}

      {/* Mobile Bottom Tab Bar */}
      <MobileBottomTabBar />

      {/* Global Components */}
      <ToastContainer />
      <CommandPalette isOpen={isCommandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
      <ModeSwitchSuggestion />
    </div>
  );
}

