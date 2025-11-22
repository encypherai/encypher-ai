import time
import docker
import os
import socket
import subprocess
import sys
import httpx
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import signal

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

def main():
    print("Starting Test Server...")
    
    # 1. Check Docker
    try:
        docker_client = docker.from_env()
        docker_client.ping()
    except Exception as e:
        print(f"Docker not available: {e}")
        sys.exit(1)

    # 2. Start Postgres
    print("Starting Postgres container...")
    container = None
    try:
        # Cleanup old container
        try:
            old = docker_client.containers.get("encypher_test_db_sdk")
            old.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            print(f"Warning cleanup: {e}")

        container = docker_client.containers.run(
            "postgres:15-alpine",
            name="encypher_test_db_sdk",
            environment={
                "POSTGRES_USER": "encypher",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "encypher_test"
            },
            ports={'5432/tcp': 54323}, # Use different port than load test
            detach=True,
            remove=False
        )
    except Exception as e:
        print(f"Failed to start container: {e}")
        sys.exit(1)

    db_host = "127.0.0.1"
    db_port = 54323
    server_port = 8093 # Different port
    
    # Cleanup function
    def cleanup(signum=None, frame=None):
        print("\nStopping server...")
        if 'proc' in locals() and proc:
            proc.terminate()
        if container:
            print("Stopping Postgres...")
            try:
                container.stop()
                container.remove()
            except:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        # Wait for DB
        print("Waiting for DB...")
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
                connected = True
                break
            except:
                time.sleep(1)
        
        if not connected:
            print("DB timeout")
            try:
                print(container.logs().decode())
            except:
                pass
            cleanup()

        # Init DB
        print("Initializing DB...")
        conn = psycopg2.connect(
            user="encypher",
            password="password",
            host=db_host,
            port=db_port,
            database="encypher_test"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        with open(os.path.join(root_dir, "scripts", "init_db.sql"), "r") as f:
            for stmt in f.read().split(';'):
                if stmt.strip():
                    cur.execute(stmt)
        
        with open(os.path.join(root_dir, "scripts", "seed_load_test_data.sql"), "r") as f:
             for stmt in f.read().split(';'):
                if stmt.strip():
                    cur.execute(stmt)
        
        cur.close()
        conn.close()
        
        # Start Server
        print(f"Starting Server on {server_port}...")
        env = os.environ.copy()
        env["DATABASE_URL"] = f"postgresql://encypher:password@{db_host}:{db_port}/encypher_test"
        env["KEY_ENCRYPTION_KEY"] = "00" * 32
        env["ENCRYPTION_NONCE"] = "00" * 12
        env["SSL_COM_API_KEY"] = "test_key"
        env["DEMO_API_KEY"] = "demo-key-load-test"
        env["PORT"] = str(server_port)
        
        script_path = os.path.join(root_dir, "tests", "load", "run_server.py")
        
        proc = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )

        # Thread to read/print output
        import threading
        def stream_output():
            for line in proc.stdout:
                print(line, end='')
                sys.stdout.flush()
        
        t = threading.Thread(target=stream_output, daemon=True)
        t.start()

        # Wait for health
        base_url = f"http://127.0.0.1:{server_port}"
        start = time.time()
        while time.time() - start < 15:
            try:
                httpx.get(f"{base_url}/health")
                print("READY")
                sys.stdout.flush()
                break
            except:
                time.sleep(0.5)
        else:
            print("Server failed to start")
            cleanup()

        # Keep running until signal
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
        cleanup()

if __name__ == "__main__":
    main()
