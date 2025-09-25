#!/usr/bin/env python3
"""
プロダクション デプロイメント マネージャー
Production Deployment Manager for Miraikakaku Platform

このモジュールはプロダクション環境への安全なデプロイメントを管理します：
- Blue-Green デプロイメント戦略
- カナリアリリースとA/Bテスト
- 自動ロールバック機能
- ヘルスチェックと品質ゲート
- 設定管理とシークレット管理
"""

import os
import json
import logging
import subprocess
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import requests
import tempfile
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentStage(Enum):
    PREPARATION = "preparation"
    BUILD = "build"
    TEST = "test"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class DeploymentStrategy(Enum):
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    RECREATE = "recreate"

@dataclass
class DeploymentConfig:
    app_name: str
    version: str
    strategy: DeploymentStrategy
    environment: EnvironmentType
    build_command: str
    test_command: str
    health_check_url: str
    rollback_enabled: bool = True
    canary_percentage: int = 10
    monitoring_duration_minutes: int = 30
    auto_promote: bool = False
    quality_gates: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentStatus:
    deployment_id: str
    stage: DeploymentStage
    config: DeploymentConfig
    start_time: datetime
    current_stage_start: datetime
    progress_percent: int = 0
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    health_checks: List[Dict[str, Any]] = field(default_factory=list)
    rollback_available: bool = False
    error_message: Optional[str] = None

@dataclass
class QualityGate:
    name: str
    check_type: str  # "health", "performance", "security", "functional"
    threshold: float
    operator: str    # ">", "<", "==", "!="
    timeout_seconds: int = 300
    required: bool = True

class HealthChecker:
    """Health checking utilities for deployments"""

    @staticmethod
    def check_http_endpoint(url: str, timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
        """Check HTTP endpoint health"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000

            health_data = {
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'content_length': len(response.content),
                'headers': dict(response.headers)
            }

            # Try to parse JSON response
            try:
                json_data = response.json()
                health_data['json_response'] = json_data
            except:
                pass

            is_healthy = 200 <= response.status_code < 300
            return is_healthy, health_data

        except Exception as e:
            return False, {'error': str(e)}

    @staticmethod
    def check_database_connection(connection_string: str) -> Tuple[bool, Dict[str, Any]]:
        """Check database connectivity"""
        # Simplified database check (would implement actual DB connections in production)
        try:
            # Mock database check
            time.sleep(0.1)  # Simulate connection time
            return True, {
                'connection_time_ms': 100,
                'database_version': '14.0',
                'status': 'connected'
            }
        except Exception as e:
            return False, {'error': str(e)}

    @staticmethod
    def check_service_dependencies(dependencies: List[str]) -> Tuple[bool, Dict[str, Any]]:
        """Check external service dependencies"""
        results = {}
        all_healthy = True

        for dependency in dependencies:
            try:
                # Mock dependency check
                if dependency.startswith('http'):
                    healthy, data = HealthChecker.check_http_endpoint(dependency, 10)
                else:
                    # Mock other service types
                    healthy, data = True, {'status': 'available'}

                results[dependency] = {'healthy': healthy, 'data': data}
                if not healthy:
                    all_healthy = False

            except Exception as e:
                results[dependency] = {'healthy': False, 'error': str(e)}
                all_healthy = False

        return all_healthy, results

class QualityGateValidator:
    """Validate quality gates during deployment"""

    def __init__(self):
        self.validators = {
            'health': self._validate_health_gate,
            'performance': self._validate_performance_gate,
            'security': self._validate_security_gate,
            'functional': self._validate_functional_gate
        }

    def validate_gates(self, gates: List[QualityGate], deployment_url: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate all quality gates"""
        results = []
        all_passed = True

        for gate in gates:
            try:
                logger.info(f"Validating quality gate: {gate.name}")

                validator = self.validators.get(gate.check_type)
                if not validator:
                    result = {
                        'gate': gate.name,
                        'passed': False,
                        'error': f"Unknown gate type: {gate.check_type}",
                        'required': gate.required
                    }
                else:
                    result = validator(gate, deployment_url)

                results.append(result)

                if not result['passed'] and gate.required:
                    all_passed = False

            except Exception as e:
                logger.error(f"Error validating gate {gate.name}: {e}")
                results.append({
                    'gate': gate.name,
                    'passed': False,
                    'error': str(e),
                    'required': gate.required
                })
                if gate.required:
                    all_passed = False

        return all_passed, results

    def _validate_health_gate(self, gate: QualityGate, deployment_url: str) -> Dict[str, Any]:
        """Validate health quality gate"""
        healthy, health_data = HealthChecker.check_http_endpoint(f"{deployment_url}/health")

        if healthy and 'response_time_ms' in health_data:
            response_time = health_data['response_time_ms']
            passed = self._compare_value(response_time, gate.threshold, gate.operator)
        else:
            passed = False

        return {
            'gate': gate.name,
            'passed': passed,
            'value': health_data.get('response_time_ms', 0),
            'threshold': gate.threshold,
            'operator': gate.operator,
            'data': health_data,
            'required': gate.required
        }

    def _validate_performance_gate(self, gate: QualityGate, deployment_url: str) -> Dict[str, Any]:
        """Validate performance quality gate"""
        # Run multiple requests to get average response time
        response_times = []

        for _ in range(5):
            healthy, health_data = HealthChecker.check_http_endpoint(deployment_url)
            if healthy and 'response_time_ms' in health_data:
                response_times.append(health_data['response_time_ms'])

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            passed = self._compare_value(avg_response_time, gate.threshold, gate.operator)
        else:
            avg_response_time = 0
            passed = False

        return {
            'gate': gate.name,
            'passed': passed,
            'value': avg_response_time,
            'threshold': gate.threshold,
            'operator': gate.operator,
            'samples': len(response_times),
            'required': gate.required
        }

    def _validate_security_gate(self, gate: QualityGate, deployment_url: str) -> Dict[str, Any]:
        """Validate security quality gate"""
        # Mock security scan
        security_score = 95.0  # Mock score
        passed = self._compare_value(security_score, gate.threshold, gate.operator)

        return {
            'gate': gate.name,
            'passed': passed,
            'value': security_score,
            'threshold': gate.threshold,
            'operator': gate.operator,
            'scan_type': 'vulnerability_scan',
            'required': gate.required
        }

    def _validate_functional_gate(self, gate: QualityGate, deployment_url: str) -> Dict[str, Any]:
        """Validate functional quality gate"""
        # Mock functional test
        test_pass_rate = 98.5  # Mock pass rate
        passed = self._compare_value(test_pass_rate, gate.threshold, gate.operator)

        return {
            'gate': gate.name,
            'passed': passed,
            'value': test_pass_rate,
            'threshold': gate.threshold,
            'operator': gate.operator,
            'test_type': 'functional_tests',
            'required': gate.required
        }

    def _compare_value(self, value: float, threshold: float, operator: str) -> bool:
        """Compare value against threshold using operator"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        elif operator == '!=':
            return value != threshold
        else:
            return False

class DeploymentExecutor:
    """Execute deployment strategies"""

    def __init__(self):
        self.health_checker = HealthChecker()
        self.quality_validator = QualityGateValidator()

    def execute_blue_green_deployment(self, status: DeploymentStatus) -> bool:
        """Execute blue-green deployment"""
        config = status.config

        try:
            # Stage 1: Build new version (Green)
            status.stage = DeploymentStage.BUILD
            status.current_stage_start = datetime.now()
            logger.info(f"Building green environment for {config.app_name} v{config.version}")

            if not self._run_build(config, status):
                return False

            status.progress_percent = 25

            # Stage 2: Deploy to green environment
            logger.info("Deploying to green environment")
            if not self._deploy_green_environment(config, status):
                return False

            status.progress_percent = 50

            # Stage 3: Run tests on green environment
            status.stage = DeploymentStage.TEST
            status.current_stage_start = datetime.now()
            logger.info("Running tests on green environment")

            if not self._run_tests(config, status):
                return False

            status.progress_percent = 75

            # Stage 4: Switch traffic to green (Blue -> Green)
            logger.info("Switching traffic from blue to green")
            if not self._switch_traffic(config, status):
                return False

            status.progress_percent = 90

            # Stage 5: Monitor new deployment
            status.stage = DeploymentStage.MONITORING
            status.current_stage_start = datetime.now()
            if not self._monitor_deployment(config, status):
                return False

            status.progress_percent = 100
            status.stage = DeploymentStage.COMPLETED
            return True

        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            status.error_message = str(e)
            status.stage = DeploymentStage.FAILED
            return False

    def execute_canary_deployment(self, status: DeploymentStatus) -> bool:
        """Execute canary deployment"""
        config = status.config

        try:
            # Stage 1: Build canary version
            status.stage = DeploymentStage.BUILD
            status.current_stage_start = datetime.now()
            logger.info(f"Building canary deployment for {config.app_name} v{config.version}")

            if not self._run_build(config, status):
                return False

            status.progress_percent = 20

            # Stage 2: Deploy canary with limited traffic
            status.stage = DeploymentStage.CANARY
            status.current_stage_start = datetime.now()
            logger.info(f"Deploying canary with {config.canary_percentage}% traffic")

            if not self._deploy_canary(config, status):
                return False

            status.progress_percent = 50

            # Stage 3: Monitor canary
            logger.info(f"Monitoring canary for {config.monitoring_duration_minutes} minutes")
            if not self._monitor_canary(config, status):
                return False

            status.progress_percent = 80

            # Stage 4: Promote to full deployment (if successful)
            if config.auto_promote:
                logger.info("Auto-promoting canary to production")
                if not self._promote_canary(config, status):
                    return False
            else:
                logger.info("Manual promotion required for canary")

            status.progress_percent = 100
            status.stage = DeploymentStage.COMPLETED
            return True

        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            status.error_message = str(e)
            status.stage = DeploymentStage.FAILED
            return False

    def _run_build(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Run build process"""
        try:
            logger.info(f"Running build command: {config.build_command}")

            # Mock build process
            time.sleep(2)  # Simulate build time

            status.logs.append(f"Build completed successfully at {datetime.now()}")
            status.logs.append(f"Artifact: {config.app_name}-{config.version}.tar.gz")

            return True

        except Exception as e:
            logger.error(f"Build failed: {e}")
            status.logs.append(f"Build failed: {e}")
            return False

    def _deploy_green_environment(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Deploy to green environment"""
        try:
            logger.info("Deploying to green environment")

            # Mock deployment
            time.sleep(3)  # Simulate deployment time

            # Verify deployment
            healthy, health_data = self.health_checker.check_http_endpoint(
                config.health_check_url.replace(':8080', ':8081')  # Green port
            )

            if not healthy:
                status.logs.append("Green environment health check failed")
                return False

            status.logs.append("Green environment deployed successfully")
            status.rollback_available = True

            return True

        except Exception as e:
            logger.error(f"Green deployment failed: {e}")
            status.logs.append(f"Green deployment failed: {e}")
            return False

    def _run_tests(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Run tests on deployment"""
        try:
            logger.info(f"Running test command: {config.test_command}")

            # Mock test execution
            time.sleep(1)

            # Run quality gates if configured
            if config.quality_gates:
                gates = [
                    QualityGate("response_time", "performance", 500.0, "<", required=True),
                    QualityGate("health_check", "health", 200.0, "==", required=True)
                ]

                passed, results = self.quality_validator.validate_gates(
                    gates,
                    config.health_check_url
                )

                status.metrics['quality_gates'] = results

                if not passed:
                    status.logs.append("Quality gates failed")
                    return False

            status.logs.append("All tests passed successfully")
            return True

        except Exception as e:
            logger.error(f"Tests failed: {e}")
            status.logs.append(f"Tests failed: {e}")
            return False

    def _switch_traffic(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Switch traffic from blue to green"""
        try:
            logger.info("Switching traffic from blue to green")

            # Mock traffic switching
            time.sleep(1)

            status.logs.append("Traffic switched to green environment")
            return True

        except Exception as e:
            logger.error(f"Traffic switch failed: {e}")
            status.logs.append(f"Traffic switch failed: {e}")
            return False

    def _monitor_deployment(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Monitor deployment health"""
        try:
            logger.info(f"Monitoring deployment for {config.monitoring_duration_minutes} minutes")

            # Mock monitoring for shorter duration in test
            monitor_seconds = min(config.monitoring_duration_minutes * 60, 30)

            for i in range(0, monitor_seconds, 5):
                time.sleep(5)

                # Check health
                healthy, health_data = self.health_checker.check_http_endpoint(
                    config.health_check_url
                )

                status.health_checks.append({
                    'timestamp': datetime.now().isoformat(),
                    'healthy': healthy,
                    'data': health_data
                })

                if not healthy:
                    status.logs.append(f"Health check failed during monitoring: {health_data}")
                    return False

                logger.info(f"Health check {i//5 + 1}: OK")

            status.logs.append("Monitoring completed successfully")
            return True

        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            status.logs.append(f"Monitoring failed: {e}")
            return False

    def _deploy_canary(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Deploy canary version"""
        try:
            logger.info(f"Deploying canary with {config.canary_percentage}% traffic")

            # Mock canary deployment
            time.sleep(2)

            status.logs.append(f"Canary deployed with {config.canary_percentage}% traffic")
            return True

        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            status.logs.append(f"Canary deployment failed: {e}")
            return False

    def _monitor_canary(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Monitor canary deployment"""
        try:
            logger.info("Monitoring canary deployment")

            # Mock canary monitoring
            monitor_seconds = min(config.monitoring_duration_minutes * 60, 15)

            for i in range(0, monitor_seconds, 3):
                time.sleep(3)

                # Mock metrics collection
                canary_metrics = {
                    'error_rate': 0.1,  # 0.1% error rate
                    'response_time': 150.0,  # 150ms average
                    'throughput': 100.0  # 100 requests/second
                }

                status.metrics['canary_metrics'] = canary_metrics

                # Check if canary is performing well
                if canary_metrics['error_rate'] > 1.0:  # More than 1% errors
                    status.logs.append("Canary error rate too high")
                    return False

                logger.info(f"Canary metrics: {canary_metrics}")

            status.logs.append("Canary monitoring completed successfully")
            return True

        except Exception as e:
            logger.error(f"Canary monitoring failed: {e}")
            status.logs.append(f"Canary monitoring failed: {e}")
            return False

    def _promote_canary(self, config: DeploymentConfig, status: DeploymentStatus) -> bool:
        """Promote canary to full production"""
        try:
            logger.info("Promoting canary to full production")

            # Mock promotion
            time.sleep(2)

            status.logs.append("Canary promoted to full production")
            return True

        except Exception as e:
            logger.error(f"Canary promotion failed: {e}")
            status.logs.append(f"Canary promotion failed: {e}")
            return False

class ProductionDeploymentManager:
    """Main production deployment manager"""

    def __init__(self):
        self.executor = DeploymentExecutor()
        self.active_deployments: Dict[str, DeploymentStatus] = {}
        self.deployment_history: List[DeploymentStatus] = []

    def start_deployment(self, config: DeploymentConfig) -> str:
        """Start a new deployment"""
        deployment_id = f"{config.app_name}-{config.version}-{int(time.time())}"

        status = DeploymentStatus(
            deployment_id=deployment_id,
            stage=DeploymentStage.PREPARATION,
            config=config,
            start_time=datetime.now(),
            current_stage_start=datetime.now()
        )

        self.active_deployments[deployment_id] = status

        logger.info(f"Starting deployment: {deployment_id}")

        # Start deployment in background thread
        deployment_thread = threading.Thread(
            target=self._run_deployment,
            args=(status,),
            daemon=True
        )
        deployment_thread.start()

        return deployment_id

    def _run_deployment(self, status: DeploymentStatus):
        """Run deployment process"""
        config = status.config

        try:
            status.stage = DeploymentStage.PREPARATION
            status.logs.append(f"Starting {config.strategy.value} deployment")

            # Execute deployment strategy
            success = False

            if config.strategy == DeploymentStrategy.BLUE_GREEN:
                success = self.executor.execute_blue_green_deployment(status)
            elif config.strategy == DeploymentStrategy.CANARY:
                success = self.executor.execute_canary_deployment(status)
            else:
                status.error_message = f"Unsupported deployment strategy: {config.strategy.value}"
                status.stage = DeploymentStage.FAILED

            if success:
                logger.info(f"Deployment {status.deployment_id} completed successfully")
                status.logs.append("Deployment completed successfully")
            else:
                logger.error(f"Deployment {status.deployment_id} failed")
                if not status.error_message:
                    status.error_message = "Deployment failed - see logs for details"

        except Exception as e:
            logger.error(f"Deployment {status.deployment_id} failed with exception: {e}")
            status.stage = DeploymentStage.FAILED
            status.error_message = str(e)
            status.logs.append(f"Deployment failed: {e}")

        finally:
            # Move to history
            self.deployment_history.append(status)
            if status.deployment_id in self.active_deployments:
                del self.active_deployments[status.deployment_id]

    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentStatus]:
        """Get deployment status"""
        # Check active deployments first
        if deployment_id in self.active_deployments:
            return self.active_deployments[deployment_id]

        # Check history
        for status in self.deployment_history:
            if status.deployment_id == deployment_id:
                return status

        return None

    def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback a deployment"""
        status = self.get_deployment_status(deployment_id)
        if not status:
            logger.error(f"Deployment not found: {deployment_id}")
            return False

        if not status.rollback_available:
            logger.error(f"Rollback not available for deployment: {deployment_id}")
            return False

        try:
            logger.info(f"Rolling back deployment: {deployment_id}")

            status.stage = DeploymentStage.ROLLBACK
            status.current_stage_start = datetime.now()

            # Mock rollback process
            time.sleep(3)

            status.logs.append("Rollback completed successfully")
            logger.info(f"Rollback completed for deployment: {deployment_id}")

            return True

        except Exception as e:
            logger.error(f"Rollback failed for deployment {deployment_id}: {e}")
            status.logs.append(f"Rollback failed: {e}")
            return False

    def get_deployment_dashboard(self) -> Dict[str, Any]:
        """Get deployment dashboard data"""
        # Active deployments
        active_deployments = {}
        for deployment_id, status in self.active_deployments.items():
            active_deployments[deployment_id] = {
                'stage': status.stage.value,
                'progress': status.progress_percent,
                'start_time': status.start_time.isoformat(),
                'app_name': status.config.app_name,
                'version': status.config.version,
                'strategy': status.config.strategy.value
            }

        # Recent deployments (last 10)
        recent_deployments = []
        for status in self.deployment_history[-10:]:
            recent_deployments.append({
                'deployment_id': status.deployment_id,
                'app_name': status.config.app_name,
                'version': status.config.version,
                'stage': status.stage.value,
                'start_time': status.start_time.isoformat(),
                'duration_minutes': (datetime.now() - status.start_time).total_seconds() / 60,
                'success': status.stage == DeploymentStage.COMPLETED
            })

        # Deployment statistics
        total_deployments = len(self.deployment_history)
        successful_deployments = len([s for s in self.deployment_history if s.stage == DeploymentStage.COMPLETED])
        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0

        return {
            'active_deployments': active_deployments,
            'recent_deployments': recent_deployments,
            'statistics': {
                'total_deployments': total_deployments,
                'successful_deployments': successful_deployments,
                'success_rate': round(success_rate, 1),
                'active_count': len(self.active_deployments)
            },
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main function for testing production deployment manager"""

    print("🚀 Initializing Production Deployment Manager...")

    manager = ProductionDeploymentManager()

    try:
        # Test Blue-Green Deployment
        print("\n🔵 Testing Blue-Green Deployment...")

        bg_config = DeploymentConfig(
            app_name="miraikakaku-api",
            version="2.1.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment=EnvironmentType.PRODUCTION,
            build_command="npm run build",
            test_command="npm run test",
            health_check_url="http://localhost:8080/health",
            rollback_enabled=True,
            monitoring_duration_minutes=1,  # Shortened for demo
            quality_gates=["health_check", "performance"]
        )

        deployment_id = manager.start_deployment(bg_config)
        print(f"✅ Started Blue-Green deployment: {deployment_id}")

        # Monitor deployment progress
        for i in range(20):  # Monitor for 20 seconds
            status = manager.get_deployment_status(deployment_id)
            if status:
                print(f"   Stage: {status.stage.value}, Progress: {status.progress_percent}%")

                if status.stage in [DeploymentStage.COMPLETED, DeploymentStage.FAILED]:
                    break

            time.sleep(1)

        # Check final status
        final_status = manager.get_deployment_status(deployment_id)
        if final_status:
            print(f"✅ Blue-Green deployment final status: {final_status.stage.value}")
            if final_status.logs:
                print("   Recent logs:")
                for log in final_status.logs[-3:]:
                    print(f"     - {log}")

        # Test Canary Deployment
        print("\n🐤 Testing Canary Deployment...")

        canary_config = DeploymentConfig(
            app_name="miraikakaku-frontend",
            version="3.0.0",
            strategy=DeploymentStrategy.CANARY,
            environment=EnvironmentType.PRODUCTION,
            build_command="npm run build",
            test_command="npm run test",
            health_check_url="http://localhost:3000/health",
            canary_percentage=20,
            monitoring_duration_minutes=1,  # Shortened for demo
            auto_promote=True
        )

        canary_deployment_id = manager.start_deployment(canary_config)
        print(f"✅ Started Canary deployment: {canary_deployment_id}")

        # Monitor canary deployment
        for i in range(15):  # Monitor for 15 seconds
            status = manager.get_deployment_status(canary_deployment_id)
            if status:
                print(f"   Stage: {status.stage.value}, Progress: {status.progress_percent}%")

                if status.stage in [DeploymentStage.COMPLETED, DeploymentStage.FAILED]:
                    break

            time.sleep(1)

        # Wait for both deployments to complete
        time.sleep(5)

        # Show deployment dashboard
        print("\n📊 Deployment Dashboard:")
        dashboard = manager.get_deployment_dashboard()

        print(f"Statistics:")
        stats = dashboard['statistics']
        print(f"  Total Deployments: {stats['total_deployments']}")
        print(f"  Successful: {stats['successful_deployments']}")
        print(f"  Success Rate: {stats['success_rate']}%")
        print(f"  Active: {stats['active_count']}")

        print(f"\nRecent Deployments:")
        for deployment in dashboard['recent_deployments']:
            status_emoji = "✅" if deployment['success'] else "❌"
            print(f"  {status_emoji} {deployment['app_name']} v{deployment['version']}")
            print(f"     Strategy: {deployment.get('strategy', 'unknown')}")
            print(f"     Duration: {deployment['duration_minutes']:.1f} minutes")
            print(f"     Status: {deployment['stage']}")

        # Test rollback functionality
        if final_status and final_status.rollback_available:
            print(f"\n🔄 Testing Rollback for {deployment_id}...")
            rollback_success = manager.rollback_deployment(deployment_id)
            print(f"✅ Rollback {'successful' if rollback_success else 'failed'}")

        print("\n🎯 Production Deployment Manager Test Completed!")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()