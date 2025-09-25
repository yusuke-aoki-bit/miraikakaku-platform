#!/usr/bin/env python3
"""
Machine Learning Model Enhancer for Miraikakaku
Improve ML model accuracy and performance
"""

import psycopg2
import numpy as np
import pandas as pd
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import warnings
warnings.filterwarnings('ignore')

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class MLModelEnhancer:
    def __init__(self):
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': 'os.getenv('DB_PASSWORD', '')',
            'database': 'miraikakaku'
        }

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def analyze_prediction_accuracy(self) -> Dict[str, Any]:
        """Analyze current prediction accuracy by model type"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_analysis': {},
            'overall_metrics': {},
            'recommendations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Get prediction accuracy by model type
            accuracy_query = """
            SELECT
                model_type,
                COUNT(*) as total_predictions,
                COUNT(CASE WHEN actual_price IS NOT NULL THEN 1 END) as validated_predictions,
                AVG(CASE
                    WHEN actual_price IS NOT NULL
                    THEN ABS(predicted_price - actual_price) / actual_price * 100
                END) as avg_percentage_error,
                AVG(confidence_score) as avg_confidence,
                MIN(prediction_date) as earliest_prediction,
                MAX(prediction_date) as latest_prediction
            FROM stock_predictions
            WHERE is_active = true
            GROUP BY model_type
            ORDER BY total_predictions DESC;
            """

            cursor.execute(accuracy_query)
            model_stats = cursor.fetchall()

            for row in model_stats:
                model_type, total, validated, avg_error, avg_confidence, earliest, latest = row

                accuracy_score = None
                if avg_error is not None:
                    accuracy_score = max(0, 100 - avg_error)

                results['model_analysis'][model_type] = {
                    'total_predictions': total,
                    'validated_predictions': validated or 0,
                    'validation_rate': round((validated or 0) / total * 100, 2) if total > 0 else 0,
                    'average_percentage_error': round(avg_error or 0, 2),
                    'accuracy_score': round(accuracy_score or 0, 2),
                    'average_confidence': round(avg_confidence or 0, 2),
                    'date_range': {
                        'earliest': str(earliest) if earliest else None,
                        'latest': str(latest) if latest else None
                    }
                }

                # Generate recommendations based on performance
                if validated and validated > 10:  # Only for models with sufficient validation data
                    if avg_error and avg_error > 15:
                        results['recommendations'].append(
                            f"Model {model_type}: High error rate ({avg_error:.1f}%) - needs improvement"
                        )
                    elif avg_error and avg_error < 5:
                        results['recommendations'].append(
                            f"Model {model_type}: Excellent performance ({avg_error:.1f}% error) - consider expanding"
                        )

                if avg_confidence and avg_confidence < 0.6:
                    results['recommendations'].append(
                        f"Model {model_type}: Low confidence scores - review feature engineering"
                    )

            # Overall system metrics
            cursor.execute("""
            SELECT
                COUNT(*) as total_predictions,
                COUNT(DISTINCT symbol) as unique_symbols,
                COUNT(DISTINCT model_type) as model_types,
                AVG(confidence_score) as system_avg_confidence
            FROM stock_predictions
            WHERE is_active = true;
            """)

            overall_stats = cursor.fetchone()
            if overall_stats:
                results['overall_metrics'] = {
                    'total_predictions': overall_stats[0],
                    'unique_symbols': overall_stats[1],
                    'model_types': overall_stats[2],
                    'system_avg_confidence': round(overall_stats[3] or 0, 3)
                }

        except Exception as e:
            logger.error(f"Error analyzing prediction accuracy: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def analyze_feature_importance(self) -> Dict[str, Any]:
        """Analyze which features contribute most to accurate predictions"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'feature_analysis': {},
            'data_patterns': {},
            'recommendations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Analyze prediction accuracy by time horizons
            horizon_query = """
            SELECT
                prediction_horizon,
                COUNT(*) as predictions,
                COUNT(CASE WHEN actual_price IS NOT NULL THEN 1 END) as validated,
                AVG(CASE
                    WHEN actual_price IS NOT NULL
                    THEN ABS(predicted_price - actual_price) / actual_price * 100
                END) as avg_error
            FROM stock_predictions
            WHERE is_active = true
            GROUP BY prediction_horizon
            ORDER BY prediction_horizon;
            """

            cursor.execute(horizon_query)
            horizon_stats = cursor.fetchall()

            for horizon, count, validated, avg_error in horizon_stats:
                results['feature_analysis'][f'{horizon}_day_horizon'] = {
                    'predictions': count,
                    'validated': validated or 0,
                    'average_error': round(avg_error or 0, 2)
                }

                if validated and validated > 5:
                    if avg_error and avg_error < 8:
                        results['recommendations'].append(
                            f"{horizon}-day predictions show good accuracy ({avg_error:.1f}% error)"
                        )
                    elif avg_error and avg_error > 20:
                        results['recommendations'].append(
                            f"{horizon}-day predictions need improvement ({avg_error:.1f}% error)"
                        )

            # Analyze prediction performance by symbol characteristics
            symbol_performance_query = """
            SELECT
                sp.symbol,
                sm.market,
                sm.sector,
                COUNT(sp.id) as predictions,
                AVG(CASE
                    WHEN sp.actual_price IS NOT NULL
                    THEN ABS(sp.predicted_price - sp.actual_price) / sp.actual_price * 100
                END) as avg_error,
                AVG(sp.confidence_score) as avg_confidence
            FROM stock_predictions sp
            LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
            WHERE sp.is_active = true
            AND sp.actual_price IS NOT NULL
            GROUP BY sp.symbol, sm.market, sm.sector
            HAVING COUNT(sp.id) >= 5
            ORDER BY avg_error ASC
            LIMIT 20;
            """

            cursor.execute(symbol_performance_query)
            symbol_stats = cursor.fetchall()

            best_performers = []
            for symbol, market, sector, predictions, avg_error, avg_confidence in symbol_stats:
                if avg_error is not None and avg_error < 10:
                    best_performers.append({
                        'symbol': symbol,
                        'market': market or 'Unknown',
                        'sector': sector or 'Unknown',
                        'predictions': predictions,
                        'avg_error': round(avg_error, 2),
                        'avg_confidence': round(avg_confidence or 0, 3)
                    })

            results['data_patterns']['best_performing_symbols'] = best_performers[:10]

            if best_performers:
                dominant_markets = {}
                dominant_sectors = {}

                for perf in best_performers:
                    market = perf['market']
                    sector = perf['sector']

                    dominant_markets[market] = dominant_markets.get(market, 0) + 1
                    dominant_sectors[sector] = dominant_sectors.get(sector, 0) + 1

                # Find most represented market and sector in top performers
                top_market = max(dominant_markets.items(), key=lambda x: x[1])
                top_sector = max(dominant_sectors.items(), key=lambda x: x[1])

                results['recommendations'].append(
                    f"Focus on {top_market[0]} market - {top_market[1]} high-performing symbols"
                )
                results['recommendations'].append(
                    f"Prioritize {top_sector[0]} sector - shows consistent accuracy"
                )

        except Exception as e:
            logger.error(f"Error analyzing feature importance: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def generate_model_improvements(self) -> Dict[str, Any]:
        """Generate specific recommendations for model improvements"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'improvement_strategies': {},
            'data_quality_issues': [],
            'enhancement_priorities': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Check data freshness and coverage
            data_quality_query = """
            SELECT
                'price_data_coverage' as metric,
                COUNT(DISTINCT symbol) as value,
                'symbols_with_recent_data' as description
            FROM stock_prices
            WHERE date >= CURRENT_DATE - INTERVAL '7 days'

            UNION ALL

            SELECT
                'prediction_coverage' as metric,
                COUNT(DISTINCT symbol) as value,
                'symbols_with_predictions' as description
            FROM stock_predictions
            WHERE prediction_date >= CURRENT_DATE
            AND is_active = true

            UNION ALL

            SELECT
                'stale_predictions' as metric,
                COUNT(*) as value,
                'predictions_older_than_30_days' as description
            FROM stock_predictions
            WHERE created_at < CURRENT_DATE - INTERVAL '30 days'
            AND is_active = true;
            """

            cursor.execute(data_quality_query)
            quality_metrics = cursor.fetchall()

            for metric, value, description in quality_metrics:
                results['improvement_strategies'][metric] = {
                    'value': value,
                    'description': description
                }

                if metric == 'stale_predictions' and value > 100:
                    results['data_quality_issues'].append(
                        f"Found {value} stale predictions - consider cleanup and refresh"
                    )

            # Analyze model diversity and bias
            model_diversity_query = """
            SELECT
                model_type,
                COUNT(DISTINCT symbol) as symbol_coverage,
                COUNT(*) as total_predictions,
                AVG(prediction_horizon) as avg_horizon
            FROM stock_predictions
            WHERE is_active = true
            AND prediction_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY model_type
            ORDER BY total_predictions DESC;
            """

            cursor.execute(model_diversity_query)
            model_stats = cursor.fetchall()

            model_coverage = {}
            total_symbols_covered = set()

            for model_type, symbol_count, predictions, avg_horizon in model_stats:
                model_coverage[model_type] = {
                    'symbol_coverage': symbol_count,
                    'total_predictions': predictions,
                    'avg_horizon': round(avg_horizon or 0, 1)
                }

                # Add to covered symbols tracking
                cursor.execute("""
                SELECT DISTINCT symbol
                FROM stock_predictions
                WHERE model_type = %s AND is_active = true
                """, (model_type,))

                symbols = cursor.fetchall()
                for (symbol,) in symbols:
                    total_symbols_covered.add(symbol)

            results['improvement_strategies']['model_coverage'] = model_coverage
            results['improvement_strategies']['total_symbols_covered'] = len(total_symbols_covered)

            # Enhancement priorities based on analysis
            enhancement_priorities = []

            # Priority 1: Improve low-performing models
            for model_type, stats in model_coverage.items():
                if stats['symbol_coverage'] < 50:
                    enhancement_priorities.append({
                        'priority': 'high',
                        'action': f'Expand {model_type} model coverage to more symbols',
                        'current_coverage': stats['symbol_coverage'],
                        'target': 'Cover at least 100 high-volume symbols'
                    })

            # Priority 2: Enhance prediction horizons
            short_term_models = [m for m, s in model_coverage.items() if s['avg_horizon'] <= 3]
            long_term_models = [m for m, s in model_coverage.items() if s['avg_horizon'] >= 7]

            if len(short_term_models) > len(long_term_models):
                enhancement_priorities.append({
                    'priority': 'medium',
                    'action': 'Develop more long-term prediction models (7+ days)',
                    'rationale': 'Currently skewed toward short-term predictions'
                })

            # Priority 3: Data quality improvements
            if len(results['data_quality_issues']) > 0:
                enhancement_priorities.append({
                    'priority': 'high',
                    'action': 'Address data quality issues',
                    'issues': results['data_quality_issues']
                })

            results['enhancement_priorities'] = enhancement_priorities

        except Exception as e:
            logger.error(f"Error generating model improvements: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def create_model_optimization_plan(self) -> Dict[str, Any]:
        """Create comprehensive optimization plan for ML models"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'optimization_plan': {},
            'implementation_steps': [],
            'success_metrics': {},
            'status': 'success'
        }

        try:
            # Get analysis results
            logger.info("Analyzing current prediction accuracy...")
            accuracy_analysis = self.analyze_prediction_accuracy()

            logger.info("Analyzing feature importance...")
            feature_analysis = self.analyze_feature_importance()

            logger.info("Generating improvement recommendations...")
            improvement_analysis = self.generate_model_improvements()

            # Compile optimization plan
            results['optimization_plan'] = {
                'current_performance': accuracy_analysis.get('overall_metrics', {}),
                'model_breakdown': accuracy_analysis.get('model_analysis', {}),
                'best_practices': feature_analysis.get('data_patterns', {}),
                'improvement_areas': improvement_analysis.get('enhancement_priorities', [])
            }

            # Create implementation steps
            implementation_steps = []

            # Step 1: Data Quality
            implementation_steps.append({
                'step': 1,
                'title': 'Data Quality Enhancement',
                'actions': [
                    'Clean up stale predictions (>30 days old)',
                    'Ensure all active symbols have recent price data',
                    'Validate prediction accuracy calculations',
                    'Implement data freshness monitoring'
                ],
                'timeline': '1-2 weeks',
                'priority': 'high'
            })

            # Step 2: Model Performance Analysis
            implementation_steps.append({
                'step': 2,
                'title': 'Model Performance Optimization',
                'actions': [
                    'Identify and improve low-performing models',
                    'Expand coverage of high-performing model types',
                    'Balance short-term vs long-term prediction horizons',
                    'Implement ensemble methods for better accuracy'
                ],
                'timeline': '2-3 weeks',
                'priority': 'high'
            })

            # Step 3: Feature Engineering
            implementation_steps.append({
                'step': 3,
                'title': 'Advanced Feature Engineering',
                'actions': [
                    'Add technical indicators (RSI, MACD, Bollinger Bands)',
                    'Include market sentiment data',
                    'Implement sector-specific features',
                    'Add volume-based indicators'
                ],
                'timeline': '3-4 weeks',
                'priority': 'medium'
            })

            # Step 4: Model Diversification
            implementation_steps.append({
                'step': 4,
                'title': 'Model Architecture Enhancement',
                'actions': [
                    'Implement transformer-based models',
                    'Add gradient boosting models (XGBoost, LightGBM)',
                    'Develop sector-specific models',
                    'Create volatility-aware models'
                ],
                'timeline': '4-6 weeks',
                'priority': 'medium'
            })

            # Step 5: Validation and Monitoring
            implementation_steps.append({
                'step': 5,
                'title': 'Validation and Continuous Monitoring',
                'actions': [
                    'Implement cross-validation frameworks',
                    'Set up automated model performance tracking',
                    'Create A/B testing for model comparison',
                    'Establish model retraining schedules'
                ],
                'timeline': '2-3 weeks',
                'priority': 'high'
            })

            results['implementation_steps'] = implementation_steps

            # Define success metrics
            results['success_metrics'] = {
                'primary_targets': {
                    'overall_accuracy': {
                        'current': 'Variable by model',
                        'target': '<8% average prediction error',
                        'measurement': 'Mean Absolute Percentage Error (MAPE)'
                    },
                    'model_coverage': {
                        'current': accuracy_analysis.get('overall_metrics', {}).get('unique_symbols', 0),
                        'target': '500+ actively predicted symbols',
                        'measurement': 'Count of symbols with recent predictions'
                    },
                    'prediction_confidence': {
                        'current': accuracy_analysis.get('overall_metrics', {}).get('system_avg_confidence', 0),
                        'target': '>0.75 average confidence',
                        'measurement': 'Average confidence score across all models'
                    }
                },
                'secondary_targets': {
                    'data_freshness': {
                        'target': '95% of predictions based on data <24h old',
                        'measurement': 'Percentage of predictions with fresh underlying data'
                    },
                    'model_diversity': {
                        'target': '5+ distinct model types in production',
                        'measurement': 'Count of active model architectures'
                    },
                    'validation_rate': {
                        'target': '80% of predictions validated with actual outcomes',
                        'measurement': 'Percentage of predictions with actual_price data'
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error creating optimization plan: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def run_full_ml_enhancement(self) -> Dict[str, Any]:
        """Run complete ML model enhancement analysis"""
        logger.info("🤖 Starting ML model enhancement analysis...")

        full_results = {
            'timestamp': datetime.now().isoformat(),
            'analyses': {},
            'optimization_plan': {},
            'overall_status': 'success',
            'summary': {}
        }

        try:
            # Run all analyses
            logger.info("Step 1/4: Analyzing prediction accuracy...")
            full_results['analyses']['accuracy'] = self.analyze_prediction_accuracy()

            logger.info("Step 2/4: Analyzing feature importance...")
            full_results['analyses']['features'] = self.analyze_feature_importance()

            logger.info("Step 3/4: Generating improvement recommendations...")
            full_results['analyses']['improvements'] = self.generate_model_improvements()

            logger.info("Step 4/4: Creating optimization plan...")
            full_results['optimization_plan'] = self.create_model_optimization_plan()

            # Generate summary
            total_recommendations = 0
            failed_analyses = 0

            for analysis_name, analysis_result in full_results['analyses'].items():
                if analysis_result.get('status') == 'failed':
                    failed_analyses += 1
                    full_results['overall_status'] = 'partial_failure'

                if 'recommendations' in analysis_result:
                    total_recommendations += len(analysis_result['recommendations'])

            full_results['summary'] = {
                'total_recommendations': total_recommendations,
                'failed_analyses': failed_analyses,
                'analyses_completed': len(full_results['analyses']),
                'optimization_plan_created': full_results['optimization_plan'].get('status') == 'success'
            }

            if failed_analyses > 0:
                logger.warning(f"⚠️  ML enhancement completed with {failed_analyses} failed analyses")
            else:
                logger.info("✅ ML model enhancement analysis completed successfully!")

        except Exception as e:
            logger.error(f"Error in ML enhancement: {e}")
            full_results['status'] = 'failed'
            full_results['error'] = str(e)

        return full_results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='ML Model Enhancer')
    parser.add_argument('--accuracy', action='store_true', help='Analyze prediction accuracy only')
    parser.add_argument('--features', action='store_true', help='Analyze feature importance only')
    parser.add_argument('--improvements', action='store_true', help='Generate improvement recommendations only')
    parser.add_argument('--plan', action='store_true', help='Create optimization plan only')
    parser.add_argument('--full', action='store_true', help='Run full ML enhancement analysis')

    args = parser.parse_args()

    enhancer = MLModelEnhancer()

    if args.accuracy:
        result = enhancer.analyze_prediction_accuracy()
        print(json.dumps(result, indent=2, default=decimal_to_float))
    elif args.features:
        result = enhancer.analyze_feature_importance()
        print(json.dumps(result, indent=2, default=decimal_to_float))
    elif args.improvements:
        result = enhancer.generate_model_improvements()
        print(json.dumps(result, indent=2, default=decimal_to_float))
    elif args.plan:
        result = enhancer.create_model_optimization_plan()
        print(json.dumps(result, indent=2, default=decimal_to_float))
    elif args.full:
        result = enhancer.run_full_ml_enhancement()
        print(json.dumps(result, indent=2, default=decimal_to_float))
    else:
        # Default: run full enhancement
        result = enhancer.run_full_ml_enhancement()
        print(json.dumps(result, indent=2, default=decimal_to_float))

if __name__ == "__main__":
    main()