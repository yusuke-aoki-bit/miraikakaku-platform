import { LucideIcon } from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon: LucideIcon;
  badge?: string;
  userLevel: ('beginner' | 'intermediate' | 'advanced')[];
  children?: NavigationItem[];
  isCollapsed?: boolean;
  hotkey?: string;
  description?: string;
  category: 'primary' | 'secondary' | 'tertiary';
}

export interface TabNavigationItem {
  id: string;
  label: string;
  href: string;
  icon: LucideIcon;
  isActive?: boolean;
  hotkey?: string;
  description?: string;
}

export interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: LucideIcon;
  action: () => void;
  category: 'navigation' | 'action' | 'search' | 'widget' | 'layout';
  keywords: string[];
  userLevel: ('beginner' | 'intermediate' | 'advanced')[];
  hotkey?: string;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: LucideIcon;
}