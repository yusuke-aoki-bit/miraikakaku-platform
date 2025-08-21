import { useState, useEffect, useCallback, useRef } from 'react';

// Performance metrics interface
export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  networkRequests: number;
  cacheHitRatio: number;
  frameRate: number;
  isLowEndDevice: boolean;
}

// Performance configuration
export interface PerformanceConfig {
  enablePreloading: boolean;
  enableLazyLoading: boolean;
  optimizeForLowEnd: boolean;
  maxConcurrentRequests: number;
  cacheStrategy: 'aggressive' | 'moderate' | 'minimal';
  imageQuality: 'high' | 'medium' | 'low';
}

const DEFAULT_CONFIG: PerformanceConfig = {
  enablePreloading: true,
  enableLazyLoading: true,
  optimizeForLowEnd: false,
  maxConcurrentRequests: 6,
  cacheStrategy: 'moderate',
  imageQuality: 'medium'
};

export function usePerformance() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    networkRequests: 0,
    cacheHitRatio: 0,
    frameRate: 60,
    isLowEndDevice: false
  });
  
  const [config, setConfig] = useState<PerformanceConfig>(DEFAULT_CONFIG);
  const performanceObserverRef = useRef<PerformanceObserver | null>(null);
  const frameCountRef = useRef(0);
  const frameStartTimeRef = useRef(0);

  // Detect device capabilities
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const detectDeviceCapabilities = () => {
      const navigator = window.navigator as any;
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      
      // Check hardware concurrency
      const cores = navigator.hardwareConcurrency || 2;
      
      // Check memory (if available)
      const memory = navigator.deviceMemory || 4;
      
      // Check connection speed
      const effectiveType = connection?.effectiveType || '4g';
      
      // Determine if this is a low-end device
      const isLowEnd = cores <= 2 || memory <= 2 || effectiveType === 'slow-2g' || effectiveType === '2g';
      
      setMetrics(prev => ({
        ...prev,
        isLowEndDevice: isLowEnd
      }));

      // Adjust config for low-end devices
      if (isLowEnd) {
        setConfig(prev => ({
          ...prev,
          optimizeForLowEnd: true,
          maxConcurrentRequests: 3,
          cacheStrategy: 'aggressive',
          imageQuality: 'low',
          enablePreloading: false
        }));
      }
    };

    detectDeviceCapabilities();
  }, []);

  // Monitor performance metrics
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Monitor navigation timing
    const updateLoadTime = () => {
      const timing = performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      if (loadTime > 0) {
        setMetrics(prev => ({ ...prev, loadTime }));
      }
    };

    // Monitor memory usage (if available)
    const updateMemoryUsage = () => {
      const memory = (performance as any).memory;
      if (memory) {
        const memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB
        setMetrics(prev => ({ ...prev, memoryUsage }));
      }
    };

    // Performance Observer for resource timing
    if ('PerformanceObserver' in window) {
      performanceObserverRef.current = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        let networkRequests = 0;
        let cacheHits = 0;

        entries.forEach((entry) => {
          if (entry.entryType === 'resource') {
            networkRequests++;
            const resourceEntry = entry as PerformanceResourceTiming;
            
            // Check if resource was served from cache
            if (resourceEntry.transferSize === 0 && resourceEntry.decodedBodySize > 0) {
              cacheHits++;
            }
          }
        });

        if (networkRequests > 0) {
          const cacheHitRatio = cacheHits / networkRequests;
          setMetrics(prev => ({
            ...prev,
            networkRequests: prev.networkRequests + networkRequests,
            cacheHitRatio: (prev.cacheHitRatio + cacheHitRatio) / 2
          }));
        }
      });

      performanceObserverRef.current.observe({ 
        entryTypes: ['resource', 'navigation', 'measure'] 
      });
    }

    // Monitor frame rate
    const measureFrameRate = () => {
      if (frameStartTimeRef.current === 0) {
        frameStartTimeRef.current = performance.now();
      }

      frameCountRef.current++;

      const elapsed = performance.now() - frameStartTimeRef.current;
      if (elapsed >= 1000) { // Calculate FPS every second
        const fps = Math.round((frameCountRef.current * 1000) / elapsed);
        setMetrics(prev => ({ ...prev, frameRate: fps }));
        
        frameCountRef.current = 0;
        frameStartTimeRef.current = performance.now();
      }

      requestAnimationFrame(measureFrameRate);
    };

    measureFrameRate();
    updateLoadTime();
    updateMemoryUsage();

    // Update memory usage periodically
    const memoryInterval = setInterval(updateMemoryUsage, 5000);

    return () => {
      if (performanceObserverRef.current) {
        performanceObserverRef.current.disconnect();
      }
      clearInterval(memoryInterval);
    };
  }, []);

  // Performance optimization functions
  const preloadResource = useCallback((url: string, type: 'script' | 'style' | 'image' | 'fetch' = 'fetch') => {
    if (!config.enablePreloading) return;

    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    
    switch (type) {
      case 'script':
        link.as = 'script';
        break;
      case 'style':
        link.as = 'style';
        break;
      case 'image':
        link.as = 'image';
        break;
      case 'fetch':
        link.as = 'fetch';
        link.crossOrigin = 'anonymous';
        break;
    }
    
    document.head.appendChild(link);
  }, [config.enablePreloading]);

  const optimizeImage = useCallback((src: string, width?: number, height?: number) => {
    if (!src) return src;

    // For demo purposes, return original src
    // In production, this would integrate with image optimization service
    const quality = config.imageQuality === 'high' ? 90 : 
                   config.imageQuality === 'medium' ? 70 : 50;
    
    // Simulate image optimization query params
    const params = new URLSearchParams();
    if (width) params.set('w', width.toString());
    if (height) params.set('h', height.toString());
    params.set('q', quality.toString());
    
    return `${src}?${params.toString()}`;
  }, [config.imageQuality]);

  const measureRenderTime = useCallback((componentName: string) => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      setMetrics(prev => ({
        ...prev,
        renderTime: (prev.renderTime + renderTime) / 2
      }));
      
      // Log slow renders in development
      if (process.env.NODE_ENV === 'development' && renderTime > 16) {
        console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
    };
  }, []);

  const throttleRequests = useCallback((requests: Promise<any>[]) => {
    const { maxConcurrentRequests } = config;
    
    if (requests.length <= maxConcurrentRequests) {
      return Promise.all(requests);
    }
    
    // Process requests in batches
    const results: any[] = [];
    const executeNext = async (index: number): Promise<void> => {
      if (index >= requests.length) return;
      
      const batch = requests.slice(index, index + maxConcurrentRequests);
      const batchResults = await Promise.allSettled(batch);
      results.push(...batchResults);
      
      await executeNext(index + maxConcurrentRequests);
    };
    
    return executeNext(0).then(() => results);
  }, [config.maxConcurrentRequests]);

  const updateConfig = useCallback((newConfig: Partial<PerformanceConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
    
    // Save to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('performance-config', JSON.stringify({ ...config, ...newConfig }));
    }
  }, [config]);

  // Load saved config
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const savedConfig = localStorage.getItem('performance-config');
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig);
        setConfig(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Failed to parse performance config:', error);
      }
    }
  }, []);

  return {
    metrics,
    config,
    updateConfig,
    preloadResource,
    optimizeImage,
    measureRenderTime,
    throttleRequests
  };
}

// Hook for lazy loading
export function useLazyLoading(threshold = 0.1) {
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(element);
        }
      },
      { threshold }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [threshold]);

  return { isVisible, elementRef };
}

// Hook for virtual scrolling
export function useVirtualScrolling<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(0);
  const scrollElementRef = useRef<HTMLElement>(null);

  const visibleItems = Math.ceil(containerHeight / itemHeight) + 2; // Buffer

  useEffect(() => {
    const handleScroll = () => {
      const scrollElement = scrollElementRef.current;
      if (!scrollElement) return;

      const scrollTop = scrollElement.scrollTop;
      const newStartIndex = Math.floor(scrollTop / itemHeight);
      const newEndIndex = Math.min(newStartIndex + visibleItems, items.length);

      setStartIndex(newStartIndex);
      setEndIndex(newEndIndex);
    };

    const scrollElement = scrollElementRef.current;
    if (scrollElement) {
      scrollElement.addEventListener('scroll', handleScroll);
      handleScroll(); // Initial calculation
    }

    return () => {
      if (scrollElement) {
        scrollElement.removeEventListener('scroll', handleScroll);
      }
    };
  }, [items.length, itemHeight, visibleItems]);

  const visibleItemsData = items.slice(startIndex, endIndex);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  return {
    visibleItems: visibleItemsData,
    totalHeight,
    offsetY,
    scrollElementRef,
    startIndex,
    endIndex
  };
}