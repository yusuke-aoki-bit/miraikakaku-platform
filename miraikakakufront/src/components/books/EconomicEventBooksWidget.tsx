'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { Calendar, Clock, TrendingUp, BookOpen, AlertCircle } from 'lucide-react';
import BookRecommendationSection from './BookRecommendationSection';
import { getBooksForEconomicEvent } from '@/data/bookRecommendations';
import { BookSection } from '@/types/books';

interface EconomicEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  importance: 'high' | 'medium' | 'low';
  country: string;
  category: 'monetary' | 'employment' | 'inflation' | 'growth' | 'trade';
  impact_expected: 'positive' | 'negative' | 'neutral';
  previous_value?: string;
  forecast_value?: string;
}


export default function EconomicEventBooksWidget() {
  const [selectedEvent, setSelectedEvent] = useState<EconomicEvent | null>(null);
  const [upcomingEvents, setUpcomingEvents] = useState<EconomicEvent[]>([]);

  useEffect(() => {
    const fetchEconomicEvents = async () => {
      try {
        const response = await apiClient.getEconomicCalendar();
        
        if (response.success && response.data) {
          const events = Array.isArray(response.data) ? response.data : [];
          const now = new Date();
          const oneWeekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
          
          // 今後1週間の重要イベントをフィルタリング
          const filtered = events.filter(event => {
            const eventDate = new Date(event.date || event.time);
            return eventDate >= now && eventDate <= oneWeekLater && 
                   (event.importance === 'high' || event.importance === 'medium');
          });
          
          setUpcomingEvents(filtered.slice(0, 4));
          
          // 最も重要な直近のイベントを自動選択
          if (filtered.length > 0) {
            const highImportanceEvents = filtered.filter(e => e.importance === 'high');
            setSelectedEvent(highImportanceEvents[0] || filtered[0]);
          }
        } else {
          setUpcomingEvents([]);
          setSelectedEvent(null);
        }
      } catch (error) {
        console.error('Failed to fetch economic events:', error);
        setUpcomingEvents([]);
        setSelectedEvent(null);
      }
    };

    fetchEconomicEvents();
  }, []);

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'low': return 'text-green-400 bg-green-500/20 border-green-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getImportanceLabel = (importance: string) => {
    switch (importance) {
      case 'high': return '高';
      case 'medium': return '中';
      case 'low': return '低';
      default: return '不明';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'monetary': return '金融政策';
      case 'employment': return '雇用';
      case 'inflation': return '物価';
      case 'growth': return '成長';
      case 'trade': return '貿易';
      default: return 'その他';
    }
  };

  const getEventTypeForBooks = (event: EconomicEvent): string => {
    if (event.title.includes('FOMC')) return 'FOMC';
    if (event.title.includes('雇用統計')) return '雇用統計';
    if (event.title.includes('CPI') || event.title.includes('物価')) return 'CPI発表';
    if (event.title.includes('GDP')) return 'GDP発表';
    return event.category;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const weekday = weekdays[date.getDay()];
    return `${month}/${day}(${weekday})`;
  };

  const getDaysUntil = (dateString: string) => {
    const eventDate = new Date(dateString);
    const now = new Date();
    const diffTime = eventDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return '本日';
    if (diffDays === 1) return '明日';
    if (diffDays < 7) return `${diffDays}日後`;
    return `${Math.floor(diffDays / 7)}週間後`;
  };

  if (upcomingEvents.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="text-center py-8">
          <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400 opacity-50" />
          <h3 className="text-white font-semibold mb-2">今後1週間に重要な経済指標はありません</h3>
          <p className="text-gray-400">新しいイベントが発表されたら、こちらでお知らせします。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 今週の重要経済指標 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Calendar className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-bold text-white">今週の重要経済指標</h2>
          <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded-full border border-red-500/30">
            要注目
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {upcomingEvents.map((event) => (
            <div
              key={event.id}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                selectedEvent?.id === event.id
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
              onClick={() => setSelectedEvent(event)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-2 py-1 rounded border ${getImportanceColor(event.importance)}`}>
                    重要度{getImportanceLabel(event.importance)}
                  </span>
                  <span className="bg-gray-600 text-gray-300 text-xs px-2 py-1 rounded">
                    {getCategoryLabel(event.category)}
                  </span>
                </div>
                <span className="text-orange-400 text-sm font-medium">
                  {getDaysUntil(event.date)}
                </span>
              </div>

              <h3 className="font-semibold text-white text-sm mb-1">{event.title}</h3>
              <p className="text-gray-400 text-xs mb-2">{event.description}</p>
              
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(event.date)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{event.time}</span>
                </div>
              </div>

              {event.forecast_value && (
                <div className="mt-2 text-xs">
                  <span className="text-gray-400">予想: </span>
                  <span className="text-white font-medium">{event.forecast_value}</span>
                  {event.previous_value && (
                    <>
                      <span className="text-gray-400 ml-2">前回: </span>
                      <span className="text-gray-300">{event.previous_value}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 選択されたイベントの詳細情報 */}
        {selectedEvent && (
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
            <h4 className="text-blue-300 font-medium mb-2 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2" />
              {selectedEvent.title} の市場への影響
            </h4>
            <p className="text-blue-200 text-sm">
              この指標は金融市場に大きな影響を与える可能性があります。
              発表前後は相場の変動が激しくなる傾向にあるため、
              関連する専門知識を事前に学習しておくことをお勧めします。
            </p>
          </div>
        )}
      </div>

      {/* 選択されたイベントに関連する書籍推薦 */}
      {selectedEvent && (() => {
        const eventType = getEventTypeForBooks(selectedEvent);
        const relatedBooks = getBooksForEconomicEvent(eventType, 3);
        
        if (relatedBooks.length > 0) {
          const bookSection: BookSection = {
            title: `${selectedEvent.title} 関連書籍`,
            subtitle: `${formatDate(selectedEvent.date)} の発表に備えて理解を深める`,
            books: relatedBooks,
            displayType: 'carousel',
            maxDisplay: 3
          };
          
          return (
            <BookRecommendationSection
              section={bookSection}
              contextTitle={`経済指標: ${selectedEvent.title}`}
            />
          );
        }
        return null;
      })()}

      {/* 経済指標学習ガイド */}
      <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-6">
        <h3 className="text-green-300 font-semibold mb-3 flex items-center">
          <BookOpen className="w-5 h-5 mr-2" />
          📈 経済指標を活用した投資戦略
        </h3>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="text-white font-medium mb-2">発表前の準備</h4>
              <ul className="space-y-1 text-green-200">
                <li>• 前回値と市場予想を確認</li>
                <li>• 関連セクターの動向をチェック</li>
                <li>• ポジションサイズを調整</li>
                <li>• ストップロス設定を見直し</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-medium mb-2">発表後の対応</h4>
              <ul className="space-y-1 text-green-200">
                <li>• サプライズの程度を評価</li>
                <li>• 市場反応の合理性を判断</li>
                <li>• 長期トレンドへの影響を分析</li>
                <li>• ポートフォリオの再配分検討</li>
              </ul>
            </div>
          </div>
          
          <div className="bg-black/30 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-green-300 font-medium text-sm">プロのアドバイス</span>
            </div>
            <p className="text-green-200 text-sm">
              経済指標は短期的な相場の変動要因ですが、長期投資においては
              ファンダメンタルズの方向性を示すシグナルとして活用しましょう。
              一つの指標だけでなく、複数の指標を総合的に判断することが重要です。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}