import pytest
import subprocess
import time
import sys
from pathlib import Path

# Path to enterprise_api root
SDK_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = SDK_ROOT.parent / "enterprise_api"

@pytest.fixture(scope="session")
def live_api_server():
    """
    Starts the Enterprise API server (and Postgres via Docker) for integration tests.
    Yields the base URL.
    """
    script_path = API_ROOT / "scripts" / "start_test_server.py"
    
    # Use 'uv run' to execute in the API environment
    # Assuming uv is in PATH
    cmd = ["uv", "run", "python", str(script_path)]
    
    log_file = open("api_server.log", "w")
    print(f"Starting API Server: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        cwd=str(API_ROOT),
        stdout=log_file,
        stderr=log_file,
        text=True,
        bufsize=1
    )
    
    try:
        # Wait for "READY" signal in the log file
        start_time = time.time()
        ready = False
        while time.time() - start_time < 60:
            log_file.flush()
            with open("api_server.log", "r") as f:
                content = f.read()
                if "READY" in content:
                    ready = True
                    break
            time.sleep(0.5)
        
        if not ready:
            print("Server failed to start within timeout.")
            log_file.flush()
            stdout, stderr = process.communicate()
            if stdout: print(f"[Server Output] {stdout}")
            if stderr: print(f"[Server Error] {stderr}")
            with open("api_server.log", "r") as f:
                print(f"[Server Log (Tail 200 lines)]\n{f.read()[-10000:]}")
            raise RuntimeError("Failed to start API server")
            
        yield "http://127.0.0.1:8093"
        
    finally:
        print("Stopping API Server...")
        if sys.platform == "win32":
            subprocess.call(["taskkill", "/F", "/T", "/PID", str(process.pid)])
        else:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        log_file.close()
