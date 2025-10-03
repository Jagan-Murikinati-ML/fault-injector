# Monitoring Deployment Automation Script for Social Network Application
# This script automates the deployment of monitoring components after the social network app is deployed

# Configuration
$NAMESPACE = "social-network"
$MONITORING_NAMESPACE = "monitoring"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Function to print colored messages
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

# Function to check if namespace exists, create if not
function Ensure-Namespace {
    param([string]$Namespace)
    
    $namespaceExists = kubectl get namespace $Namespace 2>$null
    if ($LASTEXITCODE -eq 0) {
        Print-Info "Namespace '$Namespace' already exists"
    } else {
        Print-Info "Creating namespace '$Namespace'"
        kubectl create namespace $Namespace
    }
}

# Function to wait for deployment to be ready
function Wait-ForDeployment {
    param(
        [string]$Deployment,
        [string]$Namespace,
        [int]$Timeout = 300
    )
    
    Print-Info "Waiting for deployment '$Deployment' in namespace '$Namespace' to be ready..."
    $result = kubectl wait --for=condition=available --timeout="${Timeout}s" deployment/$Deployment -n $Namespace 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Print-Info "Deployment '$Deployment' is ready"
        return $true
    } else {
        Print-Error "Deployment '$Deployment' failed to become ready within ${Timeout}s"
        return $false
    }
}

# Main deployment function
function Main {
    Print-Info "=========================================="
    Print-Info "Starting Monitoring Deployment Automation"
    Print-Info "=========================================="
    
    # Step 1: Ensure namespaces exist
    Print-Info "`n[Step 1/5] Ensuring namespaces exist..."
    Ensure-Namespace -Namespace $NAMESPACE
    Ensure-Namespace -Namespace $MONITORING_NAMESPACE
    
    # Step 2: Deploy Nginx monitoring components in order
    Print-Info "`n[Step 2/5] Deploying Nginx monitoring components..."
    
    Print-Info "  2.1 - Applying nginx-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-configmap.yaml" -n $NAMESPACE
    Start-Sleep -Seconds 2
    
    Print-Info "  2.2 - Applying nginx-log-exporter-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-log-exporter-configmap.yaml" -n $NAMESPACE
    Start-Sleep -Seconds 2
    
    Print-Info "  2.3 - Applying nginx-log-exporter-service.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-log-exporter-service.yaml" -n $NAMESPACE
    Start-Sleep -Seconds 2
    
    Print-Info "  2.4 - Applying nginx-thrift-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/nginx-thrift-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "nginx-thrift" -Namespace $NAMESPACE -Timeout 300
    
    # Step 3: Deploy Redis monitoring components
    Print-Info "`n[Step 3/5] Deploying Redis monitoring components..."
    
    Print-Info "  3.1 - Applying home-timeline-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/home-timeline-redis-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "home-timeline-redis" -Namespace $NAMESPACE -Timeout 180
    
    Print-Info "  3.2 - Applying social-graph-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/social-graph-redis-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "social-graph-redis" -Namespace $NAMESPACE -Timeout 180
    
    Print-Info "  3.3 - Applying user-timeline-redis-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/user-timeline-redis-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "user-timeline-redis" -Namespace $NAMESPACE -Timeout 180
    
    # Step 4: Deploy MongoDB monitoring components
    Print-Info "`n[Step 4/5] Deploying MongoDB monitoring components..."
    
    Print-Info "  4.1 - Applying post-storage-mongodb-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/post-storage-mongodb-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "post-storage-mongodb" -Namespace $NAMESPACE -Timeout 180
    
    Print-Info "  4.2 - Applying user-timeline-mongodb-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/user-timeline-mongodb-deployment.yaml" -n $NAMESPACE
    Wait-ForDeployment -Deployment "user-timeline-mongodb" -Namespace $NAMESPACE -Timeout 180
    
    # Step 5: Deploy Loki stack using Helm
    Print-Info "`n[Step 5/5] Deploying Loki stack using Helm..."
    
    # Check if Helm is installed
    $helmInstalled = Get-Command helm -ErrorAction SilentlyContinue
    if (-not $helmInstalled) {
        Print-Error "Helm is not installed. Please install Helm first."
        exit 1
    }
    
    # Add Grafana Helm repo if not already added
    Print-Info "  5.1 - Adding Grafana Helm repository"
    $repoList = helm repo list 2>$null | Out-String
    if ($repoList -match "grafana") {
        Print-Info "Grafana repo already exists, updating..."
        helm repo update grafana
    } else {
        Print-Info "Adding Grafana repo..."
        helm repo add grafana https://grafana.github.io/helm-charts
        helm repo update
    }
    
    # Install or upgrade Loki stack
    Print-Info "  5.2 - Installing/Upgrading Loki stack"
    $lokiExists = helm list -n $MONITORING_NAMESPACE 2>$null | Select-String "loki-stack"
    if ($lokiExists) {
        Print-Warning "Loki-stack already exists, upgrading..."
        helm upgrade loki-stack grafana/loki-stack `
            -n $MONITORING_NAMESPACE `
            -f "$SCRIPT_DIR/loki_promtail_values.yaml" `
            --set loki.image.tag=2.9.3
    } else {
        Print-Info "Installing Loki-stack..."
        helm install loki-stack grafana/loki-stack `
            -n $MONITORING_NAMESPACE `
            -f "$SCRIPT_DIR/loki_promtail_values.yaml" `
            --set loki.image.tag=2.9.3
    }
    
    # Wait for Loki to be ready
    Print-Info "  5.3 - Waiting for Loki to be ready..."
    Start-Sleep -Seconds 10
    kubectl wait --for=condition=ready pod -l app=loki -n $MONITORING_NAMESPACE --timeout=300s 2>$null
    
    # Final status check
    Print-Info "`n=========================================="
    Print-Info "Deployment Summary"
    Print-Info "=========================================="
    
    Print-Info "`nDeployments in namespace '$NAMESPACE':"
    kubectl get deployments -n $NAMESPACE | Select-String -Pattern "nginx-thrift|redis|mongodb"
    
    Print-Info "`nPods in namespace '$MONITORING_NAMESPACE':"
    kubectl get pods -n $MONITORING_NAMESPACE
    
    Print-Info "`n=========================================="
    Print-Info "Monitoring Deployment Completed Successfully!"
    Print-Info "=========================================="
    
    Print-Info "`nNext Steps:"
    Print-Info "1. Verify all pods are running: kubectl get pods -n $NAMESPACE"
    Print-Info "2. Check Loki logs: kubectl logs -l app=loki -n $MONITORING_NAMESPACE"
    Print-Info "3. Check Promtail logs: kubectl logs -l app=promtail -n $MONITORING_NAMESPACE"
    Print-Info "4. Access Grafana (if deployed) to visualize logs and metrics"
}

# Run main function
try {
    Main
} catch {
    Print-Error "An error occurred: $_"
    exit 1
}

