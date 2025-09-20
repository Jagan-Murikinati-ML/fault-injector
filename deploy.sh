#!/bin/bash
set -e

echo "🚀 Starting deployment with CeleryExecutor..."

# Step 1: Create namespace
echo "📁 Creating namespace..."
kubectl apply -f deploy/namespace.yaml

# Step 2: Deploy PostgreSQL and Redis
echo "🗄️ Deploying PostgreSQL..."
kubectl apply -f deploy/postgres.yaml

echo "📦 Deploying Redis..."
kubectl apply -f deploy/redis.yaml

# Wait for databases
echo "⏳ Waiting for databases..."
kubectl wait --for=condition=available --timeout=120s deployment/postgres -n chaos-platform
kubectl wait --for=condition=available --timeout=120s deployment/redis -n chaos-platform

# Step 3: Create ConfigMaps
echo "📦 Creating ConfigMaps..."
mkdir -p temp_configmap_experiments temp_configmap_dags

# Copy chaos experiments (YAML and JSON files)
cp src/pod/*.yaml temp_configmap_experiments/ 2>/dev/null || true
cp src/pod/*.json temp_configmap_experiments/ 2>/dev/null || true  
cp src/pod/*.py temp_configmap_experiments/ 2>/dev/null || true

# Copy DAG factory file
cp workflow/dags/dag_factory.py temp_configmap_dags/ 2>/dev/null || true

kubectl create configmap chaos-experiments \
  --from-file=temp_configmap_experiments/ \
  --namespace=chaos-platform \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap airflow-dags \
  --from-file=temp_configmap_dags/ \
  --namespace=chaos-platform \
  --dry-run=client -o yaml | kubectl apply -f -

rm -rf temp_configmap_experiments temp_configmap_dags

# Step 4: Deploy Airflow
echo "🚢 Deploying Airflow with CeleryExecutor..."
kubectl apply -f deploy/deployment.yaml
kubectl apply -f deploy/service.yaml

# Step 5: Wait for deployment
echo "⏳ Waiting for Airflow deployment..."
kubectl wait --for=condition=available --timeout=300s deployment/chaos-platform -n chaos-platform

# Step 6: Get access info
echo "✅ Deployment complete!"
echo "🌐 Getting service info..."
kubectl get service chaos-platform-service -n chaos-platform

echo ""
echo "📋 Access your Airflow UI at:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🔍 Check status with:"
echo "   kubectl get pods -n chaos-platform"
echo "   kubectl logs -f deployment/chaos-platform -n chaos-platform"
