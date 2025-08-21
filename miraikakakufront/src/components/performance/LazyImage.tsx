'use client';

import { useState, useRef, useEffect } from 'react';
import { useLazyLoading, usePerformance } from '@/hooks/usePerformance';

interface LazyImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  placeholder?: string;
  quality?: 'high' | 'medium' | 'low';
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
}

export default function LazyImage({
  src,
  alt,
  width,
  height,
  className = '',
  placeholder,
  quality,
  priority = false,
  onLoad,
  onError
}: LazyImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(placeholder || '');
  const { isVisible, elementRef } = useLazyLoading(0.1);
  const { optimizeImage } = usePerformance();
  const imgRef = useRef<HTMLImageElement>(null);

  // Load image when visible or priority is set
  useEffect(() => {
    if ((isVisible || priority) && src && !isLoaded && !hasError) {
      const optimizedSrc = optimizeImage(src, width, height);
      
      const img = new Image();
      
      img.onload = () => {
        setCurrentSrc(optimizedSrc);
        setIsLoaded(true);
        onLoad?.();
      };
      
      img.onerror = () => {
        setHasError(true);
        onError?.();
      };
      
      img.src = optimizedSrc;
    }
  }, [isVisible, priority, src, width, height, optimizeImage, isLoaded, hasError, onLoad, onError]);

  // Create responsive srcSet for high-DPI displays
  const createSrcSet = () => {
    if (!src || hasError) return undefined;
    
    const baseSrc = optimizeImage(src, width, height);
    const retinaWidth = width ? width * 2 : undefined;
    const retinaHeight = height ? height * 2 : undefined;
    const retinaSrc = optimizeImage(src, retinaWidth, retinaHeight);
    
    return `${baseSrc} 1x, ${retinaSrc} 2x`;
  };

  // Loading placeholder
  if (!isVisible && !priority) {
    return (
      <div
        ref={elementRef as React.RefObject<HTMLDivElement>}
        className={`bg-surface-hover animate-pulse ${className}`}
        style={{ width, height }}
        aria-label={`${alt}を読み込み中`}
      />
    );
  }

  // Error state
  if (hasError) {
    return (
      <div
        className={`bg-surface-hover border border-border-default rounded-lg flex items-center justify-center ${className}`}
        style={{ width, height }}
        role="img"
        aria-label={`${alt}の読み込みに失敗しました`}
      >
        <div className="text-center text-text-secondary">
          <div className="text-2xl mb-2">📷</div>
          <div className="text-xs">画像を読み込めませんでした</div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={elementRef as React.RefObject<HTMLDivElement>}
      className={`relative overflow-hidden ${className}`}
      style={{ width, height }}
    >
      {/* Placeholder/blur */}
      {placeholder && !isLoaded && (
        <img
          src={placeholder}
          alt=""
          className="absolute inset-0 w-full h-full object-cover filter blur-sm scale-110"
          aria-hidden="true"
        />
      )}
      
      {/* Loading skeleton */}
      {!placeholder && !isLoaded && (
        <div className="absolute inset-0 bg-surface-hover animate-pulse" />
      )}
      
      {/* Main image */}
      <img
        ref={imgRef}
        src={currentSrc}
        srcSet={createSrcSet()}
        alt={alt}
        width={width}
        height={height}
        className={`w-full h-full object-cover transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-0'
        }`}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
      />
      
      {/* Loading indicator */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}

// Progressive image loading component
export function ProgressiveImage({
  src,
  lowQualitySrc,
  alt,
  width,
  height,
  className = '',
  priority = false
}: {
  src: string;
  lowQualitySrc?: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
}) {
  const [highQualityLoaded, setHighQualityLoaded] = useState(false);
  const { isVisible, elementRef } = useLazyLoading(0.1);
  const { optimizeImage } = usePerformance();

  // Load high quality image when visible
  useEffect(() => {
    if ((isVisible || priority) && src && !highQualityLoaded) {
      const img = new Image();
      img.onload = () => setHighQualityLoaded(true);
      img.src = optimizeImage(src, width, height);
    }
  }, [isVisible, priority, src, width, height, optimizeImage, highQualityLoaded]);

  if (!isVisible && !priority) {
    return (
      <div
        ref={elementRef as React.RefObject<HTMLDivElement>}
        className={`bg-surface-hover animate-pulse ${className}`}
        style={{ width, height }}
      />
    );
  }

  return (
    <div 
      ref={elementRef as React.RefObject<HTMLDivElement>}
      className={`relative overflow-hidden ${className}`}
      style={{ width, height }}
    >
      {/* Low quality placeholder */}
      {lowQualitySrc && (
        <img
          src={lowQualitySrc}
          alt=""
          className={`absolute inset-0 w-full h-full object-cover filter blur-sm transition-opacity duration-500 ${
            highQualityLoaded ? 'opacity-0' : 'opacity-100'
          }`}
          aria-hidden="true"
        />
      )}
      
      {/* High quality image */}
      {(highQualityLoaded || priority) && (
        <img
          src={optimizeImage(src, width, height)}
          alt={alt}
          width={width}
          height={height}
          className={`w-full h-full object-cover transition-opacity duration-500 ${
            highQualityLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          loading={priority ? 'eager' : 'lazy'}
        />
      )}
    </div>
  );
}