'use client';

import React, { useEffect, useState } from 'react';
import { Clock, TrendingUp, Globe, DollarSign, Newspaper, ArrowRight } from 'lucide-react';

interface NewsItem {
  id: string;
  title: string;
  publishedAt: string;
  category: string;
  categoryColor: string;
  icon: React.ReactNode;
  summary?: string;
}

export default function MarketNews() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // モックニュースデータ（実際はAPIから取得）
    const mockNews: NewsItem[] = [
      {
        id: '1',
        title: '米FRB、利下げ観測強まる - 市場は年内2回の利下げを織り込み',
        publishedAt: '5分前',
        category: '海外',
        categoryColor: 'text-blue-400 bg-blue-400/10',
        icon: <Globe className="w-3 h-3" />,
        summary: '最新の経済指標を受けて、市場参加者の間で利下げ期待が高まっています。'
      },
      {
        id: '2',
        title: '日経平均、年初来高値を更新 - 半導体関連株が牽引',
        publishedAt: '15分前',
        category: '国内',
        categoryColor: 'text-green-400 bg-green-400/10',
        icon: <TrendingUp className="w-3 h-3" />,
        summary: 'AI需要の拡大期待から半導体関連株が軒並み上昇。'
      },
      {
        id: '3',
        title: '円相場、150円台で推移 - 日銀政策決定会合を前に様子見',
        publishedAt: '30分前',
        category: '為替',
        categoryColor: 'text-purple-400 bg-purple-400/10',
        icon: <DollarSign className="w-3 h-3" />,
        summary: '市場は日銀の政策変更の可能性を注視。'
      },
      {
        id: '4',
        title: 'トヨタ、EV新戦略を発表 - 2030年までに30車種投入へ',
        publishedAt: '1時間前',
        category: '企業',
        categoryColor: 'text-orange-400 bg-orange-400/10',
        icon: <Newspaper className="w-3 h-3" />,
        summary: '全固体電池の実用化も視野に、EV市場でのシェア拡大を目指す。'
      },
      {
        id: '5',
        title: '中国GDP、市場予想を上回る成長 - アジア株全面高',
        publishedAt: '2時間前',
        category: '海外',
        categoryColor: 'text-blue-400 bg-blue-400/10',
        icon: <Globe className="w-3 h-3" />,
        summary: '中国経済の回復基調が鮮明に。周辺国市場にも好影響。'
      },
      {
        id: '6',
        title: 'ビットコイン、最高値更新の可能性 - 機関投資家の参入続く',
        publishedAt: '3時間前',
        category: '暗号資産',
        categoryColor: 'text-yellow-400 bg-yellow-400/10',
        icon: <DollarSign className="w-3 h-3" />,
        summary: 'ETF承認後、機関投資家の資金流入が加速。'
      },
      {
        id: '7',
        title: '原油価格、3ヶ月ぶり高値 - 中東情勢の緊迫化で',
        publishedAt: '4時間前',
        category: '商品',
        categoryColor: 'text-red-400 bg-red-400/10',
        icon: <TrendingUp className="w-3 h-3" />,
        summary: '供給懸念から原油先物が急騰。エネルギー関連株にも買いが入る。'
      }
    ];
    
    setNews(mockNews);
    setLoading(false);
  }, []);

  const handleNewsClick = (newsId: string) => {
    // ニュース詳細ページへの遷移（実装予定）
    console.log(`Navigate to news: ${newsId}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center">
          <Newspaper className="w-5 h-5 mr-2 text-blue-400" />
          マーケットニュース
        </h2>
        <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors flex items-center">
          すべて見る
          <ArrowRight className="w-4 h-4 ml-1" />
        </button>
      </div>
      
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl">
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          </div>
        ) : (
          <div className="divide-y divide-gray-800/50">
            {news.map((item) => (
              <NewsItemComponent key={item.id} item={item} onClick={handleNewsClick} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface NewsItemComponentProps {
  item: NewsItem;
  onClick: (id: string) => void;
}

function NewsItemComponent({ item, onClick }: NewsItemComponentProps) {
  return (
    <button
      onClick={() => onClick(item.id)}
      className="w-full p-4 text-left hover:bg-gray-800/30 transition-all group"
    >
      <div className="flex items-start space-x-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-md text-xs font-medium ${item.categoryColor}`}>
              {item.icon}
              <span>{item.category}</span>
            </span>
            <span className="text-xs text-gray-500 flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {item.publishedAt}
            </span>
          </div>
          
          <h3 className="font-medium text-white group-hover:text-blue-400 transition-colors mb-1">
            {item.title}
          </h3>
          
          {item.summary && (
            <p className="text-sm text-gray-400 line-clamp-2">
              {item.summary}
            </p>
          )}
        </div>
        
        <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-blue-400 transition-colors flex-shrink-0 mt-1" />
      </div>
    </button>
  );
}