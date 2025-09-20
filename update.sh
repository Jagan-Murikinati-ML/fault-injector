#!/bin/bash
set -e

echo "🔄 Updating deployment..."

# Update ConfigMaps with latest files
echo "📦 Updating ConfigMaps..."
kubectl create configmap chaos-experiments \
  --from-file=src/pod/ \
  --namespace=chaos-platform \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap airflow-dags \
  --from-file=workflow/dags/ \
  --namespace=chaos-platform \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment to pick up changes
echo "♻️ Restarting pods..."
kubectl rollout restart deployment/chaos-platform -n chaos-platform

# Wait for rollout
kubectl rollout status deployment/chaos-platform -n chaos-platform

echo "✅ Update complete!"
