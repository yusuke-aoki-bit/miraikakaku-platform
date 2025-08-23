'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigationStore } from '@/store/navigationStore';
import { useResponsive, useResponsiveNavigation } from '@/hooks/useResponsive';
import { TabNavigationItem } from '@/types/navigation';
import { MoreHorizontal, Plus } from 'lucide-react';

interface TabNavigationProps {
  className?: string;
}

export default function TabNavigation({ className = '' }: TabNavigationProps) {
  const pathname = usePathname();
  const { getTabNavigation } = useNavigationStore();
  const { isMobile, isTablet } = useResponsive();
  const { showTabNavigation, maxNavigationItems } = useResponsiveNavigation();
  const [showOverflow, setShowOverflow] = useState(false);

  const allTabs = getTabNavigation();
  const visibleTabs = allTabs.slice(0, maxNavigationItems - 1); // Leave space for overflow
  const overflowTabs = allTabs.slice(maxNavigationItems - 1);

  // Don't show tab navigation if not needed for this breakpoint
  if (!showTabNavigation) return null;

  return (
    <div className={`sticky top-0 z-30 bg-surface-background/80 backdrop-blur-md border-b border-border-default ${className}`}>
      <div className="flex items-center overflow-x-auto scrollbar-hide">
        {/* Main Tabs */}
        <div className="flex items-center">
          {visibleTabs.map((tab) => (
            <TabItem key={tab.id} tab={tab} pathname={pathname} />
          ))}

          {/* Overflow Menu */}
          {overflowTabs.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setShowOverflow(!showOverflow)}
                className={`
                  flex items-center justify-center min-w-[60px] h-12 px-3
                  text-text-secondary hover:text-text-primary
                  hover:bg-surface-elevated transition-colors
                  ${showOverflow ? 'bg-surface-elevated text-text-primary' : ''}
                `}
              >
                <MoreHorizontal size={18} />
              </button>

              <AnimatePresence>
                {showOverflow && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    className="absolute top-full right-0 mt-1 bg-surface-card border border-border-default rounded-lg shadow-lg py-2 min-w-[200px] z-50"
                  >
                    {overflowTabs.map((tab) => (
                      <Link
                        key={tab.id}
                        href={tab.href}
                        onClick={() => setShowOverflow(false)}
                        className={`
                          flex items-center space-x-3 px-4 py-3 hover:bg-surface-elevated transition-colors
                          ${pathname === tab.href ? 'text-brand-primary bg-brand-primary/10' : 'text-text-primary'}
                        `}
                      >
                        <tab.icon size={16} />
                        <span className="font-medium">{tab.label}</span>
                      </Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Add Tab Button (Pro mode only) */}
        {(isMobile || isTablet) && (
          <button
            className="flex items-center justify-center min-w-[50px] h-12 px-3 text-text-secondary hover:text-text-primary hover:bg-surface-elevated transition-colors ml-auto"
            title="新しいタブ"
          >
            <Plus size={18} />
          </button>
        )}
      </div>

      {/* Active Tab Indicator */}
      <div className="relative">
        {visibleTabs.map((tab, index) => {
          if (pathname !== tab.href) return null;
          
          const tabWidth = isMobile ? 60 : 80;
          const translateX = index * tabWidth;
          
          return (
            <motion.div
              key="active-indicator"
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 h-0.5 bg-brand-primary"
              style={{ width: tabWidth }}
              animate={{ x: translateX }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            />
          );
        })}
      </div>
    </div>
  );
}

interface TabItemProps {
  tab: TabNavigationItem;
  pathname: string;
}

function TabItem({ tab, pathname }: TabItemProps) {
  const { isMobile } = useResponsive();
  const isActive = pathname === tab.href;

  return (
    <Link
      href={tab.href}
      className={`
        relative flex flex-col items-center justify-center
        ${isMobile ? 'min-w-[60px] h-12 px-2' : 'min-w-[80px] h-12 px-3'}
        transition-all duration-200
        ${isActive 
          ? 'text-brand-primary' 
          : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
        }
      `}
      title={tab.description || tab.label}
    >
      {/* Icon */}
      <tab.icon size={isMobile ? 16 : 18} className="mb-1" />
      
      {/* Label */}
      <span className={`text-xs font-medium leading-none ${isMobile ? 'text-[10px]' : ''}`}>
        {isMobile ? tab.label.slice(0, 4) : tab.label}
      </span>

      {/* Badge for notifications (placeholder) */}
      {tab.id === 'predictions' && (
        <div className="absolute -top-1 -right-1 w-2 h-2 bg-status-danger rounded-full" />
      )}
    </Link>
  );
}

// Bottom Tab Bar for Mobile (iOS/Android style)
export function MobileBottomTabBar({ className = '' }: { className?: string }) {
  const pathname = usePathname();
  const { getTabNavigation } = useNavigationStore();
  const { isMobile } = useResponsive();

  if (!isMobile) return null;

  const tabs = getTabNavigation().slice(0, 5); // Limit to 5 tabs for mobile

  return (
    <div className={`
      fixed bottom-0 left-0 right-0 z-50
      bg-surface-card/95 backdrop-blur-md border-t border-border-default
      safe-area-inset-bottom
      ${className}
    `}>
      <div className="flex items-center justify-around h-16 px-2">
        {tabs.map((tab) => (
          <Link
            key={tab.id}
            href={tab.href}
            className={`
              flex flex-col items-center justify-center flex-1 py-2 px-1 rounded-lg
              transition-all duration-200
              ${pathname === tab.href 
                ? 'text-brand-primary bg-brand-primary/10' 
                : 'text-text-secondary active:bg-surface-elevated'
              }
            `}
          >
            <tab.icon size={20} className="mb-1" />
            <span className="text-xs font-medium leading-none">
              {tab.label.length > 6 ? tab.label.slice(0, 5) + '...' : tab.label}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}