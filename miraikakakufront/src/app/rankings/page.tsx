'use client';

import React, { useState, useEffect } from 'react';
import { Trophy } from 'lucide-react';
import RankingTabs from '@/components/rankings/RankingTabs';
import RankingFilters, { RankingFilters as RankingFiltersType } from '@/components/rankings/RankingFilters';
import RankingsTable from '@/components/rankings/RankingsTable';
import apiClient from '@/lib/api-client';

interface RankingStock {
  rank: number;
  symbol: string;
  company_name: string;
  current_price: number;
  change?: number;
  change_percent?: number;
  volume_change?: number;
  ai_score?: number;
  growth_potential?: number;
  confidence?: number;
  sparkline_data?: number[];
}

export default function RankingsPage() {
  const [rankings, setRankings] = useState<RankingStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('gainers');
  const [filters, setFilters] = useState<RankingFiltersType>({
    market: [],
    sectors: [],
    marketCap: [],
    period: 'daily'
  });

  useEffect(() => {
    fetchRankings();
  }, [activeTab, filters]);

  const fetchRankings = async () => {
    setLoading(true);
    try {
      let response;
      const limit = 20;
      
      // タブに応じて適切なAPIを呼び出し
      switch (activeTab) {
        case 'gainers':
          response = await apiClient.getGainersRankings({ limit });
          break;
        case 'losers':
          response = await apiClient.getLosersRankings({ limit });
          break;
        case 'volume':
          response = await apiClient.getVolumeRankings(limit);
          break;
        case 'ai-score':
          response = await apiClient.getCompositeRankings({ limit });
          break;
        case 'growth':
          response = await apiClient.getGrowthPotentialRankings(limit);
          break;
        default:
          response = await apiClient.getGainersRankings({ limit });
      }
      
      if (response.status === 'success' && response.data) {
        // データをRankingStock形式に変換
        const dataArray = Array.isArray(response.data) ? response.data : [];
        const formattedData: RankingStock[] = dataArray.map((stock: any, index: number) => ({
          rank: index + 1,
          symbol: stock.symbol,
          company_name: stock.company_name || stock.symbol,
          current_price: stock.current_price || stock.close_price || 100,
          change: stock.change,
          change_percent: stock.change_percent || stock.growth_potential,
          volume_change: stock.volume_change,
          ai_score: stock.composite_score || (stock.confidence_score || stock.confidence) * 100 || 75,
          growth_potential: stock.growth_potential,
          confidence: stock.confidence_score || stock.confidence,
          sparkline_data: generateSparklineFromData(stock)
        }));
        
        setRankings(formattedData);
      }
    } catch (error) {
      console.error('Failed to fetch rankings:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const generateSparklineFromData = (stock: any): number[] => {
    // APIから実際の価格履歴データがある場合のみ使用
    if (stock.price_history && Array.isArray(stock.price_history) && stock.price_history.length > 0) {
      return stock.price_history.slice(-24).map((p: any) => p.close_price || p.price || 0);
    }
    
    // データがない場合は空配列を返す（チャートは表示されない）
    return [];
  };

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };
  
  const handleFiltersChange = (newFilters: RankingFiltersType) => {
    setFilters(newFilters);
  };
  
  const handleApplyFilters = () => {
    fetchRankings();
  };
  
  const handleStockClick = (symbol: string) => {
    window.location.href = `/stock/${symbol}`;
  };
  
  const handleWatchlistToggle = (symbol: string, isWatched: boolean) => {
    // ウォッチリスト管理の実装（LocalStorageまたはAPI）
    const watchlist = JSON.parse(localStorage.getItem('user_watchlist') || '[]');
    if (isWatched) {
      if (!watchlist.includes(symbol)) {
        watchlist.push(symbol);
      }
    } else {
      const index = watchlist.indexOf(symbol);
      if (index > -1) {
        watchlist.splice(index, 1);
      }
    }
    localStorage.setItem('user_watchlist', JSON.stringify(watchlist));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
          <Trophy className="w-8 h-8 mr-3 text-yellow-400" />
          銘柄ランキング
        </h1>
        <p className="text-gray-400">
          様々な切り口から市場で注目される銘柄を発見しよう
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* 左サイドバー: フィルター */}
        <div className="xl:col-span-1">
          <RankingFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onApplyFilters={handleApplyFilters}
          />
        </div>

        {/* メインコンテンツ */}
        <div className="xl:col-span-3 space-y-6">
          {/* タブ */}
          <RankingTabs
            activeTab={activeTab}
            onTabChange={handleTabChange}
          />

          {/* ランキングテーブル */}
          <RankingsTable
            data={rankings}
            loading={loading}
            rankingType={activeTab}
            onStockClick={handleStockClick}
            onWatchlistToggle={handleWatchlistToggle}
          />
        </div>
      </div>
    </div>
  );
}