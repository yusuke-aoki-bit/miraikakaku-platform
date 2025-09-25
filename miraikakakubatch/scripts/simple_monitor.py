#!/usr/bin/env python3
"""
Simple Miraikakaku カバレッジ監視スクリプト
依存関係なしで動作する軽量監視システム

定期実行方法:
- Linux: crontab -e で以下を追加
  0 */6 * * * /usr/bin/python3 /path/to/simple_monitor.py
- Windows: タスクスケジューラーで設定
"""

import json
import os
import sys
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError
import time

def check_coverage():
    """カバレッジ状況チェック"""
    print(f"🔍 カバレッジチェック開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # API経由でカバレッジ取得
        with urlopen('http://localhost:8000/api/finance/markets/stats', timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                stats = json.loads(data)
                
                # 現在の状況表示
                print("📊 現在のカバレッジ:")
                print(f"  日本株: {stats['database_stats']['japanese_stocks']:,}社")
                print(f"  米国株: {stats['database_stats']['us_stocks']:,}社")
                print(f"  ETF: {stats['database_stats']['etfs']:,}銘柄")
                print(f"  合計: {stats['database_stats']['total_securities']:,}証券")
                
                # レポート生成
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'coverage': stats,
                    'thresholds': {
                        'japanese_stocks_ok': stats['database_stats']['japanese_stocks'] >= 4000,
                        'us_stocks_ok': stats['database_stats']['us_stocks'] >= 8500,
                        'etfs_ok': stats['database_stats']['etfs'] >= 2900
                    }
                }
                
                # 警告チェック
                warnings = []
                if stats['database_stats']['japanese_stocks'] < 4000:
                    warnings.append(f"日本株数不足: {stats['database_stats']['japanese_stocks']} < 4000")
                if stats['database_stats']['us_stocks'] < 8500:
                    warnings.append(f"米国株数不足: {stats['database_stats']['us_stocks']} < 8500")
                if stats['database_stats']['etfs'] < 2900:
                    warnings.append(f"ETF数不足: {stats['database_stats']['etfs']} < 2900")
                
                if warnings:
                    print("⚠️ 警告:")
                    for warning in warnings:
                        print(f"  {warning}")
                    report['warnings'] = warnings
                    report['status'] = 'warning'
                else:
                    print("✅ 全カバレッジ正常")
                
                # レポート保存
                save_report(report)
                
                return True
                
            else:
                print(f"❌ API接続エラー: {response.status}")
                return False
                
    except URLError as e:
        print(f"❌ ネットワークエラー: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def save_report(report):
    """レポート保存"""
    try:
        # reportsディレクトリ作成
        os.makedirs('reports', exist_ok=True)
        
        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reports/coverage_monitor_{timestamp}.json'
        
        # レポート保存
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"💾 レポート保存: {filename}")
        
        # 古いレポートファイル削除 (30日以上前)
        cleanup_old_reports()
        
    except Exception as e:
        print(f"❌ レポート保存エラー: {e}")

def cleanup_old_reports():
    """古いレポートファイル削除"""
    try:
        import glob
        from pathlib import Path
        
        # 30日前の日時
        cutoff_time = time.time() - (30 * 24 * 60 * 60)
        
        # 古いファイル削除
        for file_path in glob.glob('reports/coverage_monitor_*.json'):
            if os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                print(f"🗑️ 古いレポート削除: {os.path.basename(file_path)}")
                
    except Exception as e:
        print(f"❌ クリーンアップエラー: {e}")

def check_api_health():
    """API健全性チェック"""
    print("🔍 API健全性チェック中...")
    
    try:
        # 基本接続テスト
        with urlopen('http://localhost:8000/health', timeout=5) as response:
            if response.status == 200:
                print("✅ API健全性OK")
                return True
            else:
                print(f"⚠️ API応答異常: {response.status}")
                return False
                
    except URLError:
        print("❌ API接続不可 - universal_stock_api.pyが起動していません")
        return False
    except Exception as e:
        print(f"❌ APIチェックエラー: {e}")
        return False

def generate_daily_summary():
    """日次サマリー生成"""
    try:
        # 今日のレポートファイル検索
        today = datetime.now().strftime('%Y%m%d')
        import glob
        
        today_reports = glob.glob(f'reports/coverage_monitor_{today}_*.json')
        
        if not today_reports:
            print("📋 本日のレポートなし")
            return
            
        # 最新レポート読み込み
        latest_report = max(today_reports)
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            
        print(f"📋 本日のサマリー ({today}):")
        print(f"  チェック回数: {len(today_reports)}")
        print(f"  最新ステータス: {report_data.get('status', 'unknown')}")
        
        if 'warnings' in report_data:
            print(f"  警告数: {len(report_data['warnings'])}")
            
    except Exception as e:
        print(f"❌ サマリー生成エラー: {e}")

def main():
    """メイン処理"""
    print("="*60)
    print("🎯 Miraikakaku カバレッジ監視システム")
    print("="*60)
    
    # API健全性チェック
    if not check_api_health():
        print("❌ APIが利用できません")
        sys.exit(1)
        
    # カバレッジチェック実行
    success = check_coverage()
    
    # 日次サマリー生成
    generate_daily_summary()
    
    print("="*60)
    print(f"監視完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())