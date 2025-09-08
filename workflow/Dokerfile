# Use official Airflow image
FROM apache/airflow:2.10.2-python3.11

USER root

# Install curl for downloading kubectl and other dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install kubectl (latest stable)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl

# Switch back to airflow user
USER airflow

# Install Chaos Toolkit + Kubernetes extension in the Airflow venv
RUN pip install --no-cache-dir \
        chaostoolkit \
        chaostoolkit-kubernetes \
        kubernetes

# Create chaos experiments folder (if not mounted from host)
RUN mkdir -p /opt/airflow/chaos_experiments

# Copy your Python chaos code
COPY --chown=airflow:airflow chaos_experiments/continuous_pod_restart.py /opt/airflow/chaos_experiments/
