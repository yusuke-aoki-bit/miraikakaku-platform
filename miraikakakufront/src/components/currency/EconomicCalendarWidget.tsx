'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Globe, Star, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface EconomicEvent {
  id: string;
  time: string;
  country: string;
  currency: string;
  event_name: string;
  importance: 'high' | 'medium' | 'low';
  actual?: string;
  forecast?: string;
  previous?: string;
  impact?: 'positive' | 'negative' | 'neutral';
  description?: string;
}

interface EconomicCalendarWidgetProps {
  limit?: number;
  showFilters?: boolean;
  selectedCurrencies?: string[];
  onEventClick?: (event: EconomicEvent) => void;
}

const IMPORTANCE_CONFIG = {
  high: { label: '高', color: 'text-red-400', bgColor: 'bg-red-500/20', stars: 3 },
  medium: { label: '中', color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', stars: 2 },
  low: { label: '低', color: 'text-green-400', bgColor: 'bg-green-500/20', stars: 1 }
};

const COUNTRY_FLAGS: { [key: string]: string } = {
  'USD': '🇺🇸',
  'EUR': '🇪🇺',
  'JPY': '🇯🇵',
  'GBP': '🇬🇧',
  'AUD': '🇦🇺',
  'CAD': '🇨🇦',
  'CHF': '🇨🇭',
  'NZD': '🇳🇿',
  'CNY': '🇨🇳'
};

export default function EconomicCalendarWidget({
  limit = 10,
  showFilters = false,
  selectedCurrencies = [],
  onEventClick
}: EconomicCalendarWidgetProps) {
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImportance, setSelectedImportance] = useState<string>('all');
  const [filteredEvents, setFilteredEvents] = useState<EconomicEvent[]>([]);

  const fetchEconomicEvents = async () => {
    try {
      setLoading(true);
      
      // 今日から7日間のデータを取得
      const today = new Date();
      const endDate = new Date(today);
      endDate.setDate(today.getDate() + 7);
      
      const response = await apiClient.getEconomicCalendar(
        today.toISOString().split('T')[0]
      );

      if (response.success && response.data) {
        const dataArray = Array.isArray(response.data) ? response.data : [];
        setEvents(dataArray.slice(0, limit));
      } else {
        // モックデータ
        const mockEvents: EconomicEvent[] = [
          {
            id: '1',
            time: '08:30',
            country: 'US',
            currency: 'USD',
            event_name: '米雇用統計（非農業部門雇用者数）',
            importance: 'high',
            actual: '---',
            forecast: '+195K',
            previous: '+187K',
            impact: 'positive',
            description: '米国の雇用市場の健全性を示す最重要指標の一つ'
          },
          {
            id: '2',
            time: '10:00',
            country: 'EU',
            currency: 'EUR',
            event_name: 'ECB政策金利発表',
            importance: 'high',
            actual: '---',
            forecast: '4.25%',
            previous: '4.25%',
            impact: 'neutral',
            description: 'ヨーロッパ中央銀行の金融政策決定'
          },
          {
            id: '3',
            time: '14:00',
            country: 'JP',
            currency: 'JPY',
            event_name: '日銀短観（大企業製造業）',
            importance: 'medium',
            actual: '---',
            forecast: '+12',
            previous: '+10',
            impact: 'positive',
            description: '日本の企業景況感を示す重要な先行指標'
          },
          {
            id: '4',
            time: '15:30',
            country: 'GB',
            currency: 'GBP',
            event_name: 'GDP成長率（前期比）',
            importance: 'medium',
            actual: '---',
            forecast: '0.3%',
            previous: '0.2%',
            impact: 'positive',
            description: '英国経済の成長率を示す重要指標'
          },
          {
            id: '5',
            time: '21:00',
            country: 'US',
            currency: 'USD',
            event_name: 'FOMC議事録公表',
            importance: 'high',
            actual: '---',
            forecast: '---',
            previous: '---',
            impact: 'neutral',
            description: 'FRBの金融政策決定プロセスの詳細'
          },
          {
            id: '6',
            time: '09:45',
            country: 'CN',
            currency: 'CNY',
            event_name: '中国製造業PMI',
            importance: 'medium',
            actual: '---',
            forecast: '50.2',
            previous: '49.8',
            impact: 'positive',
            description: '中国製造業の景況感指数'
          },
          {
            id: '7',
            time: '16:30',
            country: 'AU',
            currency: 'AUD',
            event_name: 'RBA政策金利発表',
            importance: 'high',
            actual: '---',
            forecast: '4.35%',
            previous: '4.35%',
            impact: 'neutral',
            description: 'オーストラリア準備銀行の金融政策'
          }
        ];
        
        setEvents(mockEvents.slice(0, limit));
      }
    } catch (error) {
      console.error('Failed to fetch economic events:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEconomicEvents();
    
    // 1時間ごとに更新
    const interval = setInterval(fetchEconomicEvents, 3600000);
    return () => clearInterval(interval);
  }, [limit]);

  // フィルタリング処理
  useEffect(() => {
    let filtered = events;

    // 重要度フィルター
    if (selectedImportance !== 'all') {
      filtered = filtered.filter(event => event.importance === selectedImportance);
    }

    // 通貨フィルター
    if (selectedCurrencies.length > 0) {
      filtered = filtered.filter(event => selectedCurrencies.includes(event.currency));
    }

    setFilteredEvents(filtered);
  }, [events, selectedImportance, selectedCurrencies]);

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-400 border-t-transparent"></div>
          <span className="ml-2 text-gray-400">経済指標読み込み中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Calendar className="w-6 h-6 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">重要経済指標</h3>
        </div>
        
        <div className="flex items-center space-x-2 text-xs text-gray-400">
          <Globe className="w-4 h-4" />
          <span>今後7日間</span>
        </div>
      </div>

      {/* フィルター */}
      {showFilters && (
        <div className="mb-4 flex space-x-2">
          <select
            value={selectedImportance}
            onChange={(e) => setSelectedImportance(e.target.value)}
            className="px-3 py-1 bg-gray-800/50 border border-gray-700/50 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            <option value="all">すべての重要度</option>
            <option value="high">高重要度のみ</option>
            <option value="medium">中重要度のみ</option>
            <option value="low">低重要度のみ</option>
          </select>
        </div>
      )}

      {/* イベントリスト */}
      <div className="space-y-3">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>該当する経済指標が見つかりません</p>
          </div>
        ) : (
          filteredEvents.map((event) => {
            const importanceConfig = IMPORTANCE_CONFIG[event.importance];
            const countryFlag = COUNTRY_FLAGS[event.currency] || '🌐';
            
            return (
              <div
                key={event.id}
                onClick={() => onEventClick?.(event)}
                className={`p-4 bg-gray-800/30 rounded-lg hover:bg-gray-800/50 transition-all cursor-pointer border-l-4 ${
                  event.importance === 'high' ? 'border-red-500' :
                  event.importance === 'medium' ? 'border-yellow-500' :
                  'border-green-500'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* 時刻 */}
                  <div className="flex items-center space-x-2 min-w-[60px]">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-400 font-mono">{event.time}</span>
                  </div>

                  {/* 国旗 */}
                  <div className="text-xl">{countryFlag}</div>

                  {/* イベント詳細 */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium text-white text-sm">{event.event_name}</h4>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${importanceConfig.bgColor} ${importanceConfig.color}`}>
                        {importanceConfig.label}
                      </div>
                    </div>
                    
                    {/* 予想値・前回値 */}
                    <div className="flex flex-wrap items-center gap-4 text-xs">
                      {event.forecast && (
                        <div>
                          <span className="text-gray-400">予想: </span>
                          <span className="text-white font-medium">{event.forecast}</span>
                        </div>
                      )}
                      {event.previous && (
                        <div>
                          <span className="text-gray-400">前回: </span>
                          <span className="text-gray-300">{event.previous}</span>
                        </div>
                      )}
                      {event.actual && event.actual !== '---' && (
                        <div>
                          <span className="text-gray-400">実績: </span>
                          <span className="text-yellow-400 font-medium">{event.actual}</span>
                        </div>
                      )}
                    </div>

                    {/* 説明 */}
                    {event.description && (
                      <p className="text-xs text-gray-500 mt-2">{event.description}</p>
                    )}
                  </div>

                  {/* 重要度星表示 */}
                  <div className="flex space-x-1">
                    {Array.from({ length: 3 }, (_, i) => (
                      <Star
                        key={i}
                        className={`w-3 h-3 ${
                          i < importanceConfig.stars 
                            ? `${importanceConfig.color} fill-current` 
                            : 'text-gray-600'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* フッター */}
      <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
        <span>最終更新: {new Date().toLocaleTimeString()}</span>
        <span>{filteredEvents.length}件の指標</span>
      </div>
    </div>
  );
}