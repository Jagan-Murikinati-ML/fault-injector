# /dags/chaos_dags.py
import os
import glob
from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# Updated paths to match new codebase structure
CONTAINER_SRC_DIR = "/opt/airflow/src"
DOCKER_IMAGE = "airflow_chaos:latest"

# Look for JSON files in both pod and node directories
pod_json_files = glob.glob(os.path.join(CONTAINER_SRC_DIR, "pod", "*.json"))
node_json_files = glob.glob(os.path.join(CONTAINER_SRC_DIR, "node", "*.json"))
json_files = pod_json_files + node_json_files

if not json_files:
    print(f"No JSON experiments found in {CONTAINER_SRC_DIR}/pod or {CONTAINER_SRC_DIR}/node")

for json_file_path in json_files:
    experiment_name = os.path.splitext(os.path.basename(json_file_path))[0]
    dag_id = f"chaos_{experiment_name}"

    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(2025, 1, 1),
        "retries": 0,
    }

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval="@once",
        catchup=False,
        tags=["chaos"],
    )

    # Determine the correct subdirectory and file path
    if json_file_path.find("/pod/") != -1:
        experiment_subdir = "pod"
        container_experiment_path = f"{CONTAINER_SRC_DIR}/pod/{experiment_name}.json"
        pythonpath_dir = f"{CONTAINER_SRC_DIR}/pod"
    else:
        experiment_subdir = "node"
        container_experiment_path = f"{CONTAINER_SRC_DIR}/node/{experiment_name}.json"
        pythonpath_dir = f"{CONTAINER_SRC_DIR}/node"

    run_experiment = DockerOperator(
        task_id=f"run_{experiment_name}",
        image=DOCKER_IMAGE,
        api_version="auto",
        auto_remove=True,
        command=(
            f"bash -c '"
            f"export PYTHONPATH={pythonpath_dir}:$PYTHONPATH && "
            f"export KUBECONFIG=/opt/airflow/airflow-minikube/config && "
            f"cd {pythonpath_dir} && "
            f"chaos run {container_experiment_path}'"
        ),
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        environment={
            'KUBECONFIG': '/opt/airflow/airflow-minikube/config'
        },
        mounts=[
            # Mount the entire src directory to preserve structure
            # Use relative path from current working directory
            Mount(os.path.abspath("../src"),
                  CONTAINER_SRC_DIR,
                  type="bind"),
            Mount("/home/priyanshupatel/airflow-minikube",
                  "/opt/airflow/airflow-minikube",
                  type="bind"),
            Mount("/home/priyanshupatel/.kube", "/root/.kube", type="bind")
        ],
        dag=dag,
    )

    globals()[dag_id] = dag

print(f"Loaded DAGs: {[os.path.splitext(os.path.basename(f))[0] for f in json_files]}")
