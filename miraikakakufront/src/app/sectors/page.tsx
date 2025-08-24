'use client';

import React, { useState, useEffect } from 'react';
import { Activity, Building2, BarChart3 } from 'lucide-react';
import apiClient from '@/lib/api-client';
import SectorHeatmap from '@/components/sectors/SectorHeatmap';
import SectorDetails from '@/components/sectors/SectorDetails';
import TopStocksInSector from '@/components/sectors/TopStocksInSector';

interface SectorData {
  id: string;
  name: string;
  market_cap: number;
  daily_change: number;
  weekly_change: number;
  monthly_change: number;
  stock_count: number;
  top_performers: number;
  color_intensity: number;
}

export default function SectorsPage() {
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSectorsData();
  }, []);

  const fetchSectorsData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getSectorsWithPerformance();
      if (response.status === 'success' && response.data) {
        setSectors(response.data);
      } else {
        // モックデータ
        const mockSectors: SectorData[] = [
          {
            id: 'technology',
            name: 'テクノロジー',
            market_cap: 150000000000000,
            daily_change: 2.34,
            weekly_change: 5.67,
            monthly_change: 12.45,
            stock_count: 245,
            top_performers: 15,
            color_intensity: 0.8
          },
          {
            id: 'finance',
            name: '金融',
            market_cap: 120000000000000,
            daily_change: -1.23,
            weekly_change: -2.45,
            monthly_change: -5.67,
            stock_count: 156,
            top_performers: 8,
            color_intensity: -0.4
          },
          {
            id: 'healthcare',
            name: 'ヘルスケア',
            market_cap: 95000000000000,
            daily_change: 1.89,
            weekly_change: 3.21,
            monthly_change: 8.92,
            stock_count: 134,
            top_performers: 12,
            color_intensity: 0.6
          },
          {
            id: 'consumer',
            name: '消費財',
            market_cap: 85000000000000,
            daily_change: 0.45,
            weekly_change: 1.23,
            monthly_change: 3.45,
            stock_count: 198,
            top_performers: 9,
            color_intensity: 0.2
          },
          {
            id: 'energy',
            name: 'エネルギー',
            market_cap: 75000000000000,
            daily_change: -2.67,
            weekly_change: -4.89,
            monthly_change: -8.23,
            stock_count: 87,
            top_performers: 4,
            color_intensity: -0.7
          },
          {
            id: 'realestate',
            name: '不動産',
            market_cap: 45000000000000,
            daily_change: 1.12,
            weekly_change: 2.34,
            monthly_change: 4.56,
            stock_count: 76,
            top_performers: 6,
            color_intensity: 0.3
          },
          {
            id: 'materials',
            name: '素材',
            market_cap: 35000000000000,
            daily_change: 0.78,
            weekly_change: 1.45,
            monthly_change: 2.89,
            stock_count: 92,
            top_performers: 5,
            color_intensity: 0.1
          },
          {
            id: 'industrials',
            name: '工業',
            market_cap: 65000000000000,
            daily_change: 1.45,
            weekly_change: 2.67,
            monthly_change: 6.78,
            stock_count: 167,
            top_performers: 11,
            color_intensity: 0.5
          },
          {
            id: 'utilities',
            name: '公益事業',
            market_cap: 25000000000000,
            daily_change: -0.34,
            weekly_change: -0.67,
            monthly_change: -1.23,
            stock_count: 43,
            top_performers: 2,
            color_intensity: -0.1
          },
          {
            id: 'communication',
            name: '通信サービス',
            market_cap: 55000000000000,
            daily_change: 2.12,
            weekly_change: 4.23,
            monthly_change: 9.45,
            stock_count: 78,
            top_performers: 7,
            color_intensity: 0.7
          }
        ];
        setSectors(mockSectors);
      }
    } catch (error) {
      console.error('Failed to fetch sectors data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSectorSelect = (sectorId: string) => {
    setSelectedSector(prevSelected => prevSelected === sectorId ? null : sectorId);
  };

  const handleTimeframeChange = (newTimeframe: 'daily' | 'weekly' | 'monthly') => {
    setTimeframe(newTimeframe);
  };

  const getSelectedSectorName = () => {
    const sector = sectors.find(s => s.id === selectedSector);
    return sector?.name || null;
  };

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Activity className="w-8 h-8 mr-3 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">セクター分析</h1>
            <p className="text-sm text-gray-400 mt-1">
              市場セクター別のパフォーマンス分析と投資機会の発見
            </p>
          </div>
        </div>
        
        {!loading && (
          <div className="text-right">
            <div className="text-sm text-gray-400">総銘柄数</div>
            <div className="text-2xl font-bold text-white">
              {sectors.reduce((sum, s) => sum + s.stock_count, 0).toLocaleString()}
            </div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6">
          {/* 左カラム - ヒートマップ */}
          <div className="col-span-12 lg:col-span-7">
            <SectorHeatmap
              sectors={sectors}
              selectedSector={selectedSector}
              onSectorSelect={handleSectorSelect}
              timeframe={timeframe}
              onTimeframeChange={handleTimeframeChange}
            />
          </div>

          {/* 右カラム - セクター詳細 */}
          <div className="col-span-12 lg:col-span-5">
            <SectorDetails
              sectorId={selectedSector}
              sectorName={getSelectedSectorName()}
              timeframe={timeframe}
            />
          </div>

          {/* 下部 - 選択されたセクターの銘柄一覧 */}
          <div className="col-span-12">
            <TopStocksInSector
              sectorId={selectedSector}
              sectorName={getSelectedSectorName()}
            />
          </div>
        </div>
      )}

      {/* パフォーマンスサマリー */}
      {!loading && sectors.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-green-400" />
            セクター別パフォーマンス ランキング
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sectors
              .sort((a, b) => {
                const aChange = timeframe === 'daily' ? a.daily_change 
                              : timeframe === 'weekly' ? a.weekly_change 
                              : a.monthly_change;
                const bChange = timeframe === 'daily' ? b.daily_change 
                              : timeframe === 'weekly' ? b.weekly_change 
                              : b.monthly_change;
                return bChange - aChange;
              })
              .slice(0, 6)
              .map((sector, index) => {
                const change = timeframe === 'daily' ? sector.daily_change 
                             : timeframe === 'weekly' ? sector.weekly_change 
                             : sector.monthly_change;
                
                return (
                  <button
                    key={sector.id}
                    onClick={() => handleSectorSelect(sector.id)}
                    className={`p-4 rounded-lg border transition-all hover:scale-[1.02] ${
                      selectedSector === sector.id
                        ? 'bg-blue-900/20 border-blue-500/50'
                        : 'bg-gray-800/30 border-gray-700/50 hover:bg-gray-800/50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium text-gray-300">
                        #{index + 1}
                      </div>
                      <div className={`text-lg font-bold ${
                        change >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                      </div>
                    </div>
                    <div className="text-left">
                      <div className="font-semibold text-white mb-1">
                        {sector.name}
                      </div>
                      <div className="text-sm text-gray-400">
                        {sector.stock_count}銘柄 • {sector.top_performers}社注目
                      </div>
                    </div>
                  </button>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}