🌀 Chaos Workflow Monitor
📋 Overview
This service monitors Airflow DAG workflows and automatically sends their status to the Chaos Workflow API for centralized tracking.
Use Case: Automatically track chaos engineering experiments (e.g., Memory Stress, Container Restart, Node Cordon, etc.) from Airflow and sync them with external monitoring systems.
________________________________________
🚀 Quick Setup
1. Create a Python Virtual Environment
# Create virtual environment
python3 -m venv chaos-workflow-env

# Activate virtual environment
source chaos-workflow-env/bin/activate

# Install dependencies
pip install psycopg2-binary requests
________________________________________
2. Test the Script
# Test run
python3 chaos-workflow.py
________________________________________
🔧 Setup as a System Service
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
________________________________________
2. Edit the Paths
⚠️ IMPORTANT: Replace the placeholder values with your actual configuration.
•	Replace your-username with your actual username (e.g., azureuser)
•	Replace /path/to/your/project with your actual project path (e.g., /home/azureuser/fault-injector)
________________________________________
3. Enable and Start the Service
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable chaos-workflow-monitor.service

# Start service
sudo systemctl start chaos-workflow-monitor.service
________________________________________
4. Check Service Status
sudo systemctl status chaos-workflow-monitor.service
________________________________________
5. View Logs
# Follow real-time logs
sudo journalctl -u chaos-workflow-monitor.service -f
________________________________________
📊 Service Management
# Start service
sudo systemctl start chaos-workflow-monitor.service

# Stop service
sudo systemctl stop chaos-workflow-monitor.service

# Restart service
sudo systemctl restart chaos-workflow-monitor.service

# Check status
sudo systemctl status chaos-workflow-monitor.service

# View logs
sudo journalctl -u chaos-workflow-monitor.service -f
________________________________________
✅ Expected Output
When working correctly, you should see logs similar to the following:
✅ Database connected! Found X DAG runs
🎧 Listening for workflow changes...
📨 Processing notification: Memory_Stress_Test
✅ Created workflow: Memory_Stress_Test_manual__2025-10-08 (ID: 123)


