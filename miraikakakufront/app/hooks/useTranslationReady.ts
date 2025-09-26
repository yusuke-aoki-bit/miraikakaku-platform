import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export function useTranslationReady() {
  const { t, ready } = useTranslation('common');
  const [isFullyReady, setIsFullyReady] = useState(false);
  useEffect(() => {
    // Simplified ready state - just check if translation function is available
    if (ready) {
      setIsFullyReady(true);
    }
  }, [ready, t]);
  // Emergency fallback - always set ready after 100ms to prevent infinite loading
  useEffect(() => {
    const fallbackTimer = setTimeout(() => {
      setIsFullyReady(true);
    }, 100);
    return () => clearTimeout(fallbackTimer);
  }, []);
  return { isFullyReady, t };
}