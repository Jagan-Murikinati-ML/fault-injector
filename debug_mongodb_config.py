import subprocess

POD_NAME = "user-mongodb-78f75fc787-kd4bg"
NAMESPACE = "default"

def debug_mongodb_config():
    """Debug MongoDB configuration location"""
    
    # Check common config paths
    paths_to_check = [
        "/etc/mongod.conf",
        "/etc/mongodb.conf", 
        "/data/configdb/mongod.conf",
        "/data/db/mongod.conf",
        "/usr/local/etc/mongod.conf"
    ]
    
    for path in paths_to_check:
        try:
            result = subprocess.run(
                ["kubectl", "exec", "-n", NAMESPACE, POD_NAME, "--", "ls", "-la", path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✓ Found config at: {path}")
                print(result.stdout)
            else:
                print(f"✗ Not found: {path}")
        except Exception as e:
            print(f"Error checking {path}: {e}")
    
    # Check MongoDB process to see what config it's using
    try:
        result = subprocess.run(
            ["kubectl", "exec", "-n", NAMESPACE, POD_NAME, "--", "ps", "aux"],
            capture_output=True, text=True
        )
        print("\nMongoDB processes:")
        for line in result.stdout.split('\n'):
            if 'mongod' in line:
                print(line)
    except Exception as e:
        print(f"Error checking processes: {e}")

if __name__ == "__main__":
    debug_mongodb_config()