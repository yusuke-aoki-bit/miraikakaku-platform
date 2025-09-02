# Miraikakaku Batch Processing Specification

## 1. Related Requirements

- The batch processing system must generate stock and forex predictions.
- The prediction horizon must be 6 months ahead, based on 2 years of historical data.

---

## 2. Overview

This document describes the batch processing system of the Miraikakaku platform. The system is responsible for generating and updating stock and forex predictions, as well as other data-intensive tasks.

## 3. Stock Prediction Batch

- **Model**: LSTM (Long Short-Term Memory) neural network.
- **File**: `miraikakakubatch/functions/models/lstm_predictor.py`
- **Functionality**:
  - Uses 730 days (2 years) of historical data to predict 180 days (6 months) into the future.
  - The batch process runs periodically to generate new predictions and store them in the database.

## 4. Forex Prediction Batch

- **Models**: A suite of statistical models, including:
  - `STATISTICAL_V2`
  - `TREND_FOLLOWING_V1`
  - `MEAN_REVERSION_V1`
  - `ENSEMBLE_V1`
- **File**: `miraikakakubatch/functions/services/enhanced_prediction_service.py`
- **Functionality**:
  - Uses 730 days (2 years) of historical data to predict 180 days (6 months) into the future.
  - The batch process generates predictions from multiple models and stores them in the database.

## 5. Execution

The batch processes are designed to be executed periodically using a scheduler (e.g., cron, Cloud Scheduler). The main entry points for the batch jobs are likely within the `miraikakakubatch/functions` directory, with scripts such as `massive_batch_main.py` orchestrating the execution.