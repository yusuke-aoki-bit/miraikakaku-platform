// トレーディングツール・環境推薦データ
import { BookRecommendation } from '@/types/books';

const AMAZON_ASSOCIATE_ID = process.env.NEXT_PUBLIC_AMAZON_ASSOCIATE_ID || 'miraikakaku-22';

const createAmazonUrl = (asin: string): string => {
  return `https://www.amazon.co.jp/dp/${asin}?tag=${AMAZON_ASSOCIATE_ID}`;
};

export interface TradingTool {
  asin: string;
  name: string;
  category: TradingToolCategory;
  imageUrl: string;
  amazonUrl: string;
  price: string;
  rating?: number;
  reviewCount?: number;
  description: string;
  features: string[];
  whyRecommended: string;
  useCase: string[];
  specs?: { [key: string]: string };
}

export type TradingToolCategory = 
  | 'monitor'
  | 'pc-hardware'
  | 'ergonomics'
  | 'calculator'
  | 'software'
  | 'networking'
  | 'backup'
  | 'accessories';

export const TRADING_TOOLS: TradingTool[] = [
  // 高解像度モニター
  {
    asin: 'B08XQJB7K1',
    name: 'LG 4K モニター 27インチ 27UP850-W',
    category: 'monitor',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08XQJB7K1.01.L.jpg',
    amazonUrl: createAmazonUrl('B08XQJB7K1'),
    price: '¥54,800',
    rating: 4.4,
    reviewCount: 1247,
    description: '4K解像度でチャートの詳細まで鮮明に表示。複数の銘柄を同時監視するのに最適な27インチモニター。',
    features: [
      '4K UHD (3840×2160) 解像度',
      'USB-C ワンケーブル接続',
      'HDR10 対応',
      '高さ・角度調整可能',
      'ブルーライト軽減機能'
    ],
    whyRecommended: '4つの銘柄チャートを同時表示しても文字がくっきり見え、長時間の分析作業でも目が疲れにくい設計です。',
    useCase: [
      '複数銘柄の同時監視',
      '詳細チャート分析',
      '財務データの表示',
      'ニュース・情報収集'
    ],
    specs: {
      '画面サイズ': '27インチ',
      '解像度': '4K (3840×2160)',
      '接続': 'USB-C, HDMI, DisplayPort',
      'スタンド': '高さ・角度調整可能'
    }
  },
  {
    asin: 'B087QZPKLK',
    name: 'ASUS ProArt Display 32インチ PA329C',
    category: 'monitor',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B087QZPKLK.01.L.jpg',
    amazonUrl: createAmazonUrl('B087QZPKLK'),
    price: '¥89,800',
    rating: 4.6,
    reviewCount: 234,
    description: '32インチの大画面で最大6つのチャートを快適に表示。色精度も高く、データ視覚化に最適。',
    features: [
      '32インチ 4K解像度',
      '色精度Delta E < 2',
      'Calman認証',
      'Picture-in-Picture機能',
      'KVM機能'
    ],
    whyRecommended: '大画面により一度に多くの情報を表示でき、トレーディング効率が大幅に向上します。',
    useCase: [
      'マルチチャート表示',
      'データ分析',
      'レポート作成',
      'ウェビナー視聴'
    ]
  },

  // 高性能PC・ハードウェア
  {
    asin: 'B08N5WRWNW',
    name: 'AMD Ryzen 9 5900X プロセッサー',
    category: 'pc-hardware',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08N5WRWNW.01.L.jpg',
    amazonUrl: createAmazonUrl('B08N5WRWNW'),
    price: '¥54,800',
    rating: 4.5,
    reviewCount: 892,
    description: '12コア24スレッドの高性能CPU。複数の分析ツールを同時実行してもサクサク動作。',
    features: [
      '12コア / 24スレッド',
      'ベース 3.7GHz / ブースト 4.8GHz',
      '70MB キャッシュ',
      'AM4 ソケット',
      '105W TDP'
    ],
    whyRecommended: '複数のブラウザタブ、分析ソフト、バックテスト処理を同時実行できる圧倒的なマルチタスク性能。',
    useCase: [
      'リアルタイム株価監視',
      'バックテスト処理',
      '複数分析ツール同時実行',
      '大量データ処理'
    ]
  },
  {
    asin: 'B08HR7SV3M',
    name: 'Corsair Vengeance LPX 32GB DDR4-3200',
    category: 'pc-hardware',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08HR7SV3M.01.L.jpg',
    amazonUrl: createAmazonUrl('B08HR7SV3M'),
    price: '¥12,980',
    rating: 4.3,
    reviewCount: 567,
    description: '32GBの大容量メモリで、大量の株価データや分析結果をメモリ上で高速処理。',
    features: [
      '32GB (16GB x 2)',
      'DDR4-3200 MHz',
      'CL16 レイテンシ',
      '低プロファイル設計',
      'ヒートスプレッダー付き'
    ],
    whyRecommended: '数万銘柄のデータを同時に扱う場合でも、メモリ不足によるパフォーマンス低下を防げます。',
    useCase: [
      '大量データ分析',
      'Excelでの複雑な計算',
      '機械学習モデル実行',
      '仮想メモリ使用回避'
    ]
  },

  // エルゴノミクス
  {
    asin: 'B08BLPQR4R',
    name: 'Herman Miller セイルチェア',
    category: 'ergonomics',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08BLPQR4R.01.L.jpg',
    amazonUrl: createAmazonUrl('B08BLPQR4R'),
    price: '¥68,200',
    rating: 4.2,
    reviewCount: 189,
    description: '長時間の分析作業をサポートする人間工学デザイン。腰痛や肩こりを軽減し、集中力を維持。',
    features: [
      '人間工学に基づいた設計',
      'PostureFit SLサポート',
      '前傾機能付きアームレスト',
      '12年保証',
      'リサイクル可能素材使用'
    ],
    whyRecommended: '投資判断に重要な集中力を、身体の疲労を軽減することで長時間維持できます。',
    useCase: [
      '長時間の市場監視',
      'レポート作成',
      'バックテスト作業',
      'ウェビナー参加'
    ]
  },
  {
    asin: 'B087QMXPGL',
    name: 'エルゴトロン LX デスクマウント モニターアーム',
    category: 'ergonomics',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B087QMXPGL.01.L.jpg',
    amazonUrl: createAmazonUrl('B087QMXPGL'),
    price: '¥15,800',
    rating: 4.5,
    reviewCount: 412,
    description: 'モニターを理想的な高さと角度に調整。首や肩の負担を軽減し、見やすさを向上。',
    features: [
      '3.2〜11.3kgのモニター対応',
      '360度回転',
      '上下左右調整可能',
      'ワンタッチ高さ調整',
      '10年保証'
    ],
    whyRecommended: '目線の高さでチャートを見ることで、長時間でも疲れにくく、判断精度が向上します。',
    useCase: [
      'デュアル・トリプルモニター設置',
      '理想的な視線角度の確保',
      'デスクスペースの有効活用'
    ]
  },

  // 金融電卓・計算ツール
  {
    asin: 'B000X6XF9U',
    name: 'HP 12C ファイナンシャルプログラマブル電卓',
    category: 'calculator',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B000X6XF9U.01.L.jpg',
    amazonUrl: createAmazonUrl('B000X6XF9U'),
    price: '¥9,800',
    rating: 4.1,
    reviewCount: 145,
    description: '金融業界標準の電卓。NPV、IRR、債券価格など投資計算を素早く実行。',
    features: [
      '逆ポーランド記法(RPN)',
      '金融計算専用キー',
      'プログラマブル機能',
      '130以上の内蔵関数',
      '長寿命バッテリー'
    ],
    whyRecommended: 'プロの投資家が使用する標準ツール。複雑な投資計算を瞬時に実行できます。',
    useCase: [
      'DCF計算',
      'オプション価格計算',
      '債券価格計算',
      'ローン計算'
    ]
  },

  // ネットワーク・接続環境
  {
    asin: 'B08SHTXPJL',
    name: 'BUFFALO WiFi 6 ルーター AX6000',
    category: 'networking',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08SHTXPJL.01.L.jpg',
    amazonUrl: createAmazonUrl('B08SHTXPJL'),
    price: '¥23,800',
    rating: 4.2,
    reviewCount: 298,
    description: 'WiFi 6対応で遅延を最小限に抑制。リアルタイム取引で重要な安定した高速接続を実現。',
    features: [
      'WiFi 6 (11ax) 対応',
      '最大6000Mbps',
      'MU-MIMO対応',
      '4x4アンテナ',
      'IPoE対応'
    ],
    whyRecommended: 'ミリ秒単位が重要な取引において、安定した高速通信は必須の投資です。',
    useCase: [
      'リアルタイム取引',
      '複数デバイス同時接続',
      'ライブ配信視聴',
      'クラウドサービス利用'
    ]
  },

  // バックアップ・データ保護
  {
    asin: 'B07VS8QCXC',
    name: 'WD Black SN770 NVMe SSD 2TB',
    category: 'backup',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B07VS8QCXC.01.L.jpg',
    amazonUrl: createAmazonUrl('B07VS8QCXC'),
    price: '¥24,800',
    rating: 4.4,
    reviewCount: 723,
    description: '高速SSDで取引履歴やバックテスト結果を安全に保存。システム起動も高速化。',
    features: [
      '2TB大容量',
      'PCIe Gen4 対応',
      '読込最大5150MB/s',
      '5年保証',
      'WD Dashboard対応'
    ],
    whyRecommended: '取引データの損失は致命的。高速かつ信頼性の高いストレージで大切なデータを守ります。',
    useCase: [
      '取引履歴保存',
      'バックテスト結果保管',
      'システム高速化',
      'データ分析結果保存'
    ]
  },

  // アクセサリー
  {
    asin: 'B08XQWGR2K',
    name: 'Anker PowerConf C300 ウェブカメラ',
    category: 'accessories',
    imageUrl: 'https://images-na.ssl-images-amazon.com/images/P/B08XQWGR2K.01.L.jpg',
    amazonUrl: createAmazonUrl('B08XQWGR2K'),
    price: '¥9,990',
    rating: 4.3,
    reviewCount: 567,
    description: 'オンライン投資セミナーや情報交換で重要な高画質ウェブカメラ。AI機能で常に最適な映像。',
    features: [
      '4K 30fps / 2K 60fps',
      'AI自動フレーミング',
      'ノイズキャンセリング',
      'プライバシーシャッター',
      'プラグアンドプレイ'
    ],
    whyRecommended: '投資コミュニティでの情報交換や、オンライン学習の質を向上させる重要なツールです。',
    useCase: [
      'オンライン投資セミナー参加',
      '投資仲間との情報交換',
      'YouTube配信',
      'ビデオ会議'
    ]
  }
];

// カテゴリー別取得
export const getToolsByCategory = (category: TradingToolCategory): TradingTool[] => {
  return TRADING_TOOLS.filter(tool => tool.category === category);
};

// おすすめセット構成
export interface TradingSetup {
  name: string;
  description: string;
  budget: string;
  level: 'beginner' | 'intermediate' | 'professional';
  tools: string[]; // ASINs
  totalEstimate: string;
  benefits: string[];
}

export const TRADING_SETUPS: TradingSetup[] = [
  {
    name: 'エントリー投資環境',
    description: '投資を始めたばかりの方に最適な基本セット。コストを抑えながら効率的な分析環境を構築。',
    budget: '10万円以下',
    level: 'beginner',
    tools: ['B08XQJB7K1', 'B087QMXPGL', 'B08SHTXPJL'],
    totalEstimate: '¥94,400',
    benefits: [
      '4Kモニターで詳細なチャート分析',
      '理想的な視線角度で疲労軽減',
      '安定した通信環境'
    ]
  },
  {
    name: 'パフォーマンス重視セット',
    description: '本格的な投資分析を行う方向け。処理能力とマルチタスク性能を重視した構成。',
    budget: '30万円程度',
    level: 'intermediate',
    tools: ['B087QZPKLK', 'B08N5WRWNW', 'B08HR7SV3M', 'B08BLPQR4R', 'B000X6XF9U'],
    totalEstimate: '¥300,580',
    benefits: [
      '32インチ大画面で多画面分析',
      '12コアCPUで高速データ処理',
      '32GBメモリで大量データ処理',
      '長時間作業でも快適'
    ]
  },
  {
    name: 'プロフェッショナル環境',
    description: '機関投資家レベルの分析環境。最高のパフォーマンスと信頼性を追求。',
    budget: '50万円以上',
    level: 'professional',
    tools: ['B087QZPKLK', 'B08N5WRWNW', 'B08HR7SV3M', 'B08BLPQR4R', 'B000X6XF9U', 'B07VS8QCXC', 'B08XQWGR2K'],
    totalEstimate: '¥443,170',
    benefits: [
      '機関投資家レベルの分析能力',
      '完全バックアップ体制',
      'オンライン学習・交流対応',
      '長期間の安定稼働'
    ]
  }
];