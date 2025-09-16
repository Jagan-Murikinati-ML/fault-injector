import subprocess
import os
from pathlib import Path
import requests
from logzero import logger
from typing import Optional

__all__ = ["stress_endpoint"]

def _run_process_and_wait(cmd, env=None, stdout_to_file: Optional[str] = None, debug: bool = False) -> bool:
    logger.debug("Running command: %s", " ".join(cmd))
    if env is None:
        env = os.environ.copy()
    try:
        if stdout_to_file:
            with open(stdout_to_file, "w") as fh:
                proc = subprocess.Popen(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT)
                rc = proc.wait()
        else:
            proc = subprocess.Popen(cmd, env=env, stdout=(None if debug else subprocess.PIPE), stderr=subprocess.STDOUT)
            out, _ = proc.communicate()
            if debug and out:
                logger.debug("Process output: %s", out.decode(errors="ignore") if isinstance(out, (bytes, bytearray)) else out)
            rc = proc.returncode
        logger.debug("Process finished with rc=%s", rc)
        return rc == 0
    except Exception as e:
        logger.exception("Error running process: %s", e)
        return False

def stress_endpoint(endpoint: str, vus: int = 1, duration: str = "10s",
                    username: str = None, password: str = None, log_file: str = None, debug: bool = False):
    """
    Stress a single endpoint using k6 and JWT login.
    """
    env = dict(os.environ)

    # 1️⃣ Perform login to get JWT token
    token = None
    if username and password:
        login_url = "http://4.154.253.199:8080/api/user/login"
        resp = requests.post(login_url, data={"username": username, "password": password}, allow_redirects=False)
        token = resp.cookies.get("login_token")
        if not token:
            logger.error("❌ Login failed, cannot get token")
            return False
        env["CHAOS_K6_LOGIN_TOKEN"] = token

    env["CHAOS_K6_URL"] = endpoint
    env["CHAOS_K6_VUS"] = str(vus)
    env["CHAOS_K6_DURATION"] = str(duration)

    script_path = str(Path(__file__).parent / "scripts" / "single-endpoint.js")
    if not Path(script_path).exists():
        logger.error("k6 script not found at %s", script_path)
        return False

    cmd = ["k6", "run", script_path, "--vus", str(vus), "--duration", str(duration)]
    if not debug:
        cmd.insert(2, "--quiet")

    success = _run_process_and_wait(cmd, env=env, stdout_to_file=log_file, debug=debug)
    if success:
        logger.info("✅ Stress test completed successfully")
    else:
        logger.error("❌ Stress test failed")
    if log_file:
        logger.info("k6 output logged to %s", log_file)
    return success
