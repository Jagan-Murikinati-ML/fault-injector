# Kubernetes Actions - Social Network Reinitializer

## 📋 Overview
This tool reinitializes the **Social Network** application by clearing all data (**Redis, Memcached, MongoDB**) and restarting pods, then populating with default users and posts.

### 🎯 Use Case
Complete reset and reinitialization of the social network microservices application for testing or **chaos engineering experiments**.

### 🔧 What it does
- 🧹 Clears all data from **Redis, Memcached, and MongoDB**  
- 🔄 Restarts core microservices pods  
- 👥 Creates default users and social connections  
- 📝 Posts sample data for testing  
- ✅ Complete application reset in one command  

---

## 🚀 Quick Setup

### 1️⃣ Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv k8s-actions-env

# Activate virtual environment
source k8s-actions-env/bin/activate

# Install dependencies
pip install kubernetes chaostoolkit chaostoolkit-kubernetes aiohttp
```
### 2️⃣ Setup Kubernetes Access
```
bash
Copy code
# Ensure kubectl is configured
kubectl get pods

# Or set KUBECONFIG if needed
export KUBECONFIG=/path/to/your/kubeconfig
```
### 3️⃣ Verify Dependencies
Make sure you have the required directory structure:
```
markdown
Copy code
project-root/
├── kubernetes_actions.py
├── kubernetes_actions.json
└── socialNetwork/
    └── scripts/
        └── init_social_graph.py
```
### 🔧 Execution
Run with Chaos Toolkit:
```
bash
Copy code
# Activate virtual environment
source k8s-actions-env/bin/activate

# Execute the chaos experiment
chaos run kubernetes_actions.json
```
### ✅ Expected Output
```
css
Copy code
[INFO] Starting full social network reset...
[INFO] Clearing Redis data...
[INFO] Clearing Memcached data...
[INFO] Dropping MongoDB databases...
[INFO] Restarting core microservices...
[INFO] ✅ Successfully restarted social-graph-service
[INFO] ✅ Successfully restarted user-service
[INFO] ✅ Successfully restarted post-storage-service
[INFO] Waiting 180 seconds for services to restart...
[INFO] Reinitializing social network data...
[INFO] Social network reinitialization completed successfully
```
🧩 Notes
Ensure kubectl has access to your Kubernetes cluster.

Keep your Python virtual environment active when running the script.

This script performs a complete reset, so all existing data will be lost.
