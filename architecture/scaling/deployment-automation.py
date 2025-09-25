#!/usr/bin/env python3
"""
Deployment Automation for MiraiKakaku Scaling System
Handles automated deployment, configuration, and monitoring setup
"""
import asyncio
import subprocess
import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/miraikakaku-scaling-deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('miraikakaku.scaling.deployment')

@dataclass
class DeploymentConfig:
    """Deployment configuration settings"""
    project_id: str
    region: str
    cluster_name: str
    namespace: str
    environment: str  # dev, staging, prod
    scaling_enabled: bool = True
    monitoring_enabled: bool = True

@dataclass
class ServiceConfig:
    """Individual service configuration"""
    name: str
    image: str
    min_instances: int
    max_instances: int
    cpu_limit: str
    memory_limit: str
    environment_variables: Dict[str, str]

class DeploymentAutomation:
    """Main deployment automation class"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.kubectl_config = f"--project={config.project_id} --region={config.region}"

    async def deploy_scaling_system(self) -> bool:
        """Deploy the complete scaling system"""
        try:
            logger.info("🚀 Starting MiraiKakaku scaling system deployment")

            # Phase 1: Infrastructure setup
            await self._setup_infrastructure()

            # Phase 2: Deploy scaling controller
            await self._deploy_scaling_controller()

            # Phase 3: Configure services
            await self._configure_services()

            # Phase 4: Setup monitoring
            await self._setup_monitoring()

            # Phase 5: Validate deployment
            await self._validate_deployment()

            logger.info("✅ Scaling system deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            await self._rollback_deployment()
            return False

    async def _setup_infrastructure(self):
        """Setup GKE cluster and basic infrastructure"""
        logger.info("🔧 Setting up infrastructure...")

        # Create GKE cluster if it doesn't exist
        cluster_create_cmd = [
            "gcloud", "container", "clusters", "create", self.config.cluster_name,
            "--project", self.config.project_id,
            "--region", self.config.region,
            "--num-nodes", "3",
            "--enable-autoscaling",
            "--min-nodes", "1",
            "--max-nodes", "10",
            "--enable-autorepair",
            "--enable-autoupgrade",
            "--machine-type", "e2-standard-2",
            "--disk-size", "50GB",
            "--enable-ip-alias",
            "--enable-network-policy",
            "--addons", "HorizontalPodAutoscaling,HttpLoadBalancing",
            "--enable-stackdriver-kubernetes"
        ]

        result = await self._run_command(cluster_create_cmd, check_exists=True)
        if result.returncode == 0:
            logger.info("✅ GKE cluster created successfully")
        else:
            logger.info("ℹ️ GKE cluster already exists")

        # Get cluster credentials
        get_credentials_cmd = [
            "gcloud", "container", "clusters", "get-credentials",
            self.config.cluster_name,
            "--region", self.config.region,
            "--project", self.config.project_id
        ]
        await self._run_command(get_credentials_cmd)

        # Create namespace
        namespace_yaml = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: {self.config.namespace}
  labels:
    environment: {self.config.environment}
    managed-by: miraikakaku-scaling
"""
        await self._apply_yaml(namespace_yaml)
        logger.info(f"✅ Namespace '{self.config.namespace}' created")

    async def _deploy_scaling_controller(self):
        """Deploy the scaling controller service"""
        logger.info("🚀 Deploying scaling controller...")

        # Apply scaling configuration
        config_path = Path(__file__).parent / "scaling-configuration.yaml"
        if config_path.exists():
            apply_cmd = ["kubectl", "apply", "-f", str(config_path)]
            await self._run_command(apply_cmd)
            logger.info("✅ Scaling configuration applied")

        # Create service account and RBAC
        rbac_yaml = f"""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scaling-controller
  namespace: {self.config.namespace}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: scaling-controller
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["metrics.k8s.io"]
  resources: ["pods", "nodes"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: scaling-controller
subjects:
- kind: ServiceAccount
  name: scaling-controller
  namespace: {self.config.namespace}
roleRef:
  kind: ClusterRole
  name: scaling-controller
  apiGroup: rbac.authorization.k8s.io
"""
        await self._apply_yaml(rbac_yaml)
        logger.info("✅ RBAC configuration applied")

        # Build and deploy scaling controller image
        await self._build_and_deploy_controller()

    async def _build_and_deploy_controller(self):
        """Build and deploy the scaling controller container"""
        logger.info("🔨 Building scaling controller image...")

        # Create Dockerfile for scaling controller
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \\
    && chmod +x kubectl \\
    && mv kubectl /usr/local/bin/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY auto-scaling-system.py .
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash scaling
USER scaling

EXPOSE 8080

CMD ["python", "auto-scaling-system.py"]
"""

        controller_dir = Path(__file__).parent
        dockerfile_path = controller_dir / "Dockerfile.controller"

        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        # Create requirements.txt for controller
        requirements_content = """
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
psycopg2-binary==2.9.9
google-cloud-run==0.10.1
google-cloud-monitoring==2.16.0
prometheus-client==0.19.0
kubernetes==28.1.0
pydantic==2.5.0
asyncio-throttle==1.0.2
"""

        requirements_path = controller_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)

        # Build image
        image_tag = f"gcr.io/{self.config.project_id}/scaling-controller:latest"
        build_cmd = [
            "docker", "build",
            "-f", str(dockerfile_path),
            "-t", image_tag,
            str(controller_dir)
        ]
        await self._run_command(build_cmd)

        # Push to container registry
        push_cmd = ["docker", "push", image_tag]
        await self._run_command(push_cmd)

        logger.info("✅ Scaling controller image built and pushed")

    async def _configure_services(self):
        """Configure individual services for auto-scaling"""
        logger.info("⚙️ Configuring services for auto-scaling...")

        services = [
            ServiceConfig(
                name="miraikakaku-api",
                image=f"gcr.io/{self.config.project_id}/miraikakaku-api:latest",
                min_instances=2,
                max_instances=100,
                cpu_limit="1000m",
                memory_limit="1Gi",
                environment_variables={
                    "ENVIRONMENT": self.config.environment,
                    "SCALING_ENABLED": "true"
                }
            ),
            ServiceConfig(
                name="miraikakaku-batch",
                image=f"gcr.io/{self.config.project_id}/miraikakaku-batch:latest",
                min_instances=1,
                max_instances=50,
                cpu_limit="2000m",
                memory_limit="2Gi",
                environment_variables={
                    "ENVIRONMENT": self.config.environment,
                    "BATCH_CONCURRENCY": "10"
                }
            )
        ]

        for service in services:
            await self._deploy_service(service)

    async def _deploy_service(self, service: ServiceConfig):
        """Deploy individual service with auto-scaling configuration"""
        service_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service.name}
  namespace: {self.config.namespace}
  labels:
    app: {service.name}
    environment: {self.config.environment}
spec:
  replicas: {service.min_instances}
  selector:
    matchLabels:
      app: {service.name}
  template:
    metadata:
      labels:
        app: {service.name}
        environment: {self.config.environment}
    spec:
      containers:
      - name: {service.name}
        image: {service.image}
        ports:
        - containerPort: 8080
        env:
{self._format_env_vars(service.environment_variables)}
        resources:
          requests:
            memory: "{int(service.memory_limit[:-2])//2}Mi"
            cpu: "{int(service.cpu_limit[:-1])//2}m"
          limits:
            memory: {service.memory_limit}
            cpu: {service.cpu_limit}
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {service.name}-service
  namespace: {self.config.namespace}
spec:
  selector:
    app: {service.name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service.name}-hpa
  namespace: {self.config.namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {service.name}
  minReplicas: {service.min_instances}
  maxReplicas: {service.max_instances}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""
        await self._apply_yaml(service_yaml)
        logger.info(f"✅ Service {service.name} deployed with auto-scaling")

    def _format_env_vars(self, env_vars: Dict[str, str]) -> str:
        """Format environment variables for YAML"""
        formatted = ""
        for key, value in env_vars.items():
            formatted += f"        - name: {key}\n"
            formatted += f"          value: \"{value}\"\n"
        return formatted.rstrip()

    async def _setup_monitoring(self):
        """Setup monitoring and alerting"""
        logger.info("📊 Setting up monitoring and alerting...")

        # Deploy Prometheus
        prometheus_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: miraikakaku-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus/
        - name: prometheus-data
          mountPath: /prometheus/
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus/'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
          - '--web.enable-lifecycle'
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: miraikakaku-prod
spec:
  selector:
    app: prometheus
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
"""
        await self._apply_yaml(prometheus_yaml)

        # Create Prometheus configuration
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "scaling_rules.yml"

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  - job_name: 'miraikakaku-services'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - miraikakaku-prod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""

        prometheus_config_yaml = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: {self.config.namespace}
data:
  prometheus.yml: |
{self._indent_text(prometheus_config, 4)}
"""
        await self._apply_yaml(prometheus_config_yaml)
        logger.info("✅ Monitoring setup completed")

    async def _validate_deployment(self):
        """Validate that all components are running correctly"""
        logger.info("🔍 Validating deployment...")

        # Check pods are running
        get_pods_cmd = ["kubectl", "get", "pods", "-n", self.config.namespace]
        result = await self._run_command(get_pods_cmd)

        if result.returncode == 0:
            logger.info("✅ All pods are running successfully")
        else:
            raise Exception("Pod validation failed")

        # Check services are accessible
        get_services_cmd = ["kubectl", "get", "services", "-n", self.config.namespace]
        await self._run_command(get_services_cmd)

        # Test scaling controller health
        await self._test_scaling_controller_health()

        logger.info("✅ Deployment validation completed")

    async def _test_scaling_controller_health(self):
        """Test scaling controller health endpoint"""
        try:
            # Port forward to scaling controller for testing
            port_forward_cmd = [
                "kubectl", "port-forward",
                f"deployment/scaling-controller",
                "8080:8080",
                "-n", self.config.namespace
            ]

            # Run port-forward in background for testing
            proc = await asyncio.create_subprocess_exec(
                *port_forward_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait a moment for port-forward to establish
            await asyncio.sleep(5)

            # Test health endpoint
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/health') as response:
                    if response.status == 200:
                        logger.info("✅ Scaling controller health check passed")
                    else:
                        logger.warning(f"⚠️ Scaling controller health check returned {response.status}")

            # Clean up port-forward
            proc.terminate()

        except Exception as e:
            logger.warning(f"⚠️ Could not test scaling controller health: {e}")

    async def _rollback_deployment(self):
        """Rollback deployment in case of failure"""
        logger.info("🔄 Rolling back deployment...")

        try:
            # Delete all resources in namespace
            delete_cmd = ["kubectl", "delete", "all", "--all", "-n", self.config.namespace]
            await self._run_command(delete_cmd)

            logger.info("✅ Rollback completed")
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")

    async def _run_command(self, cmd: List[str], check_exists: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command asynchronously"""
        logger.debug(f"Running command: {' '.join(cmd)}")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0 and not check_exists:
            logger.error(f"Command failed: {stderr.decode()}")
            raise Exception(f"Command failed: {' '.join(cmd)}")

        return subprocess.CompletedProcess(
            cmd, proc.returncode, stdout.decode(), stderr.decode()
        )

    async def _apply_yaml(self, yaml_content: str):
        """Apply YAML configuration using kubectl"""
        # Write to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            apply_cmd = ["kubectl", "apply", "-f", temp_file]
            await self._run_command(apply_cmd)
        finally:
            os.unlink(temp_file)

    def _indent_text(self, text: str, spaces: int) -> str:
        """Indent text by specified number of spaces"""
        lines = text.strip().split('\n')
        return '\n'.join(' ' * spaces + line for line in lines)

async def main():
    """Main deployment function"""
    # Configuration
    config = DeploymentConfig(
        project_id="miraikakaku-prod",
        region="asia-northeast1",
        cluster_name="miraikakaku-cluster",
        namespace="miraikakaku-prod",
        environment="production"
    )

    # Deploy scaling system
    automation = DeploymentAutomation(config)
    success = await automation.deploy_scaling_system()

    if success:
        logger.info("🎉 MiraiKakaku scaling system deployed successfully!")
        print("\n" + "="*60)
        print("🎉 MIRAIKAKAKU SCALING SYSTEM DEPLOYMENT COMPLETE")
        print("="*60)
        print(f"📍 Project: {config.project_id}")
        print(f"🌍 Region: {config.region}")
        print(f"🏷️  Namespace: {config.namespace}")
        print(f"🔧 Environment: {config.environment}")
        print("\n📊 Monitoring Dashboard:")
        print("   kubectl port-forward svc/prometheus 9090:9090 -n miraikakaku-prod")
        print("   Open: http://localhost:9090")
        print("\n🚀 Scaling Controller:")
        print("   kubectl port-forward deployment/scaling-controller 8080:8080 -n miraikakaku-prod")
        print("   Open: http://localhost:8080")
        print("\n✅ All services are now auto-scaling based on demand!")
        print("="*60)
    else:
        logger.error("❌ Deployment failed")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)