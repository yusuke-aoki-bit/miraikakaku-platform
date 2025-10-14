/**
 * Skeleton UI Components
 * ローディング時の視覚的なフィードバックを提供
 */

interface SkeletonProps {
  className?: string;
}

/**
 * 基本的なスケルトンコンポーネント
 */
export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`}
      aria-live="polite"
      aria-busy="true"
    />
  );
}

/**
 * カードスケルトン - ランキングカードなどに使用
 */
export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <div className="flex justify-between items-start">
        <div className="flex-1 space-y-3">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-8 w-20" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </div>
    </div>
  );
}

/**
 * テーブル行スケルトン
 */
export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
  return (
    <tr className="border-b border-gray-200 dark:border-gray-700">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}

/**
 * チャートスケルトン
 */
export function ChartSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="space-y-4">
        <Skeleton className="h-6 w-48" />
        <div className="h-64 flex items-end justify-between space-x-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton
              key={i}
              className="w-full"
              style={{ height: `${Math.random() * 80 + 20}%` }}
            />
          ))}
        </div>
        <div className="flex justify-between">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-3 w-12" />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * 統計カードスケルトン
 */
export function StatCardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <Skeleton className="h-4 w-24 mb-3" />
      <Skeleton className="h-8 w-32 mb-2" />
      <Skeleton className="h-3 w-16" />
    </div>
  );
}

/**
 * グリッドレイアウト用スケルトン
 */
export function GridSkeleton({
  items = 6,
  columns = 3
}: {
  items?: number;
  columns?: number
}) {
  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-${columns} gap-6`}
      role="status"
      aria-label="コンテンツを読み込み中"
    >
      {Array.from({ length: items }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * リストアイテムスケルトン
 */
export function ListItemSkeleton() {
  return (
    <div className="flex items-center space-x-4 p-4 border-b border-gray-200 dark:border-gray-700">
      <Skeleton className="h-12 w-12 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
      <Skeleton className="h-8 w-20" />
    </div>
  );
}

/**
 * ヘッダースケルトン
 */
export function HeaderSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 shadow">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-32" />
          <div className="flex space-x-4">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * ページ全体のスケルトン
 */
export function PageSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <HeaderSkeleton />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <GridSkeleton items={6} columns={3} />
      </div>
    </div>
  );
}

/**
 * 銘柄詳細ページスケルトン
 */
export function StockDetailSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <Skeleton className="h-8 w-32 mb-4" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-6 w-24" />
              </div>
            ))}
          </div>
        </div>

        {/* Chart */}
        <ChartSkeleton />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * ランキングページスケルトン
 */
export function RankingPageSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        <Skeleton className="h-10 w-48 mb-8" />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <Skeleton className="h-6 w-40 mb-4" />
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, j) => (
                  <ListItemSkeleton key={j} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
