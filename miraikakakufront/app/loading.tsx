import LoadingSpinner from '@/components/LoadingSpinner';

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="text-xl text-gray-700 dark:text-gray-300">読み込み中...</p>
      </div>
    </div>
  );
}
