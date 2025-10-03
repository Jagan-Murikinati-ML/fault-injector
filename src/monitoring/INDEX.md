# Monitoring Deployment Automation - Documentation Index

Welcome to the Social Network Monitoring Deployment Automation documentation. This index will help you find the information you need quickly.

## 📚 Documentation Files

### Quick References
- **[QUICK_START.md](QUICK_START.md)** - Get started in 3 steps
  - TL;DR deployment instructions
  - Common commands
  - Quick troubleshooting
  - Health check commands

### Comprehensive Guides
- **[README.md](README.md)** - Full documentation
  - Complete component descriptions
  - Detailed deployment instructions
  - Manual deployment steps
  - Verification procedures
  - Troubleshooting guide
  - Integration with Prometheus

- **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** - Automation overview
  - Problem statement and solution
  - Script descriptions
  - Usage workflow
  - Benefits and features
  - CI/CD integration examples

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - Visual diagrams
  - Component dependencies
  - Network communication
  - Resource allocation
  - Monitoring coverage

## 🛠️ Scripts

### Deployment Scripts
| Script | Platform | Purpose |
|--------|----------|---------|
| `deploy-monitoring.sh` | Linux/Mac | Main deployment automation |
| `deploy-monitoring.ps1` | Windows | Main deployment automation |

**Usage:**
```bash
# Linux/Mac
./deploy-monitoring.sh

# Windows
.\deploy-monitoring.ps1
```

### Utility Scripts
| Script | Platform | Purpose |
|--------|----------|---------|
| `update-namespace.sh` | Linux/Mac | Update namespace in YAML files |
| `update-namespace.ps1` | Windows | Update namespace in YAML files |
| `rollback-monitoring.sh` | Linux/Mac | Remove all monitoring components |
| `rollback-monitoring.ps1` | Windows | Remove all monitoring components |
| `health-check.sh` | Linux/Mac | Verify deployment health |
| `health-check.ps1` | Windows | Verify deployment health |

## 📋 YAML Files

### Nginx Monitoring
- `nginx-configmap.yaml` - Nginx configuration with Jaeger tracing
- `nginx-log-exporter-configmap.yaml` - Log exporter configuration
- `nginx-log-exporter-service.yaml` - Service for log exporter
- `nginx-thrift-deployment.yaml` - Deployment with 3 containers

### Redis Monitoring
- `home-timeline-redis-deployment.yaml` - Redis with exporter sidecar
- `social-graph-redis-deployment.yaml` - Redis with exporter sidecar
- `user-timeline-redis-deployment.yaml` - Redis with exporter sidecar

### MongoDB Monitoring
- `post-storage-mongodb-deployment.yaml` - MongoDB with exporter sidecar
- `user-timeline-mongodb-deployment.yaml` - MongoDB with exporter sidecar

### Log Aggregation
- `loki_promtail_values.yaml` - Helm values for Loki stack

## 🚀 Quick Start Paths

### Path 1: First-Time User
1. Read [QUICK_START.md](QUICK_START.md)
2. Run `./deploy-monitoring.sh` or `.\deploy-monitoring.ps1`
3. Run `./health-check.sh` or `.\health-check.ps1`
4. Done! ✓

### Path 2: Detailed Understanding
1. Read [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Understand the solution
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the architecture
3. Read [README.md](README.md) - Understand all components
4. Deploy using scripts
5. Verify with health check

### Path 3: Troubleshooting
1. Run `./health-check.sh` or `.\health-check.ps1`
2. Check [QUICK_START.md](QUICK_START.md) - Troubleshooting section
3. Check [README.md](README.md) - Troubleshooting section
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) - Component dependencies

### Path 4: Customization
1. Read [README.md](README.md) - Understand components
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand dependencies
3. Modify YAML files as needed
4. Update namespace if needed: `./update-namespace.sh`
5. Deploy and verify

## 📖 Common Tasks

### Deploy Monitoring
```bash
# See: QUICK_START.md - Step 2
./deploy-monitoring.sh  # Linux/Mac
.\deploy-monitoring.ps1  # Windows
```

### Verify Deployment
```bash
# See: QUICK_START.md - Step 3
./health-check.sh  # Linux/Mac
.\health-check.ps1  # Windows
```

### Update Namespace
```bash
# See: README.md - Manual Deployment section
./update-namespace.sh social-network  # Linux/Mac
.\update-namespace.ps1 -NewNamespace "social-network"  # Windows
```

### Rollback
```bash
# See: README.md - Cleanup section
./rollback-monitoring.sh  # Linux/Mac
.\rollback-monitoring.ps1  # Windows
```

### Check Metrics
```bash
# See: QUICK_START.md - Access Metrics section
kubectl port-forward -n social-network deployment/nginx-thrift 9113:9113
curl http://localhost:9113/metrics
```

### View Logs
```bash
# See: QUICK_START.md - View Logs section
kubectl logs -n social-network deployment/nginx-thrift -c nginx-log-exporter
kubectl logs -n monitoring -l app=loki
```

## 🔍 Find Information By Topic

### Deployment
- **Automated deployment**: [QUICK_START.md](QUICK_START.md), [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)
- **Manual deployment**: [README.md](README.md) - Manual Deployment section
- **Deployment flow**: [ARCHITECTURE.md](ARCHITECTURE.md) - Deployment Flow
- **Dependencies**: [ARCHITECTURE.md](ARCHITECTURE.md) - Component Dependencies

### Components
- **Nginx monitoring**: [README.md](README.md) - Components section
- **Redis monitoring**: [README.md](README.md) - Components section
- **MongoDB monitoring**: [README.md](README.md) - Components section
- **Loki stack**: [README.md](README.md) - Components section
- **Architecture overview**: [ARCHITECTURE.md](ARCHITECTURE.md)

### Metrics
- **Metrics exposed**: [README.md](README.md) - Metrics Exposed section
- **Access metrics**: [QUICK_START.md](QUICK_START.md) - Access Metrics
- **Metrics flow**: [ARCHITECTURE.md](ARCHITECTURE.md) - Metrics Flow
- **Prometheus integration**: [README.md](README.md) - Integration with Prometheus

### Logs
- **Log aggregation**: [README.md](README.md) - Loki Stack section
- **Logs flow**: [ARCHITECTURE.md](ARCHITECTURE.md) - Logs Flow
- **View logs**: [QUICK_START.md](QUICK_START.md) - View Logs
- **Loki configuration**: `loki_promtail_values.yaml`

### Troubleshooting
- **Quick troubleshooting**: [QUICK_START.md](QUICK_START.md) - Troubleshooting
- **Detailed troubleshooting**: [README.md](README.md) - Troubleshooting
- **Health check**: Run `./health-check.sh` or `.\health-check.ps1`
- **Common issues**: [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Troubleshooting Guide

### Scripts
- **Script overview**: [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Solution Components
- **Deployment script**: [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Main Deployment Scripts
- **Utility scripts**: [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Solution Components
- **CI/CD integration**: [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) - Integration with CI/CD

## 📊 Monitoring Coverage

| Component | Metrics Port | Logs | Documentation |
|-----------|--------------|------|---------------|
| nginx-thrift | 9113, 4040 | ✓ | [README.md](README.md) |
| home-timeline-redis | 9121 | ✓ | [README.md](README.md) |
| social-graph-redis | 9121 | ✓ | [README.md](README.md) |
| user-timeline-redis | 9121 | ✓ | [README.md](README.md) |
| post-storage-mongodb | 9216 | ✓ | [README.md](README.md) |
| user-timeline-mongodb | 9216 | ✓ | [README.md](README.md) |

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed monitoring coverage.

## 🎯 Use Cases

### Use Case 1: Fresh Deployment
**Goal:** Deploy monitoring for the first time

**Steps:**
1. Read [QUICK_START.md](QUICK_START.md)
2. Run deployment script
3. Run health check
4. Verify metrics endpoints

**Documentation:** [QUICK_START.md](QUICK_START.md) - Step 2

### Use Case 2: Update Configuration
**Goal:** Modify monitoring configuration

**Steps:**
1. Edit YAML files
2. Run deployment script (applies updates)
3. Verify with health check

**Documentation:** [README.md](README.md) - Manual Deployment

### Use Case 3: Change Namespace
**Goal:** Deploy to different namespace

**Steps:**
1. Run update-namespace script
2. Run deployment script
3. Verify deployment

**Documentation:** [QUICK_START.md](QUICK_START.md) - Step 1

### Use Case 4: Troubleshoot Issues
**Goal:** Diagnose and fix problems

**Steps:**
1. Run health check script
2. Check specific component logs
3. Review troubleshooting guides
4. Fix and redeploy

**Documentation:** [QUICK_START.md](QUICK_START.md) - Troubleshooting

### Use Case 5: Rollback
**Goal:** Remove monitoring components

**Steps:**
1. Run rollback script
2. Confirm removal
3. Optionally restore original state

**Documentation:** [README.md](README.md) - Cleanup

## 🔗 External Resources

### Prometheus Exporters
- [nginx-prometheus-exporter](https://github.com/nginxinc/nginx-prometheus-exporter)
- [prometheus-nginxlog-exporter](https://github.com/martin-helmich/prometheus-nginxlog-exporter)
- [redis_exporter](https://github.com/oliver006/redis_exporter)
- [mongodb-exporter](https://github.com/percona/mongodb_exporter)

### Loki Stack
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Promtail Documentation](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Loki Helm Chart](https://github.com/grafana/helm-charts/tree/main/charts/loki-stack)

### Grafana Dashboards
- [Nginx Dashboard](https://grafana.com/grafana/dashboards/12708)
- [Redis Dashboard](https://grafana.com/grafana/dashboards/11835)
- [MongoDB Dashboard](https://grafana.com/grafana/dashboards/2583)

## 💡 Tips

1. **Always run health check after deployment**
   ```bash
   ./deploy-monitoring.sh && ./health-check.sh
   ```

2. **Keep documentation handy**
   - Bookmark this INDEX.md
   - Keep QUICK_START.md open during deployment

3. **Test in non-production first**
   - Verify scripts work in dev/staging
   - Check resource consumption

4. **Monitor during deployment**
   ```bash
   kubectl get pods -n social-network -w
   ```

5. **Use version control**
   - Commit YAML changes
   - Keep backup of original files

## 📞 Support

If you need help:

1. **Check health**: Run `./health-check.sh` or `.\health-check.ps1`
2. **Review docs**: Start with [QUICK_START.md](QUICK_START.md)
3. **Check logs**: `kubectl logs <pod> -n <namespace>`
4. **Review events**: `kubectl get events -n <namespace>`

## 📝 Document Versions

| Document | Last Updated | Version |
|----------|--------------|---------|
| INDEX.md | 2025-10-03 | 1.0 |
| QUICK_START.md | 2025-10-03 | 1.0 |
| README.md | 2025-10-03 | 1.0 |
| AUTOMATION_SUMMARY.md | 2025-10-03 | 1.0 |
| ARCHITECTURE.md | 2025-10-03 | 1.0 |

---

**Quick Links:**
- [Quick Start](QUICK_START.md) | [Full Documentation](README.md) | [Architecture](ARCHITECTURE.md) | [Automation Summary](AUTOMATION_SUMMARY.md)

**Need help?** Start with [QUICK_START.md](QUICK_START.md) for immediate guidance.

