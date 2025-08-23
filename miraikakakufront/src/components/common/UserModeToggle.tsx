'use client';

import { User } from 'lucide-react';

interface UserModeToggleProps {
  className?: string;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function UserModeToggle({ 
  className = '', 
  showLabels = true
}: UserModeToggleProps) {
  // Always show PRO mode - no toggle functionality
  return (
    <div className={`relative ${className}`}>
      {showLabels && (
        <div className={`flex items-center space-x-2 text-sm`}>
          <User size={16} className="text-text-secondary" />
          <span className="text-text-secondary font-medium">
            プロモード
          </span>
        </div>
      )}
    </div>
  );
}