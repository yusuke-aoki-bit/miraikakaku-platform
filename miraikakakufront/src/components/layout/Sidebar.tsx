'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Compass, Folder, SlidersHorizontal, Settings, ChevronDown, BarChart3, Trophy, Brain, History, Star, Calculator, Search } from 'lucide-react';

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
}

const NavLink = ({ href, children }: NavLinkProps) => {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link 
      href={href}
      className={`w-full flex items-center px-4 py-3 rounded-lg transition-all ${
        isActive 
          ? 'bg-gradient-to-r from-red-600/20 to-pink-600/20 text-white border border-red-500/30' 
          : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
      }`}
    >
      {children}
    </Link>
  );
};

const AccordionLink = ({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) => {
  const pathname = usePathname();
  const containsActiveLink = React.Children.toArray(children).some(child => 
    React.isValidElement(child) && pathname.startsWith(child.props.href)
  );
  const [isOpen, setIsOpen] = useState(containsActiveLink);

  return (
    <div>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/50 transition-all"
      >
        <div className="flex items-center">
          {icon}
          <span className="ml-3">{title}</span>
        </div>
        <ChevronDown className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="pl-8 pt-2 space-y-2">
          {children}
        </div>
      )}
    </div>
  );
}

export default function Sidebar() {
  return (
    <div className="w-64 bg-black/95 border-r border-gray-800/50 flex flex-col backdrop-blur-sm">
      <nav className="flex-1 px-4 py-6 space-y-2 animate-slide-up">
        <NavLink href="/">
          <Home className="w-5 h-5 mr-3" />
          ホーム
        </NavLink>

        <AccordionLink title="マーケット" icon={<Compass className="w-5 h-5" />}>
          <NavLink href="/realtime">
            <BarChart3 className="w-5 h-5 mr-3" />
            リアルタイム
          </NavLink>
          <NavLink href="/rankings">
            <Trophy className="w-5 h-5 mr-3" />
            ランキング
          </NavLink>
          <NavLink href="/analysis">
            <Brain className="w-5 h-5 mr-3" />
            分析
          </NavLink>
        </AccordionLink>

        <AccordionLink title="ポートフォリオ" icon={<Folder className="w-5 h-5" />}>
          <NavLink href="/dashboard">
            <Star className="w-5 h-5 mr-3" />
            ダッシュボード
          </NavLink>
          <NavLink href="/watchlist">
            <Star className="w-5 h-5 mr-3" />
            ウォッチリスト
          </NavLink>
          <NavLink href="/history">
            <History className="w-5 h-5 mr-3" />
            取引履歴
          </NavLink>
        </AccordionLink>

        <AccordionLink title="分析ツール" icon={<SlidersHorizontal className="w-5 h-5" />}>
          <NavLink href="/predictions">
            <Search className="w-5 h-5 mr-3" />
            AI予測
          </NavLink>
          <NavLink href="/tools">
            <Calculator className="w-5 h-5 mr-3" />
            分析ツール
          </NavLink>
        </AccordionLink>

        <div className="pt-8">
          <NavLink href="/management">
            <Settings className="w-5 h-5 mr-3" />
            管理
          </NavLink>
        </div>
      </nav>
    </div>
  );
}
