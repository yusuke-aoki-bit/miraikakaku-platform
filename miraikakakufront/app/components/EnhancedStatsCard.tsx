'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Users, Target, Award, Clock } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: 'trending-up' | 'trending-down' | 'users' | 'target' | 'award' | 'clock';
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'indigo';
  animationDelay?: number;
}

const iconMap = {
  'trending-up': TrendingUp
  'trending-down': TrendingDown
  'users': Users
  'target': Target
  'award': Award
  'clock': Clock
};

const colorMap = {
  blue: 'from-blue-500 to-blue-600'
  green: 'from-green-500 to-green-600'
  purple: 'from-purple-500 to-purple-600'
  orange: 'from-orange-500 to-orange-600'
  red: 'from-red-500 to-red-600'
  indigo: 'from-indigo-500 to-indigo-600'
};

export default function EnhancedStatsCard({
  title
  value
  subtitle
  icon
  color
  animationDelay = 0
}: StatCardProps) {
  const [isVisible, setIsVisible] = useState(false
  const Icon = iconMap[icon];

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true
    }, animationDelay
    return () => clearTimeout(timer
  }, [animationDelay]
  return (
    <div
      className={`enhanced-card p-6 rounded-xl transition-all duration-500 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}
      style={{
        transitionDelay
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${colorMap[color]} flex items-center justify-center shadow-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div className="text-right">
          <div className="theme-heading-lg text-2xl font-bold">{value}</div>
          {subtitle && (
            <div className="theme-body-secondary text-sm">{subtitle}</div>
          )}
        </div>
      </div>
      <h3 className="theme-heading-sm font-medium">{title}</h3>
    </div>
}