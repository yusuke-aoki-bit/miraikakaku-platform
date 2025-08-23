#!/usr/bin/env python3
"""
ターボAIデータジェネレーター
AI決定要因とテーマ洞察を大規模生成
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.cloud_sql_only import db
from sqlalchemy import text
import numpy as np
from datetime import datetime, timedelta
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TurboAIDataGenerator:
    def __init__(self):
        self.stats = {
            'ai_factors_added': 0,
            'theme_insights_added': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # AI決定要因テンプレート（拡張版）
        self.factor_templates = [
            # テクニカル分析
            ("technical", "RSI過売買シグナル", "RSI指標が{value:.1f}で{signal}を示唆", 0.65, 0.85),
            ("technical", "移動平均線クロス", "短期MA({short}日)と長期MA({long}日)の{cross_type}", 0.60, 0.80),
            ("technical", "ボリンジャーバンド", "価格が{band}に接触、{action}の可能性", 0.55, 0.75),
            ("technical", "MACD転換", "MACD線がシグナル線を{direction}抜け", 0.70, 0.85),
            ("technical", "出来高分析", "過去{days}日平均の{ratio:.1f}倍の出来高", 0.50, 0.70),
            ("technical", "サポート/レジスタンス", "{level}円が強力な{type}として機能", 0.60, 0.80),
            ("technical", "トレンドライン", "{trend_type}トレンドラインを{action}", 0.65, 0.82),
            ("technical", "フィボナッチリトレースメント", "{fib_level}%レベルで{reaction}", 0.58, 0.78),
            
            # ファンダメンタル分析
            ("fundamental", "PER評価", "PER {per:.1f}倍は業界平均比{comparison}", 0.70, 0.90),
            ("fundamental", "PBR分析", "PBR {pbr:.1f}倍、{valuation}評価", 0.65, 0.85),
            ("fundamental", "ROE水準", "ROE {roe:.1f}%は{quality}を示唆", 0.75, 0.92),
            ("fundamental", "売上成長率", "前年同期比{growth:.1f}%の{trend}", 0.72, 0.88),
            ("fundamental", "営業利益率", "営業利益率{margin:.1f}%は{efficiency}", 0.68, 0.85),
            ("fundamental", "配当利回り", "配当利回り{yield:.2f}%は{attractiveness}", 0.60, 0.80),
            ("fundamental", "自己資本比率", "自己資本比率{ratio:.1f}%で{stability}", 0.65, 0.82),
            ("fundamental", "キャッシュフロー", "営業CF {cf_type}で{health}を示唆", 0.70, 0.87),
            
            # センチメント分析
            ("sentiment", "市場心理指標", "Fear&Greed指数{value}で{sentiment}", 0.45, 0.65),
            ("sentiment", "投資家動向", "機関投資家の{action}が活発化", 0.55, 0.75),
            ("sentiment", "SNSトレンド", "ソーシャルメディアで{trend}が急増", 0.40, 0.60),
            ("sentiment", "アナリスト評価", "{count}社中{positive}社が買い推奨", 0.60, 0.80),
            ("sentiment", "空売り比率", "空売り比率{ratio:.1f}%は{signal}", 0.50, 0.70),
            
            # パターン認識
            ("pattern", "チャートパターン", "{pattern_name}パターンを形成中", 0.55, 0.75),
            ("pattern", "エリオット波動", "第{wave}波動の{phase}段階", 0.50, 0.70),
            ("pattern", "ハーモニックパターン", "{harmonic}パターンの完成間近", 0.52, 0.72),
            ("pattern", "価格アクション", "{candle_pattern}の出現を確認", 0.58, 0.78),
            
            # ニュース・イベント
            ("news", "業績発表影響", "{quarter}決算が{impact}を与える可能性", 0.65, 0.85),
            ("news", "業界ニュース", "{sector}セクターの{event}が影響", 0.55, 0.75),
            ("news", "マクロ経済", "{indicator}の{change}が株価に影響", 0.60, 0.80),
            ("news", "規制変更", "{regulation}の{action}による影響", 0.50, 0.70)
        ]
        
        # テーマ洞察テンプレート
        self.theme_templates = [
            ("Technology", "tech", ["AI進化", "量子コンピューティング", "5G展開", "サイバーセキュリティ"]),
            ("Healthcare", "health", ["バイオテクノロジー", "遠隔医療", "個別化医療", "医療AI"]),
            ("Energy", "energy", ["再生可能エネルギー", "水素経済", "電池技術", "炭素中立"]),
            ("Finance", "finance", ["デジタル通貨", "DeFi", "ネオバンク", "ESG投資"]),
            ("Consumer", "consumer", ["D2C", "サブスクリプション", "体験経済", "サステナブル消費"]),
            ("Industrial", "industrial", ["自動化", "IoT", "3Dプリンティング", "スマートファクトリー"]),
            ("Materials", "materials", ["新素材", "リサイクル技術", "ナノテクノロジー", "バイオマテリアル"]),
            ("Real Estate", "realestate", ["PropTech", "スマートシティ", "グリーンビルディング", "共有経済"]),
            ("Transportation", "transport", ["EV革命", "自動運転", "空飛ぶ車", "ハイパーループ"]),
            ("Communication", "telecom", ["メタバース", "AR/VR", "衛星通信", "エッジコンピューティング"])
        ]
    
    def generate_ai_factors_batch(self, prediction_ids):
        """AI決定要因をバッチ生成"""
        added = 0
        
        try:
            with db.engine.begin() as conn:
                for pred_id in prediction_ids:
                    # 各予測に対して3-8個の要因を生成
                    num_factors = random.randint(3, 8)
                    selected_templates = random.sample(self.factor_templates, num_factors)
                    
                    for template in selected_templates:
                        factor_type, name_template, desc_template, min_inf, max_inf = template
                        
                        # 動的な値を生成
                        values = self._generate_factor_values(factor_type)
                        
                        # テンプレートに値を適用
                        factor_name = name_template.format(**values) if '{' in name_template else name_template
                        description = desc_template.format(**values)
                        
                        influence_score = np.random.uniform(min_inf, max_inf)
                        confidence = np.random.uniform(0.60, 0.95)
                        
                        try:
                            conn.execute(text('''
                                INSERT IGNORE INTO ai_decision_factors 
                                (prediction_id, factor_type, factor_name, influence_score, 
                                 description, confidence, created_at)
                                VALUES (:pred_id, :type, :name, :inf, :desc, :conf, NOW())
                            '''), {
                                'pred_id': pred_id,
                                'type': factor_type,
                                'name': factor_name[:100],  # カラム長制限
                                'inf': round(influence_score, 2),
                                'desc': description[:500],  # カラム長制限
                                'conf': round(confidence, 2)
                            })
                            added += 1
                        except Exception as e:
                            logger.debug(f"Factor insert error: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Batch AI factors generation error: {e}")
            self.stats['errors'] += 1
        
        self.stats['ai_factors_added'] += added
        return added
    
    def _generate_factor_values(self, factor_type):
        """要因タイプに応じた動的値を生成"""
        values = {}
        
        if factor_type == "technical":
            values['value'] = np.random.uniform(20, 80)
            values['signal'] = random.choice(['買いシグナル', '売りシグナル', '中立'])
            values['short'] = random.choice([5, 10, 20, 25])
            values['long'] = random.choice([50, 75, 100, 200])
            values['cross_type'] = random.choice(['ゴールデンクロス', 'デッドクロス'])
            values['band'] = random.choice(['上部バンド', '下部バンド'])
            values['action'] = random.choice(['反発', '突破', 'ブレイクアウト'])
            values['direction'] = random.choice(['上', '下'])
            values['days'] = random.choice([5, 10, 20, 30])
            values['ratio'] = np.random.uniform(1.5, 3.0)
            values['level'] = round(np.random.uniform(100, 5000), 0)
            values['type'] = random.choice(['サポート', 'レジスタンス'])
            values['trend_type'] = random.choice(['上昇', '下降', '水平'])
            values['fib_level'] = random.choice([23.6, 38.2, 50.0, 61.8])
            values['reaction'] = random.choice(['反発の可能性', '突破の兆候'])
            
        elif factor_type == "fundamental":
            values['per'] = np.random.uniform(5, 50)
            values['pbr'] = np.random.uniform(0.5, 5.0)
            values['roe'] = np.random.uniform(5, 30)
            values['growth'] = np.random.uniform(-20, 50)
            values['margin'] = np.random.uniform(5, 25)
            values['yield'] = np.random.uniform(0.5, 5.0)
            values['ratio'] = np.random.uniform(30, 80)
            values['comparison'] = random.choice(['割安', '割高', '適正水準'])
            values['valuation'] = random.choice(['割安', '適正', '割高'])
            values['quality'] = random.choice(['高収益性', '安定成長', '改善傾向'])
            values['trend'] = random.choice(['成長加速', '安定成長', '減速傾向'])
            values['efficiency'] = random.choice(['高効率経営', '業界平均', '改善余地あり'])
            values['attractiveness'] = random.choice(['高配当銘柄', '安定配当', '成長重視'])
            values['stability'] = random.choice(['財務健全', '安定的', '改善中'])
            values['cf_type'] = random.choice(['プラス', 'マイナス'])
            values['health'] = random.choice(['健全な資金繰り', '注意が必要', '改善傾向'])
            
        elif factor_type == "sentiment":
            values['value'] = random.randint(10, 90)
            values['sentiment'] = random.choice(['極度の恐怖', '恐怖', '中立', '楽観', '極度の楽観'])
            values['action'] = random.choice(['買い', '売り', '保有'])
            values['trend'] = random.choice(['ポジティブ言及', 'ネガティブ言及', '注目度'])
            values['count'] = random.randint(5, 20)
            values['positive'] = random.randint(3, 15)
            values['ratio'] = np.random.uniform(10, 40)
            values['signal'] = random.choice(['買い戻し圧力', '売り圧力継続', '転換点'])
            
        elif factor_type == "pattern":
            values['pattern_name'] = random.choice(['三角保ち合い', 'ダブルトップ', 'ダブルボトム', 
                                                   'ヘッドアンドショルダー', 'カップアンドハンドル'])
            values['wave'] = random.randint(1, 5)
            values['phase'] = random.choice(['初期', '中期', '終期'])
            values['harmonic'] = random.choice(['バット', 'ガートレー', 'バタフライ', 'クラブ'])
            values['candle_pattern'] = random.choice(['ハンマー', '包み線', '明けの明星', '三兵'])
            
        elif factor_type == "news":
            values['quarter'] = random.choice(['Q1', 'Q2', 'Q3', 'Q4', '通期'])
            values['impact'] = random.choice(['ポジティブ', 'ネガティブ', '中立的'])
            values['sector'] = random.choice(['テクノロジー', 'ヘルスケア', 'エネルギー', '金融'])
            values['event'] = random.choice(['規制緩和', '新技術導入', '業界再編', '需要増加'])
            values['indicator'] = random.choice(['GDP', 'CPI', '雇用統計', '金利'])
            values['change'] = random.choice(['上昇', '低下', '予想上回る', '予想下回る'])
            values['regulation'] = random.choice(['環境規制', 'データ保護', '金融規制', '独占禁止'])
            
        return values
    
    def generate_theme_insights_batch(self):
        """テーマ洞察をバッチ生成"""
        added = 0
        
        try:
            with db.engine.begin() as conn:
                for theme_name, category, subtopics in self.theme_templates:
                    # 各テーマに対して複数の洞察を生成
                    for i in range(random.randint(5, 10)):
                        subtopic = random.choice(subtopics)
                        
                        # 洞察日を過去30日間でランダムに設定
                        insight_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
                        
                        # 影響度スコアを生成
                        impact_score = np.random.uniform(60, 95)
                        
                        # キードライバーを生成
                        drivers = self._generate_key_drivers(category, subtopic)
                        
                        # 影響銘柄を生成
                        affected_stocks = self._generate_affected_stocks()
                        
                        # 予測精度を生成
                        prediction_accuracy = np.random.uniform(0.65, 0.92)
                        
                        try:
                            conn.execute(text('''
                                INSERT IGNORE INTO theme_insights 
                                (theme_name, theme_category, insight_date, key_drivers, 
                                 affected_stocks, impact_score, prediction_accuracy, created_at)
                                VALUES (:name, :cat, :date, :drivers, :stocks, :impact, :acc, NOW())
                            '''), {
                                'name': f"{theme_name}: {subtopic}",
                                'cat': category,
                                'date': insight_date,
                                'drivers': drivers,
                                'stocks': affected_stocks,
                                'impact': round(impact_score, 1),
                                'acc': round(prediction_accuracy, 3)
                            })
                            added += 1
                        except Exception as e:
                            logger.debug(f"Theme insight insert error: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Batch theme insights generation error: {e}")
            self.stats['errors'] += 1
        
        self.stats['theme_insights_added'] += added
        return added
    
    def _generate_key_drivers(self, category, subtopic):
        """キードライバーを生成"""
        drivers_templates = {
            "tech": [
                f"{subtopic}の技術革新が加速",
                f"大手企業による{subtopic}投資拡大",
                f"{subtopic}市場規模が前年比30%成長",
                f"規制緩和により{subtopic}普及が加速"
            ],
            "health": [
                f"{subtopic}の臨床試験で有望な結果",
                f"FDA承認により{subtopic}市場が拡大",
                f"{subtopic}への研究開発投資が増加",
                f"高齢化により{subtopic}需要が急増"
            ],
            "energy": [
                f"{subtopic}のコスト効率が大幅改善",
                f"政府による{subtopic}支援策を発表",
                f"{subtopic}技術のブレークスルー",
                f"ESG投資により{subtopic}への資金流入"
            ],
            "finance": [
                f"{subtopic}の規制フレームワーク確立",
                f"若年層の{subtopic}利用が急増",
                f"{subtopic}のセキュリティ技術が向上",
                f"大手金融機関が{subtopic}参入"
            ]
        }
        
        base_drivers = drivers_templates.get(category, [f"{subtopic}の市場動向が活発化"])
        selected = random.sample(base_drivers, min(3, len(base_drivers)))
        return ", ".join(selected)
    
    def _generate_affected_stocks(self):
        """影響を受ける銘柄を生成"""
        # 実際の銘柄シンボルをランダムに選択
        us_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'JNJ']
        jp_stocks = ['7203', '9984', '6758', '6861', '6902', '8306', '9432', '6501', '4063', '7267']
        
        selected_stocks = random.sample(us_stocks + jp_stocks, random.randint(3, 8))
        return ", ".join(selected_stocks)
    
    def run_turbo_generation(self):
        """ターボ生成を実行"""
        logger.info("🚀 ターボAIデータ生成開始")
        logger.info("=" * 80)
        
        with db.engine.connect() as conn:
            # 既存の予測IDを取得（AI決定要因と紐付け）
            result = conn.execute(text('''
                SELECT sp.id 
                FROM stock_predictions sp
                LEFT JOIN ai_decision_factors adf ON sp.id = adf.prediction_id
                WHERE adf.id IS NULL
                ORDER BY sp.created_at DESC
                LIMIT 10000
            ''')).fetchall()
            
            prediction_ids = [row[0] for row in result]
            logger.info(f"📊 AI決定要因生成対象: {len(prediction_ids):,}個の予測")
        
        # 並列処理で高速化
        max_workers = 8
        batch_size = 100
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # AI決定要因生成
            futures = []
            for i in range(0, len(prediction_ids), batch_size):
                batch = prediction_ids[i:i+batch_size]
                future = executor.submit(self.generate_ai_factors_batch, batch)
                futures.append(future)
            
            # テーマ洞察生成（並列で100バッチ実行）
            for _ in range(100):
                future = executor.submit(self.generate_theme_insights_batch)
                futures.append(future)
            
            # 完了を待機
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    completed += 1
                    
                    if completed % 10 == 0:
                        elapsed = time.time() - self.stats['start_time']
                        logger.info(f"進捗: {completed}/{len(futures)} バッチ完了 - "
                                  f"AI要因: {self.stats['ai_factors_added']:,}, "
                                  f"テーマ: {self.stats['theme_insights_added']:,}")
                except Exception as e:
                    logger.error(f"バッチ処理エラー: {e}")
                    self.stats['errors'] += 1
        
        # 最終結果
        duration = time.time() - self.stats['start_time']
        logger.info("=" * 80)
        logger.info("🎯 ターボAIデータ生成完了")
        logger.info(f"⏱️  実行時間: {duration:.2f}秒")
        logger.info(f"🧠 AI決定要因追加: {self.stats['ai_factors_added']:,}件")
        logger.info(f"🎯 テーマ洞察追加: {self.stats['theme_insights_added']:,}件")
        logger.info(f"❌ エラー: {self.stats['errors']:,}件")
        logger.info(f"🚀 処理速度: {(self.stats['ai_factors_added'] + self.stats['theme_insights_added'])/duration:.1f}件/秒")
        logger.info("=" * 80)
        
        return self.stats

if __name__ == "__main__":
    generator = TurboAIDataGenerator()
    generator.run_turbo_generation()