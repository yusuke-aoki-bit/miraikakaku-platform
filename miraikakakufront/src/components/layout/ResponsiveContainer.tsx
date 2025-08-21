'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { useResponsive, useResponsiveNavigation } from '@/hooks/useResponsive';

interface ResponsiveContainerProps {
  children: ReactNode;
  className?: string;
}

export default function ResponsiveContainer({ children, className = '' }: ResponsiveContainerProps) {
  const { breakpoint, isMobile, isTablet } = useResponsive();
  const { sidebarMode } = useResponsiveNavigation();

  const containerClasses = {
    mobile: 'px-4 py-4',
    tablet: 'px-6 py-6', 
    desktop: 'px-8 py-8',
    ultrawide: 'px-12 py-8'
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={`
        w-full h-full
        ${containerClasses[breakpoint]}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}

interface ResponsiveGridProps {
  children: ReactNode;
  className?: string;
  gap?: 'sm' | 'md' | 'lg';
}

export function ResponsiveGrid({ children, className = '', gap = 'md' }: ResponsiveGridProps) {
  const { breakpoint } = useResponsive();

  const gapClasses = {
    sm: 'gap-2 md:gap-3 lg:gap-4',
    md: 'gap-4 md:gap-6 lg:gap-8',
    lg: 'gap-6 md:gap-8 lg:gap-12'
  };

  const gridClasses = {
    mobile: 'grid-cols-1',
    tablet: 'grid-cols-1 md:grid-cols-2',
    desktop: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    ultrawide: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  };

  return (
    <div className={`
      grid auto-rows-fr
      ${gridClasses[breakpoint]}
      ${gapClasses[gap]}
      ${className}
    `}>
      {children}
    </div>
  );
}

interface MobileOptimizedCardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  collapsible?: boolean;
}

export function MobileOptimizedCard({ 
  children, 
  title, 
  className = '',
  collapsible = false 
}: MobileOptimizedCardProps) {
  const { isMobile } = useResponsive();

  if (isMobile) {
    return (
      <motion.div
        layout
        className={`
          bg-surface-card border border-border-default rounded-xl
          overflow-hidden
          ${className}
        `}
      >
        {title && (
          <div className="p-4 border-b border-border-default bg-surface-elevated/50">
            <h3 className="font-semibold text-text-primary text-lg">{title}</h3>
          </div>
        )}
        <div className="p-4">
          {children}
        </div>
      </motion.div>
    );
  }

  return (
    <div className={`
      bg-surface-card border border-border-default rounded-2xl
      ${className}
    `}>
      {title && (
        <div className="p-6 border-b border-border-default">
          <h3 className="font-semibold text-text-primary text-xl">{title}</h3>
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}

interface ResponsiveTableProps {
  data: any[];
  columns: {
    key: string;
    label: string;
    mobile?: boolean; // Show on mobile
    render?: (value: any, row: any) => ReactNode;
  }[];
  className?: string;
}

export function ResponsiveTable({ data, columns, className = '' }: ResponsiveTableProps) {
  const { isMobile } = useResponsive();

  if (isMobile) {
    // Card-based layout for mobile
    return (
      <div className={`space-y-3 ${className}`}>
        {data.map((row, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-surface-elevated rounded-lg p-4"
          >
            {columns
              .filter(col => col.mobile !== false)
              .map(column => (
                <div key={column.key} className="flex justify-between items-center py-1">
                  <span className="text-text-secondary text-sm">{column.label}:</span>
                  <span className="text-text-primary font-medium">
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </span>
                </div>
              ))}
          </motion.div>
        ))}
      </div>
    );
  }

  // Traditional table for larger screens
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-border-default">
            {columns.map(column => (
              <th key={column.key} className="text-left p-4 font-medium text-text-secondary">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <motion.tr
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.05 }}
              className="border-b border-border-default hover:bg-surface-elevated transition-colors"
            >
              {columns.map(column => (
                <td key={column.key} className="p-4 text-text-primary">
                  {column.render ? column.render(row[column.key], row) : row[column.key]}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface TouchOptimizedButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}

export function TouchOptimizedButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false
}: TouchOptimizedButtonProps) {
  const { isMobile } = useResponsive();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-brand-primary text-white hover:bg-brand-primary-hover focus:ring-brand-primary',
    secondary: 'bg-surface-elevated text-text-primary hover:bg-surface-elevated border border-border-default focus:ring-brand-primary',
    ghost: 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated focus:ring-brand-primary'
  };

  // Mobile gets larger touch targets (44px minimum)
  const sizeClasses = {
    sm: isMobile ? 'px-4 py-3 text-sm min-h-touch' : 'px-3 py-2 text-sm',
    md: isMobile ? 'px-6 py-3 text-base min-h-touch' : 'px-4 py-2 text-base',
    lg: isMobile ? 'px-8 py-4 text-lg min-h-lg' : 'px-6 py-3 text-lg'
  };

  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <motion.button
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      onClick={disabled ? undefined : onClick}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${disabledClasses}
        ${className}
      `}
      disabled={disabled}
    >
      {children}
    </motion.button>
  );
}