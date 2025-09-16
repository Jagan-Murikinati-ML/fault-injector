import time
import redis

def redis_memory_stress_test(host="127.0.0.1", port=6379, limit_in_kb=1,
                             eviction_policy="noeviction", duration=0):
    """
    Set Redis memory limit and eviction policy for a given duration.
    After duration, rollback to defaults automatically.
    """
    client = redis.StrictRedis(host=host, port=port, decode_responses=True)

    # Apply tiny memory limit
    client.config_set("maxmemory", f"{limit_in_kb}kb")
    client.config_set("maxmemory-policy", eviction_policy)

    print(f"[INFO] Set maxmemory={limit_in_kb}KB, policy={eviction_policy}")

    # Report current memory stats
    used_memory = client.info("memory")["used_memory_human"]
    evicted = client.info("stats").get("evicted_keys", 0)

    print(f"[INFO] Redis used memory: {used_memory}")
    print(f"[INFO] Keys evicted: {evicted}")

    # Wait if duration specified
    if duration > 0:
        print(f"[INFO] Holding stress for {duration} seconds...")
        time.sleep(duration)
        reset_maxmemory(host, port)

    return {"used_memory": used_memory, "evicted_keys": evicted, "duration": duration}


def reset_maxmemory(host="127.0.0.1", port=6379):
    """
    Rollback: reset maxmemory and eviction policy to default values.
    """
    client = redis.StrictRedis(host=host, port=port, decode_responses=True)

    client.config_set("maxmemory", 0)  # 0 = no limit
    client.config_set("maxmemory-policy", "noeviction")  # default

    print("[INFO] Redis maxmemory reset to unlimited, policy reset to noeviction")

    return {"status": "reset", "maxmemory": "0", "policy": "noeviction"}
