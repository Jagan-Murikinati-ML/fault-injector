import datetime
import json
import logging
import math
import random
import re
import shlex
import time
from typing import Any, Dict, List, Union

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client, stream
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.stream.ws_client import ERROR_CHANNEL, STDERR_CHANNEL, STDOUT_CHANNEL

from chaosk8s import create_k8s_api_client

__all__ = ["restart_containers", "restart_containers_continuous"]
logger = logging.getLogger("chaostoolkit")

def restart_containers(
    label_selector: str = None,
    name_pattern: str = None,
    qty: int = 1,
    rand: bool = False,
    mode: str = "fixed",
    ns: str = "default",
    order: str = "alphabetic",
    container_name: str = None,
    restart_command: List[str] = None,
    secrets: Secrets = None,
):
    """
    Restart containers by sending SIGINT signal to the main process.
    This keeps the same pod but restarts the container when the process exits.

    Parameters:
    - restart_command: Custom command to trigger restart (optional)
                      Default: Uses SIGINT signal which works reliably
    """
    print("🔄 Container restart function started!")

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    pods = _select_pods(
        v1, label_selector, name_pattern, False, rand, mode, qty, ns, order
    )

    restarted_containers = []

    for pod in pods:
        pod_name = pod.metadata.name
        print(f"🎯 Restarting container in pod: {pod_name}")

        # Auto-select container if none provided (skip sidecars)
        if container_name is None:
            names = [c.name for c in pod.spec.containers]
            selected_container = next((n for n in names if not re.search(r"(istio|linkerd|proxy)", n)), names[0])
            print(f"📦 Auto-selected container: {selected_container}")
        else:
            selected_container = container_name

        try:
            # Get restart count before triggering restart
            before_count = _get_restart_count(v1, pod_name, ns, selected_container)
            print(f"📊 Current restart count: {before_count}")

            # Try multiple restart strategies, starting with SIGINT (which works!)
            restart_strategies = [
                ["sh", "-c", "kill -INT 1"],     # SIGINT - works for most containers
                ["sh", "-c", "kill -2 1"],       # Same as SIGINT (signal number)
                ["sh", "-c", "kill -TERM 1"],    # SIGTERM - fallback
                ["sh", "-c", "kill -9 1"],       # SIGKILL - last resort
            ]

            if restart_command:
                restart_strategies.insert(0, restart_command)  # Use custom command first

            restart_successful = False

            for i, cmd in enumerate(restart_strategies):
                print(f"🔧 Trying restart strategy {i+1}: {' '.join(cmd)}")

                try:
                    resp = stream.stream(
                        v1.connect_get_namespaced_pod_exec,
                        pod_name,
                        ns,
                        container=selected_container,
                        command=cmd,
                        stderr=True,
                        stdin=False,
                        stdout=True,
                        tty=False,
                        _preload_content=False,
                    )

                    resp.run_forever(timeout=10)

                    # Read all output channels
                    stdout = resp.read_channel(STDOUT_CHANNEL)
                    stderr = resp.read_channel(STDERR_CHANNEL)  # Real process stderr
                    ctrl_err = resp.read_channel(ERROR_CHANNEL)  # K8s control status

                    print(f"✅ Signal sent successfully to container in pod {pod_name}")
                    if stdout:
                        print(f"📤 STDOUT: {stdout}")
                    if stderr:
                        print(f"📤 STDERR: {stderr}")

                    # Wait for restart to occur (should happen within ~10-30 seconds)
                    print(f"⏳ Waiting for container restart (up to 60 seconds)...")
                    restart_verified = False
                    deadline = time.time() + 60

                    while time.time() < deadline:
                        current_count = _get_restart_count(v1, pod_name, ns, selected_container)
                        if before_count is not None and current_count is not None and current_count > before_count:
                            print(f"✅ Container restart verified! Count: {before_count} → {current_count}")
                            restart_successful = True
                            restart_verified = True
                            break
                        time.sleep(2)

                    if restart_verified:
                        break  # Success! No need to try other strategies
                    else:
                        print(f"⚠️  Strategy {i+1} didn't cause restart, trying next...")

                except Exception as strategy_e:
                    print(f"❌ Strategy {i+1} failed: {strategy_e}")
                    continue

            if restart_successful:
                current_count = _get_restart_count(v1, pod_name, ns, selected_container)
                restarted_containers.append({
                    "pod_name": pod_name,
                    "container_name": selected_container,
                    "status": "restart_verified",
                    "before_count": before_count,
                    "after_count": current_count,
                    "stdout": stdout if 'stdout' in locals() else None,
                    "stderr": stderr if 'stderr' in locals() else None
                })
            else:
                print(f"❌ All restart strategies failed - container restart not verified")
                restarted_containers.append({
                    "pod_name": pod_name,
                    "container_name": selected_container,
                    "status": "restart_failed",
                    "before_count": before_count,
                    "strategies_tried": len(restart_strategies),
                    "stdout": stdout if 'stdout' in locals() else None,
                    "stderr": stderr if 'stderr' in locals() else None
                })

        except Exception as e:
            print(f"❌ Failed to restart container in pod {pod_name}: {e}")
            restarted_containers.append({
                "pod_name": pod_name,
                "container_name": selected_container,
                "status": "failed",
                "error": str(e)
            })

    successful_restarts = [r for r in restarted_containers if r.get("status") == "restart_verified"]       
    print(f"🏁 Restart operation completed for {len(restarted_containers)} containers")
    print(f"✅ Successfully restarted: {len(successful_restarts)} containers")
    return restarted_containers


def restart_containers_continuous(
    label_selector: str = None,
    name_pattern: str = None,
    qty: int = 1,
    rand: bool = False,
    mode: str = "fixed",
    ns: str = "default",
    order: str = "alphabetic",
    container_name: str = None,
    restart_command: List[str] = None,
    interval: int = 30,  # ✅ Time between restarts (seconds)
    duration: int = 300,  # ✅ Total runtime (seconds)
    secrets: Secrets = None,
):
    """
    Continuously restart containers at specified intervals.

    Parameters:
    - interval: Time between restarts (seconds)
    - duration: Total time to run the experiment (seconds)
    - restart_command: Custom command to restart containers
    - container_name: Specific container to target (optional)
    - All other parameters same as restart_containers
    """
    print(f"🚀 Starting continuous container restart experiment")
    print(f"📅 Interval: {interval} seconds")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"🎯 Target: {label_selector}")
    print(f"📍 Namespace: {ns}")
    print(f"📦 Container: {container_name or 'default'}")

    start_time = time.time()
    restart_count = 0
    total_containers_restarted = 0

    while time.time() - start_time < duration:
        restart_count += 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'='*60}")
        print(f"🔄 Container Restart #{restart_count} at {current_time}")
        print(f"{'='*60}")

        try:
            # Call the container restart function
            result = restart_containers(
                label_selector=label_selector,
                name_pattern=name_pattern,
                qty=qty,
                rand=rand,
                mode=mode,
                ns=ns,
                order=order,
                container_name=container_name,
                restart_command=restart_command,
                secrets=secrets
            )

            successful_restarts = [r for r in result if r.get("status") != "failed"]
            failed_restarts = [r for r in result if r.get("status") == "failed"]

            total_containers_restarted += len(successful_restarts)

            print(f"✅ Successfully restarted {len(successful_restarts)} containers")
            if failed_restarts:
                print(f"❌ Failed to restart {len(failed_restarts)} containers")

            for restart_info in successful_restarts:
                print(f"   📦 {restart_info['pod_name']}: {restart_info['status']}")

        except Exception as e:
            print(f"❌ Error during restart #{restart_count}: {e}")

        # Calculate remaining time
        elapsed = time.time() - start_time
        remaining = duration - elapsed

        # Check if we should continue
        if remaining <= interval:
            print(f"⏰ Less than {interval} seconds remaining, stopping experiment")
            break

        # Wait for the interval
        print(f"⏳ Waiting {interval} seconds until next restart...")
        print(f"📊 Time remaining: {remaining:.0f} seconds")
        print(f"📈 Total containers restarted so far: {total_containers_restarted}")
        time.sleep(interval)

    total_duration = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🏁 Container Restart Experiment Completed!")
    print(f"{'='*60}")
    print(f"📈 Total restart cycles: {restart_count}")
    print(f"📦 Total containers restarted: {total_containers_restarted}")
    print(f"⏱️  Total duration: {total_duration:.0f} seconds")
    print(f"📊 Average cycle time: {total_duration/restart_count:.1f} seconds" if restart_count > 0 else "No restarts performed")
    print(f"🎯 Target selector: {label_selector}")
    print(f"📍 Namespace: {ns}")

    return {
        "restart_cycles": restart_count,
        "total_containers_restarted": total_containers_restarted,
        "duration": total_duration,
        "status": "completed",
        "target": label_selector,
        "namespace": ns,
        "container_name": container_name
    }


def _select_pods(
    v1,
    label_selector: str = None,
    name_pattern: str = None,
    all: bool = False,
    rand: bool = False,
    mode: str = "fixed",
    qty: int = 1,
    ns: str = "default",
    order: str = "alphabetic",
):
    """
    Select pods based on the given criteria.
    """
    print(f"🔍 Selecting pods with label_selector: {label_selector}")

    if label_selector:
        ret = v1.list_namespaced_pod(namespace=ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_pod(namespace=ns)

    pods = ret.items
    print(f"📋 Found {len(pods)} pods initially")

    if name_pattern:
        pattern = re.compile(name_pattern)
        pods = [p for p in pods if pattern.search(p.metadata.name)]
        print(f"🔍 After name pattern filter: {len(pods)} pods")

    if not pods:
        print("⚠️  No pods found matching criteria")
        return []

    if order == "oldest":
        pods.sort(key=_sort_by_pod_creation_timestamp)

    if all:
        print("📌 Selecting all matching pods")
        return pods

    if mode == "percentage":
        qty = int(math.ceil((qty / 100.0) * len(pods)))
        print(f"📊 Percentage mode: selecting {qty} pods")

    if rand:
        pods = random.sample(pods, min(qty, len(pods)))
        print(f"🎲 Random selection: {len(pods)} pods")
    else:
        pods = pods[:qty]
        print(f"📝 Sequential selection: {len(pods)} pods")

    selected_names = [p.metadata.name for p in pods]
    print(f"✅ Selected pods: {selected_names}")
    return pods


def _sort_by_pod_creation_timestamp(pod: V1Pod) -> datetime.datetime:
    """
    Function that serves as a key for the sort pods comparison
    """
    return pod.metadata.creation_timestamp


def _get_restart_count(v1, pod_name: str, ns: str, container_name: str) -> int:
    """Get the restart count for a specific container in a pod."""
    try:
        pod_status = v1.read_namespaced_pod_status(pod_name, ns)
        for container_status in pod_status.status.container_statuses or []:
            if container_status.name == container_name:
                return container_status.restart_count
        return None
    except Exception as e:
        print(f"⚠️  Failed to get restart count: {e}")
        return None
