from pymongo import MongoClient

MONGO_URI = "mongodb://4.149.182.40:27017"  # LoadBalancer IP


def probe_max_connections(expected_connections: int = None) -> bool:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")

        server_status = client.admin.command("serverStatus")
        available = server_status.get("connections", {}).get("available")
        current = server_status.get("connections", {}).get("current")

        print(f"Mongo connections: current={current}, available={available}")

        if expected_connections and available < expected_connections:
            print(f"Expected at least {expected_connections}, found {available}")
            return False

        return True
    except Exception as e:
        print(f"Probe failed: {e}")
        return False


def probe_runtime_parameters() -> bool:
    """Check what parameters can be set at runtime"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        
        # Get all parameters
        all_params = client.admin.command("getParameter", "*")
        
        # Look for connection-related parameters
        connection_params = {k: v for k, v in all_params.items() if 'conn' in k.lower() or 'max' in k.lower()}
        
        print("Connection-related parameters:")
        for param, value in connection_params.items():
            print(f"  {param}: {value}")
            
        client.close()
        return True
        
    except Exception as e:
        print(f"Failed to get parameters: {e}")
        return False


def exhaust_mongo_connections(num_connections, hold_until_rollback=True):
    """Create multiple connections to exhaust MongoDB connection pool"""
    print(f"Attempting to open {num_connections} connections...")
    clients = []
    
    try:
        for i in range(num_connections):
            try:
                # Create client with valid parameters
                client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=2000,
                    socketTimeoutMS=5000,
                    connectTimeoutMS=2000,
                    maxPoolSize=1  # Each client gets 1 connection
                )
                # Test connection
                client.admin.command("ping")
                clients.append(client)
                print(f"Connection {i+1} established")
                
            except Exception as e:
                print(f"Connection {i+1} failed: {e}")
                break
                
        print(f"Successfully opened {len(clients)} connections")
        
        # Check current connection status
        if clients:
            server_status = clients[0].admin.command("serverStatus")
            current = server_status.get("connections", {}).get("current")
            available = server_status.get("connections", {}).get("available")
            print(f"Mongo connections: current={current}, available={available}")
        
        if hold_until_rollback and clients:
            print(f"Holding {len(clients)} connections alive until experiment ends...")
            return clients
        else:
            # Close connections immediately
            for c in clients:
                try:
                    c.close()
                except:
                    pass
            return []
            
    except Exception as e:
        print(f"Connection exhaustion failed: {e}")
        # Clean up any opened connections
        for c in clients:
            try:
                c.close()
            except:
                pass
        return []
