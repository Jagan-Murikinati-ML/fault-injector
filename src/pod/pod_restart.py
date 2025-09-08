
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

from chaosk8s import create_k8s_api_client

__all__ = ["terminate_pods", "restart_pods_continuous"]
logger = logging.getLogger("chaostoolkit")

def terminate_pods(
    label_selector: str = None,
    name_pattern: str = None,
    all: bool = False,
    rand: bool = False,
    mode: str = "fixed",
    qty: int = 1,
    grace_period: int = -1,
    ns: str = "default",
    order: str = "alphabetic",
    secrets: Secrets = None,
):
    """
    Terminate a pod gracefully. Select the appropriate pods by label and/or
    name patterns.
    """
    print("Hello world - terminate function started!")

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    pods = _select_pods(
        v1, label_selector, name_pattern, all, rand, mode, qty, ns, order
    )

    body = client.V1DeleteOptions()
    if grace_period >= 0:
        body = client.V1DeleteOptions(grace_period_seconds=grace_period)

    deleted_pods = []
    for p in pods:
        print(f"Deleting pod: {p.metadata.name}")
        v1.delete_namespaced_pod(p.metadata.name, ns, body=body)
        deleted_pods.append(p.metadata.name)

    print(f"Deleted {len(deleted_pods)} pods: {deleted_pods}")
    return deleted_pods


def restart_pods_continuous(
    label_selector: str = None,
    name_pattern: str = None,
    qty: int = 1,
    rand: bool = False,
    mode: str = "fixed",
    grace_period: int = -1,
    ns: str = "default",
    order: str = "alphabetic",
    interval: int=3,  # ✅ Your custom parameter (seconds between restarts)
    duration: int= 30,  # ✅ Your custom parameter (total runtime in seconds)
    secrets: Secrets = None,
):
    """
    Continuously restart pods at specified intervals.
    
    Parameters:
    - interval: Time between restarts (seconds)
    - duration: Total time to run the experiment (seconds)
    - All other parameters same as terminate_pods
    """
    print(f"🚀 Starting continuous pod restart experiment")
    print(f"📅 Interval: {interval} seconds")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"🎯 Target: {label_selector}")
    print(f"📍 Namespace: {ns}")
    
    start_time = time.time()
    restart_count = 0
    
    while time.time() - start_time < duration:
        restart_count += 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*50}")
        print(f"🔄 Restart #{restart_count} at {current_time}")
        print(f"{'='*50}")
        
        try:
            # Call your existing terminate_pods function
            result = terminate_pods(
                label_selector=label_selector,
                name_pattern=name_pattern,
                all=False,  # Don't terminate all pods
                rand=rand,
                mode=mode,
                qty=qty,
                grace_period=grace_period,
                ns=ns,
                order=order,
                secrets=secrets
            )
            print(f"✅ Successfully restarted pods: {result}")
            
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
        time.sleep(interval)
    
    total_duration = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"🏁 Experiment Completed!")
    print(f"{'='*50}")
    print(f"📈 Total restarts performed: {restart_count}")
    print(f"⏱️  Total duration: {total_duration:.0f} seconds")
    print(f"📊 Average interval: {total_duration/restart_count:.1f} seconds" if restart_count > 0 else "No restarts performed")
    
    return {
        "restart_count": restart_count,
        "duration": total_duration,
        "status": "completed",
        "target": label_selector,
        "namespace": ns
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
    print(f"Selecting pods with label_selector: {label_selector}")
    
    if label_selector:
        ret = v1.list_namespaced_pod(namespace=ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_pod(namespace=ns)

    pods = ret.items
    print(f"Found {len(pods)} pods initially")

    if name_pattern:
        pattern = re.compile(name_pattern)
        pods = [p for p in pods if pattern.search(p.metadata.name)]
        print(f"After name pattern filter: {len(pods)} pods")

    if not pods:
        print("No pods found matching criteria")
        return []

    if order == "oldest":
        pods.sort(key=_sort_by_pod_creation_timestamp)

    if all:
        print("Selecting all matching pods")
        return pods

    if mode == "percentage":
        qty = int(math.ceil((qty / 100.0) * len(pods)))
        print(f"Percentage mode: selecting {qty} pods")

    if rand:
        pods = random.sample(pods, min(qty, len(pods)))
        print(f"Random selection: {len(pods)} pods")
    else:
        pods = pods[:qty]
        print(f"Sequential selection: {len(pods)} pods")

    return pods


def _sort_by_pod_creation_timestamp(pod: V1Pod) -> datetime.datetime:
    """
    Function that serves as a key for the sort pods comparison
    """
    return pod.metadata.creation_timestamp
