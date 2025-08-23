'use client';

import { useVirtualScrolling } from '@/hooks/usePerformance';
import { ReactNode, CSSProperties } from 'react';

interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  height: number;
  renderItem: (item: T, index: number) => ReactNode;
  className?: string;
  overscan?: number;
}

export default function VirtualList<T>({
  items,
  itemHeight,
  height,
  renderItem,
  className = '',
  overscan = 5
}: VirtualListProps<T>) {
  const {
    visibleItems,
    totalHeight,
    scrollElementRef,
    startIndex
  } = useVirtualScrolling(items, itemHeight, height);

  // Add overscan items
  const overscanStart = Math.max(0, startIndex - overscan);
  const overscanEnd = Math.min(items.length, startIndex + visibleItems.length + overscan);
  const overscanItems = items.slice(overscanStart, overscanEnd);

  const containerStyle: CSSProperties = {
    height,
    overflow: 'auto',
    position: 'relative'
  };

  const contentStyle: CSSProperties = {
    height: totalHeight,
    position: 'relative'
  };

  const viewportStyle: CSSProperties = {
    transform: `translateY(${overscanStart * itemHeight}px)`,
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0
  };

  return (
    <div
      ref={scrollElementRef as React.RefObject<HTMLDivElement>}
      className={`virtual-list ${className}`}
      style={containerStyle}
      role="list"
    >
      <div style={contentStyle}>
        <div style={viewportStyle}>
          {overscanItems.map((item, index) => {
            const itemIndex = overscanStart + index;
            return (
              <div
                key={itemIndex}
                style={{
                  height: itemHeight,
                  position: 'relative'
                }}
                role="listitem"
              >
                {renderItem(item, itemIndex)}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Virtual table component for stock data
interface VirtualTableProps {
  data: any[];
  columns: {
    key: string;
    label: string;
    width: number;
    render?: (value: any, row: any, index: number) => ReactNode;
  }[];
  rowHeight?: number;
  height: number;
  className?: string;
}

export function VirtualTable({
  data,
  columns,
  rowHeight = 48,
  height,
  className = ''
}: VirtualTableProps) {
  const renderRow = (row: any, index: number) => (
    <div 
      className="flex items-center border-b border-border-default hover:bg-surface-hover transition-colors"
      style={{ height: rowHeight }}
    >
      {columns.map((column) => (
        <div
          key={column.key}
          className="px-4 py-2 text-text-primary"
          style={{ width: column.width, minWidth: column.width }}
        >
          {column.render 
            ? column.render(row[column.key], row, index)
            : row[column.key]
          }
        </div>
      ))}
    </div>
  );

  return (
    <div className={`virtual-table ${className}`}>
      {/* Header */}
      <div className="flex bg-surface-elevated border-b border-border-default sticky top-0 z-10">
        {columns.map((column) => (
          <div
            key={column.key}
            className="px-4 py-3 font-semibold text-text-primary"
            style={{ width: column.width, minWidth: column.width }}
          >
            {column.label}
          </div>
        ))}
      </div>
      
      {/* Virtual list body */}
      <VirtualList
        items={data}
        itemHeight={rowHeight}
        height={height - 50} // Subtract header height
        renderItem={renderRow}
      />
    </div>
  );
}

// Infinite scroll component
interface InfiniteScrollProps<T> {
  items: T[];
  loadMore: () => Promise<void>;
  hasMore: boolean;
  isLoading: boolean;
  renderItem: (item: T, index: number) => ReactNode;
  threshold?: number;
  className?: string;
}

export function InfiniteScroll<T>({
  items,
  loadMore,
  hasMore,
  isLoading,
  renderItem,
  threshold = 100,
  className = ''
}: InfiniteScrollProps<T>) {
  const handleScroll = async (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    
    if (
      scrollHeight - scrollTop - clientHeight < threshold &&
      hasMore &&
      !isLoading
    ) {
      await loadMore();
    }
  };

  return (
    <div
      className={`infinite-scroll ${className}`}
      onScroll={handleScroll}
      style={{ height: '100%', overflow: 'auto' }}
    >
      {items.map((item, index) => (
        <div key={index} role="listitem">
          {renderItem(item, index)}
        </div>
      ))}
      
      {isLoading && (
        <div className="flex items-center justify-center p-4">
          <div className="w-6 h-6 border-2 border-brand-primary border-t-transparent rounded-full animate-spin" />
          <span className="ml-2 text-text-secondary">読み込み中...</span>
        </div>
      )}
      
      {!hasMore && items.length > 0 && (
        <div className="text-center p-4 text-text-secondary">
          すべてのデータを表示しました
        </div>
      )}
    </div>
  );
}