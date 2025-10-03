#!/bin/bash

# Health Check Script for Social Network Monitoring
# This script verifies all monitoring components are running correctly

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="social-network"
MONITORING_NAMESPACE="monitoring"

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl first."
    exit 1
fi

print_header "Social Network Monitoring Health Check"

# Check namespaces
print_header "1. Checking Namespaces"
if kubectl get namespace $NAMESPACE &> /dev/null; then
    print_success "Namespace '$NAMESPACE' exists"
else
    print_error "Namespace '$NAMESPACE' not found"
fi

if kubectl get namespace $MONITORING_NAMESPACE &> /dev/null; then
    print_success "Namespace '$MONITORING_NAMESPACE' exists"
else
    print_error "Namespace '$MONITORING_NAMESPACE' not found"
fi

# Check deployments in social-network namespace
print_header "2. Checking Deployments in '$NAMESPACE'"

deployments=(
    "nginx-thrift"
    "home-timeline-redis"
    "social-graph-redis"
    "user-timeline-redis"
    "post-storage-mongodb"
    "user-timeline-mongodb"
)

for deployment in "${deployments[@]}"; do
    if kubectl get deployment $deployment -n $NAMESPACE &> /dev/null; then
        ready=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
        desired=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.spec.replicas}')
        if [ "$ready" == "$desired" ]; then
            print_success "$deployment: $ready/$desired replicas ready"
        else
            print_warning "$deployment: $ready/$desired replicas ready"
        fi
    else
        print_error "$deployment: not found"
    fi
done

# Check pods in social-network namespace
print_header "3. Checking Pods in '$NAMESPACE'"
echo ""
kubectl get pods -n $NAMESPACE | grep -E "nginx-thrift|redis|mongodb" || print_error "No monitoring pods found"

# Check ConfigMaps
print_header "4. Checking ConfigMaps"
configmaps=(
    "nginx-thrift"
    "nginx-log-exporter-config"
)

for cm in "${configmaps[@]}"; do
    if kubectl get configmap $cm -n $NAMESPACE &> /dev/null; then
        print_success "ConfigMap '$cm' exists"
    else
        print_error "ConfigMap '$cm' not found"
    fi
done

# Check Services
print_header "5. Checking Services"
if kubectl get service nginx-log-exporter -n $NAMESPACE &> /dev/null; then
    print_success "Service 'nginx-log-exporter' exists"
else
    print_error "Service 'nginx-log-exporter' not found"
fi

# Check Loki stack
print_header "6. Checking Loki Stack in '$MONITORING_NAMESPACE'"
if helm list -n $MONITORING_NAMESPACE 2>/dev/null | grep -q "loki-stack"; then
    print_success "Loki stack Helm release found"
    
    # Check Loki pods
    loki_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=loki --no-headers 2>/dev/null | wc -l)
    if [ "$loki_pods" -gt 0 ]; then
        print_success "Loki pods running: $loki_pods"
    else
        print_error "No Loki pods found"
    fi
    
    # Check Promtail pods
    promtail_pods=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=promtail --no-headers 2>/dev/null | wc -l)
    if [ "$promtail_pods" -gt 0 ]; then
        print_success "Promtail pods running: $promtail_pods"
    else
        print_error "No Promtail pods found"
    fi
else
    print_error "Loki stack not found"
fi

# Check metrics endpoints
print_header "7. Checking Metrics Endpoints"

# Function to check if a pod has a specific container
check_container() {
    local pod=$1
    local container=$2
    local namespace=$3
    
    if kubectl get pod $pod -n $namespace -o jsonpath="{.spec.containers[*].name}" 2>/dev/null | grep -q $container; then
        return 0
    else
        return 1
    fi
}

# Check nginx-thrift exporters
nginx_pod=$(kubectl get pods -n $NAMESPACE -l service=nginx-thrift -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$nginx_pod" ]; then
    if check_container $nginx_pod "metrics" $NAMESPACE; then
        print_success "Nginx prometheus exporter container found in $nginx_pod"
    else
        print_error "Nginx prometheus exporter container not found"
    fi
    
    if check_container $nginx_pod "nginx-log-exporter" $NAMESPACE; then
        print_success "Nginx log exporter container found in $nginx_pod"
    else
        print_error "Nginx log exporter container not found"
    fi
fi

# Check Redis exporters
for redis_deployment in "home-timeline-redis" "social-graph-redis" "user-timeline-redis"; do
    redis_pod=$(kubectl get pods -n $NAMESPACE -l service=$redis_deployment -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$redis_pod" ]; then
        if check_container $redis_pod "redis-exporter" $NAMESPACE; then
            print_success "Redis exporter found in $redis_deployment"
        else
            print_error "Redis exporter not found in $redis_deployment"
        fi
    fi
done

# Check MongoDB exporters
for mongo_deployment in "post-storage-mongodb" "user-timeline-mongodb"; do
    mongo_pod=$(kubectl get pods -n $NAMESPACE -l service=$mongo_deployment -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$mongo_pod" ]; then
        if check_container $mongo_pod "mongodb-exporter" $NAMESPACE; then
            print_success "MongoDB exporter found in $mongo_deployment"
        else
            print_error "MongoDB exporter not found in $mongo_deployment"
        fi
    fi
done

# Summary
print_header "8. Summary"
echo ""
echo "To view detailed pod status:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get pods -n $MONITORING_NAMESPACE"
echo ""
echo "To check metrics endpoints:"
echo "  kubectl port-forward -n $NAMESPACE deployment/nginx-thrift 9113:9113"
echo "  kubectl port-forward -n $NAMESPACE deployment/nginx-thrift 4040:4040"
echo "  kubectl port-forward -n $NAMESPACE deployment/home-timeline-redis 9121:9121"
echo ""
echo "To check logs:"
echo "  kubectl logs -n $NAMESPACE deployment/nginx-thrift -c nginx-log-exporter"
echo "  kubectl logs -n $MONITORING_NAMESPACE -l app=loki"
echo "  kubectl logs -n $MONITORING_NAMESPACE -l app=promtail"
echo ""

print_header "Health Check Complete"

