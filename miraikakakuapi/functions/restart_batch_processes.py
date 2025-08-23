#!/usr/bin/env python3
"""
停止中バッチ処理の再起動 - 問題修正後の確実な処理実行
"""

import logging
import subprocess
import time
import os
import sys

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restart_batch_processes():
    """停止中のバッチ処理を安全に再起動"""
    
    logger.info("🔄 停止中バッチ処理の再起動開始")
    
    # 必要なパッケージをインストール
    try:
        subprocess.run(['pip', 'install', 'schedule'], check=True, capture_output=True)
        logger.info("✅ schedule パッケージをインストールしました")
    except subprocess.CalledProcessError:
        logger.warning("⚠️  schedule パッケージのインストールに失敗")
    
    # 再起動対象のバッチ処理リスト
    batch_scripts = [
        {
            'name': 'turbo_expansion',
            'script': 'turbo_expansion.py',
            'log': 'turbo_expansion_restart.log',
            'priority': 1
        },
        {
            'name': 'instant_mega_boost',
            'script': 'instant_mega_boost.py', 
            'log': 'instant_mega_boost_restart.log',
            'priority': 2
        },
        {
            'name': 'continuous_247_pipeline',
            'script': 'continuous_247_pipeline.py',
            'log': 'continuous_247_restart.log',
            'priority': 3
        },
        {
            'name': 'synthetic_data_booster',
            'script': 'synthetic_data_booster.py',
            'log': 'synthetic_boost_restart.log',
            'priority': 4
        }
    ]
    
    # 優先度順で再起動
    batch_scripts.sort(key=lambda x: x['priority'])
    
    restarted_count = 0
    
    for batch in batch_scripts:
        try:
            logger.info(f"🚀 {batch['name']} を再起動中...")
            
            # バックグラウンドで実行
            cmd = f"source venv/bin/activate && python {batch['script']} > {batch['log']} 2>&1 &"
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                executable='/bin/bash',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 短時間待機（プロセス開始確認）
            time.sleep(2)
            
            if process.poll() is None:  # プロセスが実行中
                logger.info(f"  ✅ {batch['name']} 再起動成功 (PID: {process.pid})")
                restarted_count += 1
            else:
                logger.warning(f"  ⚠️  {batch['name']} 即座に終了")
            
            # 次のバッチとの間隔
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"  ❌ {batch['name']} 再起動エラー: {e}")
            continue
    
    logger.info(f"🎯 バッチ再起動完了: {restarted_count}/{len(batch_scripts)}")
    
    # 実行中プロセス確認
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode == 0:
            python_processes = [
                line for line in result.stdout.split('\n') 
                if 'python' in line.lower() and any(batch['script'].replace('.py', '') in line for batch in batch_scripts)
            ]
            logger.info(f"📊 実行中バッチプロセス: {len(python_processes)}個")
            
            for proc in python_processes[:5]:  # 最初の5個のみ表示
                script_name = None
                for batch in batch_scripts:
                    if batch['script'].replace('.py', '') in proc:
                        script_name = batch['name']
                        break
                logger.info(f"  🟢 {script_name or 'Unknown'}: 実行中")
    
    except Exception as e:
        logger.error(f"プロセス確認エラー: {e}")
    
    return restarted_count

if __name__ == "__main__":
    result = restart_batch_processes()
    logger.info(f"✅ 再起動完了: {result}個のバッチプロセス")