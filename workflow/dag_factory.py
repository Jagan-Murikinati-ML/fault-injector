# /dags/chaos_dags.py
import os
import glob
from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

CONTAINER_CHAOS_DIR = "/opt/airflow/chaos_experiments"
DOCKER_IMAGE = "airflow_chaos:latest"

json_files = glob.glob(os.path.join(CONTAINER_CHAOS_DIR, "*.json"))
if not json_files:
    print(f"No JSON experiments found in {CONTAINER_CHAOS_DIR}")

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

    run_experiment = DockerOperator(
        task_id=f"run_{experiment_name}",
        image=DOCKER_IMAGE,
        api_version="auto",
        auto_remove=True,
        command=(
            f"bash -c 'export PYTHONPATH={CONTAINER_CHAOS_DIR}:$PYTHONPATH && "
            f"export KUBECONFIG=/opt/airflow/airflow-minikube/config && "
            f"chaos run {CONTAINER_CHAOS_DIR}/{experiment_name}.json'"
        ),
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        mounts=[
            Mount("/home/priyanshupatel/airflow-fresh/chaos_experiments",
                  CONTAINER_CHAOS_DIR,
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
