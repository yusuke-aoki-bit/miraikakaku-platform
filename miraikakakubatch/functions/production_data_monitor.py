#!/usr/bin/env python3
"""
本番環境データ監視・検証システム
リアルデータの品質と最新性を継続的に監視
"""

import pymysql
import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDataMonitor:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        
    def get_connection(self):
        return pymysql.connect(**self.db_config)
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """データの最新性チェック"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 最新データの日付確認
                cursor.execute("""
                    SELECT 
                        MAX(DATE(date)) as latest_date,
                        COUNT(DISTINCT symbol) as unique_symbols,
                        COUNT(*) as total_records
                    FROM stock_price_history 
                    WHERE data_source LIKE '%Yahoo Finance Real%' 
                    OR data_source = 'yfinance'
                """)
                
                result = cursor.fetchone()
                latest_date = result[0]
                unique_symbols = result[1] 
                total_records = result[2]
                
                # 今日の日付との比較
                today = datetime.now().date()
                days_behind = (today - latest_date).days if latest_date else 999
                
                return {
                    "latest_date": str(latest_date),
                    "days_behind": days_behind,
                    "unique_symbols": unique_symbols,
                    "total_records": total_records,
                    "is_fresh": days_behind <= 1  # 1日以内なら新鮮
                }
                
        finally:
            connection.close()
    
    def verify_market_coverage(self) -> Dict[str, Any]:
        """市場カバレッジ検証"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 国別・取引所別の銘柄数
                cursor.execute("""
                    SELECT country, exchange, COUNT(DISTINCT symbol) as count
                    FROM stock_master 
                    WHERE is_active = 1
                    GROUP BY country, exchange
                    ORDER BY count DESC
                """)
                
                coverage = cursor.fetchall()
                
                # 主要市場の存在確認
                major_markets = {
                    'US': 0, 'JP': 0, 'UK': 0, 'DE': 0, 'FR': 0, 'CH': 0
                }
                
                for row in coverage:
                    country = row[0]
                    if country in major_markets:
                        major_markets[country] += row[2]
                
                return {
                    "market_coverage": major_markets,
                    "total_markets": len(set([row[0] for row in coverage])),
                    "detailed_coverage": [
                        {"country": row[0], "exchange": row[1], "symbols": row[2]} 
                        for row in coverage
                    ]
                }
                
        finally:
            connection.close()
    
    def validate_price_data_quality(self) -> Dict[str, Any]:
        """価格データ品質検証"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 異常値検出
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        SUM(CASE WHEN close_price <= 0 THEN 1 ELSE 0 END) as zero_prices,
                        SUM(CASE WHEN volume < 0 THEN 1 ELSE 0 END) as negative_volumes,
                        AVG(data_quality_score) as avg_quality_score
                    FROM stock_price_history 
                    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                """)
                
                quality = cursor.fetchone()
                
                # 最近のデータ更新状況
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as update_date,
                        COUNT(*) as updates
                    FROM stock_price_history 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY update_date DESC
                """)
                
                recent_updates = cursor.fetchall()
                
                return {
                    "total_records_30d": quality[0],
                    "zero_prices": quality[1],
                    "negative_volumes": quality[2],
                    "avg_quality_score": float(quality[3]) if quality[3] else 0.0,
                    "data_quality_percentage": max(0, 100 - (quality[1] + quality[2]) / max(1, quality[0]) * 100),
                    "recent_update_activity": [
                        {"date": str(row[0]), "updates": row[1]} 
                        for row in recent_updates
                    ]
                }
                
        finally:
            connection.close()
    
    def generate_production_report(self) -> Dict[str, Any]:
        """本番環境総合レポート生成"""
        logger.info("📊 本番環境データ監視レポート生成中...")
        
        freshness = self.check_data_freshness()
        coverage = self.verify_market_coverage()
        quality = self.validate_price_data_quality()
        
        # 総合スコア計算
        freshness_score = 100 if freshness["is_fresh"] else max(0, 100 - freshness["days_behind"] * 10)
        coverage_score = min(100, coverage["total_markets"] * 15)  # 市場数ベース
        quality_score = quality["data_quality_percentage"]
        
        overall_score = (freshness_score + coverage_score + quality_score) / 3
        
        # ステータス判定
        if overall_score >= 90:
            status = "EXCELLENT"
        elif overall_score >= 75:
            status = "GOOD" 
        elif overall_score >= 60:
            status = "FAIR"
        else:
            status = "NEEDS_IMPROVEMENT"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(overall_score, 1),
            "status": status,
            "data_freshness": freshness,
            "market_coverage": coverage,
            "data_quality": quality,
            "recommendations": self.generate_recommendations(freshness, coverage, quality)
        }
        
        return report
    
    def generate_recommendations(self, freshness, coverage, quality) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        if not freshness["is_fresh"]:
            recommendations.append(f"データが{freshness['days_behind']}日古いです。データ更新頻度を向上させてください。")
        
        if coverage["total_markets"] < 6:
            recommendations.append("主要市場のカバレッジを拡大してください。")
        
        if quality["data_quality_percentage"] < 95:
            recommendations.append("データ品質の向上が必要です。異常値検出を強化してください。")
        
        if quality["zero_prices"] > 0:
            recommendations.append(f"{quality['zero_prices']}件のゼロ価格データがあります。")
        
        if not recommendations:
            recommendations.append("✅ 全てのメトリクスが良好です。現在の品質を維持してください。")
        
        return recommendations
    
    def print_detailed_report(self):
        """詳細レポート出力"""
        report = self.generate_production_report()
        
        print("=" * 70)
        print("📊 MIRAIKAKAKU 本番環境データ監視レポート")
        print("=" * 70)
        print(f"🕒 生成時刻: {report['timestamp']}")
        print(f"📈 総合スコア: {report['overall_score']}/100")
        print(f"🎯 ステータス: {report['status']}")
        print()
        
        print("📅 データ最新性")
        freshness = report['data_freshness']
        print(f"  最新データ日: {freshness['latest_date']}")
        print(f"  遅延日数: {freshness['days_behind']}日")
        print(f"  実銘柄数: {freshness['unique_symbols']}銘柄")
        print(f"  総レコード数: {freshness['total_records']:,}件")
        print()
        
        print("🌍 市場カバレッジ") 
        coverage = report['market_coverage']
        for country, count in coverage['market_coverage'].items():
            if count > 0:
                print(f"  {country}: {count}銘柄")
        print()
        
        print("📊 データ品質")
        quality = report['data_quality']
        print(f"  品質スコア: {quality['data_quality_percentage']:.1f}%")
        print(f"  平均品質評価: {quality['avg_quality_score']:.3f}")
        print(f"  30日間レコード: {quality['total_records_30d']:,}件")
        print()
        
        print("🔍 改善推奨事項")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("=" * 70)

if __name__ == "__main__":
    monitor = ProductionDataMonitor()
    try:
        monitor.print_detailed_report()
    except Exception as e:
        logger.error(f"❌ モニタリングエラー: {e}")
        import traceback
        traceback.print_exc()