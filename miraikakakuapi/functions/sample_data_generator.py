#!/usr/bin/env python3
"""
サンプルデータ生成スクリプト - 差別化機能のためのデモデータ
"""
import sys
import os
import random
from datetime import datetime, timedelta, date
from typing import List, Dict

# パスを追加してモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from database.models import (
    UserProfiles, UserWatchlists, UserPortfolios,
    AiDecisionFactors, PredictionContests, UserContestPredictions, ThemeInsights,
    StockPredictions
)

def generate_user_profiles():
    """ユーザープロファイルのサンプルデータを生成"""
    db = SessionLocal()
    try:
        sample_users = [
            {
                "user_id": "demo_conservative_001",
                "username": "SafeInvestor",
                "email": "safe@example.com",
                "investment_style": "conservative",
                "risk_tolerance": "low",
                "investment_experience": "beginner",
                "preferred_sectors": ["finance", "consumer"],
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
                "preferred_sectors": ["technology", "healthcare"],
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
                "preferred_sectors": ["technology", "finance", "energy"],
                "investment_goals": "リスクとリターンのバランスを取った分散投資",
                "total_portfolio_value": 800000.0
            }
        ]
        
        for user_data in sample_users:
            existing_user = db.query(UserProfiles).filter(
                UserProfiles.user_id == user_data["user_id"]
            ).first()
            
            if not existing_user:
                user = UserProfiles(**user_data)
                db.add(user)
                print(f"Created user profile: {user_data['username']}")
        
        db.commit()
        print("✅ User profiles created successfully")
        
    except Exception as e:
        print(f"❌ Error creating user profiles: {e}")
        db.rollback()
    finally:
        db.close()

def generate_ai_decision_factors():
    """AI判断根拠のサンプルデータを生成"""
    db = SessionLocal()
    try:
        # 最新の予測データを取得
        recent_predictions = db.query(StockPredictions).order_by(
            StockPredictions.created_at.desc()
        ).limit(50).all()
        
        factor_templates = [
            {
                "factor_type": "technical",
                "factor_name": "RSI反発シグナル",
                "description": "RSI指標が30を下回った後、反発上昇を示している",
                "influence_score": 0.85,
                "confidence": 0.78
            },
            {
                "factor_type": "fundamental", 
                "factor_name": "業績予想上方修正",
                "description": "次四半期のEPS予想が15%上方修正された",
                "influence_score": 0.92,
                "confidence": 0.88
            },
            {
                "factor_type": "sentiment",
                "factor_name": "投資家心理改善",
                "description": "アナリストの強気コメントが増加、機関投資家の買い増し観測",
                "influence_score": 0.73,
                "confidence": 0.65
            },
            {
                "factor_type": "news",
                "factor_name": "新製品発表影響",
                "description": "革新的な新製品の発表により市場期待が高まっている",
                "influence_score": 0.89,
                "confidence": 0.82
            },
            {
                "factor_type": "pattern",
                "factor_name": "上昇三角形パターン",
                "description": "チャート上で上昇三角形パターンを形成、ブレイクアウト間近",
                "influence_score": 0.76,
                "confidence": 0.71
            }
        ]
        
        created_count = 0
        for prediction in recent_predictions:
            # 各予測に2-4個の判断根拠を生成
            num_factors = random.randint(2, 4)
            selected_factors = random.sample(factor_templates, num_factors)
            
            for i, factor_template in enumerate(selected_factors):
                # スコアに多少のランダム性を追加
                influence_score = factor_template["influence_score"] + random.uniform(-0.1, 0.1)
                confidence = factor_template["confidence"] + random.uniform(-0.1, 0.1)
                
                factor = AiDecisionFactors(
                    prediction_id=prediction.id,
                    factor_type=factor_template["factor_type"],
                    factor_name=factor_template["factor_name"],
                    description=factor_template["description"],
                    influence_score=max(0.1, min(1.0, influence_score)),
                    confidence=max(0.1, min(1.0, confidence))
                )
                db.add(factor)
                created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} AI decision factors")
        
    except Exception as e:
        print(f"❌ Error creating AI decision factors: {e}")
        db.rollback()
    finally:
        db.close()

def generate_prediction_contests():
    """予測コンテストのサンプルデータを生成"""
    db = SessionLocal()
    try:
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META"]
        
        contests = []
        for i, symbol in enumerate(popular_symbols[:3]):
            contest_date = date.today() + timedelta(days=i*7)
            contest = PredictionContests(
                contest_name=f"Weekly {symbol} Price Challenge",
                symbol=symbol,
                contest_start_date=contest_date,
                prediction_deadline=datetime.combine(
                    contest_date + timedelta(days=5), 
                    datetime.min.time().replace(hour=23, minute=59)
                ),
                target_date=contest_date + timedelta(days=7),
                status="active",
                prize_description="Top 3 winners get digital badges and recognition"
            )
            db.add(contest)
            contests.append(contest)
        
        db.commit()
        print(f"✅ Created {len(contests)} prediction contests")
        
        # コンテストの参加データを生成
        generate_contest_predictions(db, contests)
        
    except Exception as e:
        print(f"❌ Error creating prediction contests: {e}")
        db.rollback()
    finally:
        db.close()

def generate_contest_predictions(db: SessionLocal, contests: List[PredictionContests]):
    """コンテスト予測のサンプルデータを生成"""
    try:
        users = db.query(UserProfiles).all()
        if not users:
            print("No users found, skipping contest predictions")
            return
        
        created_count = 0
        for contest in contests:
            # 各コンテストに1-2人のユーザーが参加
            participating_users = random.sample(users, min(len(users), random.randint(1, 2)))
            
            for user in participating_users:
                # 現在価格の±20%の範囲で予測価格を生成
                base_price = random.uniform(150, 300)  # Mock base price
                predicted_price = base_price * random.uniform(0.8, 1.2)
                
                prediction = UserContestPredictions(
                    contest_id=contest.id,
                    user_id=user.user_id,
                    predicted_price=round(predicted_price, 2),
                    confidence_level=random.choice(["low", "medium", "high"]),
                    reasoning=f"Based on technical analysis and market sentiment for {contest.symbol}"
                )
                db.add(prediction)
                created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} contest predictions")
        
    except Exception as e:
        print(f"❌ Error creating contest predictions: {e}")
        db.rollback()

def generate_theme_insights():
    """テーマ別インサイトのサンプルデータを生成"""
    db = SessionLocal()
    try:
        insights_data = [
            {
                "theme_name": "AI Revolution",
                "theme_category": "technology", 
                "title": "AI企業の第3四半期決算分析：成長継続の鍵",
                "summary": "生成AIブームが続く中、主要AI企業の決算発表が相次いでいます。NVIDIA、Microsoft、Googleなどの業績から見える今後のトレンドと投資機会を分析します。",
                "key_metrics": {
                    "sector_growth": "35.2%",
                    "market_cap_increase": "$2.1T",
                    "pe_ratio_average": 45.3
                },
                "related_symbols": ["NVDA", "MSFT", "GOOGL", "AMZN"],
                "trend_direction": "bullish",
                "impact_score": 9.2
            },
            {
                "theme_name": "Green Energy Transition",
                "theme_category": "energy",
                "title": "再生エネルギー政策と関連株への影響",
                "summary": "各国の脱炭素政策強化により、太陽光、風力発電関連企業に注目が集まっています。政策動向と業界の成長見通しを詳しく解説します。", 
                "key_metrics": {
                    "policy_support": "89%",
                    "capacity_growth": "28.5%",
                    "cost_reduction": "15.2%"
                },
                "related_symbols": ["NEE", "ENPH", "SEDG", "FSLR"],
                "trend_direction": "bullish",
                "impact_score": 8.7
            },
            {
                "theme_name": "Healthcare Innovation",
                "theme_category": "healthcare",
                "title": "バイオテック新薬承認ラッシュの投資チャンス",
                "summary": "2024年は新薬承認が活発化しており、特にがん治療薬や希少疾患治療薬の分野で画期的な承認が相次いでいます。関連企業の業績向上が期待されます。",
                "key_metrics": {
                    "new_approvals": 47,
                    "market_size": "$850B",
                    "r_and_d_increase": "12.3%"
                },
                "related_symbols": ["JNJ", "PFE", "MRNA", "GILD"],
                "trend_direction": "neutral", 
                "impact_score": 7.9
            }
        ]
        
        created_count = 0
        for insight_data in insights_data:
            insight_data["insight_date"] = date.today() - timedelta(days=random.randint(0, 30))
            
            insight = ThemeInsights(**insight_data)
            db.add(insight)
            created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} theme insights")
        
    except Exception as e:
        print(f"❌ Error creating theme insights: {e}")
        db.rollback()
    finally:
        db.close()

def generate_user_watchlists_and_portfolios():
    """ユーザーのウォッチリストとポートフォリオのサンプルデータを生成"""
    db = SessionLocal()
    try:
        users = db.query(UserProfiles).all()
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "JPM", "V", "JNJ"]
        
        for user in users:
            # ウォッチリスト生成 (3-6銘柄)
            watchlist_symbols = random.sample(popular_symbols, random.randint(3, 6))
            for symbol in watchlist_symbols:
                watchlist_item = UserWatchlists(
                    user_id=user.user_id,
                    symbol=symbol,
                    alert_threshold_up=random.uniform(5, 15),  # 5-15%上昇アラート
                    alert_threshold_down=random.uniform(-15, -5),  # 5-15%下落アラート
                    notes=f"{symbol}の長期投資候補として監視中",
                    priority=random.choice(["high", "medium", "low"])
                )
                db.add(watchlist_item)
            
            # ポートフォリオ生成 (2-4銘柄)
            if user.investment_style in ["conservative", "moderate"]:
                portfolio_symbols = random.sample(["AAPL", "MSFT", "JPM", "JNJ", "V"], random.randint(2, 4))
            else:  # aggressive, growth
                portfolio_symbols = random.sample(["TSLA", "NVDA", "GOOGL", "META", "AMZN"], random.randint(2, 4))
            
            total_weight = 100.0
            for i, symbol in enumerate(portfolio_symbols):
                if i == len(portfolio_symbols) - 1:  # 最後の銘柄
                    weight = total_weight
                else:
                    weight = random.uniform(15, 40)
                    total_weight -= weight
                
                shares = random.uniform(10, 100)
                avg_cost = random.uniform(100, 300)
                
                portfolio_item = UserPortfolios(
                    user_id=user.user_id,
                    symbol=symbol,
                    shares=round(shares, 2),
                    average_cost=round(avg_cost, 2),
                    purchase_date=date.today() - timedelta(days=random.randint(30, 365)),
                    portfolio_weight=round(weight, 2),
                    is_active=True
                )
                db.add(portfolio_item)
        
        db.commit()
        print("✅ Created user watchlists and portfolios")
        
    except Exception as e:
        print(f"❌ Error creating watchlists and portfolios: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """メインの実行関数"""
    print("🚀 Generating sample data for enhanced features...")
    print("=" * 60)
    
    try:
        print("1. Generating user profiles...")
        generate_user_profiles()
        
        print("\n2. Generating AI decision factors...")
        generate_ai_decision_factors()
        
        print("\n3. Generating prediction contests...")
        generate_prediction_contests()
        
        print("\n4. Generating theme insights...")
        generate_theme_insights()
        
        print("\n5. Generating user watchlists and portfolios...")
        generate_user_watchlists_and_portfolios()
        
        print("\n" + "=" * 60)
        print("✅ Sample data generation completed successfully!")
        print("\nGenerated data includes:")
        print("- User profiles with different investment styles")
        print("- AI decision factors for predictions")
        print("- Active prediction contests")
        print("- Theme-based market insights")
        print("- User watchlists and portfolios")
        
    except Exception as e:
        print(f"\n❌ Error during sample data generation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)