#!/usr/bin/env python3
"""
新機能用サンプルデータ生成バッチ
差別化機能のためのデモデータを生成します
"""

import sys
import os
import asyncio
import random
import logging
import traceback
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# パスを追加してモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.cloud_sql_only import get_cloud_sql_connection
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
except ImportError as e:
    logger.error(f"インポートエラー: {e}")
    sys.exit(1)

async def create_enhanced_tables():
    """新機能用テーブルを作成"""
    conn = await get_cloud_sql_connection()
    
    try:
        # テーブル作成SQL
        tables_sql = [
            # ユーザープロファイル
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) UNIQUE NOT NULL,
                username VARCHAR(50),
                email VARCHAR(100),
                investment_style ENUM('conservative', 'moderate', 'aggressive', 'growth', 'value') DEFAULT 'moderate',
                risk_tolerance ENUM('low', 'medium', 'high') DEFAULT 'medium',
                investment_experience ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
                preferred_sectors JSON,
                investment_goals TEXT,
                total_portfolio_value DECIMAL(15,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_investment_style (investment_style)
            );
            """,
            # AI判断根拠テーブル
            """
            CREATE TABLE IF NOT EXISTS ai_decision_factors (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                prediction_id BIGINT NOT NULL,
                factor_type ENUM('technical', 'fundamental', 'sentiment', 'news', 'pattern') NOT NULL,
                factor_name VARCHAR(100) NOT NULL,
                influence_score DECIMAL(5,2) NOT NULL,
                description TEXT,
                confidence DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_prediction_id (prediction_id),
                INDEX idx_factor_type (factor_type)
            );
            """,
            # コンテストテーブル
            """
            CREATE TABLE IF NOT EXISTS prediction_contests (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                contest_name VARCHAR(100) NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                contest_start_date DATE NOT NULL,
                prediction_deadline DATETIME NOT NULL,
                target_date DATE NOT NULL,
                actual_price DECIMAL(12,4),
                status ENUM('active', 'closed', 'completed') DEFAULT 'active',
                prize_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_contest_status (status),
                INDEX idx_target_date (target_date)
            );
            """,
            # テーマインサイトテーブル
            """
            CREATE TABLE IF NOT EXISTS theme_insights (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                theme_name VARCHAR(50) NOT NULL,
                theme_category ENUM('technology', 'energy', 'finance', 'healthcare', 'consumer', 'industrial', 'materials') NOT NULL,
                insight_date DATE NOT NULL,
                title VARCHAR(200) NOT NULL,
                summary TEXT NOT NULL,
                key_metrics JSON,
                related_symbols JSON,
                trend_direction ENUM('bullish', 'bearish', 'neutral') DEFAULT 'neutral',
                impact_score DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_theme_date (theme_name, insight_date),
                INDEX idx_category (theme_category),
                INDEX idx_trend (trend_direction)
            );
            """,
            # ウォッチリストテーブル
            """
            CREATE TABLE IF NOT EXISTS user_watchlists (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_threshold_up DECIMAL(5,2),
                alert_threshold_down DECIMAL(5,2),
                notes TEXT,
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium',
                UNIQUE KEY unique_user_symbol (user_id, symbol),
                INDEX idx_user_id (user_id)
            );
            """
        ]
        
        for sql in tables_sql:
            await conn.execute(text(sql))
            await conn.commit()
        
        logger.info("✅ Enhanced tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False
    finally:
        await conn.close()

async def generate_user_profiles():
    """ユーザープロファイルサンプルデータ生成"""
    conn = await get_cloud_sql_connection()
    
    try:
        sample_users = [
            {
                "user_id": "demo_conservative_001",
                "username": "SafeInvestor",
                "email": "safe@example.com",
                "investment_style": "conservative",
                "risk_tolerance": "low",
                "investment_experience": "beginner",
                "preferred_sectors": '["finance", "consumer"]',
                "investment_goals": "長期的な資産保全と安定したリターンを目指します",
                "total_portfolio_value": 500000.0
            },
            {
                "user_id": "demo_aggressive_002", 
                "username": "TechGrowth",
                "email": "growth@example.com",
                "investment_style": "growth",
                "risk_tolerance": "high",
                "investment_experience": "advanced",
                "preferred_sectors": '["technology", "healthcare"]',
                "investment_goals": "技術株を中心とした積極的な成長投資",
                "total_portfolio_value": 1200000.0
            },
            {
                "user_id": "demo_balanced_003",
                "username": "BalancedTrader", 
                "email": "balanced@example.com",
                "investment_style": "moderate",
                "risk_tolerance": "medium",
                "investment_experience": "intermediate",
                "preferred_sectors": '["technology", "finance", "energy"]',
                "investment_goals": "リスクとリターンのバランスを取った分散投資",
                "total_portfolio_value": 800000.0
            }
        ]
        
        created_count = 0
        for user_data in sample_users:
            try:
                # 既存ユーザーチェック
                result = await conn.execute(text(
                    "SELECT id FROM user_profiles WHERE user_id = :user_id"
                ), {"user_id": user_data["user_id"]})
                
                if result.fetchone():
                    logger.info(f"User {user_data['user_id']} already exists")
                    continue
                
                # ユーザー作成
                await conn.execute(text("""
                    INSERT INTO user_profiles 
                    (user_id, username, email, investment_style, risk_tolerance, 
                     investment_experience, preferred_sectors, investment_goals, total_portfolio_value)
                    VALUES (:user_id, :username, :email, :investment_style, :risk_tolerance,
                            :investment_experience, :preferred_sectors, :investment_goals, :total_portfolio_value)
                """), user_data)
                
                created_count += 1
                logger.info(f"Created user profile: {user_data['username']}")
                
            except IntegrityError:
                logger.info(f"User {user_data['user_id']} already exists (skipping)")
                continue
        
        await conn.commit()
        logger.info(f"✅ Created {created_count} user profiles")
        return created_count
        
    except Exception as e:
        logger.error(f"❌ Error creating user profiles: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        await conn.close()

async def generate_ai_decision_factors():
    """AI判断根拠サンプルデータ生成"""
    conn = await get_cloud_sql_connection()
    
    try:
        # 最新の予測データを取得（最大50件）
        result = await conn.execute(text("""
            SELECT id, symbol FROM stock_predictions 
            ORDER BY created_at DESC 
            LIMIT 50
        """))
        predictions = result.fetchall()
        
        if not predictions:
            logger.warning("No predictions found for decision factors")
            return 0
        
        factor_templates = [
            {
                "factor_type": "technical",
                "factor_name": "RSI反発シグナル",
                "description": "RSI指標が30を下回った後、反発上昇を示している",
                "base_influence": 0.85,
                "base_confidence": 0.78
            },
            {
                "factor_type": "fundamental", 
                "factor_name": "業績予想上方修正",
                "description": "次四半期のEPS予想が15%上方修正された",
                "base_influence": 0.92,
                "base_confidence": 0.88
            },
            {
                "factor_type": "sentiment",
                "factor_name": "投資家心理改善",
                "description": "アナリストの強気コメントが増加、機関投資家の買い増し観測",
                "base_influence": 0.73,
                "base_confidence": 0.65
            },
            {
                "factor_type": "news",
                "factor_name": "新製品発表影響",
                "description": "革新的な新製品の発表により市場期待が高まっている",
                "base_influence": 0.89,
                "base_confidence": 0.82
            },
            {
                "factor_type": "pattern",
                "factor_name": "上昇三角形パターン",
                "description": "チャート上で上昇三角形パターンを形成、ブレイクアウト間近",
                "base_influence": 0.76,
                "base_confidence": 0.71
            }
        ]
        
        created_count = 0
        for prediction in predictions:
            # 各予測に2-4個の判断根拠を生成
            num_factors = random.randint(2, 4)
            selected_factors = random.sample(factor_templates, num_factors)
            
            for factor_template in selected_factors:
                # スコアにランダム性を追加
                influence_score = factor_template["base_influence"] + random.uniform(-0.1, 0.1)
                confidence = factor_template["base_confidence"] + random.uniform(-0.1, 0.1)
                
                await conn.execute(text("""
                    INSERT INTO ai_decision_factors 
                    (prediction_id, factor_type, factor_name, description, influence_score, confidence)
                    VALUES (:prediction_id, :factor_type, :factor_name, :description, :influence_score, :confidence)
                """), {
                    "prediction_id": prediction.id,
                    "factor_type": factor_template["factor_type"],
                    "factor_name": factor_template["factor_name"],
                    "description": factor_template["description"],
                    "influence_score": max(0.1, min(1.0, influence_score)),
                    "confidence": max(0.1, min(1.0, confidence))
                })
                created_count += 1
        
        await conn.commit()
        logger.info(f"✅ Created {created_count} AI decision factors")
        return created_count
        
    except Exception as e:
        logger.error(f"❌ Error creating AI decision factors: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        await conn.close()

async def generate_prediction_contests():
    """予測コンテストサンプルデータ生成"""
    conn = await get_cloud_sql_connection()
    
    try:
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META"]
        
        created_count = 0
        for i, symbol in enumerate(popular_symbols[:3]):
            contest_date = date.today() + timedelta(days=i*7)
            
            # 既存コンテストチェック
            result = await conn.execute(text("""
                SELECT id FROM prediction_contests 
                WHERE symbol = :symbol AND contest_start_date = :contest_start_date
            """), {"symbol": symbol, "contest_start_date": contest_date})
            
            if result.fetchone():
                logger.info(f"Contest for {symbol} on {contest_date} already exists")
                continue
            
            await conn.execute(text("""
                INSERT INTO prediction_contests 
                (contest_name, symbol, contest_start_date, prediction_deadline, target_date, status, prize_description)
                VALUES (:contest_name, :symbol, :contest_start_date, :prediction_deadline, :target_date, :status, :prize_description)
            """), {
                "contest_name": f"Weekly {symbol} Price Challenge",
                "symbol": symbol,
                "contest_start_date": contest_date,
                "prediction_deadline": datetime.combine(contest_date + timedelta(days=5), datetime.min.time().replace(hour=23, minute=59)),
                "target_date": contest_date + timedelta(days=7),
                "status": "active",
                "prize_description": "Top 3 winners get digital badges and recognition"
            })
            created_count += 1
            logger.info(f"Created contest: Weekly {symbol} Challenge")
        
        await conn.commit()
        logger.info(f"✅ Created {created_count} prediction contests")
        return created_count
        
    except Exception as e:
        logger.error(f"❌ Error creating prediction contests: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        await conn.close()

async def generate_theme_insights():
    """テーマインサイトサンプルデータ生成"""
    conn = await get_cloud_sql_connection()
    
    try:
        insights_data = [
            {
                "theme_name": "AI Revolution",
                "theme_category": "technology", 
                "title": "AI企業の第3四半期決算分析：成長継続の鍵",
                "summary": "生成AIブームが続く中、主要AI企業の決算発表が相次いでいます。NVIDIA、Microsoft、Googleなどの業績から見える今後のトレンドと投資機会を分析します。",
                "key_metrics": '{"sector_growth": "35.2%", "market_cap_increase": "$2.1T", "pe_ratio_average": 45.3}',
                "related_symbols": '["NVDA", "MSFT", "GOOGL", "AMZN"]',
                "trend_direction": "bullish",
                "impact_score": 9.2
            },
            {
                "theme_name": "Green Energy Transition",
                "theme_category": "energy",
                "title": "再生エネルギー政策と関連株への影響",
                "summary": "各国の脱炭素政策強化により、太陽光、風力発電関連企業に注目が集まっています。政策動向と業界の成長見通しを詳しく解説します。", 
                "key_metrics": '{"policy_support": "89%", "capacity_growth": "28.5%", "cost_reduction": "15.2%"}',
                "related_symbols": '["NEE", "ENPH", "SEDG", "FSLR"]',
                "trend_direction": "bullish",
                "impact_score": 8.7
            },
            {
                "theme_name": "Healthcare Innovation",
                "theme_category": "healthcare",
                "title": "バイオテック新薬承認ラッシュの投資チャンス",
                "summary": "2024年は新薬承認が活発化しており、特にがん治療薬や希少疾患治療薬の分野で画期的な承認が相次いでいます。関連企業の業績向上が期待されます。",
                "key_metrics": '{"new_approvals": 47, "market_size": "$850B", "r_and_d_increase": "12.3%"}',
                "related_symbols": '["JNJ", "PFE", "MRNA", "GILD"]',
                "trend_direction": "neutral", 
                "impact_score": 7.9
            }
        ]
        
        created_count = 0
        for insight_data in insights_data:
            insight_data["insight_date"] = date.today() - timedelta(days=random.randint(0, 30))
            
            # 既存インサイトチェック
            result = await conn.execute(text("""
                SELECT id FROM theme_insights 
                WHERE theme_name = :theme_name AND insight_date = :insight_date
            """), {
                "theme_name": insight_data["theme_name"],
                "insight_date": insight_data["insight_date"]
            })
            
            if result.fetchone():
                logger.info(f"Insight for {insight_data['theme_name']} already exists")
                continue
            
            await conn.execute(text("""
                INSERT INTO theme_insights 
                (theme_name, theme_category, insight_date, title, summary, key_metrics, related_symbols, trend_direction, impact_score)
                VALUES (:theme_name, :theme_category, :insight_date, :title, :summary, :key_metrics, :related_symbols, :trend_direction, :impact_score)
            """), insight_data)
            created_count += 1
            logger.info(f"Created insight: {insight_data['title']}")
        
        await conn.commit()
        logger.info(f"✅ Created {created_count} theme insights")
        return created_count
        
    except Exception as e:
        logger.error(f"❌ Error creating theme insights: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        await conn.close()

async def generate_user_watchlists():
    """ユーザーウォッチリストサンプルデータ生成"""
    conn = await get_cloud_sql_connection()
    
    try:
        # ユーザー取得
        result = await conn.execute(text("SELECT user_id FROM user_profiles"))
        users = result.fetchall()
        
        if not users:
            logger.warning("No users found for watchlists")
            return 0
        
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "JPM", "V", "JNJ"]
        
        created_count = 0
        for user in users:
            # ウォッチリスト生成 (3-6銘柄)
            watchlist_symbols = random.sample(popular_symbols, random.randint(3, 6))
            
            for symbol in watchlist_symbols:
                try:
                    await conn.execute(text("""
                        INSERT INTO user_watchlists 
                        (user_id, symbol, alert_threshold_up, alert_threshold_down, notes, priority)
                        VALUES (:user_id, :symbol, :alert_threshold_up, :alert_threshold_down, :notes, :priority)
                    """), {
                        "user_id": user.user_id,
                        "symbol": symbol,
                        "alert_threshold_up": random.uniform(5, 15),
                        "alert_threshold_down": random.uniform(-15, -5),
                        "notes": f"{symbol}の長期投資候補として監視中",
                        "priority": random.choice(["high", "medium", "low"])
                    })
                    created_count += 1
                except IntegrityError:
                    # 重複の場合はスキップ
                    continue
        
        await conn.commit()
        logger.info(f"✅ Created {created_count} watchlist items")
        return created_count
        
    except Exception as e:
        logger.error(f"❌ Error creating watchlists: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        await conn.close()

async def main():
    """メイン実行関数"""
    logger.info("🚀 Enhanced Data Generator Starting...")
    logger.info("=" * 60)
    
    try:
        # 1. テーブル作成
        logger.info("1. Creating enhanced tables...")
        await create_enhanced_tables()
        
        # 2. ユーザープロファイル生成
        logger.info("\n2. Generating user profiles...")
        user_count = await generate_user_profiles()
        
        # 3. AI判断根拠生成
        logger.info("\n3. Generating AI decision factors...")
        factor_count = await generate_ai_decision_factors()
        
        # 4. 予測コンテスト生成
        logger.info("\n4. Generating prediction contests...")
        contest_count = await generate_prediction_contests()
        
        # 5. テーマインサイト生成
        logger.info("\n5. Generating theme insights...")
        insight_count = await generate_theme_insights()
        
        # 6. ウォッチリスト生成
        logger.info("\n6. Generating user watchlists...")
        watchlist_count = await generate_user_watchlists()
        
        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("✅ Enhanced data generation completed!")
        logger.info(f"📊 Generated:")
        logger.info(f"   - User profiles: {user_count}")
        logger.info(f"   - AI decision factors: {factor_count}")
        logger.info(f"   - Prediction contests: {contest_count}")
        logger.info(f"   - Theme insights: {insight_count}")
        logger.info(f"   - Watchlist items: {watchlist_count}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error during enhanced data generation: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())