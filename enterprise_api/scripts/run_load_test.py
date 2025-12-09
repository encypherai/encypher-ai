import os
import socket
import subprocess
import sys
import time

import docker
import httpx
import numpy as np
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

def main():
    print("Starting Load Test Script (Fixed Sync Init)...")
    
    # 1. Check Docker
    try:
        docker_client = docker.from_env()
        docker_client.ping()
        print("Docker is available.")
    except Exception as e:
        print(f"Docker not available: {e}")
        print("Please ensure Docker Desktop is running.")
        sys.exit(1)

    # 2. Start Postgres
    print("Starting Postgres container...")
    container = None
    try:
        # Stop existing container if any (cleanup from previous failed runs)
        try:
            old_containers = docker_client.containers.list(all=True, filters={"name": "encypher_load_test_db"})
            for c in old_containers:
                print(f"Removing old container {c.name}...")
                c.remove(force=True)
        except Exception as e:
            print(f"Warning during cleanup: {e}")

        container = docker_client.containers.run(
            "postgres:15-alpine",
            name="encypher_load_test_db",
            environment={
                "POSTGRES_USER": "encypher",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "encypher_test"
            },
            ports={'5432/tcp': 54322},
            detach=True,
            remove=False # Keep container for debugging if test fails
        )
        print(f"Container started with ID: {container.short_id}")
    except Exception as e:
        print(f"Failed to start container: {e}")
        sys.exit(1)

    # Use 127.0.0.1 to avoid IPv6 issues on Windows
    db_host = "127.0.0.1"
    db_port = 54322
    # Asyncpg URL for the APP (will be passed to server)
    async_db_url = f"postgresql+asyncpg://encypher:password@{db_host}:{db_port}/encypher_test"
    server_port = 8092

    try:
        # Wait for DB (Socket check)
        print("Waiting for DB port...")
        start_time = time.time()
        connected = False
        while time.time() - start_time < 30:
            try:
                with socket.create_connection((db_host, db_port), timeout=1):
                    connected = True
                    break
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(1)
        
        if not connected:
            print("DB port timeout. Container logs:")
            try:
                print(container.logs().decode('utf-8'))
            except:
                pass
            raise Exception("DB port timeout")

        # Wait for DB (Connection check)
        print("Waiting for DB ready (accepting connections)...")
        start_time = time.time()
        connected = False
        while time.time() - start_time < 30:
            try:
                conn = psycopg2.connect(
                    user="encypher",
                    password="password",
                    host=db_host,
                    port=db_port,
                    database="encypher_test"
                )
                conn.close()
                print("DB Ready!")
                connected = True
                break
            except Exception:
                time.sleep(1)
        
        if not connected:
            print("DB connection timeout. Container logs:")
            try:
                print(container.logs().decode('utf-8'))
            except:
                pass
            raise Exception("DB connection timeout")

        # 3. Init DB (Sync using psycopg2)
        print("Initializing DB schema...")
        try:
            conn = psycopg2.connect(
                user="encypher",
                password="password",
                host=db_host,
                port=db_port,
                database="encypher_test"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            sql_path = os.path.join(root_dir, "scripts", "init_db.sql")
            if not os.path.exists(sql_path):
                 raise FileNotFoundError(f"SQL file not found at {sql_path}")

            with open(sql_path, "r") as f:
                schema_sql = f.read()
                # Execute statements one by one
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        try:
                            cur.execute(statement)
                        except Exception as sql_err:
                            print(f"Error executing statement: {statement[:50]}...")
                            print(f"Error: {sql_err}")
                            raise
            
            # Seed test data
            print("Seeding test data...")
            seed_path = os.path.join(root_dir, "scripts", "seed_load_test_data.sql")
            if os.path.exists(seed_path):
                with open(seed_path, "r") as f:
                    seed_sql = f.read()
                    for statement in seed_sql.split(';'):
                        if statement.strip():
                            try:
                                cur.execute(statement)
                            except Exception as sql_err:
                                print(f"Error executing seed statement: {statement[:50]}...")
                                print(f"Error: {sql_err}")
                                raise
            else:
                print(f"Warning: Seed file not found at {seed_path}")

            cur.close()
            conn.close()
            print("Schema initialized and seeded.")
        except Exception as e:
            print(f"Schema init failed: {e}")
            try:
                print(container.logs().decode('utf-8'))
            except:
                pass
            raise

        # 4. Start Server
        print(f"Starting Server on port {server_port}...")
        env = os.environ.copy()
        # Pass unmodified URL if app replaces it, or modify here.
        # App replaces postgresql:// -> postgresql+asyncpg://
        # We pass postgresql://
        env["DATABASE_URL"] = async_db_url.replace("+asyncpg", "") 
        env["KEY_ENCRYPTION_KEY"] = "00" * 32
        env["ENCRYPTION_NONCE"] = "00" * 12
        env["SSL_COM_API_KEY"] = "test_key"
        env["DEMO_API_KEY"] = "demo-key-load-test"
        env["PORT"] = str(server_port)
        # env["ENVIRONMENT"] = "production"
        
        script_path = os.path.join(root_dir, "tests", "load", "run_server.py")
        
        # Open a log file for the server
        server_log_file = open("server_load_test.log", "w")
        
        proc = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=server_log_file,
            stderr=server_log_file
        )

        try:
            # Wait for server
            base_url = f"http://127.0.0.1:{server_port}"
            start_time = time.time()
            server_up = False
            while time.time() - start_time < 15:
                try:
                    httpx.get(f"{base_url}/health")
                    server_up = True
                    print("Server is up!")
                    break
                except (httpx.ConnectError, httpx.ReadTimeout):
                    time.sleep(0.5)
            
            if not server_up:
                print("Server failed to start. Logs:")
                server_log_file.flush()
                with open("server_load_test.log", "r") as f:
                    print(f.read())
                sys.exit(1)

            # 5. Run Load
            print("\n=== Starting Load Generation ===")
            headers = {"Authorization": "Bearer demo-key-load-test"}
            payload = {"text": "This is a load test content string." * 10, "title": "Load Test"}
            
            # Warmup
            print("Warming up (5 reqs)...")
            for _ in range(5):
                try:
                    resp = httpx.post(f"{base_url}/api/v1/sign", json=payload, headers=headers, timeout=10.0)
                    if resp.status_code != 200:
                        print(f"Warmup failed: {resp.status_code} - {resp.text}")
                except Exception as e:
                    print(f"Warmup exception: {e}")

            # Measure
            print("Sending 50 requests...")
            latencies = []
            start_total = time.time()
            for i in range(50):
                t0 = time.time()
                try:
                    resp = httpx.post(f"{base_url}/api/v1/sign", json=payload, headers=headers, timeout=10.0)
                    t1 = time.time()
                    if resp.status_code != 200:
                        print(f"Req {i} failed: {resp.status_code}")
                    latencies.append((t1 - t0) * 1000)
                except Exception as e:
                    print(f"Req {i} exception: {e}")
                    latencies.append(0) # Penalty?
            
            total_time = time.time() - start_total
            
            # Print server logs if there were failures
            if any(l == 0 for l in latencies) or any(l == 500 for l in latencies): # rudimentary check
                 print("\n--- Server Logs (Tail) ---")
                 server_log_file.flush()
                 with open("server_load_test.log", "r") as f:
                     print(f.read()[-2000:])
            
            # Stats
            if latencies:
                p95 = np.percentile(latencies, 95)
                avg = np.mean(latencies)
                
                print("-" * 30)
                print(f"Total Time: {total_time:.2f}s")
                print(f"Avg Latency: {avg:.2f}ms")
                print(f"P95 Latency: {p95:.2f}ms")
                print("-" * 30)
                
                if p95 < 150:
                    print("SUCCESS: P95 < 150ms (Target met)")
                else:
                    print(f"FAILURE: P95 {p95:.2f}ms >= 150ms")
                    sys.exit(1)
            else:
                print("No successful requests.")
                sys.exit(1)

        finally:
            print("Stopping server...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            server_log_file.close()

    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if container:
            print("Stopping Postgres container...")
            try:
                container.stop()
                container.remove()
                print("Container removed.")
            except:
                pass

if __name__ == "__main__":
    main()
