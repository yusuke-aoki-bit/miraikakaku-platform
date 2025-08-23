'use client';

import { useEffect, useRef, ReactNode, useState, useCallback } from 'react';
import { useFocusManagement } from '@/hooks/useAccessibility';

interface FocusTrapProps {
  children: ReactNode;
  isActive: boolean;
  restoreFocus?: boolean;
  initialFocus?: string; // CSS selector for initial focus element
}

export default function FocusTrap({ 
  children, 
  isActive, 
  restoreFocus = true,
  initialFocus 
}: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { trapFocus } = useFocusManagement();
  const previousActiveElementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;

    // Store the currently focused element
    if (document.activeElement instanceof HTMLElement) {
      previousActiveElementRef.current = document.activeElement;
    }

    // Set initial focus
    const setInitialFocus = () => {
      let elementToFocus: HTMLElement | null = null;

      if (initialFocus) {
        elementToFocus = container.querySelector(initialFocus) as HTMLElement;
      }

      if (!elementToFocus) {
        // Find the first focusable element
        const focusableElements = container.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as NodeListOf<HTMLElement>;
        elementToFocus = focusableElements[0];
      }

      if (!elementToFocus) {
        // If no focusable element found, make the container focusable
        container.setAttribute('tabindex', '-1');
        elementToFocus = container;
      }

      elementToFocus?.focus();
    };

    // Set up focus trap
    const cleanup = trapFocus(container);
    
    // Set initial focus after a short delay to ensure DOM is ready
    setTimeout(setInitialFocus, 0);

    return () => {
      cleanup();
      
      // Restore focus when the trap is deactivated
      if (restoreFocus && previousActiveElementRef.current) {
        // Use setTimeout to ensure the element is still in the DOM
        setTimeout(() => {
          if (previousActiveElementRef.current && 
              document.contains(previousActiveElementRef.current)) {
            previousActiveElementRef.current.focus();
          }
        }, 0);
      }
    };
  }, [isActive, trapFocus, restoreFocus, initialFocus]);

  // Handle Escape key to close trap
  useEffect(() => {
    if (!isActive) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        
        // Trigger restore focus
        if (restoreFocus && previousActiveElementRef.current) {
          previousActiveElementRef.current.focus();
        }
      }
    };

    document.addEventListener('keydown', handleEscape, true);
    return () => document.removeEventListener('keydown', handleEscape, true);
  }, [isActive, restoreFocus]);

  if (!isActive) {
    return <>{children}</>;
  }

  return (
    <div 
      ref={containerRef}
      className="focus-trap-container"
      role="dialog"
      aria-modal="true"
    >
      {children}
    </div>
  );
}

// Hook for managing focus trap state
export function useFocusTrap() {
  const [isActive, setIsActive] = useState(false);

  const activate = useCallback(() => setIsActive(true), []);
  const deactivate = useCallback(() => setIsActive(false), []);

  return { isActive, activate, deactivate };
}