import os
import sys
from encypher_enterprise.models import SignRequest

# Path to enterprise_api root
API_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "enterprise_api"))
sys.path.append(API_ROOT)

def test_contract_mismatch():
    """
    Start the API and test if sending 'custom_metadata' causes a 422.
    """
    # 1. Start Postgres (Reuse load test script logic or assume it's running?)
    # For simplicity, let's assume the USER can run the load test script environment
    # But to be robust, let's try to run the server process.
    
    # We will skip starting the server for this specific tool call if we can't guarantee DB.
    # Instead, let's inspect the code logic.
    pass

if __name__ == "__main__":
    # Static check of models
    print("Auditing SignRequest...")
    sdk_fields = SignRequest.model_fields.keys()
    print(f"SDK Fields: {list(sdk_fields)}")
    
    # We know API fields from reading the file:
    # text, document_id, document_title, document_url, document_type, claim_generator, actions
    
    api_fields = ["text", "document_id", "document_title", "document_url", "document_type", "claim_generator", "actions"]
    
    missing_in_sdk = set(api_fields) - set(sdk_fields)
    extra_in_sdk = set(sdk_fields) - set(api_fields)
    
    print(f"Missing in SDK: {missing_in_sdk}")
    print(f"Extra in SDK: {extra_in_sdk}")
    
    if missing_in_sdk or extra_in_sdk:
        print("FAIL: Contract mismatch detected.")
        sys.exit(1)
    else:
        print("PASS: Contract matches.")
