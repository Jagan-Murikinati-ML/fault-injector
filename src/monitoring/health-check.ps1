# Health Check Script for Social Network Monitoring
# This script verifies all monitoring components are running correctly

$NAMESPACE = "social-network"
$MONITORING_NAMESPACE = "monitoring"

function Print-Header {
    param([string]$Message)
    Write-Host "`n==========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "==========================================" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Check if kubectl is available
$kubectlInstalled = Get-Command kubectl -ErrorAction SilentlyContinue
if (-not $kubectlInstalled) {
    Print-Error "kubectl not found. Please install kubectl first."
    exit 1
}

Print-Header "Social Network Monitoring Health Check"

# Check namespaces
Print-Header "1. Checking Namespaces"
$namespaceCheck = kubectl get namespace $NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Print-Success "Namespace '$NAMESPACE' exists"
} else {
    Print-Error "Namespace '$NAMESPACE' not found"
}

$monitoringNsCheck = kubectl get namespace $MONITORING_NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Print-Success "Namespace '$MONITORING_NAMESPACE' exists"
} else {
    Print-Error "Namespace '$MONITORING_NAMESPACE' not found"
}

# Check deployments in social-network namespace
Print-Header "2. Checking Deployments in '$NAMESPACE'"

$deployments = @(
    "nginx-thrift",
    "home-timeline-redis",
    "social-graph-redis",
    "user-timeline-redis",
    "post-storage-mongodb",
    "user-timeline-mongodb"
)

foreach ($deployment in $deployments) {
    $deploymentCheck = kubectl get deployment $deployment -n $NAMESPACE 2>$null
    if ($LASTEXITCODE -eq 0) {
        $ready = kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>$null
        $desired = kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>$null
        if ($ready -eq $desired) {
            Print-Success "$deployment`: $ready/$desired replicas ready"
        } else {
            Print-Warning "$deployment`: $ready/$desired replicas ready"
        }
    } else {
        Print-Error "$deployment`: not found"
    }
}

# Check pods in social-network namespace
Print-Header "3. Checking Pods in '$NAMESPACE'"
Write-Host ""
kubectl get pods -n $NAMESPACE | Select-String -Pattern "nginx-thrift|redis|mongodb"

# Check ConfigMaps
Print-Header "4. Checking ConfigMaps"
$configmaps = @(
    "nginx-thrift",
    "nginx-log-exporter-config"
)

foreach ($cm in $configmaps) {
    $cmCheck = kubectl get configmap $cm -n $NAMESPACE 2>$null
    if ($LASTEXITCODE -eq 0) {
        Print-Success "ConfigMap '$cm' exists"
    } else {
        Print-Error "ConfigMap '$cm' not found"
    }
}

# Check Services
Print-Header "5. Checking Services"
$svcCheck = kubectl get service nginx-log-exporter -n $NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Print-Success "Service 'nginx-log-exporter' exists"
} else {
    Print-Error "Service 'nginx-log-exporter' not found"
}

# Check Loki stack
Print-Header "6. Checking Loki Stack in '$MONITORING_NAMESPACE'"
$lokiRelease = helm list -n $MONITORING_NAMESPACE 2>$null | Select-String "loki-stack"
if ($lokiRelease) {
    Print-Success "Loki stack Helm release found"
    
    # Check Loki pods
    $lokiPods = kubectl get pods -n $MONITORING_NAMESPACE -l app=loki --no-headers 2>$null
    if ($lokiPods) {
        $lokiPodCount = ($lokiPods | Measure-Object).Count
        Print-Success "Loki pods running: $lokiPodCount"
    } else {
        Print-Error "No Loki pods found"
    }
    
    # Check Promtail pods
    $promtailPods = kubectl get pods -n $MONITORING_NAMESPACE -l app=promtail --no-headers 2>$null
    if ($promtailPods) {
        $promtailPodCount = ($promtailPods | Measure-Object).Count
        Print-Success "Promtail pods running: $promtailPodCount"
    } else {
        Print-Error "No Promtail pods found"
    }
} else {
    Print-Error "Loki stack not found"
}

# Check metrics endpoints
Print-Header "7. Checking Metrics Endpoints"

# Function to check if a pod has a specific container
function Test-Container {
    param(
        [string]$Pod,
        [string]$Container,
        [string]$Namespace
    )
    
    $containers = kubectl get pod $Pod -n $Namespace -o jsonpath="{.spec.containers[*].name}" 2>$null
    if ($containers -match $Container) {
        return $true
    } else {
        return $false
    }
}

# Check nginx-thrift exporters
$nginxPod = kubectl get pods -n $NAMESPACE -l service=nginx-thrift -o jsonpath='{.items[0].metadata.name}' 2>$null
if ($nginxPod) {
    if (Test-Container -Pod $nginxPod -Container "metrics" -Namespace $NAMESPACE) {
        Print-Success "Nginx prometheus exporter container found in $nginxPod"
    } else {
        Print-Error "Nginx prometheus exporter container not found"
    }
    
    if (Test-Container -Pod $nginxPod -Container "nginx-log-exporter" -Namespace $NAMESPACE) {
        Print-Success "Nginx log exporter container found in $nginxPod"
    } else {
        Print-Error "Nginx log exporter container not found"
    }
}

# Check Redis exporters
$redisDeployments = @("home-timeline-redis", "social-graph-redis", "user-timeline-redis")
foreach ($redisDeployment in $redisDeployments) {
    $redisPod = kubectl get pods -n $NAMESPACE -l service=$redisDeployment -o jsonpath='{.items[0].metadata.name}' 2>$null
    if ($redisPod) {
        if (Test-Container -Pod $redisPod -Container "redis-exporter" -Namespace $NAMESPACE) {
            Print-Success "Redis exporter found in $redisDeployment"
        } else {
            Print-Error "Redis exporter not found in $redisDeployment"
        }
    }
}

# Check MongoDB exporters
$mongoDeployments = @("post-storage-mongodb", "user-timeline-mongodb")
foreach ($mongoDeployment in $mongoDeployments) {
    $mongoPod = kubectl get pods -n $NAMESPACE -l service=$mongoDeployment -o jsonpath='{.items[0].metadata.name}' 2>$null
    if ($mongoPod) {
        if (Test-Container -Pod $mongoPod -Container "mongodb-exporter" -Namespace $NAMESPACE) {
            Print-Success "MongoDB exporter found in $mongoDeployment"
        } else {
            Print-Error "MongoDB exporter not found in $mongoDeployment"
        }
    }
}

# Summary
Print-Header "8. Summary"
Write-Host ""
Write-Host "To view detailed pod status:"
Write-Host "  kubectl get pods -n $NAMESPACE"
Write-Host "  kubectl get pods -n $MONITORING_NAMESPACE"
Write-Host ""
Write-Host "To check metrics endpoints:"
Write-Host "  kubectl port-forward -n $NAMESPACE deployment/nginx-thrift 9113:9113"
Write-Host "  kubectl port-forward -n $NAMESPACE deployment/nginx-thrift 4040:4040"
Write-Host "  kubectl port-forward -n $NAMESPACE deployment/home-timeline-redis 9121:9121"
Write-Host ""
Write-Host "To check logs:"
Write-Host "  kubectl logs -n $NAMESPACE deployment/nginx-thrift -c nginx-log-exporter"
Write-Host "  kubectl logs -n $MONITORING_NAMESPACE -l app=loki"
Write-Host "  kubectl logs -n $MONITORING_NAMESPACE -l app=promtail"
Write-Host ""

Print-Header "Health Check Complete"

