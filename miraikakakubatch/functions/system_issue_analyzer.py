#!/usr/bin/env python3
"""
システム課題分析・解決システム
"""

import pymysql
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemIssueAnalyzer:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        self.issues = []
        self.solutions = []
    
    def analyze_all_issues(self):
        """全システム課題の分析"""
        connection = pymysql.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                logger.info("🔍 システム課題分析開始")
                
                # 1. データ鮮度の問題
                self.analyze_data_freshness(cursor)
                
                # 2. カバレッジの問題  
                self.analyze_data_coverage(cursor)
                
                # 3. システム稼働状況
                self.analyze_system_health(cursor)
                
                # 4. データ品質の問題
                self.analyze_data_quality(cursor)
                
                # 5. 自動化の問題
                self.analyze_automation_gaps(cursor)
                
                # 課題レポート出力
                self.generate_issue_report()
                
                # 解決策提案
                self.propose_solutions()
                
        except Exception as e:
            logger.error(f"❌ 分析エラー: {e}")
        finally:
            connection.close()
    
    def analyze_data_freshness(self, cursor):
        """データ鮮度分析"""
        logger.info("📊 データ鮮度分析")
        
        try:
            # 価格データの鮮度
            cursor.execute("""
                SELECT COUNT(DISTINCT symbol) FROM stock_price_history 
                WHERE date >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
            """)
            recent_price_symbols = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_price_history")
            total_price_symbols = cursor.fetchone()[0]
            
            freshness_rate = (recent_price_symbols / total_price_symbols) * 100 if total_price_symbols > 0 else 0
            
            if freshness_rate < 30:
                self.issues.append({
                    'severity': 'HIGH',
                    'category': 'データ鮮度',
                    'description': f'価格データが古い: {freshness_rate:.1f}%のみ1日以内',
                    'impact': 'ユーザーに古い情報を表示、投資判断に悪影響'
                })
            
            # ニュースデータの鮮度
            cursor.execute("""
                SELECT COUNT(*) FROM financial_news 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            """)
            recent_news = cursor.fetchone()[0]
            
            if recent_news < 50:
                self.issues.append({
                    'severity': 'MEDIUM',
                    'category': 'データ鮮度', 
                    'description': f'新しいニュースが不足: 1日で{recent_news}件のみ',
                    'impact': '最新情報の提供不足'
                })
                
        except Exception as e:
            logger.warning(f"⚠️ 鮮度分析エラー: {e}")
    
    def analyze_data_coverage(self, cursor):
        """データカバレッジ分析"""
        logger.info("📈 データカバレッジ分析")
        
        try:
            # 価格データカバレッジ
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
            total_stocks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_price_history")
            stocks_with_price = cursor.fetchone()[0]
            
            price_coverage = (stocks_with_price / total_stocks) * 100
            
            if price_coverage < 80:
                self.issues.append({
                    'severity': 'HIGH',
                    'category': 'データカバレッジ',
                    'description': f'価格データカバー率不足: {price_coverage:.1f}%',
                    'impact': '多くの銘柄で価格情報が欠如'
                })
            
            # 予測データカバレッジ
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")
            stocks_with_predictions = cursor.fetchone()[0]
            
            prediction_coverage = (stocks_with_predictions / total_stocks) * 100
            
            if prediction_coverage < 70:
                self.issues.append({
                    'severity': 'MEDIUM',
                    'category': 'データカバレッジ',
                    'description': f'予測データカバー率不足: {prediction_coverage:.1f}%',
                    'impact': '予測機能が限定的'
                })
                
        except Exception as e:
            logger.warning(f"⚠️ カバレッジ分析エラー: {e}")
    
    def analyze_system_health(self, cursor):
        """システム稼働状況分析"""
        logger.info("💊 システム稼働状況分析")
        
        try:
            # バッチ処理の稼働状況（データ更新頻度から推測）
            cursor.execute("""
                SELECT COUNT(*) FROM stock_price_history 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """)
            recent_updates = cursor.fetchone()[0]
            
            if recent_updates < 100:
                self.issues.append({
                    'severity': 'HIGH',
                    'category': 'システム稼働',
                    'description': f'データ更新が停滞: 1時間で{recent_updates}件のみ',
                    'impact': 'リアルタイム性の欠如、システム停止の可能性'
                })
            
            # 予測システムの稼働状況
            cursor.execute("SELECT COUNT(*) FROM stock_predictions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
            recent_predictions = cursor.fetchone()[0]
            
            if recent_predictions < 1000:
                self.issues.append({
                    'severity': 'MEDIUM',
                    'category': 'システム稼働',
                    'description': f'予測生成が低調: 1日で{recent_predictions}件',
                    'impact': '予測機能の品質低下'
                })
                
        except Exception as e:
            logger.warning(f"⚠️ 稼働状況分析エラー: {e}")
    
    def analyze_data_quality(self, cursor):
        """データ品質分析"""
        logger.info("🔍 データ品質分析")
        
        try:
            # NULL値や空データの確認
            cursor.execute("""
                SELECT COUNT(*) FROM stock_master 
                WHERE is_active = 1 AND (name IS NULL OR name = '' OR sector IS NULL)
            """)
            incomplete_stocks = cursor.fetchone()[0]
            
            if incomplete_stocks > 100:
                self.issues.append({
                    'severity': 'MEDIUM',
                    'category': 'データ品質',
                    'description': f'不完全な銘柄データ: {incomplete_stocks}件',
                    'impact': '銘柄情報の表示品質低下'
                })
            
            # 価格データの異常値チェック（0円や極端な値）
            cursor.execute("""
                SELECT COUNT(*) FROM stock_price_history 
                WHERE close_price <= 0 OR close_price > 10000
            """)
            abnormal_prices = cursor.fetchone()[0]
            
            if abnormal_prices > 50:
                self.issues.append({
                    'severity': 'MEDIUM',
                    'category': 'データ品質',
                    'description': f'異常な価格データ: {abnormal_prices}件',
                    'impact': '価格表示・計算の信頼性低下'
                })
                
        except Exception as e:
            logger.warning(f"⚠️ 品質分析エラー: {e}")
    
    def analyze_automation_gaps(self, cursor):
        """自動化のギャップ分析"""
        logger.info("🤖 自動化ギャップ分析")
        
        # 手動での対応が必要な課題を特定
        self.issues.append({
            'severity': 'HIGH',
            'category': '自動化',
            'description': 'リアルタイム価格取得の自動化未実装',
            'impact': '手動更新に依存、スケーラビリティの欠如'
        })
        
        self.issues.append({
            'severity': 'MEDIUM',
            'category': '自動化',
            'description': 'ニュース収集の自動化未実装',
            'impact': '情報の鮮度維持が困難'
        })
        
        self.issues.append({
            'severity': 'MEDIUM', 
            'category': '自動化',
            'description': 'モデル精度監視・再学習の自動化未実装',
            'impact': '予測精度の継続的な改善困難'
        })
    
    def generate_issue_report(self):
        """課題レポート生成"""
        logger.info("📋 課題レポート生成")
        
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        
        print("\n🚨 === 重要課題 (HIGH) ===")
        for i, issue in enumerate(high_issues, 1):
            print(f"{i}. [{issue['category']}] {issue['description']}")
            print(f"   影響: {issue['impact']}")
        
        print("\n⚠️ === 中程度課題 (MEDIUM) ===") 
        for i, issue in enumerate(medium_issues, 1):
            print(f"{i}. [{issue['category']}] {issue['description']}")
            print(f"   影響: {issue['impact']}")
        
        print(f"\n📊 課題サマリー: 重要{len(high_issues)}件、中程度{len(medium_issues)}件")
    
    def propose_solutions(self):
        """解決策提案"""
        logger.info("💡 解決策提案")
        
        solutions = [
            {
                'priority': 1,
                'title': 'リアルタイム価格更新システム構築',
                'description': 'Yahoo Finance APIを使用した自動価格取得バッチの毎時実行',
                'implementation': 'Google Cloud Schedulerで毎時実行のバッチジョブを設定'
            },
            {
                'priority': 2,
                'title': '価格データカバレッジの完全化',
                'description': '残り47%の銘柄の価格データを大量取得・補填',
                'implementation': '並列処理による一括データ取得システム'
            },
            {
                'priority': 3,
                'title': 'ニュース自動収集システム',
                'description': 'RSS/API経由での金融ニュース自動収集',
                'implementation': '複数ソースからのニュース収集バッチ処理'
            },
            {
                'priority': 4,
                'title': 'データ品質監視システム',
                'description': '異常データの自動検出・修正機能',
                'implementation': 'データ検証ルールとアラート機能'
            },
            {
                'priority': 5,
                'title': '予測モデル精度改善',
                'description': '機械学習モデルの継続学習・精度監視',
                'implementation': 'MLOpsパイプラインの構築'
            }
        ]
        
        print("\n💡 === 解決策提案 ===")
        for solution in solutions:
            print(f"{solution['priority']}. {solution['title']}")
            print(f"   概要: {solution['description']}")  
            print(f"   実装: {solution['implementation']}")
            print()
        
        self.solutions = solutions

def main():
    analyzer = SystemIssueAnalyzer()
    analyzer.analyze_all_issues()
    
    logger.info("✅ システム課題分析完了")

if __name__ == "__main__":
    main()