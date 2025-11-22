import uvicorn
import os
import sys

# Add parent directory to path (enterprise_api root)
current_dir = os.path.dirname(os.path.abspath(__file__)) # tests/load
root_dir = os.path.dirname(os.path.dirname(current_dir)) # enterprise_api
sys.path.insert(0, root_dir)

if __name__ == "__main__":
    # Env vars should be passed by caller
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)), log_level="error")
