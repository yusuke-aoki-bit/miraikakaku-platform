'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, Layers } from 'lucide-react';
import SectorHeatmap from '@/components/sectors/SectorHeatmap';
import TopStocksInSector from '@/components/sectors/TopStocksInSector';
import SectorDetails from '@/components/sectors/SectorDetails';
import apiClient from '@/lib/api-client';

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
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  useEffect(() => {
    fetchSectorsData();
  }, []);

  const fetchSectorsData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getSectorsWithPerformance();
      if (response.success && response.data) {
        const dataArray = Array.isArray(response.data) ? response.data : [];
        setSectors(dataArray);
      } else {
        // API失敗時は空配列
        setSectors([]);
      }
    } catch (error) {
      console.error('Failed to fetch sectors data:', error);
      setSectors([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSectorSelect = (sectorId: string) => {
    setSelectedSector(sectorId);
  };

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Layers className="w-8 h-8 mr-3 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">セクター分析</h1>
            <p className="text-sm text-gray-400 mt-1">
              業界セクター別のパフォーマンス分析と投資機会の発見
            </p>
          </div>
        </div>

      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* メインビュー */}
          <SectorHeatmap
            sectors={sectors}
            onSectorSelect={handleSectorSelect}
            selectedSector={selectedSector}
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
          />

          {/* セクター詳細 */}
          {selectedSector && (
            <div className="space-y-6">
              <SectorDetails 
                sectorId={selectedSector} 
                sectorName={sectors.find(s => s.id === selectedSector)?.name || null}
                timeframe={timeframe}
              />
              <TopStocksInSector 
                sectorId={selectedSector} 
                sectorName={sectors.find(s => s.id === selectedSector)?.name || selectedSector}
              />
            </div>
          )}

          {/* セクターが選択されていない場合の説明 */}
          {!selectedSector && sectors.length > 0 && (
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-300 mb-2">
                セクターを選択してください
              </h3>
              <p className="text-gray-500">
                上のヒートマップまたはテーブルからセクターをクリックすると、
                <br />
                詳細な分析と関連銘柄を表示します。
              </p>
            </div>
          )}

          {/* データなしの場合 */}
          {sectors.length === 0 && !loading && (
            <div className="text-center py-12">
              <Layers className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-300 mb-2">
                データを読み込めませんでした
              </h3>
              <p className="text-gray-500 mb-4">
                セクターデータの取得に失敗しました。
                <br />
                しばらく時間をおいてから再度お試しください。
              </p>
              <button
                onClick={fetchSectorsData}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                再読み込み
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}