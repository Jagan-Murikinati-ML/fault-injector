# Script to update namespace in all YAML files
# Usage: .\update-namespace.ps1 -NewNamespace "social-network"

param(
    [string]$NewNamespace = "social-network"
)

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Updating namespace to: $NewNamespace" -ForegroundColor Green

# List of YAML files to update (excluding loki values file)
$YAML_FILES = @(
    "nginx-configmap.yaml",
    "nginx-log-exporter-configmap.yaml",
    "nginx-log-exporter-service.yaml",
    "nginx-thrift-deployment.yaml",
    "home-timeline-redis-deployment.yaml",
    "post-storage-mongodb-deployment.yaml",
    "social-graph-redis-deployment.yaml",
    "user-timeline-mongodb-deployment.yaml",
    "user-timeline-redis-deployment.yaml"
)

foreach ($file in $YAML_FILES) {
    $filePath = Join-Path $SCRIPT_DIR $file
    
    if (Test-Path $filePath) {
        Write-Host "Updating $file..." -ForegroundColor Yellow
        
        # Read file content
        $content = Get-Content $filePath -Raw
        
        # Create backup
        $backupPath = "$filePath.bak"
        Copy-Item $filePath $backupPath -Force
        
        # Replace namespace: default with namespace: <new-namespace>
        $updatedContent = $content -replace 'namespace: default', "namespace: $NewNamespace"
        
        # Write updated content
        Set-Content -Path $filePath -Value $updatedContent -NoNewline
        
        Write-Host "  ✓ Updated $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ File not found: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Namespace update complete!" -ForegroundColor Green
Write-Host "Backup files created with .bak extension" -ForegroundColor Cyan
Write-Host ""
Write-Host "To apply changes, run: .\deploy-monitoring.ps1" -ForegroundColor Yellow

