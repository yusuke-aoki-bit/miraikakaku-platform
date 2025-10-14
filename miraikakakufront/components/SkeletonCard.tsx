export default function SkeletonCard() {
  return (
    <div className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded w-8"></div>
            <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
          </div>
          <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-32"></div>
        </div>
        <div className="text-right">
          <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-16 mb-1"></div>
          <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-12"></div>
        </div>
      </div>
    </div>
  );
}
