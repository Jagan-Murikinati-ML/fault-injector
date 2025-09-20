import subprocess
import yaml
import os
import sys
import time
from pymongo import MongoClient

# Kubernetes details
POD_NAME = "user-mongodb-78f75fc787-kd4bg"    # adjust if different
NAMESPACE = "default"          # adjust if different
MONGOD_CONF_PATH = "/social-network-microservices/config/mongod.conf"
BACKUP_PATH = "/social-network-microservices/config/mongod.conf.bak"
MONGO_URI = "mongodb://4.149.182.40:27017"  # LoadBalancer IP


def run_kubectl_exec(cmd):
    """Run command inside the MongoDB pod"""
    full_cmd = ["kubectl", "exec", "-n", NAMESPACE, POD_NAME, "--"] + cmd
    proc = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"Command failed: {proc.stderr.strip()}")
        sys.exit(1)
    return proc.stdout.strip()


def copy_to_pod(src, dest):
    """Copy file from local to pod"""
    # First, remove the destination file if it exists
    try:
        run_kubectl_exec(["rm", "-f", dest])
        print(f"Removed existing file: {dest}")
    except:
        print(f"File {dest} didn't exist or couldn't be removed")
    
    # Now copy the file
    try:
        result = subprocess.run(
            ["kubectl", "cp", src, f"{NAMESPACE}/{POD_NAME}:{dest}"],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            print(f"kubectl cp failed: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
        print(f"Successfully copied {src} to {dest}")
    except Exception as e:
        print(f"Copy failed: {e}")
        raise


def get_mongodb_pod_name():
    """Get the current MongoDB pod name dynamically"""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", NAMESPACE, "-l", "app=user-mongodb", "-o", "jsonpath={.items[0].metadata.name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # Fallback to hardcoded name
        return POD_NAME

def restart_pod():
    """Delete pod to force restart"""
    current_pod = get_mongodb_pod_name()
    try:
        subprocess.run(["kubectl", "delete", "pod", current_pod, "-n", NAMESPACE], check=True)
        print(f"Deleted pod {current_pod}, Kubernetes will restart it automatically")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete pod {current_pod}: {e}")
        raise


def update_mongodb_max_connections(new_max_connections: int):
    """Update MongoDB ConfigMap with new maxIncomingConnections and restart deployment"""
    print(f"Updating MongoDB maxIncomingConnections to {new_max_connections}...")
    
    try:
        # Create updated ConfigMap content
        updated_config = f"""apiVersion: v1
data:
  mongod.conf: |
    net:
      tls:
        mode: disabled
      maxIncomingConnections: {new_max_connections}
kind: ConfigMap
metadata:
  name: user-mongodb
  namespace: default
"""
        
        # Write to temp file and apply
        with open('/tmp/updated-mongodb-configmap.yaml', 'w') as f:
            f.write(updated_config)
        
        # Apply the updated ConfigMap
        result = subprocess.run(
            ["kubectl", "apply", "-f", "/tmp/updated-mongodb-configmap.yaml"],
            capture_output=True, text=True, check=True
        )
        print("ConfigMap updated successfully")
        
        # Restart the deployment to pick up new config
        subprocess.run(["kubectl", "rollout", "restart", "deployment/user-mongodb"], check=True)
        print("Deployment restart initiated...")
        
        # Wait for rollout to complete
        subprocess.run(["kubectl", "rollout", "status", "deployment/user-mongodb", "--timeout=120s"], check=True)
        print(f"MongoDB restarted with maxIncomingConnections: {new_max_connections}")
        
        # Wait a bit for MongoDB to fully start
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"Failed to update MongoDB configuration: {e}")
        return False


def rollback_mongodb_max_connections():
    """Rollback MongoDB ConfigMap to original configuration"""
    print("Rolling back MongoDB configuration...")
    
    try:
        # Restore original ConfigMap
        original_config = """apiVersion: v1
data:
  mongod.conf: |
    net:
      tls:
        mode: disabled
kind: ConfigMap
metadata:
  name: user-mongodb
  namespace: default
"""
        
        with open('/tmp/original-mongodb-configmap.yaml', 'w') as f:
            f.write(original_config)
        
        subprocess.run(["kubectl", "apply", "-f", "/tmp/original-mongodb-configmap.yaml"], check=True)
        subprocess.run(["kubectl", "rollout", "restart", "deployment/user-mongodb"], check=True)
        subprocess.run(["kubectl", "rollout", "status", "deployment/user-mongodb", "--timeout=120s"], check=True)
        
        print("MongoDB configuration rolled back successfully")
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"Failed to rollback MongoDB configuration: {e}")
        return False


def exhaust_mongo_connections(max_connections: int = 100, hold_until_rollback: bool = True):
    """Open connections until exhaustion and hold them alive"""
    clients = []
    total = 0
    try:
        print(f"Attempting to open {max_connections} connections...")
        while total < max_connections:
            client = MongoClient(
                MONGO_URI, 
                maxPoolSize=1, 
                connect=True, 
                serverSelectionTimeoutMS=10000,
                socketTimeoutMS=3000,
                maxIdleTimeMS=3000
            )
            client.admin.command("ping")
            clients.append(client)
            total += 1
            print(f"Opened connection #{total}")
            
    except Exception as e:
        print(f"Connection exhausted after {total} successful connections: {e}")
    
    if hold_until_rollback and clients:
        print(f"Holding {len(clients)} connections alive until experiment ends...")
        return len(clients)  # Return count instead of client objects
    else:
        for c in clients:
            try:
                c.close()
            except:
                pass
        return 0  # Return count instead of empty list


def update_mongodb_max_connections_runtime(new_max_connections: int):
    """Update connection limits using available runtime parameters"""
    print(f"Setting connPoolMaxConnsPerHost to {new_max_connections} via admin command...")
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Get current value BEFORE change
        current_before = client.admin.command("getParameter", connPoolMaxConnsPerHost=1)
        print(f"BEFORE: connPoolMaxConnsPerHost = {current_before.get('connPoolMaxConnsPerHost')}")
        
        # Set the parameter at runtime
        result = client.admin.command("setParameter", connPoolMaxConnsPerHost=new_max_connections)
        print(f"setParameter result: {result}")
        
        # Verify the change AFTER
        current_after = client.admin.command("getParameter", connPoolMaxConnsPerHost=1)
        print(f"AFTER: connPoolMaxConnsPerHost = {current_after.get('connPoolMaxConnsPerHost')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Failed to update connPoolMaxConnsPerHost: {e}")
        return False
