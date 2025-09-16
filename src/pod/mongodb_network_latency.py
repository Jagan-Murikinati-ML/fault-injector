# mongodb_network_latency.py

import subprocess
import time
from logzero import logger

__all__ = ["inject_latency"]

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return False

def inject_latency(interface: str = "lo", delay_ms: int = 200, duration_s: int = 30):
    """
    Inject network latency on a given interface for a duration.
    
    Args:
        interface: network interface (e.g., 'lo' for loopback)
        delay_ms: delay in milliseconds
        duration_s: duration of injection in seconds
    """
    logger.info(f"Injecting {delay_ms}ms latency on {interface} for {duration_s}s")
    
    # Add latency
    add_cmd = f"sudo tc qdisc add dev {interface} root netem delay {delay_ms}ms"
    if not run_command(add_cmd):
        logger.error("Failed to add latency")
        return False

    logger.info("Latency injected, sleeping for duration...")
    time.sleep(duration_s)

    # Remove latency
    del_cmd = f"sudo tc qdisc del dev {interface} root netem"
    if not run_command(del_cmd):
        logger.error("Failed to remove latency")
        return False

    logger.info("Latency removed successfully")
    return True
