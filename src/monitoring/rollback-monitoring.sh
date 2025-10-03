#!/bin/bash

# Rollback script for monitoring deployment
# This script removes all monitoring components deployed by deploy-monitoring.sh

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE="social-network"
MONITORING_NAMESPACE="monitoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Confirmation prompt
read -p "This will remove all monitoring components. Are you sure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    print_info "Rollback cancelled."
    exit 0
fi

print_info "=========================================="
print_info "Starting Monitoring Rollback"
print_info "=========================================="

# Step 1: Remove Loki stack
print_info "\n[Step 1/3] Removing Loki stack..."
if helm list -n $MONITORING_NAMESPACE | grep -q "loki-stack"; then
    print_info "Uninstalling loki-stack..."
    helm uninstall loki-stack -n $MONITORING_NAMESPACE
    print_info "Loki stack removed"
else
    print_warning "Loki stack not found, skipping..."
fi

# Step 2: Remove modified deployments
print_info "\n[Step 2/3] Removing modified deployments..."

deployments=(
    "nginx-thrift-deployment.yaml"
    "home-timeline-redis-deployment.yaml"
    "social-graph-redis-deployment.yaml"
    "user-timeline-redis-deployment.yaml"
    "post-storage-mongodb-deployment.yaml"
    "user-timeline-mongodb-deployment.yaml"
)

for deployment in "${deployments[@]}"; do
    if [ -f "$SCRIPT_DIR/$deployment" ]; then
        print_info "Deleting $deployment..."
        kubectl delete -f "$SCRIPT_DIR/$deployment" -n $NAMESPACE --ignore-not-found=true
    fi
done

# Step 3: Remove ConfigMaps and Services
print_info "\n[Step 3/3] Removing ConfigMaps and Services..."

print_info "Removing nginx-log-exporter-service..."
kubectl delete -f "$SCRIPT_DIR/nginx-log-exporter-service.yaml" -n $NAMESPACE --ignore-not-found=true

print_info "Removing nginx-log-exporter-configmap..."
kubectl delete -f "$SCRIPT_DIR/nginx-log-exporter-configmap.yaml" -n $NAMESPACE --ignore-not-found=true

print_info "Removing nginx-configmap..."
kubectl delete -f "$SCRIPT_DIR/nginx-configmap.yaml" -n $NAMESPACE --ignore-not-found=true

print_info "\n=========================================="
print_info "Rollback Complete"
print_info "=========================================="

print_warning "\nNote: Original deployments from helm chart may need to be reapplied."
print_info "To restore original state, run:"
print_info "  helm upgrade social-network <chart-path> -n $NAMESPACE"

