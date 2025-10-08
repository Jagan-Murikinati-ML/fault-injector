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
```

## 2️⃣ Test the Script
### Test run

```
python3 chaos-workflow.py
```

## 🔧 Setup as a System Service
### 1️⃣ Create the Service File
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
## ⚠️ Edit the Paths

Replace the placeholders with your actual configuration:

your-username → e.g., azureuser

/path/to/your/project → e.g., /home/azureuser/fault-injector

## 3️⃣ Enable and Start the Service
```
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable chaos-workflow-monitor.service

# Start service
sudo systemctl start chaos-workflow-monitor.service

```
## 4️⃣ Check Service Status
```
sudo systemctl status chaos-workflow-monitor.service

```
## 5️⃣ View Logs
```
# Follow real-time logs
sudo journalctl -u chaos-workflow-monitor.service -f
```
📊 Service Management
```
| Action             | Command                                                 |
| ------------------ | ------------------------------------------------------- |
| ▶️ Start Service   | `sudo systemctl start chaos-workflow-monitor.service`   |
| ⏸ Stop Service     | `sudo systemctl stop chaos-workflow-monitor.service`    |
| 🔁 Restart Service | `sudo systemctl restart chaos-workflow-monitor.service` |
| 📋 Check Status    | `sudo systemctl status chaos-workflow-monitor.service`  |
| 📜 View Logs       | `sudo journalctl -u chaos-workflow-monitor.service -f`  |

```
## ✅ Expected Output

When working correctly, you should see logs similar to the following:
```
✅ Database connected! Found X DAG runs
🎧 Listening for workflow changes...
📨 Processing notification: Memory_Stress_Test
✅ Created workflow: Memory_Stress_Test_manual__2025-10-08 (ID: 123)
```







