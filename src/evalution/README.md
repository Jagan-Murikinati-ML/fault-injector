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

🔧 Setup as a System Service
1️⃣ Create the Service File
```
sudo nano /etc/systemd/system/chaos-workflow-monitor.service
```
Paste the following content:
```
[Unit]
Description=Chaos Workflow Monitor Service
After=network.target postgresql.service
Wants=network.target

[Service]
Type=simple
User=your-username
Group=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/chaos-workflow-env/bin/python3 -u /path/to/your/project/chaos-workflow.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
⚠️ Edit the Paths

Replace the placeholders with your actual configuration:

your-username → e.g., azureuser

/path/to/your/project → e.g., /home/azureuser/fault-injector


