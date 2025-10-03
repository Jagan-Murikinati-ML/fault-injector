# Social Network Monitoring Deployment Automation

This directory contains custom Kubernetes YAML files and automation scripts for deploying monitoring components to the Social Network microservices application.

## Overview

After deploying the Social Network application, these monitoring components enhance observability by adding:
- **Prometheus exporters** for metrics collection (Nginx, Redis, MongoDB)
- **Loki & Promtail** for centralized log aggregation
- **Custom configurations** for monitoring specific services

## Directory Structure

```
kubetnetes_YAMLs/
├── deploy-monitoring.sh              # Bash automation script (Linux/Mac)
├── deploy-monitoring.ps1             # PowerShell automation script (Windows)
├── README.md                         # This file
│
├── nginx-configmap.yaml              # Nginx configuration
├── nginx-log-exporter-configmap.yaml # Nginx log exporter configuration
├── nginx-log-exporter-service.yaml   # Service for nginx log exporter
├── nginx-thrift-deployment.yaml      # Nginx deployment with exporters
│
├── home-timeline-redis-deployment.yaml      # Redis with exporter
├── social-graph-redis-deployment.yaml       # Redis with exporter
├── user-timeline-redis-deployment.yaml      # Redis with exporter
│
├── post-storage-mongodb-deployment.yaml     # MongoDB with exporter
├── user-timeline-mongodb-deployment.yaml    # MongoDB with exporter
│
└── loki_promtail_values.yaml        # Helm values for Loki stack
```

## Components

### 1. Nginx Monitoring
- **nginx-configmap.yaml**: Main nginx configuration with Jaeger tracing
- **nginx-log-exporter-configmap.yaml**: Configuration for prometheus-nginxlog-exporter
- **nginx-log-exporter-service.yaml**: Kubernetes service exposing metrics endpoint
- **nginx-thrift-deployment.yaml**: Updated deployment with 3 containers:
  - `nginx-thrift`: Main OpenResty/Nginx container
  - `metrics`: nginx-prometheus-exporter (port 9113)
  - `nginx-log-exporter`: prometheus-nginxlog-exporter (port 4040)

### 2. Redis Monitoring
Enhanced Redis deployments with `redis_exporter` sidecar containers:
- `home-timeline-redis-deployment.yaml`
- `social-graph-redis-deployment.yaml`
- `user-timeline-redis-deployment.yaml`

Each exposes metrics on port 9121.

### 3. MongoDB Monitoring
Enhanced MongoDB deployments with `mongodb-exporter` sidecar containers:
- `post-storage-mongodb-deployment.yaml`
- `user-timeline-mongodb-deployment.yaml`

Each exposes metrics on port 9216.

### 4. Loki Stack (Log Aggregation)
- **loki_promtail_values.yaml**: Helm values for deploying Loki and Promtail
  - Loki: Log aggregation backend
  - Promtail: Log collection agent
  - Configured to scrape nginx and redis logs

## Prerequisites

1. **Kubernetes cluster** with kubectl configured
2. **Social Network application** already deployed
3. **Helm 3.x** installed (for Loki deployment)
4. **Sufficient cluster resources** for monitoring components

## Deployment Order

The automation scripts deploy components in this specific order:

1. **Namespaces**: Ensure `social-network` and `monitoring` namespaces exist
2. **Nginx monitoring** (in order):
   - nginx-configmap
   - nginx-log-exporter-configmap
   - nginx-log-exporter-service
   - nginx-thrift-deployment
3. **Redis monitoring**: All Redis deployments with exporters
4. **MongoDB monitoring**: All MongoDB deployments with exporters
5. **Loki stack**: Helm installation with custom values

## Usage

### Option 1: Automated Deployment (Recommended)

#### On Linux/Mac:
```bash
cd socialNetwork/kubetnetes_YAMLs
chmod +x deploy-monitoring.sh
./deploy-monitoring.sh
```

#### On Windows (PowerShell):
```powershell
cd socialNetwork\kubetnetes_YAMLs
.\deploy-monitoring.ps1
```

### Option 2: Manual Deployment

If you prefer to deploy manually or need to deploy specific components:

#### 1. Create namespaces (if needed):
```bash
kubectl create namespace social-network
kubectl create namespace monitoring
```

#### 2. Deploy Nginx monitoring:
```bash
kubectl apply -f nginx-configmap.yaml -n social-network
kubectl apply -f nginx-log-exporter-configmap.yaml -n social-network
kubectl apply -f nginx-log-exporter-service.yaml -n social-network
kubectl apply -f nginx-thrift-deployment.yaml -n social-network
```

#### 3. Deploy Redis monitoring:
```bash
kubectl apply -f home-timeline-redis-deployment.yaml -n social-network
kubectl apply -f social-graph-redis-deployment.yaml -n social-network
kubectl apply -f user-timeline-redis-deployment.yaml -n social-network
```

#### 4. Deploy MongoDB monitoring:
```bash
kubectl apply -f post-storage-mongodb-deployment.yaml -n social-network
kubectl apply -f user-timeline-mongodb-deployment.yaml -n social-network
```

#### 5. Deploy Loki stack:
```bash
# Add Grafana Helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki stack
helm install loki-stack grafana/loki-stack \
  -n monitoring \
  -f loki_promtail_values.yaml \
  --set loki.image.tag=2.9.3
```

## Verification

### Check deployment status:
```bash
# Check social-network namespace
kubectl get pods -n social-network
kubectl get deployments -n social-network

# Check monitoring namespace
kubectl get pods -n monitoring
kubectl get pvc -n monitoring
```

### Verify metrics endpoints:
```bash
# Port-forward to check metrics
kubectl port-forward -n social-network deployment/nginx-thrift 9113:9113
# Access http://localhost:9113/metrics

kubectl port-forward -n social-network deployment/nginx-thrift 4040:4040
# Access http://localhost:4040/metrics

kubectl port-forward -n social-network deployment/home-timeline-redis 9121:9121
# Access http://localhost:9121/metrics
```

### Check Loki logs:
```bash
kubectl logs -l app=loki -n monitoring
kubectl logs -l app=promtail -n monitoring
```

## Metrics Exposed

### Nginx Metrics (Port 9113)
- Request rate, response codes, connections
- Upstream server stats

### Nginx Log Metrics (Port 4040)
- Parsed log metrics with labels (method, path, status)
- Request duration, response size

### Redis Metrics (Port 9121)
- Memory usage, keyspace stats
- Commands processed, connections
- Replication status

### MongoDB Metrics (Port 9216)
- Database operations, connections
- Memory and storage metrics
- Replication lag

## Troubleshooting

### Pods not starting:
```bash
kubectl describe pod <pod-name> -n social-network
kubectl logs <pod-name> -n social-network
```

### Exporter not working:
```bash
# Check if exporter container is running
kubectl get pod <pod-name> -n social-network -o jsonpath='{.spec.containers[*].name}'

# Check exporter logs
kubectl logs <pod-name> -c redis-exporter -n social-network
kubectl logs <pod-name> -c mongodb-exporter -n social-network
kubectl logs <pod-name> -c nginx-log-exporter -n social-network
```

### Loki not receiving logs:
```bash
# Check Promtail is running
kubectl get pods -l app=promtail -n monitoring

# Check Promtail logs
kubectl logs -l app=promtail -n monitoring

# Verify Loki service
kubectl get svc -n monitoring
```

## Cleanup

To remove all monitoring components:

```bash
# Remove Loki stack
helm uninstall loki-stack -n monitoring

# Remove modified deployments (will revert to original)
kubectl delete -f nginx-thrift-deployment.yaml -n social-network
kubectl delete -f home-timeline-redis-deployment.yaml -n social-network
kubectl delete -f social-graph-redis-deployment.yaml -n social-network
kubectl delete -f user-timeline-redis-deployment.yaml -n social-network
kubectl delete -f post-storage-mongodb-deployment.yaml -n social-network
kubectl delete -f user-timeline-mongodb-deployment.yaml -n social-network

# Remove services and configmaps
kubectl delete -f nginx-log-exporter-service.yaml -n social-network
kubectl delete -f nginx-log-exporter-configmap.yaml -n social-network
kubectl delete -f nginx-configmap.yaml -n social-network
```

## Notes

- **Namespace**: Most components deploy to `social-network` namespace, Loki to `monitoring`
- **Resource limits**: Exporters have minimal resource requests/limits
- **Persistence**: Loki uses 10Gi PVC for log storage (configurable in values file)
- **Log retention**: Set to 24 hours in Loki config (adjustable)
- **Compatibility**: Tested with Kubernetes 1.20+

## Integration with Prometheus

These exporters are configured with Prometheus annotations:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "<port>"
  prometheus.io/path: "/metrics"
```

If you have Prometheus deployed with Kubernetes service discovery, it will automatically scrape these endpoints.

## Next Steps

1. **Deploy Prometheus**: To collect metrics from all exporters
2. **Deploy Grafana**: To visualize metrics and logs
3. **Create Dashboards**: Import pre-built dashboards for Redis, MongoDB, Nginx
4. **Set up Alerts**: Configure alerting rules for critical metrics

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name> -n social-network`
2. Verify configurations in YAML files
3. Ensure all prerequisites are met
4. Check Kubernetes events: `kubectl get events -n social-network`

