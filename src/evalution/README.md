# 🌀 Chaos Workflow Monitor

## 📋 Overview
The **Chaos Workflow Monitor** service monitors **Airflow DAG workflows** and automatically sends their status to the **Chaos Workflow API** for centralized tracking.

### 🎯 Use Case
Automatically track **chaos engineering experiments** such as:
- 🧠 Memory Stress  
- 🔁 Container Restart  
- 📦 Node Cordon  

and sync them with external monitoring systems.

---

## 🚀 Quick Setup

### 1️⃣ Create a Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv chaos-workflow-env

# Activate virtual environment
source chaos-workflow-env/bin/activate

# Install dependencies
pip install psycopg2-binary requests

2️⃣ Test the Script
# Test run
python3 chaos-workflow.py

```
###🔧 Setup as a System Service
1️⃣ Create the Service File
sudo nano /etc/systemd/system/chaos-workflow-monitor.service
