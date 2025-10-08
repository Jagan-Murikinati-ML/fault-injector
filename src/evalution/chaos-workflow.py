import psycopg2
import json
import requests
import time
import threading
from datetime import datetime

class WorkflowMonitor:
    def __init__(self):
        self.db_config = {
            'host': '145.132.105.207',
            'port': 5433,
            'database': 'airflow',
            'user': 'airflow',
            'password': 'airflow'
        }
        # Updated ngrok API endpoint

        self.api_base_url = "http://20.120.234.156/v1/chaos-workflow-run"
        self.workflow_ids = {}  # Track workflow_name -> workflow_id mapping

    def setup_workflow_tracking_table(self):
        """Create table to persist workflow ID mappings"""
        conn = psycopg2.connect(**self.db_config)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_tracking (
                workflow_name VARCHAR(255) PRIMARY KEY,
                workflow_id INTEGER NOT NULL,
                dag_id VARCHAR(255) NOT NULL,
                run_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        print("✅ Workflow tracking table setup complete")
        conn.close()

    def clear_all_workflow_tracking(self):
        """Clear all workflow tracking on startup to start fresh"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("DELETE FROM workflow_tracking;")
            print("🧹 Cleared all workflow tracking records on startup")

            # Also clear in-memory tracking
            self.workflow_ids.clear()
            print("🧹 Cleared in-memory workflow IDs")

            conn.close()
        except Exception as e:
            print(f"⚠️ Error clearing workflow tracking: {e}")

    def save_workflow_id(self, workflow_name, workflow_id, dag_id, run_id):
        """Persist workflow ID ONLY for running workflows"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workflow_tracking (workflow_name, workflow_id, dag_id, run_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (workflow_name) DO UPDATE SET
                    workflow_id = %s,
                    dag_id = %s,
                    run_id = %s
            """, (workflow_name, workflow_id, dag_id, run_id, workflow_id, dag_id, run_id))
            conn.commit()
            conn.close()

            # Also store in memory
            self.workflow_ids[workflow_name] = workflow_id
            print(f"💾 Saved RUNNING workflow ID: {workflow_name} -> {workflow_id}")

        except Exception as e:
            print(f"❌ Error saving workflow ID: {e}")

    def remove_workflow_id(self, workflow_name):
        """Remove workflow ID when workflow completes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workflow_tracking WHERE workflow_name = %s", (workflow_name,))   
            conn.commit()
            conn.close()

            # Also remove from memory
            if workflow_name in self.workflow_ids:
                del self.workflow_ids[workflow_name]

            print(f"🗑️ Removed completed workflow ID: {workflow_name}")

        except Exception as e:
            print(f"❌ Error removing workflow ID: {e}")

    def get_workflow_id(self, workflow_name):
        """Get workflow ID from memory or database"""
        # Check memory first
        if workflow_name in self.workflow_ids:
            return self.workflow_ids[workflow_name]

        # Check database
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT workflow_id FROM workflow_tracking WHERE workflow_name = %s", (workflow_name,))
            result = cursor.fetchone()
            conn.close()

            if result:
                workflow_id = result[0]
                self.workflow_ids[workflow_name] = workflow_id  # Cache it
                print(f"🔍 Found workflow ID in database: {workflow_name} -> {workflow_id}")
                return workflow_id

        except Exception as e:
            print(f"❌ Error getting workflow ID: {e}")

        return None

    def recover_missed_notifications(self):
        """Recover any notifications missed during disconnection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Find recently completed DAGs that might have been missed
            cursor.execute("""
                SELECT dag_id, run_id, state, end_date, start_date
                FROM dag_run
                WHERE state IN ('success', 'failed', 'skipped', 'upstream_failed')
                AND end_date > NOW() - INTERVAL '10 minutes'
                ORDER BY end_date DESC
            """)

            recovered_count = 0
            for dag_id, run_id, state, end_date, start_date in cursor.fetchall():
                #🚫 Skip Continuous_Load workflows in recovery too
                if 'continuous_load' in dag_id.lower():
                    continue
                workflow_name = f"{dag_id}_{run_id}"
                workflow_id = self.get_workflow_id(workflow_name)
                if workflow_id:
                    # Check if already completed via API
                    if not self.is_workflow_completed(workflow_id):
                        print(f"🔄 Recovering missed completion: {workflow_name} -> {state}")
                        self.update_workflow(dag_id, run_id, state, end_date)
                        recovered_count += 1

            if recovered_count > 0:
                print(f"✅ Recovered {recovered_count} missed notifications")
            else:
                print("✅ No missed notifications to recover")

            conn.close()

        except Exception as e:
            print(f"❌ Error in recovery: {e}")

    def is_workflow_completed(self, workflow_id):
        """Check if workflow is already completed via API"""
        try:
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Airflow-Monitor/1.0'
            }
            response = requests.get(f"{self.api_base_url}/{workflow_id}", headers=headers, timeout=10)   
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'completed'
        except:
            pass
        return False

    def periodic_sync(self):
        """Run periodic sync every 60 seconds"""
        while True:
            try:
                time.sleep(60)
                print("🔍 Running periodic sync...")
                self.recover_missed_notifications()
            except Exception as e:
                print(f"❌ Periodic sync error: {e}")

    def get_workflow_alerts(self, dag_id):
        """Get workflow-specific alerts based on DAG ID patterns"""
        dag_id_lower = dag_id.lower()

        if 'container' in dag_id_lower and 'restart' in dag_id_lower:
            return ["nginx_http_response_5xx_errors_high", "pod_container_restart"]
        elif 'cordon' in dag_id_lower or 'uncordon' in dag_id_lower or 'node' in dag_id_lower:
            return ["nginx_http_response_5xx_errors_high", "node_unschedulable"]
        else:
            # Default alerts for other workflows
            return [f"{dag_id}_alert", "WorkflowStatusChange"]

    def get_root_cause_from_db(self, dag_id, state=None):
        """Get workflow-specific root cause from database (always fetch regardless of state)"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            dag_id_lower = dag_id.lower()
            cursor.execute("""
                SELECT root_cause_description
                FROM workflow_rootcause_mapping
                WHERE %s LIKE CONCAT('%%', workflow_pattern, '%%')
                ORDER BY LENGTH(workflow_pattern) DESC
                LIMIT 1
            """, (dag_id_lower,))

            result = cursor.fetchone()
            conn.close()

            if result:
                print(f"🧠 Found expected root cause mapping for {dag_id}")
                return result[0]
            else:
                print(f"⚠️ No root cause mapping found for {dag_id}")
                return f"Chaos workflow triggered from DAG {dag_id}"

        except Exception as e:
            print(f"❌ Error fetching root cause from DB: {e}")
            return f"Chaos workflow triggered from DAG {dag_id}"

    def create_workflow(self, dag_id, run_id, state, start_date=None, end_date=None):
        """POST: Create new workflow using correct schema and expected root cause"""
        # 🚫 FIRST LINE - Skip Continuous_Load workflows EVERYWHERE
        if 'continuous_load' in dag_id.lower():
            print(f"⏭️ BLOCKED in create_workflow: {dag_id}_{run_id}")
            return False
        status_mapping = {
            'running': 'started',
            'success': 'completed',
            'failed': 'failed',
            'queued': 'started',
            'up_for_retry': 'failed',
            'up_for_reschedule': 'started',
            'upstream_failed': 'failed',
            'skipped': 'completed'
        }

        mapped_status = status_mapping.get(state, state)
        start_time = (
            start_date if isinstance(start_date, str)
            else start_date.isoformat() if start_date
            else datetime.now().isoformat()
        )
        end_time = (
            end_date if isinstance(end_date, str)
            else end_date.isoformat() if end_date
            else None
        )

        workflow_name = f"{dag_id}_{run_id}"
        alert_names = self.get_workflow_alerts(dag_id)

        # 🧠 Get expected root cause description from DB (always, not just success)
        root_cause = self.get_root_cause_from_db(dag_id, state)
        if not root_cause:
            root_cause = f"Chaos workflow triggered from DAG {dag_id}"

        # ✅ Include end_time + root cause as description
        payload = {
            "workflow_runs": [
                {
                    "workflow_name": workflow_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": mapped_status,
                    "alert_names": alert_names,
                    "workflow_description": root_cause
                }
            ]
        }

        print(f"📤 Sending payload to API:\n{json.dumps(payload, indent=2)}")

        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Airflow-Monitor/1.0'
            }

            response = requests.post(
                self.api_base_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            print(f"✅ POST Response: {response.status_code}")
            print(f"📄 Response: {response.text}")

            if response.status_code in [200, 201, 202]:
                result = response.json()

                # ✅ Handle correct response format
                if isinstance(result, dict) and "workflow_runs" in result:
                    workflow_data = result["workflow_runs"][0]
                elif isinstance(result, list) and len(result) > 0:
                    workflow_data = result[0]
                else:
                    workflow_data = result

                if workflow_data and "id" in workflow_data:
                    workflow_id = workflow_data["id"]
                    self.save_workflow_id(workflow_name, workflow_id, dag_id, run_id)
                    print(f"✅ Created workflow: {workflow_name} (ID: {workflow_id})")
                    return workflow_id

                print("⚠️ Workflow created but no ID returned")
                return True
            else:
                print(f"❌ Failed to create workflow: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error creating workflow: {e}")
            return False


    def update_workflow(self, dag_id, run_id, state, end_date=None):
        """PUT: Update workflow and REMOVE ID when completed"""
        workflow_name = f"{dag_id}_{run_id}"
        workflow_id = self.get_workflow_id(workflow_name)

        if not workflow_id:
            print(f"⚠️ No workflow ID found for {workflow_name}, cannot update")
            return False

        # Map Airflow states to API statuses
        status_mapping = {
            'success': 'completed',
            'failed': 'failed',
            'upstream_failed': 'failed',
            'skipped': 'completed',
            'running': 'started',
            'queued': 'started'
        }

        mapped_status = status_mapping.get(state, state)

        updates = {
            "status": mapped_status
        }

        if end_date:
            end_time = end_date if isinstance(end_date, str) else end_date.isoformat()
            updates["end_time"] = end_time
        else:
            updates["end_time"] = datetime.utcnow().isoformat()

        print(f"📤 Sending PUT payload for workflow_id={workflow_id}:\n{json.dumps(updates, indent=2)}") 

        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Airflow-Monitor/1.0'
            }

            response = requests.put(
                f"{self.api_base_url}/{workflow_id}",
                json=updates,
                headers=headers,
                timeout=30
            )

            print(f"✅ PUT Response: {response.status_code}")
            print(f"📄 Response: {response.text}")

            if response.status_code in [200, 201, 202]:
                print(f"✅ Updated workflow: {workflow_name} -> {mapped_status}")

                # remove completed workflow
                if mapped_status in ['completed', 'failed']:
                    self.remove_workflow_id(workflow_name)
                return True

            elif response.status_code == 404:
                print(f"⚠️ Workflow ID {workflow_id} not found in API")
                self.remove_workflow_id(workflow_name)  # cleanup
                return False

            elif response.status_code == 422:
                print(f"⚠️ Validation failed for PUT payload: {response.text}")
                return False

            else:
                print(f"❌ Failed to update workflow: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error updating workflow: {e}")
            return False


    def setup_rootcause_table(self):
        """Setup root cause mapping table with updated mappings"""
        conn = psycopg2.connect(**self.db_config)
        conn.autocommit = True
        cursor = conn.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_rootcause_mapping (
                id SERIAL PRIMARY KEY,
                workflow_pattern VARCHAR(255) NOT NULL,
                root_cause_description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workflow_pattern
            ON workflow_rootcause_mapping(workflow_pattern)
        """)

        # Insert container restart mapping if not exists
        cursor.execute("""
            INSERT INTO workflow_rootcause_mapping (workflow_pattern, root_cause_description)
            SELECT
                'container_restart',
                'As part of container restart workflow, compose-post-service container running inside the pod with label "app=compose-post-service" is restarted continuously for 7 minutes. Due to this, some of the http requests to the endpoint /post/compose in the social networking application fails with 500 error as the container is not up and running to cater to the http requests.'
            WHERE NOT EXISTS (
                SELECT 1 FROM workflow_rootcause_mapping
                WHERE workflow_pattern = 'container_restart'
            )
        """)


        # Insert cordon node mapping if not exists
        cursor.execute("""
            INSERT INTO workflow_rootcause_mapping (workflow_pattern, root_cause_description)
            SELECT 'cordon', 'All the nodes are cordoned by fault generation tool for 5 minutes. During this time, fault generation tool deletes post-storage-service pod. Since the nodes are cordoned, deleted pod will not be able to join any node, So all the http requests will fail with HTTP 5xx errors due to service unavailability caused by cordoning the nodes.'
            WHERE NOT EXISTS (
                SELECT 1 FROM workflow_rootcause_mapping
                WHERE workflow_pattern = 'cordon'
            )
        """)

        # Insert uncordon node mapping if not exists (same as cordon)
        cursor.execute("""
            INSERT INTO workflow_rootcause_mapping (workflow_pattern, root_cause_description)
            SELECT 'uncordon', 'All the nodes are cordoned by fault generation tool for 5 minutes. During this time, fault generation tool deletes post-storage-service pod. Since the nodes are cordoned, deleted pod will not be able to join any node, So all the http requests will fail with HTTP 5xx errors due to service unavailability caused by cordoning the nodes.'
            WHERE NOT EXISTS (
                SELECT 1 FROM workflow_rootcause_mapping
                WHERE workflow_pattern = 'uncordon'
            )
        """)

        # Insert node pattern mapping if not exists (same as cordon)
        cursor.execute("""
            INSERT INTO workflow_rootcause_mapping (workflow_pattern, root_cause_description)
            SELECT 'node', 'All the nodes are cordoned by fault generation tool for 5 minutes. During this time, fault generation tool deletes post-storage-service pod. Since the nodes are cordoned, deleted pod will not be able to join any node, So all the http requests will fail with HTTP 5xx errors due to service unavailability caused by cordoning the nodes.'
            WHERE NOT EXISTS (
                SELECT 1 FROM workflow_rootcause_mapping
                WHERE workflow_pattern = 'node'
            )
        """)

        print("✅ Root cause mapping table setup complete")
        conn.close()

    def setup_trigger(self):
        """Setup database trigger and notification"""
        conn = psycopg2.connect(**self.db_config)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("""
        CREATE OR REPLACE FUNCTION notify_workflow_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND OLD.state != NEW.state) THEN
                PERFORM pg_notify('workflow_changes',
                    json_build_object(
                        'dag_id', NEW.dag_id,
                        'run_id', NEW.run_id,
                        'state', NEW.state,
                        'start_date', NEW.start_date,
                        'end_date', NEW.end_date,
                        'operation', TG_OP
                    )::text
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
        DROP TRIGGER IF EXISTS workflow_change_trigger ON dag_run;
        CREATE TRIGGER workflow_change_trigger
            AFTER INSERT OR UPDATE ON dag_run
            FOR EACH ROW
            EXECUTE FUNCTION notify_workflow_change();
        """)

        print("✅ Database trigger setup complete")
        conn.close()

    def handle_notification(self, payload):
        """Handle database notification with POST/PUT logic"""
        try:
            data = json.loads(payload)
            print(f"📨 Processing notification: {data}")

            dag_id = data['dag_id']
            run_id = data['run_id']
            state = data['state']
            operation = data['operation']
            workflow_name = f"{dag_id}_{run_id}"

           # 🚫 Skip Continuous_Load workflows entirely
            if 'continuous_load' in dag_id.lower():
                print(f"⏭️ Skipping Continuous_Load workflow: {workflow_name}")
                return

            if operation == 'INSERT':
                # New workflow - POST to create
                print(f"🆕 Creating new workflow: {workflow_name}")
                self.create_workflow(
                    dag_id, run_id, state,
                    data.get('start_date')
                )
            else:
                # UPDATE - only PUT for final states
                final_states = ['success', 'failed', 'skipped', 'upstream_failed']

                if state in final_states:
                    print(f"🔄 Updating workflow to final state: {workflow_name} -> {state}")
                    self.update_workflow(
                        dag_id, run_id, state,
                        data.get('end_date')
                    )
                else:
                    print(f"⏳ Ignoring intermediate state: {workflow_name} -> {state}")

        except Exception as e:
            print(f"❌ Error handling notification: {e}")

    def listen_for_changes(self):
        """Listen for database notifications with robust recovery"""
        connection_count = 0

        while True:
            try:
                connection_count += 1
                # Use keepalives BUT still have recovery as backup
                conn = psycopg2.connect(
                    **self.db_config,
                    keepalives_idle=30,      # Start keepalives after 30s of inactivity
                    keepalives_interval=10,  # Send keepalive every 10s
                    keepalives_count=3,      # Allow 3 failed keepalives before disconnect
                    connect_timeout=30,      # 30s to establish connection
                    application_name='WorkflowMonitor'
                )
                conn.autocommit = True
                cursor = conn.cursor()

                cursor.execute("LISTEN workflow_changes;")
                print(f"🎧 Listening with keepalives + recovery backup (Connection #{connection_count})")

                # ALWAYS recover on reconnection (safety net)
                if connection_count > 1:
                    print("🔍 Recovering missed notifications...")
                    self.recover_missed_notifications()

                last_heartbeat = time.time()

                while True:
                    conn.poll()

                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        print(f"📨 Received notification: {notify.payload}")
                        self.handle_notification(notify.payload)
                        last_heartbeat = time.time()

                    # Light heartbeat every 60 seconds
                    current_time = time.time()
                    if current_time - last_heartbeat > 60:
                        try:
                            cursor.execute("SELECT 1;")
                            print(f"   Connection alive at {datetime.now().strftime('%H:%M:%S')}")       
                            last_heartbeat = current_time
                        except Exception as e:
                            print(f"💔 Heartbeat failed: {e}")
                            raise psycopg2.OperationalError("Heartbeat failed")

                    time.sleep(0.1)

            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                print(f"🔄 Connection lost: {e}")
                print("🔄 Reconnecting in 5 seconds...")
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                print("\n🛑 Stopping workflow monitor...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(5)
                continue
            finally:
                try:
                    conn.close()
                    print(f"🔌 Connection #{connection_count} closed")
                except:
                    pass

    def start_monitoring(self):
        """Start the monitoring process"""
        print("🚀 Starting Workflow Monitor...")
        print(f"📊 Database: {self.db_config['host']}:{self.db_config['port']}")
        print(f"🌐 API Endpoint: {self.api_base_url}")

        try:
            print("🔍 Testing database connection...")
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dag_run;")
            count = cursor.fetchone()[0]
            print(f"✅ Database connected! Found {count} DAG runs")
            conn.close()

            # CLEAR ALL IDs on startup
            self.clear_all_workflow_tracking()

            # Setup tables
            self.setup_workflow_tracking_table()
            self.setup_trigger()
            self.setup_rootcause_table()

            # Start periodic sync in background
            sync_thread = threading.Thread(target=self.periodic_sync, daemon=True)
            sync_thread.start()
            print("🔄 Started periodic sync thread")

            # Sync any missed completions from startup
            print("🔍 Checking for missed completions on startup...")
            self.recover_missed_notifications()

            # Listen for real-time notifications
            self.listen_for_changes()

        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")

def main():
    monitor = WorkflowMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()