// 書籍推薦データベース
import { BookRecommendation, BookCategory } from '@/types/books';

// Amazon Associate ID (本番環境では環境変数から取得)
const AMAZON_ASSOCIATE_ID = process.env.NEXT_PUBLIC_AMAZON_ASSOCIATE_ID || 'miraikakaku-22';

// Amazon URLを生成する関数
const createAmazonUrl = (asin: string): string => {
  return `https://www.amazon.co.jp/dp/${asin}?tag=${AMAZON_ASSOCIATE_ID}`;
};

// 書籍データベース
export const BOOK_RECOMMENDATIONS: BookRecommendation[] = [
  // AI投資関連書籍
  {
    asin: 'B08XQJX9VH',
    title: 'AI投資アルゴリズムの作り方',
    author: '藤原弘子',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08XQJX9VH.01.L.jpg',
    amazonUrl: createAmazonUrl('B08XQJX9VH'),
    price: '¥2,970',
    rating: 4.2,
    reviewCount: 47,
    description: 'Pythonを使ったAI投資アルゴリズムの構築方法を詳しく解説。機械学習による株価予測から実際の取引まで、実践的な内容が学べる一冊。',
    category: 'ai-investing',
    tags: ['Python', '機械学習', 'アルゴリズム取引', '株価予測'],
    relevanceScore: 95
  },
  {
    asin: 'B0792GKZN9',
    title: '機械学習による株式投資入門',
    author: '斎藤康毅',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B0792GKZN9.01.L.jpg',
    amazonUrl: createAmazonUrl('B0792GKZN9'),
    price: '¥3,520',
    rating: 4.1,
    reviewCount: 73,
    description: '機械学習の基礎から株式投資への応用まで、初心者にも分かりやすく解説。実際のデータを使った分析事例も豊富。',
    category: 'ai-investing',
    tags: ['機械学習', '株式投資', 'データ分析', '初心者向け'],
    relevanceScore: 90
  },
  
  // テクニカル分析
  {
    asin: 'B07NPQMG47',
    title: '先物市場のテクニカル分析',
    author: 'ジョン・J・マーフィー',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B07NPQMG47.01.L.jpg',
    amazonUrl: createAmazonUrl('B07NPQMG47'),
    price: '¥6,380',
    rating: 4.5,
    reviewCount: 156,
    description: 'テクニカル分析の世界的バイブル。チャートパターン、指標の使い方、市場心理まで網羅した決定版。',
    category: 'technical-analysis',
    tags: ['テクニカル分析', 'チャート', '先物取引', '投資理論'],
    relevanceScore: 98
  },
  {
    asin: 'B085W9BTQX',
    title: 'デイトレード',
    author: 'オリバー・ベレス',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B085W9BTQX.01.L.jpg',
    amazonUrl: createAmazonUrl('B085W9BTQX'),
    price: '¥2,420',
    rating: 4.3,
    reviewCount: 198,
    description: '短期トレードの心構えから実践的な手法まで、プロトレーダーの思考プロセスを学べる名著。',
    category: 'technical-analysis',
    tags: ['デイトレード', '短期投資', 'トレード心理', 'チャート分析'],
    relevanceScore: 88
  },
  
  // ファンダメンタルズ分析
  {
    asin: 'B08GKQ5RXJ',
    title: '企業価値評価の理論と実践',
    author: '柳良平',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08GKQ5RXJ.01.L.jpg',
    amazonUrl: createAmazonUrl('B08GKQ5RXJ'),
    price: '¥4,950',
    rating: 4.4,
    reviewCount: 89,
    description: 'DCF法やマルチプル法など、企業価値算定の基本から応用まで詳しく解説。実務で使える評価技術が身につく。',
    category: 'fundamental-analysis',
    tags: ['企業価値', 'DCF', 'バリュエーション', '財務分析'],
    relevanceScore: 92
  },
  {
    asin: 'B07Q6DMJZR',
    title: '決算書がスラスラわかる財務3表一体理解法',
    author: '國貞克則',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B07Q6DMJZR.01.L.jpg',
    amazonUrl: createAmazonUrl('B07Q6DMJZR'),
    price: '¥1,650',
    rating: 4.2,
    reviewCount: 234,
    description: '財務諸表の基本から投資判断に活用する方法まで、初心者にも分かりやすく解説した入門書。',
    category: 'fundamental-analysis',
    tags: ['財務諸表', '決算分析', '投資基礎', '企業分析'],
    relevanceScore: 85
  },
  
  // セクター特化
  {
    asin: 'B09HRJQ2VT',
    title: '脱炭素投資入門',
    author: '末吉竹二郎',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B09HRJQ2VT.01.L.jpg',
    amazonUrl: createAmazonUrl('B09HRJQ2VT'),
    price: '¥1,760',
    rating: 4.1,
    reviewCount: 67,
    description: '脱炭素社会に向けた投資機会と企業評価のポイント。ESG投資の実践的ガイドブック。',
    category: 'sector-specific',
    tags: ['脱炭素', 'ESG投資', 'グリーンファイナンス', 'サステナブル'],
    relevanceScore: 90
  },
  {
    asin: 'B08N6QJKXM',
    title: 'テクノロジー株投資の教科書',
    author: '広瀬隆雄',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08N6QJKXM.01.L.jpg',
    amazonUrl: createAmazonUrl('B08N6QJKXM'),
    price: '¥1,980',
    rating: 4.3,
    reviewCount: 112,
    description: 'AI、IoT、5Gなど成長テクノロジー銘柄の見分け方と投資戦略を詳しく解説。',
    category: 'sector-specific',
    tags: ['テクノロジー株', 'AI', 'IoT', '5G', '成長株'],
    relevanceScore: 93
  },
  
  // マクロ経済
  {
    asin: 'B07TQXM9PL',
    title: '金融政策の「誤解」',
    author: '早川英男',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B07TQXM9PL.01.L.jpg',
    amazonUrl: createAmazonUrl('B07TQXM9PL'),
    price: '¥1,540',
    rating: 4.2,
    reviewCount: 78,
    description: '中央銀行の政策決定プロセスから市場への影響まで、金融政策の本質を元日銀審議委員が解説。',
    category: 'macro-economics',
    tags: ['金融政策', 'FOMC', '中央銀行', '金利'],
    relevanceScore: 88
  },
  {
    asin: 'B08F7QMNJX',
    title: '経済指標の読み方・使い方',
    author: '木内登英',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08F7QMNJX.01.L.jpg',
    amazonUrl: createAmazonUrl('B08F7QMNJX'),
    price: '¥2,200',
    rating: 4.0,
    reviewCount: 45,
    description: 'GDP、雇用統計、CPI等の経済指標の見方から投資判断への活用法まで実践的に解説。',
    category: 'macro-economics',
    tags: ['経済指標', 'GDP', '雇用統計', 'CPI'],
    relevanceScore: 85
  },
  
  // トレーディング心理
  {
    asin: 'B083RY8QJX',
    title: 'ゾーン — 相場心理学入門',
    author: 'マーク・ダグラス',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B083RY8QJX.01.L.jpg',
    amazonUrl: createAmazonUrl('B083RY8QJX'),
    price: '¥3,080',
    rating: 4.4,
    reviewCount: 203,
    description: 'トレードにおける心理的要因とその克服法を詳しく分析。勝ち続けるメンタリティを身につけるための必読書。',
    category: 'trading-psychology',
    tags: ['トレード心理', 'メンタルマネジメント', '相場心理', 'リスク管理'],
    relevanceScore: 94
  },
  
  // トレーディングツール関連
  {
    asin: 'B08XYQRMNP',
    title: 'Python×トレード自動化入門',
    author: '酒井潤一',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08XYQRMNP.01.L.jpg',
    amazonUrl: createAmazonUrl('B08XYQRMNP'),
    price: '¥2,948',
    rating: 4.1,
    reviewCount: 56,
    description: 'Pythonを使った自動売買システムの構築方法を基礎から応用まで実例付きで解説。',
    category: 'trading-tools',
    tags: ['Python', '自動売買', 'システムトレード', 'API'],
    relevanceScore: 87
  }
];

// セクター別書籍マッピング
export const SECTOR_BOOK_MAPPING: Record<string, string[]> = {
  'テクノロジー': ['B08N6QJKXM', 'B08XQJX9VH', 'B0792GKZN9'],
  '金融': ['B08GKQ5RXJ', 'B07Q6DMJZR', 'B07TQXM9PL'],
  'エネルギー': ['B09HRJQ2VT'],
  'ヘルスケア': ['B08GKQ5RXJ', 'B07Q6DMJZR'],
  '消費財': ['B07Q6DMJZR', 'B08F7QMNJX'],
  '通信': ['B08N6QJKXM'],
  '不動産': ['B08GKQ5RXJ', 'B07Q6DMJZR'],
  '素材': ['B09HRJQ2VT', 'B08F7QMNJX'],
  '工業': ['B08GKQ5RXJ', 'B07Q6DMJZR']
};

// テーマ別書籍マッピング
export const THEME_BOOK_MAPPING: Record<string, string[]> = {
  '脱炭素': ['B09HRJQ2VT'],
  'AI・テクノロジー': ['B08XQJX9VH', 'B0792GKZN9', 'B08N6QJKXM'],
  'デジタル化': ['B08N6QJKXM', 'B08XYQRMNP'],
  '自動運転': ['B08N6QJKXM', 'B08XQJX9VH'],
  '5G': ['B08N6QJKXM'],
  'バイオテクノロジー': ['B08GKQ5RXJ'],
  '金融政策': ['B07TQXM9PL', 'B08F7QMNJX'],
  'インフレ': ['B08F7QMNJX', 'B07TQXM9PL']
};

// 経済イベント別書籍マッピング
export const ECONOMIC_EVENT_BOOK_MAPPING: Record<string, string[]> = {
  'FOMC': ['B07TQXM9PL', 'B08F7QMNJX'],
  '雇用統計': ['B08F7QMNJX'],
  'CPI発表': ['B08F7QMNJX', 'B07TQXM9PL'],
  'GDP発表': ['B08F7QMNJX'],
  '決算発表': ['B07Q6DMJZR', 'B08GKQ5RXJ'],
  '株主総会': ['B08GKQ5RXJ']
};

// ASINから書籍情報を取得
export const getBookByAsin = (asin: string): BookRecommendation | undefined => {
  return BOOK_RECOMMENDATIONS.find(book => book.asin === asin);
};

// 複数ASINから書籍リストを取得
export const getBooksByAsins = (asins: string[]): BookRecommendation[] => {
  return asins
    .map(asin => getBookByAsin(asin))
    .filter((book): book is BookRecommendation => book !== undefined)
    .sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));
};

// セクター関連書籍を取得
export const getBooksForSector = (sectorName: string, limit = 3): BookRecommendation[] => {
  const asins = SECTOR_BOOK_MAPPING[sectorName] || [];
  return getBooksByAsins(asins).slice(0, limit);
};

// テーマ関連書籍を取得
export const getBooksForTheme = (themeName: string, limit = 3): BookRecommendation[] => {
  const asins = THEME_BOOK_MAPPING[themeName] || [];
  return getBooksByAsins(asins).slice(0, limit);
};

// 経済イベント関連書籍を取得
export const getBooksForEconomicEvent = (eventType: string, limit = 3): BookRecommendation[] => {
  const asins = ECONOMIC_EVENT_BOOK_MAPPING[eventType] || [];
  return getBooksByAsins(asins).slice(0, limit);
};

// カテゴリー別書籍を取得
export const getBooksByCategory = (category: BookCategory, limit = 5): BookRecommendation[] => {
  return BOOK_RECOMMENDATIONS
    .filter(book => book.category === category)
    .sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0))
    .slice(0, limit);
};

// ランダム推薦書籍を取得（一般的な推薦用）
export const getRandomBooks = (limit = 4): BookRecommendation[] => {
  const shuffled = [...BOOK_RECOMMENDATIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, limit);
};