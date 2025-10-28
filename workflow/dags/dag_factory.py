import os
import json
import glob
from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client as k8s

# Persistent volume paths
GENERATED_WORKFLOWS_DIR = "/opt/airflow/generated_workflows"

# Default configuration
DEFAULT_NAMESPACE = "airflow"
DEFAULT_IMAGE = "priyanshu01ce/airflow_chaos:latest"
DEFAULT_SERVICE_ACCOUNT = "airflow-worker"

print("line 18")

def create_dag_from_config(config_file_path):
    """Create a DAG from configuration JSON file"""
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # Ensure dag_id exists — if not, skip DAG creation
    dag_id = config.get("dag_id")
    if not dag_id:
        print(f"Skipping {config_file_path}: Missing 'dag_id'")
        return None, None

    print(f" Found dag_id: {dag_id}")

    task_id = config.get('task_id', f"run_{dag_id}")
    task_name = config.get('task_name', dag_id.replace('_', '-'))
    experiment_json = config.get('experiment_json', f"{dag_id}.json")

    # Pull tags, description, and schedule from JSON, else use defaults
    dag_tags = config.get('tags', ["chaos", "kubernetes"])
    dag_description = config.get('description', f"Chaos experiment: {experiment_json}")
    dag_schedule = config.get('schedule', "@once")

    print(dag_schedule)
    print(dag_description)
    print(dag_tags)

    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(2025, 1, 1),
        "retries": 0,
    }
   
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule=dag_schedule,
        catchup=False,
        tags=dag_tags,
        description=dag_description,
    )

    run_experiment = KubernetesPodOperator(
        task_id=task_id,
        name=task_name,
        namespace=DEFAULT_NAMESPACE,
        image=DEFAULT_IMAGE,
        get_logs=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        service_account_name=DEFAULT_SERVICE_ACCOUNT,
        cmds=["bash", "-c"],
        arguments=[
            f"cd /opt/airflow/generated_workflows && "
            f"echo 'Listing files:' && ls -la && "
            f"echo 'Chaos toolkit version:' && chaos --version && "
            f"echo 'Running experiment: {experiment_json}' && "
            f"cat {experiment_json} && "
            f"chaos run {experiment_json}"
        ],
        volumes=[
            k8s.V1Volume(
                name="airflow-shared-operations",
                persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                    claim_name="airflow-pvc-shared"
                ),
            )
        ],
        volume_mounts=[
            k8s.V1VolumeMount(
                name="airflow-shared-operations",
                mount_path="/opt/airflow/generated_workflows",
                read_only=False,
            )
        ],
        env_vars={"PYTHONPATH": "/opt/airflow/generated_workflows:$PYTHONPATH"},
        dag=dag,
    )

    return dag_id, dag

# Load DAG configurations
config_files = glob.glob(os.path.join(GENERATED_WORKFLOWS_DIR, "*.json"))

if not config_files:
    print(f"No configuration files found in {GENERATED_WORKFLOWS_DIR}")
else:
    print(f"Found {len(config_files)} configuration files")

loaded_dags = []
for config_file_path in config_files:
    try:
        dag_id, dag = create_dag_from_config(config_file_path)
        if dag_id and dag:
            globals()[dag_id] = dag
            loaded_dags.append(dag_id)
            print(f" Loaded DAG: {dag_id}")
        else:
            print(f"  Skipped DAG creation for {config_file_path}")
    except Exception as e:
        print(f"Failed to load DAG from {config_file_path}: {str(e)}")
