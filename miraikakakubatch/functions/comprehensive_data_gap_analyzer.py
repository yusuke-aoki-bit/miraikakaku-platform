#!/usr/bin/env python3
"""
包括的データギャップ分析システム
全テーブルの補填すべきデータを特定
"""

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDataAnalyzer:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }
    
    def analyze_all_gaps(self):
        """全データテーブルのギャップを分析"""
        connection = psycopg2.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                print("🔍 === 包括的データギャップ分析 ===\n")
                
                # 1. ニュースデータ分析
                self.analyze_financial_news(cursor)
                
                # 2. 銘柄マスタ詳細情報分析
                self.analyze_stock_master_details(cursor)
                
                # 3. 価格データの時系列ギャップ分析
                self.analyze_price_data_gaps(cursor)
                
                # 4. モデル性能データ分析
                self.analyze_model_performance(cursor)
                
                # 5. アセット関連データ分析
                self.analyze_asset_data(cursor)
                
                # 6. 予測履歴データ分析
                self.analyze_prediction_history(cursor)
                
                print("\n🎯 === 補填優先度ランキング ===")
                self.print_priority_recommendations()
                
        except Exception as e:
            logger.error(f"❌ 分析エラー: {e}")
        finally:
            connection.close()
    
    def analyze_financial_news(self, cursor):
        """ニュースデータ分析"""
        print("📰 【ニュースデータ分析】")
        
        try:
            # ニュース総数
            cursor.execute("SELECT COUNT(*) FROM financial_news")
            total_news = cursor.fetchone()[0]
            
            # 直近のニュース
            cursor.execute("""
                SELECT COUNT(*) FROM financial_news 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            recent_news = cursor.fetchone()[0]
            
            # ニュースがある銘柄数 (symbolカラム存在確認)
            try:
                cursor.execute("SELECT COUNT(DISTINCT symbol) FROM financial_news WHERE symbol IS NOT NULL")
                symbols_with_news = cursor.fetchone()[0]
            except:
                symbols_with_news = "不明（symbolカラムなし）"
            
            print(f"  総ニュース: {total_news:,}件")
            print(f"  直近7日: {recent_news:,}件")
            print(f"  対象銘柄: {symbols_with_news}")
            
            if total_news < 1000:
                print("  ⚠️  ニュースデータが不足 - 日次収集が必要")
                
        except Exception as e:
            print(f"  ❌ ニュース分析エラー: {e}")
    
    def analyze_stock_master_details(self, cursor):
        """銘柄マスタの詳細情報分析"""
        print("\n🏢 【銘柄マスタ詳細情報】")
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN website IS NOT NULL AND website != '' THEN 1 END) as with_website,
                    COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as with_description,
                    COUNT(CASE WHEN country IS NOT NULL AND country != '' THEN 1 END) as with_country,
                    COUNT(CASE WHEN currency IS NOT NULL AND currency != '' THEN 1 END) as with_currency
                FROM stock_master 
                WHERE is_active = 1
            """)
            
            data = cursor.fetchone()
            total, website, desc, country, currency = data
            
            website_rate = (website / total) * 100
            desc_rate = (desc / total) * 100
            country_rate = (country / total) * 100
            currency_rate = (currency / total) * 100
            
            print(f"  ウェブサイト補填率: {website_rate:.1f}% ({website:,}/{total:,})")
            print(f"  説明文補填率: {desc_rate:.1f}% ({desc:,}/{total:,})")
            print(f"  国情報補填率: {country_rate:.1f}% ({country:,}/{total:,})")
            print(f"  通貨情報補填率: {currency_rate:.1f}% ({currency:,}/{total:,})")
            
            # 補填の必要性評価
            if website_rate < 50:
                print("  🔴 ウェブサイト情報の大規模補填が必要")
            if desc_rate < 50:
                print("  🔴 説明文の大規模補填が必要")
            if country_rate < 90:
                print("  🟡 国情報の補填推奨")
                
        except Exception as e:
            print(f"  ❌ マスタ分析エラー: {e}")
    
    def analyze_price_data_gaps(self, cursor):
        """価格データのギャップ分析"""
        print("\n💹 【価格データ時系列ギャップ】")
        
        try:
            # 価格データがない銘柄
            cursor.execute("""
                SELECT COUNT(DISTINCT sm.symbol)
                FROM stock_master sm
                LEFT JOIN stock_price_history ph ON sm.symbol = ph.symbol
                WHERE sm.is_active = 1 AND ph.symbol IS NULL
            """)
            no_price_data = cursor.fetchone()[0]
            
            # 古いデータしかない銘柄
            cursor.execute("""
                SELECT COUNT(DISTINCT sm.symbol)
                FROM stock_master sm
                JOIN stock_price_history ph ON sm.symbol = ph.symbol
                WHERE sm.is_active = 1 
                AND ph.date < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                AND sm.symbol NOT IN (
                    SELECT DISTINCT symbol FROM stock_price_history 
                    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                )
            """)
            old_data_only = cursor.fetchone()[0]
            
            print(f"  価格データなし: {no_price_data:,}銘柄")
            print(f"  30日以上古いデータのみ: {old_data_only:,}銘柄")
            
            total_gap = no_price_data + old_data_only
            if total_gap > 1000:
                print("  🔴 大量の価格データギャップあり - 集中補填必要")
            elif total_gap > 100:
                print("  🟡 中程度の価格データギャップあり")
                
        except Exception as e:
            print(f"  ❌ 価格データ分析エラー: {e}")
    
    def analyze_model_performance(self, cursor):
        """モデル性能データ分析"""
        print("\n🤖 【モデル性能データ】")
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT model_type) as model_types,
                    AVG(accuracy) as avg_accuracy,
                    MIN(updated_at) as oldest_update,
                    MAX(updated_at) as latest_update
                FROM model_performance 
                WHERE is_active = 1
            """)
            
            data = cursor.fetchone()
            total, types, accuracy, oldest, latest = data
            
            print(f"  性能記録: {total:,}件")
            print(f"  モデル種類: {types:,}種類")
            print(f"  平均精度: {accuracy:.1%}" if accuracy else "  平均精度: データなし")
            print(f"  最新更新: {latest}")
            
            if total < 20:
                print("  🟡 モデル性能データが少ない - 定期評価が必要")
                
        except Exception as e:
            print(f"  ❌ モデル性能分析エラー: {e}")
    
    def analyze_asset_data(self, cursor):
        """アセット関連データ分析"""
        print("\n🏦 【アセット・資産データ】")
        
        try:
            # assets テーブル
            cursor.execute("SELECT COUNT(*) FROM assets")
            assets_count = cursor.fetchone()[0]
            
            # asset_details
            cursor.execute("SELECT COUNT(*) FROM asset_details")
            details_count = cursor.fetchone()[0]
            
            # asset_statistics  
            cursor.execute("SELECT COUNT(*) FROM asset_statistics")
            stats_count = cursor.fetchone()[0]
            
            print(f"  総アセット: {assets_count:,}件")
            print(f"  詳細情報: {details_count:,}件")
            print(f"  統計データ: {stats_count:,}件")
            
            if assets_count == 0:
                print("  🔴 アセットデータが空 - 初期データ投入が必要")
            elif details_count < assets_count * 0.8:
                print("  🟡 アセット詳細情報の補填推奨")
                
        except Exception as e:
            print(f"  ❌ アセット分析エラー: {e}")
    
    def analyze_prediction_history(self, cursor):
        """予測履歴データ分析"""
        print("\n📊 【予測履歴・精度データ】")
        
        try:
            cursor.execute("SELECT COUNT(*) FROM prediction_history")
            history_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM prediction_history 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            recent_history = cursor.fetchone()[0]
            
            print(f"  予測履歴: {history_count:,}件")
            print(f"  直近30日: {recent_history:,}件")
            
            if recent_history == 0 and history_count > 0:
                print("  🟡 予測履歴の更新が停止している可能性")
            elif history_count < 1000:
                print("  🟡 予測履歴データの蓄積推奨")
                
        except Exception as e:
            print(f"  ❌ 予測履歴分析エラー: {e}")
    
    def print_priority_recommendations(self):
        """補填優先度の推奨"""
        priorities = [
            "🔴 高優先度",
            "1. ニュースデータの日次自動収集",
            "2. 銘柄マスタの企業情報補填（ウェブサイト、説明文）",
            "3. 価格データギャップの埋め合わせ",
            "",
            "🟡 中優先度", 
            "4. アセットデータの初期投入",
            "5. 国・通貨情報の補填",
            "6. 予測履歴データの継続蓄積",
            "",
            "🟢 低優先度",
            "7. モデル性能データの定期更新",
            "8. アセット統計データの拡充"
        ]
        
        for priority in priorities:
            print(priority)

def main():
    analyzer = ComprehensiveDataAnalyzer()
    analyzer.analyze_all_gaps()

if __name__ == "__main__":
    main()