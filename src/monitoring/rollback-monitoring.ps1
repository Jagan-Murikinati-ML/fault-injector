# Rollback script for monitoring deployment
# This script removes all monitoring components deployed by deploy-monitoring.ps1

$NAMESPACE = "social-network"
$MONITORING_NAMESPACE = "monitoring"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Confirmation prompt
$confirm = Read-Host "This will remove all monitoring components. Are you sure? (yes/no)"
if ($confirm -ne "yes") {
    Print-Info "Rollback cancelled."
    exit 0
}

Print-Info "=========================================="
Print-Info "Starting Monitoring Rollback"
Print-Info "=========================================="

# Step 1: Remove Loki stack
Print-Info "`n[Step 1/3] Removing Loki stack..."
$lokiExists = helm list -n $MONITORING_NAMESPACE 2>$null | Select-String "loki-stack"
if ($lokiExists) {
    Print-Info "Uninstalling loki-stack..."
    helm uninstall loki-stack -n $MONITORING_NAMESPACE
    Print-Info "Loki stack removed"
} else {
    Print-Warning "Loki stack not found, skipping..."
}

# Step 2: Remove modified deployments
Print-Info "`n[Step 2/3] Removing modified deployments..."

$deployments = @(
    "nginx-thrift-deployment.yaml",
    "home-timeline-redis-deployment.yaml",
    "social-graph-redis-deployment.yaml",
    "user-timeline-redis-deployment.yaml",
    "post-storage-mongodb-deployment.yaml",
    "user-timeline-mongodb-deployment.yaml"
)

foreach ($deployment in $deployments) {
    $filePath = Join-Path $SCRIPT_DIR $deployment
    if (Test-Path $filePath) {
        Print-Info "Deleting $deployment..."
        kubectl delete -f $filePath -n $NAMESPACE --ignore-not-found=true
    }
}

# Step 3: Remove ConfigMaps and Services
Print-Info "`n[Step 3/3] Removing ConfigMaps and Services..."

Print-Info "Removing nginx-log-exporter-service..."
kubectl delete -f "$SCRIPT_DIR/nginx-log-exporter-service.yaml" -n $NAMESPACE --ignore-not-found=true

Print-Info "Removing nginx-log-exporter-configmap..."
kubectl delete -f "$SCRIPT_DIR/nginx-log-exporter-configmap.yaml" -n $NAMESPACE --ignore-not-found=true

Print-Info "Removing nginx-configmap..."
kubectl delete -f "$SCRIPT_DIR/nginx-configmap.yaml" -n $NAMESPACE --ignore-not-found=true

Print-Info "`n=========================================="
Print-Info "Rollback Complete"
Print-Info "=========================================="

Print-Warning "`nNote: Original deployments from helm chart may need to be reapplied."
Print-Info "To restore original state, run:"
Print-Info "  helm upgrade social-network <chart-path> -n $NAMESPACE"

