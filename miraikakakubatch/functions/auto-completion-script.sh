#!/bin/bash

# 継続的データベース完備スクリプト
# 2時間おきに実行され、目標達成まで継続

echo "🔄 継続的データベース完備システム開始..."

TARGET_SYMBOLS=5000
CURRENT_RUN=1

while true; do
    echo "===================="
    echo "実行回数: $CURRENT_RUN"
    echo "時刻: $(date)"
    echo "===================="
    
    # バッチジョブを実行
    JOB_NAME="auto-completion-$(date +%Y%m%d-%H%M%S)"
    
    echo "📊 ジョブ「$JOB_NAME」を実行中..."
    
    gcloud batch jobs submit $JOB_NAME \
        --location=us-central1 \
        --config=continuous-completion-job.yaml
    
    if [ $? -eq 0 ]; then
        echo "✅ ジョブ送信成功"
        
        # ジョブ完了まで待機
        echo "⏳ ジョブ完了を待機中..."
        
        while true; do
            STATE=$(gcloud batch jobs describe $JOB_NAME --location=us-central1 --format="get(status.state)" 2>/dev/null)
            
            case "$STATE" in
                "SUCCEEDED")
                    echo "✅ ジョブ完了"
                    break
                    ;;
                "FAILED")
                    echo "❌ ジョブ失敗"
                    break
                    ;;
                "RUNNING"|"SCHEDULED")
                    echo "🔄 実行中... ($STATE)"
                    sleep 30
                    ;;
                *)
                    echo "📊 状態: $STATE"
                    sleep 30
                    ;;
            esac
        done
        
        # 完備状況をチェック（簡易版）
        echo "📊 完備状況チェック中..."
        
        # データベースに直接接続してチェック
        SYMBOL_COUNT=$(gcloud sql connect miraikakaku-db --user=miraikakaku-user --database=miraikakaku --quiet <<EOF
SELECT COUNT(DISTINCT symbol) FROM stock_predictions;
\q
EOF
        )
        
        echo "現在の銘柄数: $SYMBOL_COUNT"
        
        if [ "$SYMBOL_COUNT" -ge $TARGET_SYMBOLS ]; then
            echo "🎉🎉🎉 目標達成！データベース完備完了！🎉🎉🎉"
            echo "最終銘柄数: $SYMBOL_COUNT / $TARGET_SYMBOLS"
            break
        else
            REMAINING=$((TARGET_SYMBOLS - SYMBOL_COUNT))
            echo "📈 残り銘柄数: $REMAINING"
            echo "⏳ 2時間後に次回実行..."
            sleep 7200  # 2時間待機
        fi
        
    else
        echo "❌ ジョブ送信失敗、30分後に再試行..."
        sleep 1800  # 30分待機
    fi
    
    CURRENT_RUN=$((CURRENT_RUN + 1))
    
    # 安全装置：100回で停止
    if [ $CURRENT_RUN -gt 100 ]; then
        echo "⚠️ 最大実行回数（100回）に達しました。停止します。"
        break
    fi
done

echo "🏁 継続的データベース完備システム終了"