#!/bin/bash

# MiraiKakaku Auto-Scaling System Deployment Script
# Comprehensive deployment automation for production environment

set -e  # Exit on any error

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-miraikakaku-prod}"
REGION="${GCP_REGION:-asia-northeast1}"
CLUSTER_NAME="${CLUSTER_NAME:-miraikakaku-cluster}"
NAMESPACE="${NAMESPACE:-miraikakaku-prod}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found. Please install kubectl."
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker."
        exit 1
    fi

    # Verify gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi

    # Set project
    gcloud config set project $PROJECT_ID
    success "Prerequisites check completed"
}

# Enable required APIs
enable_apis() {
    log "Enabling required Google Cloud APIs..."

    apis=(
        "container.googleapis.com"
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "compute.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done

    success "All required APIs enabled"
}

# Create GKE cluster
create_cluster() {
    log "Creating GKE cluster: $CLUSTER_NAME..."

    # Check if cluster already exists
    if gcloud container clusters describe $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        warning "Cluster $CLUSTER_NAME already exists"
        return 0
    fi

    # Create cluster with optimized configuration
    gcloud container clusters create $CLUSTER_NAME \
        --project=$PROJECT_ID \
        --region=$REGION \
        --num-nodes=3 \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --machine-type=e2-standard-4 \
        --disk-size=100GB \
        --disk-type=pd-ssd \
        --enable-ip-alias \
        --enable-network-policy \
        --enable-shielded-nodes \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,NetworkPolicy \
        --enable-stackdriver-kubernetes \
        --workload-pool=$PROJECT_ID.svc.id.goog \
        --enable-shielded-nodes \
        --maintenance-window-start="2024-01-01T02:00:00Z" \
        --maintenance-window-end="2024-01-01T06:00:00Z" \
        --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SU"

    success "GKE cluster created successfully"
}

# Get cluster credentials
get_credentials() {
    log "Getting cluster credentials..."

    gcloud container clusters get-credentials $CLUSTER_NAME \
        --region=$REGION \
        --project=$PROJECT_ID

    success "Cluster credentials configured"
}

# Create namespace and basic resources
create_namespace() {
    log "Creating namespace: $NAMESPACE..."

    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Label the namespace
    kubectl label namespace $NAMESPACE \
        environment=$ENVIRONMENT \
        managed-by=miraikakaku-scaling \
        --overwrite

    success "Namespace created and labeled"
}

# Deploy scaling configuration
deploy_scaling_config() {
    log "Deploying scaling configuration..."

    # Apply scaling configuration
    if [ -f "architecture/scaling/scaling-configuration.yaml" ]; then
        kubectl apply -f architecture/scaling/scaling-configuration.yaml
        success "Scaling configuration applied"
    else
        error "Scaling configuration file not found"
        exit 1
    fi
}

# Build and push container images
build_images() {
    log "Building and pushing container images..."

    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker

    # Build API image
    log "Building API image..."
    if [ -d "miraikakakuapi" ]; then
        docker build -t gcr.io/$PROJECT_ID/miraikakaku-api:latest ./miraikakakuapi/
        docker push gcr.io/$PROJECT_ID/miraikakaku-api:latest
        success "API image built and pushed"
    fi

    # Build batch image
    log "Building batch image..."
    if [ -d "miraikakakubatch" ]; then
        docker build -t gcr.io/$PROJECT_ID/miraikakaku-batch:latest ./miraikakakubatch/
        docker push gcr.io/$PROJECT_ID/miraikakaku-batch:latest
        success "Batch image built and pushed"
    fi

    # Build frontend image
    log "Building frontend image..."
    if [ -d "miraikakakufront" ]; then
        docker build -t gcr.io/$PROJECT_ID/miraikakaku-frontend:latest ./miraikakakufront/
        docker push gcr.io/$PROJECT_ID/miraikakaku-frontend:latest
        success "Frontend image built and pushed"
    fi

    # Build scaling controller image
    log "Building scaling controller image..."
    cd architecture/scaling

    # Create Dockerfile for scaling controller
    cat > Dockerfile.controller << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \\
    && chmod +x kubectl \\
    && mv kubectl /usr/local/bin/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY auto-scaling-system.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash scaling
USER scaling

EXPOSE 8080

CMD ["python", "auto-scaling-system.py"]
EOF

    # Create requirements.txt
    cat > requirements.txt << EOF
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
aiohttp==3.9.1
EOF

    docker build -f Dockerfile.controller -t gcr.io/$PROJECT_ID/scaling-controller:latest .
    docker push gcr.io/$PROJECT_ID/scaling-controller:latest
    cd ../..

    success "All images built and pushed successfully"
}

# Deploy services with auto-scaling
deploy_services() {
    log "Deploying services with auto-scaling..."

    # Apply service deployments
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: miraikakaku-api
  namespace: $NAMESPACE
  labels:
    app: miraikakaku-api
    environment: $ENVIRONMENT
spec:
  replicas: 2
  selector:
    matchLabels:
      app: miraikakaku-api
  template:
    metadata:
      labels:
        app: miraikakaku-api
        environment: $ENVIRONMENT
    spec:
      containers:
      - name: miraikakaku-api
        image: gcr.io/$PROJECT_ID/miraikakaku-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "$ENVIRONMENT"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: url
              optional: true
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: miraikakaku-api-service
  namespace: $NAMESPACE
spec:
  selector:
    app: miraikakaku-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: miraikakaku-api-hpa
  namespace: $NAMESPACE
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: miraikakaku-api
  minReplicas: 2
  maxReplicas: 100
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
EOF

    success "API service deployed with auto-scaling"

    # Deploy batch service
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: miraikakaku-batch
  namespace: $NAMESPACE
  labels:
    app: miraikakaku-batch
    environment: $ENVIRONMENT
spec:
  replicas: 1
  selector:
    matchLabels:
      app: miraikakaku-batch
  template:
    metadata:
      labels:
        app: miraikakaku-batch
        environment: $ENVIRONMENT
    spec:
      containers:
      - name: miraikakaku-batch
        image: gcr.io/$PROJECT_ID/miraikakaku-batch:latest
        env:
        - name: ENVIRONMENT
          value: "$ENVIRONMENT"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: url
              optional: true
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: miraikakaku-batch-hpa
  namespace: $NAMESPACE
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: miraikakaku-batch
  minReplicas: 1
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
EOF

    success "Batch service deployed with auto-scaling"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring stack..."

    # Deploy Prometheus
    cat << EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: $NAMESPACE
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
        - role: pod
          namespaces:
            names:
            - $NAMESPACE
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
          action: replace
          regex: ([^:]+)(?::\d+)?;(\d+)
          replacement: \$1:\$2
          target_label: __address__
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: $NAMESPACE
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
          - '--storage.tsdb.retention.time=7d'
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-data
        emptyDir: {}
      serviceAccountName: prometheus
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: $NAMESPACE
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["extensions", "apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: $NAMESPACE
roleRef:
  kind: ClusterRole
  name: prometheus
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: $NAMESPACE
spec:
  selector:
    app: prometheus
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
EOF

    success "Monitoring stack deployed"
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."

    # Wait for deployments to be ready
    log "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/miraikakaku-api -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n $NAMESPACE

    # Check pod status
    log "Checking pod status..."
    kubectl get pods -n $NAMESPACE

    # Check services
    log "Checking services..."
    kubectl get services -n $NAMESPACE

    # Check HPA status
    log "Checking HPA status..."
    kubectl get hpa -n $NAMESPACE

    success "Deployment validation completed"
}

# Create startup script for easy management
create_management_scripts() {
    log "Creating management scripts..."

    # Create monitoring access script
    cat > access-monitoring.sh << EOF
#!/bin/bash
echo "🚀 Starting port-forward to monitoring dashboard..."
echo "📊 Prometheus will be available at: http://localhost:9090"
echo "⚡ Press Ctrl+C to stop"
kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE
EOF
    chmod +x access-monitoring.sh

    # Create scaling status script
    cat > check-scaling.sh << EOF
#!/bin/bash
echo "📊 MiraiKakaku Auto-Scaling Status"
echo "=================================="
echo ""
echo "🔍 HPA Status:"
kubectl get hpa -n $NAMESPACE
echo ""
echo "📦 Pod Status:"
kubectl get pods -n $NAMESPACE
echo ""
echo "🌐 Service Status:"
kubectl get services -n $NAMESPACE
echo ""
echo "📈 Recent Scaling Events:"
kubectl get events --field-selector reason=SuccessfulRescale -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
EOF
    chmod +x check-scaling.sh

    # Create cleanup script
    cat > cleanup-deployment.sh << EOF
#!/bin/bash
echo "⚠️  This will delete the entire MiraiKakaku scaling deployment"
echo "Are you sure? (yes/no)"
read -r response
if [[ \$response == "yes" ]]; then
    echo "🧹 Cleaning up deployment..."
    kubectl delete namespace $NAMESPACE
    echo "✅ Cleanup completed"
else
    echo "❌ Cleanup cancelled"
fi
EOF
    chmod +x cleanup-deployment.sh

    success "Management scripts created"
}

# Main deployment function
main() {
    echo ""
    echo "🚀 MiraiKakaku Auto-Scaling System Deployment"
    echo "=============================================="
    echo "📍 Project: $PROJECT_ID"
    echo "🌍 Region: $REGION"
    echo "🏷️  Environment: $ENVIRONMENT"
    echo ""

    check_prerequisites
    enable_apis
    create_cluster
    get_credentials
    create_namespace
    deploy_scaling_config
    build_images
    deploy_services
    setup_monitoring
    validate_deployment
    create_management_scripts

    echo ""
    echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "====================================="
    echo ""
    echo "📊 Access monitoring:"
    echo "   ./access-monitoring.sh"
    echo ""
    echo "📈 Check scaling status:"
    echo "   ./check-scaling.sh"
    echo ""
    echo "🧹 Cleanup deployment:"
    echo "   ./cleanup-deployment.sh"
    echo ""
    echo "🌐 Get external IP:"
    echo "   kubectl get services -n $NAMESPACE"
    echo ""
    echo "✅ Your MiraiKakaku system is now auto-scaling!"
    echo ""
}

# Error handling
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"