import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWAState {
  isInstallable: boolean;
  isInstalled: boolean;
  isOnline: boolean;
  isUpdateAvailable: boolean;
  hasNotificationPermission: boolean;
  isSupported: boolean;
}

interface PWAActions {
  installApp: () => Promise<void>;
  updateApp: () => Promise<void>;
  requestNotificationPermission: () => Promise<NotificationPermission>;
  sendNotification: (title: string, options?: NotificationOptions) => void;
  clearCache: () => Promise<void>;
  refreshData: () => Promise<void>;
}

export function usePWA(): PWAState & PWAActions {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [hasNotificationPermission, setHasNotificationPermission] = useState(false);
  const [serviceWorker, setServiceWorker] = useState<ServiceWorkerRegistration | null>(null);

  const isSupported = typeof window !== 'undefined' && 'serviceWorker' in navigator;

  // Register service worker
  useEffect(() => {
    if (!isSupported) return;

    const registerSW = async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });
        
        setServiceWorker(registration);
        console.log('Service Worker registered successfully');

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setIsUpdateAvailable(true);
              }
            });
          }
        });

        // Listen for messages from service worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          if (event.data && event.data.type === 'UPDATE_AVAILABLE') {
            setIsUpdateAvailable(true);
          }
        });

      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    };

    registerSW();
  }, [isSupported]);

  // Handle install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      setInstallPrompt(e);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener);
      window.addEventListener('appinstalled', handleAppInstalled as EventListener);

      return () => {
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener);
        window.removeEventListener('appinstalled', handleAppInstalled as EventListener);
      };
    }
  }, []);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    if (typeof window !== 'undefined') {
      setIsOnline(navigator.onLine);
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, []);

  // Check if app is installed (running in standalone mode)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const isInStandaloneMode = 
        window.matchMedia('(display-mode: standalone)').matches ||
        (window.navigator as any).standalone ||
        document.referrer.includes('android-app://');
      
      setIsInstalled(isInStandaloneMode);
    }
  }, []);

  // Check notification permission
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setHasNotificationPermission(Notification.permission === 'granted');
    }
  }, []);

  // Install app
  const installApp = useCallback(async () => {
    if (!installPrompt) {
      throw new Error('Install prompt not available');
    }

    try {
      await installPrompt.prompt();
      const { outcome } = await installPrompt.userChoice;
      
      if (outcome === 'accepted') {
        setIsInstalled(true);
        setIsInstallable(false);
        setInstallPrompt(null);
      }
    } catch (error) {
      console.error('Failed to install app:', error);
      throw error;
    }
  }, [installPrompt]);

  // Update app
  const updateApp = useCallback(async () => {
    if (!serviceWorker) {
      throw new Error('Service worker not available');
    }

    try {
      // Skip waiting and reload
      if (serviceWorker.waiting) {
        serviceWorker.waiting.postMessage({ type: 'SKIP_WAITING' });
        
        // Listen for controlling change
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          window.location.reload();
        });
      } else {
        // Force update check
        await serviceWorker.update();
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to update app:', error);
      throw error;
    }
  }, [serviceWorker]);

  // Request notification permission
  const requestNotificationPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (!('Notification' in window)) {
      throw new Error('Notifications not supported');
    }

    try {
      const permission = await Notification.requestPermission();
      setHasNotificationPermission(permission === 'granted');
      return permission;
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      throw error;
    }
  }, []);

  // Send notification
  const sendNotification = useCallback((title: string, options?: NotificationOptions) => {
    if (!hasNotificationPermission) {
      console.warn('Notification permission not granted');
      return;
    }

    if (!('Notification' in window)) {
      console.warn('Notifications not supported');
      return;
    }

    try {
      new Notification(title, {
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        tag: 'miraikakaku-notification',
        // renotify: true, // Not supported in all browsers
        ...options
      });
    } catch (error) {
      console.error('Failed to send notification:', error);
    }
  }, [hasNotificationPermission]);

  // Clear cache
  const clearCache = useCallback(async () => {
    if (!isSupported || !serviceWorker) {
      throw new Error('Service worker not available');
    }

    try {
      // Send message to service worker to clear cache
      navigator.serviceWorker.controller?.postMessage({
        type: 'CACHE_INVALIDATE'
      });

      // Also clear browser caches
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
      }

      console.log('Cache cleared successfully');
    } catch (error) {
      console.error('Failed to clear cache:', error);
      throw error;
    }
  }, [isSupported, serviceWorker]);

  // Refresh data (background sync)
  const refreshData = useCallback(async () => {
    if (!isSupported || !serviceWorker) {
      throw new Error('Service worker not available');
    }

    try {
      // Trigger background sync
      if ('sync' in serviceWorker && serviceWorker.sync) {
        await (serviceWorker.sync as any).register('background-data-sync');
      }

      console.log('Background sync triggered');
    } catch (error) {
      console.error('Failed to trigger background sync:', error);
      throw error;
    }
  }, [isSupported, serviceWorker]);

  return {
    // State
    isInstallable,
    isInstalled,
    isOnline,
    isUpdateAvailable,
    hasNotificationPermission,
    isSupported,
    
    // Actions
    installApp,
    updateApp,
    requestNotificationPermission,
    sendNotification,
    clearCache,
    refreshData
  };
}

// Hook for PWA install banner
export function usePWAInstallBanner() {
  const { isInstallable, isInstalled, installApp } = usePWA();
  const [showBanner, setShowBanner] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Show banner if app is installable, not installed, and not dismissed
    const shouldShow = isInstallable && !isInstalled && !dismissed;
    
    // Delay showing banner to avoid interrupting user
    if (shouldShow) {
      const timer = setTimeout(() => {
        setShowBanner(true);
      }, 5000); // 5 second delay

      return () => clearTimeout(timer);
    } else {
      setShowBanner(false);
    }
  }, [isInstallable, isInstalled, dismissed]);

  const handleInstall = async () => {
    try {
      await installApp();
      setShowBanner(false);
    } catch (error) {
      console.error('Failed to install app:', error);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    setDismissed(true);
    
    // Remember dismissal for this session
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('pwa-banner-dismissed', 'true');
    }
  };

  // Check if banner was dismissed in this session
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const wasDismissed = sessionStorage.getItem('pwa-banner-dismissed');
      if (wasDismissed) {
        setDismissed(true);
      }
    }
  }, []);

  return {
    showBanner,
    handleInstall,
    handleDismiss
  };
}

// Hook for offline indicator
export function useOfflineIndicator() {
  const { isOnline } = usePWA();
  const [showOfflineIndicator, setShowOfflineIndicator] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      setShowOfflineIndicator(true);
    } else {
      // Hide indicator after a short delay when back online
      const timer = setTimeout(() => {
        setShowOfflineIndicator(false);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isOnline]);

  return {
    isOnline,
    showOfflineIndicator
  };
}