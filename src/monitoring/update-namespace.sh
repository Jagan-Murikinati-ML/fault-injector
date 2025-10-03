#!/bin/bash

# Script to update namespace in all YAML files
# Usage: ./update-namespace.sh <new-namespace>

NEW_NAMESPACE=${1:-social-network}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating namespace to: $NEW_NAMESPACE"

# List of YAML files to update (excluding loki values file)
YAML_FILES=(
    "nginx-configmap.yaml"
    "nginx-log-exporter-configmap.yaml"
    "nginx-log-exporter-service.yaml"
    "nginx-thrift-deployment.yaml"
    "home-timeline-redis-deployment.yaml"
    "post-storage-mongodb-deployment.yaml"
    "social-graph-redis-deployment.yaml"
    "user-timeline-mongodb-deployment.yaml"
    "user-timeline-redis-deployment.yaml"
)

for file in "${YAML_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo "Updating $file..."
        # Use sed to replace namespace: default with namespace: <new-namespace>
        sed -i.bak "s/namespace: default/namespace: $NEW_NAMESPACE/g" "$SCRIPT_DIR/$file"
        echo "  ✓ Updated $file"
    else
        echo "  ✗ File not found: $file"
    fi
done

echo ""
echo "Namespace update complete!"
echo "Backup files created with .bak extension"
echo ""
echo "To apply changes, run: ./deploy-monitoring.sh"

