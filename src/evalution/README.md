# 🌀 Chaos Workflow Monitor

## 📋 Overview
This service monitors **Airflow DAG workflows** and automatically sends their status to the **Chaos Workflow API** for centralized tracking.

**Use Case:**  
Automatically track chaos engineering experiments (e.g., **Memory Stress**, **Container Restart**, **Node Cordon**, etc.) from Airflow and sync them with external monitoring systems.

---

## 🚀 Quick Setup

### 1️⃣ Create a Python Virtual Environment

#### Create virtual environment
```bash
python3 -m venv chaos-workflow-env
Activate virtual environment
bash
Copy code
source chaos-workflow-env/bin/activate
Install dependencies
bash
Copy code
pip install psycopg2-binary requests
2️⃣ Test the Script
Test run
bash
Copy code
python3 chaos-workflow.py
🔧 Setup as a System Service
Create the Service File
bash
Copy code
sudo nano /etc/systemd/system/chaos-workflow-monitor.service
Paste the following content:
ini
Copy code
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
⚠️ Edit the Paths
Replace the placeholders with your actual configuration:

your-username → e.g., azureuser

/path/to/your/project → e.g., /home/azureuser/fault-injector

Enable and Start the Service
Reload systemd
bash
Copy code
sudo systemctl daemon-reload
Enable service (start on boot)
bash
Copy code
sudo systemctl enable chaos-workflow-monitor.service
Start service
bash
Copy code
sudo systemctl start chaos-workflow-monitor.service
Check Service Status
bash
Copy code
sudo systemctl status chaos-workflow-monitor.service
View Logs
Follow real-time logs
bash
Copy code
sudo journalctl -u chaos-workflow-monitor.service -f
📊 Service Management
Action	Command
Start service	sudo systemctl start chaos-workflow-monitor.service
Stop service	sudo systemctl stop chaos-workflow-monitor.service
Restart service	sudo systemctl restart chaos-workflow-monitor.service
Check status	sudo systemctl status chaos-workflow-monitor.service
View logs	sudo journalctl -u chaos-workflow-monitor.service -f

✅ Expected Output
When working correctly, you should see logs similar to the following:

yaml
Copy code
✅ Database connected!
Found X DAG runs
🎧 Listening for workflow changes...
📨 Processing notification: Memory_Stress_Test
✅ Created workflow: Memory_Stress_Test_manual__2025-10-08 (ID: 123)
