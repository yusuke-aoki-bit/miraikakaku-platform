'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useNavigationStore } from '@/store/navigationStore';
import { useUserModeStore } from '@/store/userModeStore';
import { NavigationItem } from '@/types/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Star, BookmarkCheck } from 'lucide-react';

interface NavigationItemComponentProps {
  item: NavigationItem;
  isCollapsed: boolean;
  depth?: number;
}

const NavigationItemComponent = ({ item, isCollapsed, depth = 0 }: NavigationItemComponentProps) => {
  const pathname = usePathname();
  const { 
    favoritePages, 
    toggleFavoritePage, 
    addRecentPage,
    sidebarCollapsed
  } = useNavigationStore();
  const { trackFeatureUsage } = useUserModeStore();
  const [isExpanded, setIsExpanded] = useState(false);
  
  const isActive = item.href ? pathname === item.href : false;
  const hasChildren = item.children && item.children.length > 0;
  const isFavorite = item.href ? favoritePages.includes(item.href) : false;

  useEffect(() => {
    if (hasChildren && item.children?.some(child => child.href === pathname)) {
      setIsExpanded(true);
    }
  }, [pathname, hasChildren, item.children]);

  const handleClick = (e: React.MouseEvent) => {
    if (hasChildren) {
      e.preventDefault();
      setIsExpanded(!isExpanded);
      trackFeatureUsage('navigation-expand');
    } else if (item.href) {
      addRecentPage(item.href);
      trackFeatureUsage('navigation-click');
    }
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (item.href) {
      toggleFavoritePage(item.href);
      trackFeatureUsage('navigation-favorite');
    }
  };

  const Icon = item.icon;
  const indentLevel = depth * 16;

  if (item.href && !hasChildren) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: depth * 0.05 }}
      >
        <Link
          href={item.href}
          onClick={handleClick}
          className={`
            group relative flex items-center py-3 px-4 rounded-xl transition-all duration-200
            ${isActive 
              ? 'bg-brand-primary text-white shadow-lg' 
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
            }
          `}
          style={{ paddingLeft: `${16 + indentLevel}px` }}
          title={isCollapsed ? item.label : item.description}
        >
          <Icon size={20} className="flex-shrink-0" />
          
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="flex items-center justify-between flex-1 ml-3 overflow-hidden"
              >
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="font-medium truncate">{item.label}</span>
                  {item.hotkey && (
                    <span className="text-xs opacity-60 font-mono">
                      {item.hotkey}
                    </span>
                  )}
                </div>
                
                {item.href && (
                  <button
                    onClick={handleFavoriteClick}
                    className={`
                      ml-2 p-1 rounded-md opacity-0 group-hover:opacity-100 transition-opacity
                      ${isFavorite ? 'text-status-warning' : 'text-text-tertiary hover:text-text-secondary'}
                    `}
                  >
                    {isFavorite ? <Star size={14} fill="currentColor" /> : <Star size={14} />}
                  </button>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {item.badge && !isCollapsed && (
            <span className="ml-2 px-2 py-0.5 bg-brand-primary text-white text-xs rounded-full">
              {item.badge}
            </span>
          )}
        </Link>
      </motion.div>
    );
  }

  return (
    <div>
      <motion.button
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: depth * 0.05 }}
        onClick={handleClick}
        className="group w-full flex items-center py-3 px-4 rounded-xl text-text-secondary hover:text-text-primary hover:bg-surface-elevated transition-all duration-200"
        style={{ paddingLeft: `${16 + indentLevel}px` }}
        title={isCollapsed ? item.label : item.description}
      >
        <Icon size={20} className="flex-shrink-0" />
        
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              className="flex items-center justify-between flex-1 ml-3 overflow-hidden"
            >
              <div className="flex flex-col min-w-0 flex-1">
                <span className="font-medium truncate">{item.label}</span>
                {item.hotkey && (
                  <span className="text-xs opacity-60 font-mono">
                    {item.hotkey}
                  </span>
                )}
              </div>
              
              {hasChildren && (
                <motion.div
                  animate={{ rotate: isExpanded ? 90 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="ml-2"
                >
                  <ChevronRight size={16} />
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {item.badge && !isCollapsed && (
          <span className="ml-2 px-2 py-0.5 bg-brand-primary text-white text-xs rounded-full">
            {item.badge}
          </span>
        )}
      </motion.button>

      <AnimatePresence>
        {hasChildren && isExpanded && !isCollapsed && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-1 space-y-1"
          >
            {item.children?.map((child) => (
              <NavigationItemComponent
                key={child.id}
                item={child}
                isCollapsed={isCollapsed}
                depth={depth + 1}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function Sidebar() {
  const { 
    sidebarCollapsed, 
    toggleSidebar, 
    getPrimaryNavigation, 
    favoritePages, 
    recentPages 
  } = useNavigationStore();
  const { config: userConfig } = useUserModeStore();

  const primaryNavigation = getPrimaryNavigation(userConfig.mode);
  const favoriteNavigation = primaryNavigation
    .filter(item => item.href && favoritePages.includes(item.href))
    .slice(0, 5);

  return (
    <motion.div
      animate={{ 
        width: sidebarCollapsed ? 80 : 256 
      }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="bg-surface-background border-r border-border-default flex flex-col backdrop-blur-sm"
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default">
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              className="flex items-center space-x-2"
            >
              <div className="w-8 h-8 bg-brand-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <div>
                <h3 className="font-semibold text-text-primary text-sm">Miraikakaku</h3>
                <p className="text-text-tertiary text-xs">
                  {userConfig.mode === 'pro' ? 'プロモード' : 'ライトモード'}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <button
          onClick={toggleSidebar}
          className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
          title={sidebarCollapsed ? 'サイドバーを展開' : 'サイドバーを折りたたむ'}
        >
          <motion.div
            animate={{ rotate: sidebarCollapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight size={18} />
          </motion.div>
        </button>
      </div>

      {/* Navigation Content */}
      <div className="flex-1 overflow-y-auto">
        <nav className="p-4 space-y-2">
          {/* Favorites Section */}
          {!sidebarCollapsed && favoriteNavigation.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-3 px-2">
                <Star size={14} className="text-status-warning" />
                <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                  お気に入り
                </span>
              </div>
              <div className="space-y-1">
                {favoriteNavigation.map((item) => (
                  <NavigationItemComponent
                    key={`fav-${item.id}`}
                    item={item}
                    isCollapsed={sidebarCollapsed}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Primary Navigation */}
          <div className="space-y-1">
            {primaryNavigation.map((item) => (
              <NavigationItemComponent
                key={item.id}
                item={item}
                isCollapsed={sidebarCollapsed}
              />
            ))}
          </div>
        </nav>
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-border-default">
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="text-center"
            >
              <div className="text-xs text-text-tertiary mb-2">
                最近のページ: {recentPages.length}
              </div>
              <div className="text-xs text-text-tertiary">
                お気に入り: {favoritePages.length}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
