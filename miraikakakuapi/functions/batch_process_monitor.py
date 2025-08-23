#!/usr/bin/env python3
"""
バッチプロセス監視 - 現在稼働中のバッチ処理状況を詳細に監視・報告
"""

import subprocess
import psutil
import logging
import os
import sys
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_running_batch_processes():
    """稼働中のバッチプロセス一覧取得"""
    
    logger.info("🔍 稼働中バッチプロセス検索中...")
    
    batch_processes = []
    
    try:
        # プロセス一覧取得
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # バッチスクリプトを検出
                    batch_scripts = [
                        'comprehensive_batch.py',
                        'turbo_expansion.py', 
                        'ultimate_100_point_system.py',
                        'instant_mega_boost.py',
                        'continuous_247_pipeline.py',
                        'synthetic_data_booster.py',
                        'massive_data_expansion.py',
                        'quick_boost.py',
                        'fix_foreign_key_constraints.py',
                        'main.py'  # APIサーバー
                    ]
                    
                    detected_script = None
                    for script in batch_scripts:
                        if script in cmdline:
                            detected_script = script
                            break
                    
                    if detected_script:
                        # プロセス情報収集
                        create_time = datetime.fromtimestamp(proc.info['create_time'])
                        running_time = datetime.now() - create_time
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                        
                        batch_processes.append({
                            'pid': proc.info['pid'],
                            'script': detected_script,
                            'create_time': create_time,
                            'running_time': running_time,
                            'memory_mb': memory_mb,
                            'cpu_percent': proc.info.get('cpu_percent', 0),
                            'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                        })
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    except Exception as e:
        logger.error(f"プロセス検索エラー: {e}")
    
    return batch_processes

def check_log_files():
    """ログファイルの状況確認"""
    
    logger.info("📋 ログファイル確認中...")
    
    log_files = [
        'comprehensive_batch_bg.log',
        'turbo_expansion_bg.log', 
        'turbo_expansion.log',
        'ultimate_system.log',
        'instant_mega_boost.log',
        'continuous_247_restart.log',
        'synthetic_boost.log',
        'massive_expansion.log',
        'quick_boost.log',
        'fix_constraints_bg.log'
    ]
    
    log_status = []
    
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                stat = os.stat(log_file)
                size_mb = stat.st_size / 1024 / 1024
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                # 最後の数行を読んで進捗確認
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-3:] if lines else []
                        
                        # エラーパターン検索
                        error_count = sum(1 for line in lines if any(err in line.upper() for err in ['ERROR', 'FAILED', 'EXCEPTION']))
                        success_count = sum(1 for line in lines if any(success in line for success in ['✅', '成功', 'SUCCESS', '完了']))
                        
                except Exception:
                    last_lines = ['読み込み不可']
                    error_count = 0
                    success_count = 0
                
                log_status.append({
                    'file': log_file,
                    'size_mb': size_mb,
                    'modified': modified,
                    'last_lines': last_lines,
                    'error_count': error_count,
                    'success_count': success_count,
                    'exists': True
                })
            else:
                log_status.append({
                    'file': log_file,
                    'exists': False
                })
                
        except Exception as e:
            log_status.append({
                'file': log_file,
                'error': str(e),
                'exists': False
            })
    
    return log_status

def check_database_activity():
    """データベース活動確認"""
    
    logger.info("🗄️  データベース活動確認中...")
    
    try:
        # パスを追加
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # 最近のデータ追加確認
        result = db.execute(text("""
            SELECT 
                COUNT(*) as recent_prices,
                (SELECT COUNT(*) FROM stock_prices WHERE created_at >= NOW() - INTERVAL 1 HOUR) as hour_prices,
                (SELECT COUNT(*) FROM stock_predictions WHERE created_at >= NOW() - INTERVAL 1 HOUR) as hour_preds,
                (SELECT COUNT(DISTINCT symbol) FROM stock_prices WHERE created_at >= NOW() - INTERVAL 1 HOUR) as hour_symbols
            FROM stock_prices 
            WHERE created_at >= NOW() - INTERVAL 10 MINUTE
        """))
        
        activity = result.fetchone()
        db.close()
        
        return {
            '10分間の価格追加': activity[0],
            '1時間の価格追加': activity[1], 
            '1時間の予測追加': activity[2],
            '1時間の対象銘柄': activity[3],
            'db_accessible': True
        }
        
    except Exception as e:
        logger.error(f"DB活動確認エラー: {e}")
        return {
            'db_accessible': False,
            'error': str(e)
        }

def generate_batch_status_report():
    """バッチプロセス状況の総合レポート生成"""
    
    logger.info("=" * 80)
    logger.info("📊 稼働中バッチプロセス状況レポート")
    logger.info(f"📅 レポート時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    # 1. 稼働中プロセス確認
    processes = get_running_batch_processes()
    
    logger.info(f"🚀 稼働中プロセス: {len(processes)}個")
    logger.info("-" * 60)
    
    if processes:
        # スクリプト別グループ化
        script_groups = {}
        for proc in processes:
            script = proc['script']
            if script not in script_groups:
                script_groups[script] = []
            script_groups[script].append(proc)
        
        for script, procs in script_groups.items():
            logger.info(f"📦 {script}: {len(procs)}個プロセス")
            
            for proc in procs[:3]:  # 最初の3個のみ表示
                running_hours = proc['running_time'].total_seconds() / 3600
                logger.info(f"  PID {proc['pid']}: {running_hours:.1f}時間稼働, RAM {proc['memory_mb']:.1f}MB")
            
            if len(procs) > 3:
                logger.info(f"  ... 他 {len(procs)-3}個プロセス")
    else:
        logger.warning("⚠️ 稼働中バッチプロセスが見つかりません")
    
    logger.info("")
    
    # 2. ログファイル状況
    logs = check_log_files()
    
    logger.info("📋 ログファイル状況")
    logger.info("-" * 60)
    
    active_logs = [log for log in logs if log.get('exists', False)]
    
    for log in active_logs:
        age = datetime.now() - log['modified']
        age_str = f"{age.total_seconds()/3600:.1f}h前" if age.total_seconds() > 3600 else f"{age.total_seconds()/60:.0f}m前"
        
        status_emoji = "🟢" if age.total_seconds() < 600 else "🟡" if age.total_seconds() < 3600 else "🔴"
        
        logger.info(f"{status_emoji} {log['file']}: {log['size_mb']:.1f}MB, 更新{age_str}")
        logger.info(f"   成功:{log['success_count']}件, エラー:{log['error_count']}件")
        
        # 最新の進捗表示
        if log['last_lines']:
            latest_line = log['last_lines'][-1].strip()[:80]
            if latest_line:
                logger.info(f"   最新: {latest_line}")
    
    logger.info("")
    
    # 3. データベース活動
    db_activity = check_database_activity()
    
    logger.info("🗄️ データベース活動")
    logger.info("-" * 60)
    
    if db_activity.get('db_accessible', False):
        logger.info(f"✅ 直近10分: {db_activity['10分間の価格追加']}件の価格データ追加")
        logger.info(f"📊 直近1時間: 価格{db_activity['1時間の価格追加']}件, 予測{db_activity['1時間の予測追加']}件")
        logger.info(f"🎯 対象銘柄: {db_activity['1時間の対象銘柄']}銘柄")
    else:
        logger.error(f"❌ データベース接続エラー: {db_activity.get('error', 'Unknown')}")
    
    # 4. システムリソース
    logger.info("")
    logger.info("💻 システムリソース")
    logger.info("-" * 60)
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        logger.info(f"CPU使用率: {cpu_percent}%")
        logger.info(f"メモリ使用率: {memory.percent}% ({memory.used/1024/1024/1024:.1f}GB/{memory.total/1024/1024/1024:.1f}GB)")
        logger.info(f"ディスク使用率: {disk.percent}% ({disk.free/1024/1024/1024:.1f}GB空き)")
        
    except Exception as e:
        logger.error(f"システムリソース確認エラー: {e}")
    
    # 5. 推奨事項
    logger.info("")
    logger.info("💡 推奨事項")
    logger.info("-" * 60)
    
    if len(processes) == 0:
        logger.warning("⚠️ バッチプロセスが停止中 - restart_batch_processes.py実行を推奨")
    elif len(processes) > 15:
        logger.warning("⚠️ プロセス数が多すぎます - リソース監視を推奨")
    else:
        logger.info("✅ プロセス数適正 - 継続監視中")
    
    if db_activity.get('10分間の価格追加', 0) == 0:
        logger.warning("⚠️ 直近データ追加なし - バッチ処理確認が必要")
    else:
        logger.info("✅ データ追加継続中")
    
    logger.info("=" * 80)
    
    return {
        'processes': len(processes),
        'active_logs': len(active_logs),
        'db_activity': db_activity,
        'script_groups': len(script_groups) if processes else 0
    }

if __name__ == "__main__":
    report = generate_batch_status_report()
    logger.info(f"📈 監視完了: {report['processes']}プロセス稼働中")