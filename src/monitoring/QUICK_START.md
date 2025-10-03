# Quick Start Guide - Monitoring Deployment Automation

## TL;DR - Get Started in 3 Steps

### Step 1: Update Namespace (if needed)
If your social network app is deployed in a namespace other than `social-network`:

**Linux/Mac:**
```bash
cd socialNetwork/kubetnetes_YAMLs
chmod +x update-namespace.sh
./update-namespace.sh your-namespace-name
```

**Windows:**
```powershell
cd socialNetwork\kubetnetes_YAMLs
.\update-namespace.ps1 -NewNamespace "your-namespace-name"
```

### Step 2: Deploy Monitoring

**Linux/Mac:**
```bash
chmod +x deploy-monitoring.sh
./deploy-monitoring.sh
```

**Windows:**
```powershell
.\deploy-monitoring.ps1
```

### Step 3: Verify Deployment

```bash
# Check pods in social-network namespace
kubectl get pods -n social-network

# Check monitoring namespace
kubectl get pods -n monitoring

# Verify metrics endpoints
kubectl port-forward -n social-network deployment/nginx-thrift 9113:9113
# Open browser: http://localhost:9113/metrics
```

---

## What Gets Deployed?

| Component | Type | Metrics Port | Purpose |
|-----------|------|--------------|---------|
| nginx-thrift | Deployment | 9113, 4040 | Nginx metrics + log metrics |
| home-timeline-redis | Deployment | 9121 | Redis metrics |
| social-graph-redis | Deployment | 9121 | Redis metrics |
| user-timeline-redis | Deployment | 9121 | Redis metrics |
| post-storage-mongodb | Deployment | 9216 | MongoDB metrics |
| user-timeline-mongodb | Deployment | 9216 | MongoDB metrics |
| loki-stack | Helm Chart | 3100 | Log aggregation |
| promtail | DaemonSet | - | Log collection |

---

## Common Commands

### Check Deployment Status
```bash
# All pods in social-network namespace
kubectl get pods -n social-network

# All pods in monitoring namespace
kubectl get pods -n monitoring

# Check specific deployment
kubectl get deployment nginx-thrift -n social-network
```

### View Logs
```bash
# Nginx logs
kubectl logs -n social-network deployment/nginx-thrift -c nginx-thrift

# Nginx exporter logs
kubectl logs -n social-network deployment/nginx-thrift -c nginx-log-exporter

# Redis exporter logs
kubectl logs -n social-network deployment/home-timeline-redis -c redis-exporter

# Loki logs
kubectl logs -n monitoring -l app=loki

# Promtail logs
kubectl logs -n monitoring -l app=promtail
```

### Access Metrics
```bash
# Nginx metrics (port 9113)
kubectl port-forward -n social-network deployment/nginx-thrift 9113:9113
curl http://localhost:9113/metrics

# Nginx log metrics (port 4040)
kubectl port-forward -n social-network deployment/nginx-thrift 4040:4040
curl http://localhost:4040/metrics

# Redis metrics (port 9121)
kubectl port-forward -n social-network deployment/home-timeline-redis 9121:9121
curl http://localhost:9121/metrics

# MongoDB metrics (port 9216)
kubectl port-forward -n social-network deployment/post-storage-mongodb 9216:9216
curl http://localhost:9216/metrics
```

### Rollback (Remove Monitoring)
```bash
# Linux/Mac
chmod +x rollback-monitoring.sh
./rollback-monitoring.sh

# Windows
.\rollback-monitoring.ps1
```

---

## Troubleshooting

### Problem: Pods not starting

**Solution:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n social-network

# Check events
kubectl get events -n social-network --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n social-network
```

### Problem: Exporter container failing

**Solution:**
```bash
# Check specific container logs
kubectl logs <pod-name> -c redis-exporter -n social-network
kubectl logs <pod-name> -c mongodb-exporter -n social-network
kubectl logs <pod-name> -c nginx-log-exporter -n social-network

# Check container status
kubectl get pod <pod-name> -n social-network -o jsonpath='{.status.containerStatuses[*].name}'
```

### Problem: Loki not receiving logs

**Solution:**
```bash
# Check Promtail is running
kubectl get pods -l app=promtail -n monitoring

# Check Promtail configuration
kubectl logs -l app=promtail -n monitoring | grep -i error

# Verify Loki service
kubectl get svc loki-stack -n monitoring

# Test Loki API
kubectl port-forward -n monitoring svc/loki-stack 3100:3100
curl http://localhost:3100/ready
```

### Problem: Metrics not showing up

**Solution:**
```bash
# Verify annotations on pods
kubectl get pod <pod-name> -n social-network -o yaml | grep -A 5 annotations

# Check if Prometheus is scraping
kubectl logs -n monitoring <prometheus-pod> | grep <service-name>

# Manually test metrics endpoint
kubectl exec -it <pod-name> -n social-network -- wget -O- http://localhost:9113/metrics
```

---

## File Descriptions

| File | Purpose |
|------|---------|
| `deploy-monitoring.sh/ps1` | Main deployment automation script |
| `rollback-monitoring.sh/ps1` | Remove all monitoring components |
| `update-namespace.sh/ps1` | Update namespace in all YAML files |
| `README.md` | Comprehensive documentation |
| `QUICK_START.md` | This file - quick reference |

---

## Deployment Flow

```
1. Ensure namespaces exist
   ↓
2. Deploy Nginx ConfigMaps
   ↓
3. Deploy Nginx Log Exporter ConfigMap
   ↓
4. Deploy Nginx Log Exporter Service
   ↓
5. Deploy Nginx Deployment (with exporters)
   ↓
6. Deploy Redis Deployments (with exporters)
   ↓
7. Deploy MongoDB Deployments (with exporters)
   ↓
8. Deploy Loki Stack via Helm
   ↓
9. Verify all components
```

---

## Next Steps After Deployment

1. **Deploy Prometheus** (if not already deployed):
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
   ```

2. **Access Grafana** (if deployed with Prometheus):
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
   # Default credentials: admin/prom-operator
   ```

3. **Add Loki as Grafana Data Source**:
   - URL: `http://loki-stack:3100`
   - Type: Loki

4. **Import Dashboards**:
   - Nginx: Dashboard ID 12708
   - Redis: Dashboard ID 11835
   - MongoDB: Dashboard ID 2583

---

## Support & Resources

- **Full Documentation**: See `README.md`
- **Check Logs**: `kubectl logs <pod-name> -n <namespace>`
- **Describe Resources**: `kubectl describe <resource> <name> -n <namespace>`
- **Events**: `kubectl get events -n <namespace>`

---

## Quick Health Check

Run this to verify everything is working:

```bash
#!/bin/bash
echo "=== Checking Social Network Namespace ==="
kubectl get pods -n social-network | grep -E "nginx-thrift|redis|mongodb"

echo -e "\n=== Checking Monitoring Namespace ==="
kubectl get pods -n monitoring

echo -e "\n=== Checking Metrics Endpoints ==="
kubectl get svc -n social-network | grep exporter

echo -e "\n=== Checking Loki Stack ==="
helm list -n monitoring | grep loki-stack
```

Save this as `health-check.sh` and run it anytime!

