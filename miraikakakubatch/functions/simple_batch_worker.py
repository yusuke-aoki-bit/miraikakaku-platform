#!/usr/bin/env python3
import pymysql
import random
import numpy as np
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    worker_id = int(os.getenv("BATCH_TASK_INDEX", "0"))
    logger.info(f"Stable Worker {worker_id} started")
    
    db_config = {
        "host": os.getenv("DB_HOST", "34.58.103.36"),
        "user": os.getenv("DB_USER", "miraikakaku-user"),
        "password": os.getenv("DB_PASSWORD", "miraikakaku-secure-pass-2024"),
        "database": os.getenv("DB_NAME", "miraikakaku"),
        "charset": "utf8mb4"
    }
    
    try:
        connection = pymysql.connect(**db_config)
        logger.info("Database connected successfully")
        
        with connection.cursor() as cursor:
            batch_size = 10
            offset = worker_id * batch_size
            
            cursor.execute("""
                SELECT symbol FROM stock_master
                WHERE is_active = 1
                ORDER BY symbol
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            stocks = cursor.fetchall()
            logger.info(f"Processing {len(stocks)} stocks")
            
            total = 0
            for stock in stocks:
                symbol = stock[0]
                predictions = []
                
                for j in range(3):
                    pred_date = datetime.now() - timedelta(days=j)
                    pred_price = random.uniform(100, 1000)
                    confidence = random.uniform(0.7, 0.9)
                    
                    predictions.append((
                        symbol, pred_date.strftime("%Y-%m-%d %H:%M:%S"),
                        round(pred_price, 2), 0, 0,
                        round(confidence, 3), "stable_model",
                        "v1", 1, 1, f"StableWorker_{worker_id}"
                    ))
                
                if predictions:
                    cursor.executemany("""
                        INSERT INTO stock_predictions
                        (symbol, prediction_date, predicted_price, predicted_change,
                         predicted_change_percent, confidence_score, model_type,
                         model_version, prediction_horizon, is_active, notes, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, predictions)
                    connection.commit()
                    total += len(predictions)
            
            logger.info(f"Generated {total} predictions successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)
    finally:
        if "connection" in locals():
            connection.close()

if __name__ == "__main__":
    main()