#!/bin/bash

# Monitoring Deployment Automation Script for Social Network Application
# This script automates the deployment of monitoring components after the social network app is deployed

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="social-network"
MONITORING_NAMESPACE="monitoring2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if namespace exists, create if not
ensure_namespace() {
    local ns=$1
    if kubectl get namespace "$ns" &> /dev/null; then
        print_info "Namespace '$ns' already exists"
    else
        print_info "Creating namespace '$ns'"
        kubectl create namespace "$ns"
    fi
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local deployment=$1
    local namespace=$2
    local timeout=${3:-300}  # Default 5 minutes
    
    print_info "Waiting for deployment '$deployment' in namespace '$namespace' to be ready..."
    if kubectl wait --for=condition=available --timeout=${timeout}s deployment/$deployment -n $namespace; then
        print_info "Deployment '$deployment' is ready"
        return 0
    else
        print_error "Deployment '$deployment' failed to become ready within ${timeout}s"
        return 1
    fi
}

# Function to apply YAML and wait
apply_and_wait() {
    local file=$1
    local resource_type=$2
    local resource_name=$3
    local namespace=$4
    
    print_info "Applying $file..."
    kubectl apply -f "$SCRIPT_DIR/$file" -n $namespace
    
    if [ "$resource_type" == "deployment" ]; then
        wait_for_deployment "$resource_name" "$namespace"
    else
        sleep 2  # Short wait for non-deployment resources
    fi
}

# Main deployment function
main() {
    print_info "=========================================="
    print_info "Starting Monitoring Deployment Automation"
    print_info "=========================================="
    
    # Step 1: Ensure namespaces exist
    print_info "\n[Step 1/5] Ensuring namespaces exist..."
    ensure_namespace "$NAMESPACE"
    ensure_namespace "$MONITORING_NAMESPACE"
    
    # Step 2: Deploy Nginx monitoring components in order
    print_info "\n[Step 2/5] Deploying Nginx monitoring components..."
    
    print_info "  2.1 - Applying nginx-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-configmap.yaml" -n $NAMESPACE
    sleep 2
    
    print_info "  2.2 - Applying nginx-log-exporter-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-log-exporter-configmap.yaml" -n $NAMESPACE
    sleep 2
    
    print_info "  2.3 - Applying nginx-log-exporter-service.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-log-exporter-service.yaml" -n $NAMESPACE
    sleep 2
    
    print_info "  2.4 - Applying nginx-thrift-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-thrift-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "nginx-thrift" "$NAMESPACE" 300
    
    # Step 3: Deploy Redis monitoring components
    print_info "\n[Step 3/5] Deploying Redis monitoring components..."
    
    print_info "  3.1 - Applying home-timeline-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/home-timeline-redis-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "home-timeline-redis" "$NAMESPACE" 180
    
    print_info "  3.2 - Applying social-graph-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/social-graph-redis-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "social-graph-redis" "$NAMESPACE" 180
    
    print_info "  3.3 - Applying user-timeline-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/user-timeline-redis-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "user-timeline-redis" "$NAMESPACE" 180
    
    # Step 4: Deploy MongoDB monitoring components
    print_info "\n[Step 4/5] Deploying MongoDB monitoring components..."
    
    print_info "  4.1 - Applying post-storage-mongodb-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/post-storage-mongodb-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "post-storage-mongodb" "$NAMESPACE" 180
    
    print_info "  4.2 - Applying user-timeline-mongodb-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/user-timeline-mongodb-deployment.yaml" -n $NAMESPACE
    wait_for_deployment "user-timeline-mongodb" "$NAMESPACE" 180
    
    # Step 5: Deploy Loki stack using Helm
    print_info "\n[Step 5/5] Deploying Loki stack using Helm..."
    
    # Check if Helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed. Please install Helm first."
        exit 1
    fi
    
    # Add Grafana Helm repo if not already added
    print_info "  5.1 - Adding Grafana Helm repository"
    if helm repo list | grep -q "^grafana"; then
        print_info "Grafana repo already exists, updating..."
        helm repo update grafana
    else
        print_info "Adding Grafana repo..."
        helm repo add grafana https://grafana.github.io/helm-charts
        helm repo update
    fi
    
    # Install or upgrade Loki stack
    print_info "  5.2 - Installing/Upgrading Loki stack"
    if helm list -n $MONITORING_NAMESPACE | grep -q "loki-stack"; then
        print_warning "Loki-stack already exists, upgrading..."
        helm upgrade loki-stack-v2 grafana/loki-stack \
            -n $MONITORING_NAMESPACE \
            -f "$SCRIPT_DIR/loki_promtail_values.yaml" \
            --set loki.image.tag=2.9.3
    else
        print_info "Installing Loki-stack..."
        helm install loki-stack-v2 grafana/loki-stack \
            -n $MONITORING_NAMESPACE \
            -f "$SCRIPT_DIR/loki_promtail_values.yaml" \
            --set loki.image.tag=2.9.3
    fi
    
    # Wait for Loki to be ready
    print_info "  5.3 - Waiting for Loki to be ready..."
    sleep 10
    kubectl wait --for=condition=ready pod -l app=loki -n $MONITORING_NAMESPACE --timeout=300s || true
    
    # Final status check
    print_info "\n=========================================="
    print_info "Deployment Summary"
    print_info "=========================================="
    
    print_info "\nDeployments in namespace '$NAMESPACE':"
    kubectl get deployments -n $NAMESPACE | grep -E "nginx-thrift|redis|mongodb" || true
    
    print_info "\nPods in namespace '$MONITORING_NAMESPACE':"
    kubectl get pods -n $MONITORING_NAMESPACE
    
    print_info "\n=========================================="
    print_info "Monitoring Deployment Completed Successfully!"
    print_info "=========================================="
    
    print_info "\nNext Steps:"
    print_info "1. Verify all pods are running: kubectl get pods -n $NAMESPACE"
    print_info "2. Check Loki logs: kubectl logs -l app=loki -n $MONITORING_NAMESPACE"
    print_info "3. Check Promtail logs: kubectl logs -l app=promtail -n $MONITORING_NAMESPACE"
    print_info "4. Access Grafana (if deployed) to visualize logs and metrics"
}

# Run main function
main "$@"

