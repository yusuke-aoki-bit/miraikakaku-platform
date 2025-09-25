import dynamic from 'next/dynamic';
import LoadingSpinner from './LoadingSpinner';

// Heavy components with dynamic imports for code splitting
export const StockChart = dynamic(
  () => import('./StockChart')
  {
    loading: () => <LoadingSpinner size="md" />
    ssr: false
  }
export const SystemStatus = dynamic(
  () => import('./SystemStatus')
  {
    loading: () => null
    ssr: false
  }
export const RankingCard = dynamic(
  () => import('./RankingCard')
  {
    loading: () => (
      <div className="rounded-lg p-6 glass-effect animate-pulse">
        <div className="h-6 bg-gray-300 rounded mb-4"></div>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    )
    ssr: true
  }
// Monetization components - loaded only when needed
export const AmazonAssociatesWidget = dynamic(
  () => import('./MonetizationComponents').then(mod => ({ default: mod.AmazonAssociatesWidget }))
  {
    loading: () => null
    ssr: false
  }
export const GoogleAdSenseWidget = dynamic(
  () => import('./MonetizationComponents').then(mod => ({ default: mod.GoogleAdSenseWidget }))
  {
    loading: () => null
    ssr: false
  }
export const NewsletterSignup = dynamic(
  () => import('./MonetizationComponents').then(mod => ({ default: mod.NewsletterSignup }))
  {
    loading: () => null
    ssr: false
  }
// Statistics component - defer loading to improve initial performance
export const EnhancedStatsCard = dynamic(
  () => import('./EnhancedStatsCard')
  {
    loading: () => (
      <div className="enhanced-card p-6 rounded-xl animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-gray-300 rounded-lg"></div>
          <div className="text-right">
            <div className="h-8 w-16 bg-gray-300 rounded mb-1"></div>
            <div className="h-4 w-12 bg-gray-200 rounded"></div>
          </div>
        </div>
        <div className="h-5 w-20 bg-gray-300 rounded"></div>
      </div>
    )
    ssr: true
  }
);