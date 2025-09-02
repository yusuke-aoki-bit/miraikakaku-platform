#!/usr/bin/env python3
"""
データベース補填状況の緊急確認スクリプト
"""

import psycopg2
from datetime import datetime

# PostgreSQL接続設定
db_config = {
    "host": "34.173.9.214",
    "user": "miraikakaku-user", 
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "port": 5432
}

def check_data_status():
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        print('✅ PostgreSQL接続成功')
        
        print('\n📊 データベース補填状況レポート')
        print('=' * 60)
        
        # 1. stock_predictions テーブル確認
        cursor.execute('''
            SELECT 
                COUNT(*) as total_predictions,
                COUNT(DISTINCT symbol) as unique_symbols,
                COUNT(DISTINCT model_type) as unique_models,
                MAX(prediction_horizon) as max_horizon,
                DATE(MAX(prediction_date)) as latest_date
            FROM stock_predictions
        ''')
        
        result = cursor.fetchone()
        if result:
            total, symbols, models, max_horizon, latest = result
            print(f'📋 stock_predictions:')
            print(f'  - 総予測数: {total:,}件')
            print(f'  - 銘柄数: {symbols}')
            print(f'  - モデル数: {models}')
            print(f'  - 最大予測日数: {max_horizon}日')
            print(f'  - 最新予測日: {latest}')
            
            # カバレッジ計算
            target_symbols = 25
            target_models = 5
            target_predictions = target_symbols * target_models * 12  # 1,500件
            
            symbol_coverage = min(100, (symbols / target_symbols) * 100)
            model_coverage = min(100, (models / target_models) * 100)
            prediction_coverage = min(100, (total / target_predictions) * 100)
            overall_coverage = (symbol_coverage + model_coverage + prediction_coverage) / 3
            
            print(f'\n🎯 カバレッジ分析:')
            print(f'  - 銘柄カバレッジ: {symbol_coverage:.1f}% ({symbols}/{target_symbols})')
            print(f'  - モデルカバレッジ: {model_coverage:.1f}% ({models}/{target_models})')
            print(f'  - 予測カバレッジ: {prediction_coverage:.1f}% ({total:,}/{target_predictions:,})')
            print(f'  - 総合カバレッジ: {overall_coverage:.1f}%')
        
        # 2. stock_price_history テーブル確認
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    DATE(MIN(date)) as earliest_date,
                    DATE(MAX(date)) as latest_date
                FROM stock_price_history
            ''')
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                total_records, price_symbols, earliest, latest = result
                print(f'\n💰 stock_price_history:')
                print(f'  - 総レコード数: {total_records:,}件')
                print(f'  - 銘柄数: {price_symbols}')
                print(f'  - データ期間: {earliest} ～ {latest}')
            else:
                print(f'\n💰 stock_price_history: データなし（0件）')
                
        except Exception as e:
            print(f'\n💰 stock_price_history: テーブル未作成または確認エラー - {e}')
        
        # 3. 銘柄一覧確認
        cursor.execute('SELECT DISTINCT symbol FROM stock_predictions ORDER BY symbol LIMIT 20')
        symbols_list = [row[0] for row in cursor.fetchall()]
        print(f'\n📈 予測対象銘柄（最初20銘柄）:')
        print(f'  {", ".join(symbols_list)}')
        
        # 4. モデル一覧確認
        cursor.execute('SELECT DISTINCT model_type FROM stock_predictions ORDER BY model_type')
        models_list = [row[0] for row in cursor.fetchall()]
        print(f'\n🤖 使用モデル:')
        print(f'  {", ".join(models_list)}')
        
        # 5. 180日予測確認
        cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE prediction_horizon >= 180')
        long_term_count = cursor.fetchone()[0]
        print(f'\n📅 180日以上予測: {long_term_count}件')
        
        connection.close()
        
        # 6. 補填完了判定
        print('\n' + '='*60)
        if overall_coverage >= 100:
            print('🎉 データ補填完了！100%達成済み！')
        elif overall_coverage >= 80:
            print(f'🚀 データ補填順調！{overall_coverage:.1f}%達成')
            print(f'   あと{100-overall_coverage:.1f}%で完了')
        else:
            print(f'⏳ データ補填継続中: {overall_coverage:.1f}%')
            print('   追加のバッチジョブが必要')
        
    except Exception as e:
        print(f'❌ データベース接続エラー: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_status()