#!/usr/bin/env python3
"""
Simple test script to verify Kubernetes connection from within Docker container
"""

import os
import sys
from kubernetes import client, config
from chaosk8s import create_k8s_api_client

def test_k8s_connection():
    """Test Kubernetes connection and list basic cluster info"""
    
    print("🔍 Testing Kubernetes Connection...")
    print("=" * 50)
    
    # Print environment info
    print(f"🔍 KUBECONFIG: {os.environ.get('KUBECONFIG', 'NOT SET')}")
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Python path: {sys.path}")
    
    # Check kubeconfig file
    kubeconfig_path = os.environ.get('KUBECONFIG')
    if kubeconfig_path:
        if os.path.exists(kubeconfig_path):
            print(f"✅ KUBECONFIG file exists: {kubeconfig_path}")
            with open(kubeconfig_path, 'r') as f:
                content = f.read()
                print(f"📄 KUBECONFIG content length: {len(content)} characters")
        else:
            print(f"❌ KUBECONFIG file not found: {kubeconfig_path}")
    
    # Test connection using chaosk8s method
    try:
        print("\n🔗 Testing connection using chaosk8s...")
        api = create_k8s_api_client(None)
        v1 = client.CoreV1Api(api)
        
        # Try to list namespaces
        namespaces = v1.list_namespace()
        print(f"✅ Successfully connected! Found {len(namespaces.items)} namespaces:")
        for ns in namespaces.items[:5]:  # Show first 5
            print(f"   - {ns.metadata.name}")
            
        # Try to list pods in default namespace
        pods = v1.list_namespaced_pod(namespace="default")
        print(f"✅ Found {len(pods.items)} pods in default namespace:")
        for pod in pods.items[:5]:  # Show first 5
            print(f"   - {pod.metadata.name} (Status: {pod.status.phase})")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_k8s_connection()
    sys.exit(0 if success else 1)
