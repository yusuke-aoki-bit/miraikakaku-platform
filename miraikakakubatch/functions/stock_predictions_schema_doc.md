# stock_predictions テーブル設計書

## 概要
株価予測システムで生成される予測結果と実際の価格データを格納し、予測精度の追跡・評価を行うためのテーブルです。

## テーブル構造

### 主要カラム

#### 基本情報
- `id`: BIGINT AUTO_INCREMENT PRIMARY KEY - レコード一意識別子
- `symbol`: VARCHAR(20) NOT NULL - 銘柄コード（例：7203, AAPL）
- `prediction_date`: DATE NOT NULL - 予測を行った日付
- `target_date`: DATE NOT NULL - 予測対象日（何日後の価格を予測したか）
- `prediction_horizon_days`: INT NOT NULL - 予測期間（日数）

#### 予測価格データ
- `predicted_open`: DECIMAL(10,3) - 予測始値
- `predicted_high`: DECIMAL(10,3) - 予測高値
- `predicted_low`: DECIMAL(10,3) - 予測安値
- `predicted_close`: DECIMAL(10,3) - 予測終値
- `predicted_volume`: BIGINT - 予測出来高

#### 実際の価格データ（後から更新）
- `actual_open`: DECIMAL(10,3) - 実際の始値
- `actual_high`: DECIMAL(10,3) - 実際の高値
- `actual_low`: DECIMAL(10,3) - 実際の安値
- `actual_close`: DECIMAL(10,3) - 実際の終値
- `actual_volume`: BIGINT - 実際の出来高

#### 予測精度メトリクス
- `accuracy_score`: DECIMAL(5,4) - 総合精度スコア（0-1）
- `mse_score`: DECIMAL(10,6) - 平均二乗誤差
- `mae_score`: DECIMAL(10,6) - 平均絶対誤差
- `direction_accuracy`: DECIMAL(5,4) - 方向性精度（上昇/下降予測の正解率）

#### モデル情報
- `model_name`: VARCHAR(50) NOT NULL - 使用したモデル名
- `model_version`: VARCHAR(20) - モデルバージョン
- `confidence_score`: DECIMAL(5,4) - 予測信頼度

#### メタ情報
- `features_used`: TEXT - 使用した特徴量の詳細
- `training_data_start`: DATE - 学習データ開始日
- `training_data_end`: DATE - 学習データ終了日

#### システム情報
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP - レコード作成日時
- `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP - 最終更新日時

## インデックス設計

### パフォーマンス最適化インデックス
1. `idx_symbol_date` (symbol, prediction_date) - 銘柄別・日付別検索
2. `idx_target_date` (target_date) - 予測対象日での検索
3. `idx_model` (model_name, model_version) - モデル別検索
4. `idx_accuracy` (accuracy_score) - 精度ソート検索

### 一意性制約
- `unique_prediction` (symbol, prediction_date, target_date, model_name) - 重複予測防止

## 関連ビュー

### prediction_accuracy_summary
```sql
CREATE OR REPLACE VIEW prediction_accuracy_summary AS
SELECT 
    model_name,
    model_version,
    COUNT(*) as total_predictions,
    AVG(accuracy_score) as avg_accuracy,
    AVG(direction_accuracy) as avg_direction_accuracy,
    AVG(confidence_score) as avg_confidence,
    MIN(prediction_date) as first_prediction,
    MAX(prediction_date) as last_prediction
FROM stock_predictions 
WHERE accuracy_score IS NOT NULL
GROUP BY model_name, model_version
ORDER BY avg_accuracy DESC
```

## 使用例

### 1. 予測結果の登録
```sql
INSERT INTO stock_predictions (
    symbol, prediction_date, target_date, prediction_horizon_days,
    predicted_close, model_name, model_version, confidence_score
) VALUES (
    '7203', '2025-08-31', '2025-09-01', 1,
    1200.50, 'LSTM_v2', '2.1', 0.85
);
```

### 2. 実際の結果で更新（精度計算）
```sql
UPDATE stock_predictions SET
    actual_close = 1195.30,
    accuracy_score = 0.9956,
    direction_accuracy = 1.0000
WHERE symbol = '7203' AND prediction_date = '2025-08-31' 
    AND target_date = '2025-09-01' AND model_name = 'LSTM_v2';
```

### 3. モデル精度の比較
```sql
SELECT * FROM prediction_accuracy_summary
WHERE total_predictions >= 100
ORDER BY avg_accuracy DESC;
```

### 4. 特定銘柄の予測履歴
```sql
SELECT prediction_date, target_date, predicted_close, actual_close,
       accuracy_score, model_name
FROM stock_predictions 
WHERE symbol = '7203'
ORDER BY prediction_date DESC
LIMIT 30;
```

## 運用方針

### データライフサイクル
1. **予測時**: 予測結果のみ登録（actual_*カラムはNULL）
2. **検証時**: target_dateになったら実際の価格データで更新
3. **精度計算**: 予測と実際の差分から各種メトリクスを算出

### パフォーマンス考慮
- 大量データに対応するためBIGINTのidを使用
- 頻繁な検索パターンに最適化されたインデックス設計
- パーティショニング（将来的にprediction_date基準で月次分割も検討）

### データ品質
- NOT NULL制約により必須データの保証
- UNIQUE制約により重複予測の防止
- DECIMAL型による高精度な価格・スコア格納