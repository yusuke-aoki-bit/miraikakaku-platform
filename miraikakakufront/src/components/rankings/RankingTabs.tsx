'use client';

import React from 'react';
import { TrendingUp, TrendingDown, Volume2, Zap, Target } from 'lucide-react';

export interface RankingTab {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

interface RankingTabsProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export const RANKING_TABS: RankingTab[] = [
  {
    id: 'gainers',
    label: '値上がり率',
    icon: <TrendingUp className="w-4 h-4" />,
    description: '最も上昇している銘柄'
  },
  {
    id: 'losers',
    label: '値下がり率',
    icon: <TrendingDown className="w-4 h-4" />,
    description: '最も下落している銘柄'
  },
  {
    id: 'volume',
    label: '出来高',
    icon: <Volume2 className="w-4 h-4" />,
    description: '取引量の多い銘柄'
  },
  {
    id: 'ai-score',
    label: 'AIスコア',
    icon: <Zap className="w-4 h-4" />,
    description: 'AI総合評価が高い銘柄'
  },
  {
    id: 'growth',
    label: '成長ポテンシャル',
    icon: <Target className="w-4 h-4" />,
    description: 'AI予測成長率が高い銘柄'
  }
];

export default function RankingTabs({ activeTab, onTabChange }: RankingTabsProps) {
  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
      <div className="flex flex-wrap gap-2">
        {RANKING_TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50 hover:text-white'
            }`}
            title={tab.description}
          >
            {tab.icon}
            <span className="font-medium">{tab.label}</span>
          </button>
        ))}
      </div>
      
      {/* 現在選択中のタブの説明 */}
      <div className="mt-3 pt-3 border-t border-gray-800/50">
        {RANKING_TABS.map((tab) => 
          activeTab === tab.id && (
            <div key={tab.id} className="text-sm text-gray-400 flex items-center space-x-2">
              {tab.icon}
              <span>{tab.description}</span>
            </div>
          )
        )}
      </div>
    </div>
  );
}