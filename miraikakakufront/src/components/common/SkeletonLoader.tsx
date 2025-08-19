'use client';

import React from 'react';

interface SkeletonLoaderProps {
  width?: string;
  height?: string;
  className?: string;
  borderRadius?: string;
}

export default function SkeletonLoader({
  width = '100%',
  height = '20px',
  className = '',
  borderRadius = 'rounded-md',
}: SkeletonLoaderProps) {
  return (
    <div
      className={`animate-pulse bg-dark-border ${borderRadius} ${className}`}
      style={{ width, height }}
    />
  );
}
