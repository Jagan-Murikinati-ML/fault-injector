import psycopg2
from psycopg2 import OperationalError
import threading
import time
import logging
import sys
import subprocess
import os


#can get the data from config file or .env file
CONF_FILE = "/etc/postgresql/16/main/postgresql.conf"
SETTING = "max_connections"
#NEW_VALUE = 50

def update_max_connections(new_max_connection_value: int):
    """
    Chaos Toolkit action to change PostgreSQL max_connections.
    Requires the user to have sudo privileges (password will be prompted if needed).
    """
    print(f"Updating max_connections to {new_max_connection_value} in {CONF_FILE}...")

    # Construct sed command to run with sudo
    sed_command = (
        f"sed -i 's/^\\s*{SETTING}\\s*=.*/{SETTING} = {new_max_connection_value}/' {CONF_FILE}"
    )

    try:
        # Update the config using sudo
        subprocess.run(["sudo", "bash", "-c", sed_command], check=True)
        print(" Config file updated.")

        # Restart PostgreSQL using sudo
        print(" Restarting PostgreSQL...")
        subprocess.run(["sudo", "systemctl", "restart", "postgresql"], check=True)

        print(" max_connections updated and PostgreSQL restarted.")
    except subprocess.CalledProcessError as e:
        print(" Failed to update configuration or restart PostgreSQL.")
        raise e
    



def update_max_connections_without_password(new_max_connection_value: int):
    """
    Chaos Toolkit action to change PostgreSQL max_connections.
    Hardcoded sudo password approach (INSECURE — for local testing only).
    """
    sudo_password = "---"  # Hardcoded password

    print(f" Updating max_connections to {new_max_connection_value} in {CONF_FILE}...")

    # Construct sed command
    sed_command = f"sed -i 's/^\\s*{SETTING}\\s*=.*/{SETTING} = {new_max_connection_value}/' {CONF_FILE}"

    try:
        # Run sed with sudo using the password via stdin
        sed_proc = subprocess.run(
            ["sudo", "-S", "bash", "-c", sed_command],
            input=f"{sudo_password}\n",
            text=True,
            check=True
        )
        print("Config file updated.")

        # Restart PostgreSQL with sudo using password via stdin
        restart_proc = subprocess.run(
            ["sudo", "-S", "systemctl", "restart", "postgresql"],
            input=f"{sudo_password}\n",
            text=True,
            check=True
        )
        print("max_connections updated and PostgreSQL restarted.")

    except subprocess.CalledProcessError as e:
        print("Failed to update configuration or restart PostgreSQL.")
        print(e)




def connection_test(number_of_connections: int):
    # Setup logger
    logger = logging.getLogger("connection_test")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(console_handler)

    # DB parameters
    PG_HOST = "localhost"
    PG_DB = "postgres"
    PG_USER = "postgres"
    PG_PASS = "123456"
    PG_PORT = 5432
    #NUM_CONNECTIONS = 12

    # Shared counters
    success_count = 0
    fail_count = 0
    lock = threading.Lock()

    def open_connection(index):
        nonlocal success_count, fail_count
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_DB,
                user=PG_USER,
                password=PG_PASS,
                port=PG_PORT
            )
            with lock:
                success_count += 1
            logger.info(f"[{index}] Connection SUCCESS (Current active: {success_count})")

            cur = conn.cursor()
            cur.execute("SELECT pg_sleep(60);")  # hold connection
            cur.close()
            conn.close()
            logger.info(f"[{index}] Connection CLOSED")

        except OperationalError as e:
            with lock:
                fail_count += 1
            logger.error(f"[{index}] Connection FAILED: {e} (Total failures: {fail_count})")

    # Launch threads
    threads = []

    for i in range(number_of_connections):
        t = threading.Thread(target=open_connection, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.01)

    for t in threads:
        t.join()

    logger.info(f"Test completed: {success_count} successful, {fail_count} failed connections")
    print(f"Test completed: {success_count} successful, {fail_count} failed connections")
