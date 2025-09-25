#!/usr/bin/env python3
"""
Improved Batch Environment Setup for GCP Batch Jobs
Addresses exit code 127 (command not found) issues by ensuring proper Python environment setup.
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/batch_environment.log')
    ]
)
logger = logging.getLogger(__name__)

class BatchEnvironmentSetup:
    """Enhanced environment setup for GCP Batch jobs."""

    def __init__(self):
        self.start_time = time.time()
        self.required_packages = [
            'psycopg2-binary==2.9.7',
            'pandas==2.0.3',
            'yfinance==0.2.28',
            'numpy==1.24.3',
            'requests==2.31.0',
            'python-dotenv==1.0.0',
            'sqlalchemy==2.0.19',
        ]

    def log_system_info(self):
        """Log comprehensive system information for debugging."""
        logger.info("=== BATCH ENVIRONMENT SETUP START ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"PATH: {os.environ.get('PATH', 'NOT_SET')}")
        logger.info(f"HOME: {os.environ.get('HOME', 'NOT_SET')}")
        logger.info(f"USER: {os.environ.get('USER', 'NOT_SET')}")

        # Check available commands
        commands_to_check = ['python3', 'pip3', 'pip', 'which', 'whoami']
        for cmd in commands_to_check:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True, timeout=10)
                logger.info(f"{cmd} location: {result.stdout.strip() if result.returncode == 0 else 'NOT_FOUND'}")
            except Exception as e:
                logger.warning(f"Error checking {cmd}: {e}")

    def setup_python_environment(self):
        """Set up Python environment with proper error handling."""
        logger.info("Setting up Python environment...")

        try:
            # Ensure pip is available
            pip_commands = ['pip3', 'pip', f'{sys.executable} -m pip']
            pip_cmd = None

            for cmd in pip_commands:
                try:
                    result = subprocess.run(cmd.split() + ['--version'],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        pip_cmd = cmd
                        logger.info(f"Using pip command: {pip_cmd}")
                        logger.info(f"Pip version: {result.stdout.strip()}")
                        break
                except Exception as e:
                    logger.warning(f"Failed to check {cmd}: {e}")
                    continue

            if not pip_cmd:
                logger.error("No pip command found. Installing pip...")
                # Try to install pip
                try:
                    subprocess.run([sys.executable, '-m', 'ensurepip', '--upgrade'],
                                 check=True, timeout=120)
                    pip_cmd = f'{sys.executable} -m pip'
                except Exception as e:
                    logger.error(f"Failed to install pip: {e}")
                    raise

            # Upgrade pip
            logger.info("Upgrading pip...")
            try:
                subprocess.run(pip_cmd.split() + ['install', '--upgrade', 'pip'],
                             check=True, timeout=120)
            except Exception as e:
                logger.warning(f"Failed to upgrade pip: {e}")

            # Install required packages
            logger.info("Installing required packages...")
            for package in self.required_packages:
                logger.info(f"Installing {package}...")
                try:
                    subprocess.run(pip_cmd.split() + ['install', package],
                                 check=True, timeout=300)
                    logger.info(f"Successfully installed {package}")
                except Exception as e:
                    logger.error(f"Failed to install {package}: {e}")
                    # Continue with other packages
                    continue

            # Verify installations
            logger.info("Verifying package installations...")
            try:
                import psycopg2
                import pandas as pd
                import yfinance as yf
                import numpy as np
                import requests
                logger.info("All critical packages imported successfully")
            except ImportError as e:
                logger.error(f"Package import failed: {e}")
                raise

        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            raise

    def setup_database_config(self):
        """Set up database configuration."""
        logger.info("Setting up database configuration...")

        # Database configuration
        db_config = {
            'POSTGRES_HOST': '34.173.9.214',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'os.getenv('DB_PASSWORD', '')',
            'POSTGRES_DB': 'miraikakaku',
            'POSTGRES_PORT': '5432'
        }

        # Set environment variables
        for key, value in db_config.items():
            os.environ[key] = value
            logger.info(f"Set {key} environment variable")

        # Test database connection
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=db_config['POSTGRES_HOST'],
                user=db_config['POSTGRES_USER'],
                password=db_config['POSTGRES_PASSWORD'],
                database=db_config['POSTGRES_DB'],
                port=db_config['POSTGRES_PORT']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"Database connection successful: {version[0]}")
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    def run_simple_data_collection(self):
        """Run a simple data collection task to verify everything works."""
        logger.info("Running simple data collection test...")

        try:
            import yfinance as yf
            import pandas as pd
            import psycopg2

            # Test data fetch
            logger.info("Testing yfinance data fetch...")
            ticker = yf.Ticker("AAPL")
            data = ticker.history(period="5d")

            if not data.empty:
                logger.info(f"Successfully fetched {len(data)} rows of AAPL data")
                logger.info(f"Latest close price: ${data['Close'].iloc[-1]:.2f}")
            else:
                logger.warning("No data fetched from yfinance")

            # Test database insert
            logger.info("Testing database insert...")
            conn = psycopg2.connect(
                host=os.environ['POSTGRES_HOST'],
                user=os.environ['POSTGRES_USER'],
                password=os.environ['POSTGRES_PASSWORD'],
                database=os.environ['POSTGRES_DB'],
                port=os.environ['POSTGRES_PORT']
            )

            cursor = conn.cursor()

            # Insert test data
            test_query = """
            INSERT INTO stock_prices (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (symbol, date) DO UPDATE SET
                close_price = EXCLUDED.close_price,
                updated_at = NOW()
            """

            if not data.empty:
                latest_row = data.iloc[-1]
                cursor.execute(test_query, (
                    'AAPL',
                    data.index[-1].date(),
                    float(latest_row['Open']),
                    float(latest_row['High']),
                    float(latest_row['Low']),
                    float(latest_row['Close']),
                    int(latest_row['Volume'])
                ))

                conn.commit()
                logger.info("Successfully inserted test data into database")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Data collection test failed: {e}")
            raise

    def generate_report(self):
        """Generate final environment setup report."""
        elapsed_time = time.time() - self.start_time

        logger.info("=== BATCH ENVIRONMENT SETUP REPORT ===")
        logger.info(f"Setup completed in {elapsed_time:.2f} seconds")
        logger.info("Environment status: READY")
        logger.info("Database connection: VERIFIED")
        logger.info("Data collection: TESTED")
        logger.info("=== READY FOR PRODUCTION TASKS ===")

def main():
    """Main execution function."""
    setup = BatchEnvironmentSetup()

    try:
        # Step 1: Log system information
        setup.log_system_info()

        # Step 2: Set up Python environment
        setup.setup_python_environment()

        # Step 3: Set up database configuration
        setup.setup_database_config()

        # Step 4: Run simple test
        setup.run_simple_data_collection()

        # Step 5: Generate report
        setup.generate_report()

        logger.info("🎉 BATCH ENVIRONMENT SETUP SUCCESSFUL! 🎉")
        return 0

    except Exception as e:
        logger.error(f"❌ BATCH ENVIRONMENT SETUP FAILED: {e}")
        logger.error("Check the logs above for detailed error information")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)