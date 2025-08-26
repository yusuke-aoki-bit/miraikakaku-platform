// Amazon Associate 書籍推薦システム用の型定義

export interface BookRecommendation {
  asin: string; // Amazon Standard Identification Number
  title: string;
  author: string;
  imageUrl: string;
  amazonUrl: string;
  price?: string;
  rating?: number;
  reviewCount?: number;
  description: string;
  category: BookCategory;
  tags: string[];
  relevanceScore?: number; // 0-100のスコア
}

export type BookCategory = 
  | 'ai-investing'
  | 'technical-analysis' 
  | 'fundamental-analysis'
  | 'macro-economics'
  | 'sector-specific'
  | 'trading-psychology'
  | 'financial-markets'
  | 'cryptocurrency'
  | 'esg-investing'
  | 'trading-tools';

export interface BookSection {
  title: string;
  subtitle?: string;
  books: BookRecommendation[];
  displayType: 'grid' | 'list' | 'carousel';
  maxDisplay?: number;
}

export interface BookRecommendationContext {
  contextType: 'sector' | 'ai-analysis' | 'theme' | 'economic-event' | 'general';
  contextValue: string; // セクター名、テーマ名、イベント名など
  relatedKeywords: string[];
}