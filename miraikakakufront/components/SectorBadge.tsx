import Link from 'next/link';

interface SectorBadgeProps {
  sector: string;
  size?: 'sm' | 'md' | 'lg';
  showLink?: boolean;
  className?: string;
}

const sectorColors: Record<string, string> = {
  'Technology': 'bg-blue-100 text-blue-800 hover:bg-blue-200',
  'Healthcare': 'bg-green-100 text-green-800 hover:bg-green-200',
  'Financial Services': 'bg-purple-100 text-purple-800 hover:bg-purple-200',
  'Consumer Cyclical': 'bg-pink-100 text-pink-800 hover:bg-pink-200',
  'Consumer Defensive': 'bg-orange-100 text-orange-800 hover:bg-orange-200',
  'Industrials': 'bg-gray-100 text-gray-800 hover:bg-gray-200',
  'Energy': 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
  'Basic Materials': 'bg-amber-100 text-amber-800 hover:bg-amber-200',
  'Real Estate': 'bg-teal-100 text-teal-800 hover:bg-teal-200',
  'Utilities': 'bg-cyan-100 text-cyan-800 hover:bg-cyan-200',
  'Communication Services': 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200',
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
  lg: 'text-base px-3 py-1.5',
};

export function SectorBadge({ 
  sector, 
  size = 'md', 
  showLink = true,
  className = '' 
}: SectorBadgeProps) {
  const colorClass = sectorColors[sector] || 'bg-gray-100 text-gray-800 hover:bg-gray-200';
  const sizeClass = sizeClasses[size];
  const baseClass = `inline-flex items-center rounded-full font-medium transition-colors ${sizeClass} ${colorClass} ${className}`;

  if (showLink) {
    return (
      <Link 
        href={`/rankings?sector=${encodeURIComponent(sector)}`}
        className={baseClass}
        title={`View ${sector} rankings`}
      >
        {sector}
      </Link>
    );
  }

  return (
    <span className={baseClass}>
      {sector}
    </span>
  );
}
