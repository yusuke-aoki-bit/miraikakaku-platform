import React from 'react';

// Skeleton animation CSS class - using our custom dark theme animation
const skeletonClass = "skeleton-animate rounded shimmer-effect";

export const StockHeaderSkeleton: React.FC = () => (
  <div className="rounded-lg shadow-md p-6 mb-8" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
      <div className="mb-4 md:mb-0">
        {/* Symbol and name skeleton */}
        <div className={`${skeletonClass} h-8 w-32 mb-2`}></div>
        <div className={`${skeletonClass} h-6 w-48`}></div>
      </div>
      <div className="text-right">
        {/* Price skeleton */}
        <div className={`${skeletonClass} h-10 w-24 mb-2 ml-auto`}></div>
        <div className={`${skeletonClass} h-5 w-20 ml-auto`}></div>
      </div>
    </div>
  </div>
);
export const StockChartSkeleton: React.FC = () => (
  <div className="rounded-lg shadow-md p-6 mb-8" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    {/* Chart title skeleton */}
    <div className={`${skeletonClass} h-6 w-40 mb-4`}></div>

    {/* Chart area skeleton */}
    <div className={`${skeletonClass} h-80 w-full mb-4`}></div>

    {/* Chart controls skeleton */}
    <div className="flex gap-2">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className={`${skeletonClass} h-8 w-12`}></div>
      ))}
    </div>
  </div>
);
export const AnalysisCardSkeleton: React.FC<{ title?: string }> = ({ title }) => (
  <div className="rounded-lg shadow-md p-6 mb-6" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    {/* Title */}
    {title ? (
      <div className="text-lg font-semibold mb-4" style={{ color: 'var(--yt-music-text)' }}>
        {title}
      </div>
    ) : (
      <div className={`${skeletonClass} h-6 w-32 mb-4`}></div>
    )}

    {/* Content lines */}
    <div className="space-y-3">
      <div className={`${skeletonClass} h-4 w-full`}></div>
      <div className={`${skeletonClass} h-4 w-5/6`}></div>
      <div className={`${skeletonClass} h-4 w-4/5`}></div>
      <div className={`${skeletonClass} h-4 w-3/4`}></div>
    </div>
  </div>
);
export const PredictionTableSkeleton: React.FC = () => (
  <div className="rounded-lg shadow-md p-6 mb-8" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    {/* Table title */}
    <div className={`${skeletonClass} h-6 w-40 mb-4`}></div>

    {/* Table header */}
    <div className="grid grid-cols-4 gap-4 mb-3 pb-2 border-b" style={{ borderColor: 'var(--yt-music-border)' }}>
      {['Date', 'Price', 'Change', 'Confidence'].map(header => (
        <div key={header} className={`${skeletonClass} h-4 w-16`}></div>
      ))}
    </div>

    {/* Table rows */}
    {[1, 2, 3, 4, 5].map(i => (
      <div key={i} className="grid grid-cols-4 gap-4 py-2">
        <div className={`${skeletonClass} h-4 w-20`}></div>
        <div className={`${skeletonClass} h-4 w-16`}></div>
        <div className={`${skeletonClass} h-4 w-12`}></div>
        <div className={`${skeletonClass} h-4 w-10`}></div>
      </div>
    ))}
  </div>
);
export const TechnicalAnalysisSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
    {/* Technical indicators */}
    <div className="rounded-lg shadow-md p-6" style={{
      backgroundColor: 'var(--yt-music-surface)',
      border: '1px solid var(--yt-music-border)'
    }}>
      <div className={`${skeletonClass} h-6 w-32 mb-4`}></div>
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="text-center">
            <div className={`${skeletonClass} h-4 w-16 mx-auto mb-2`}></div>
            <div className={`${skeletonClass} h-6 w-12 mx-auto`}></div>
          </div>
        ))}
      </div>
    </div>

    {/* Risk analysis */}
    <div className="rounded-lg shadow-md p-6" style={{
      backgroundColor: 'var(--yt-music-surface)',
      border: '1px solid var(--yt-music-border)'
    }}>
      <div className={`${skeletonClass} h-6 w-24 mb-4`}></div>
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex justify-between">
            <div className={`${skeletonClass} h-4 w-20`}></div>
            <div className={`${skeletonClass} h-4 w-16`}></div>
          </div>
        ))}
      </div>
    </div>
  </div>
);
export const SidebarStatsSkeleton: React.FC = () => (
  <div className="rounded-lg shadow-md p-6" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    {/* Title */}
    <div className={`${skeletonClass} h-5 w-24 mb-4`}></div>

    {/* Stats rows */}
    <div className="space-y-3">
      {[1, 2, 3, 4, 5, 6].map(i => (
        <div key={i} className="flex justify-between">
          <div className={`${skeletonClass} h-4 w-20`}></div>
          <div className={`${skeletonClass} h-4 w-16`}></div>
        </div>
      ))}
    </div>
  </div>
);
export const PriceAlertsSkeleton: React.FC = () => (
  <div className="rounded-lg shadow-md p-6" style={{
    backgroundColor: 'var(--yt-music-surface)',
    border: '1px solid var(--yt-music-border)'
  }}>
    {/* Title */}
    <div className={`${skeletonClass} h-5 w-24 mb-4`}></div>

    {/* Alert form */}
    <div className="space-y-4">
      <div className={`${skeletonClass} h-10 w-full`}></div>
      <div className={`${skeletonClass} h-8 w-20`}></div>
    </div>
  </div>
);
// Compound loading component for different stages
export const ProgressiveDetailSkeleton: React.FC<{
  showHeader?: boolean;
  showChart?: boolean;
  showAnalysis?: boolean;
}> = ({
  showHeader = true,
  showChart = false,
  showAnalysis = false
}) => (
  <div className="max-w-7xl mx-auto p-4 md:p-8">
    {/* Always show header skeleton initially */}
    {showHeader && <StockHeaderSkeleton />}

    {/* Show chart skeleton after basic data loads */}
    {showChart && (
      <>
        <StockChartSkeleton />
        <PredictionTableSkeleton />
      </>
    )}

    {/* Show analysis skeleton last */}
    {showAnalysis && (
      <>
        <TechnicalAnalysisSkeleton />
        <AnalysisCardSkeleton title="AI Decision Factors" />
        <AnalysisCardSkeleton title="Financial Analysis" />
      </>
    )}
  </div>
);