'use client';

import { useAriaLiveRegion } from '@/hooks/useAccessibility';

interface AriaLiveRegionProps {
  'aria-live'?: 'polite' | 'assertive' | 'off';
  'aria-atomic'?: boolean;
  className?: string;
}

export default function AriaLiveRegion({ 
  'aria-live': priority = 'polite',
  'aria-atomic': atomic = true,
  className = 'sr-only'
}: AriaLiveRegionProps) {
  const { liveRegionMessage } = useAriaLiveRegion();

  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic={atomic}
      className={className}
    >
      {liveRegionMessage}
    </div>
  );
}

// Component for screen reader only content
export function ScreenReaderOnly({ 
  children, 
  className = '' 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) {
  return (
    <span className={`sr-only ${className}`}>
      {children}
    </span>
  );
}

// Component for status announcements
export function StatusAnnouncement({ 
  message, 
  priority = 'polite' 
}: { 
  message: string;
  priority?: 'polite' | 'assertive';
}) {
  if (!message) return null;

  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
}