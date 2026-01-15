#!/usr/bin/env python3
"""
Manual test: Sign content and verify it to confirm backend works.
Tests the full flow: sign via enterprise_api → verify via verification-service.
"""
import httpx
import json
import sys

API_BASE = "http://localhost:8000/api/v1"
ENTERPRISE_API_BASE = "http://localhost:9000/api/v1"

def test_sign_and_verify():
    """Sign content with demo key, then verify it."""
    
    # Step 1: Sign content using enterprise_api
    print("=" * 60)
    print("STEP 1: Signing content via enterprise_api")
    print("=" * 60)
    
    sign_payload = {
        "text": "Hello, world.",
        "metadata_format": "c2pa",
        "signer_id": "org_demo"
    }
    
    print(f"\nPOST {ENTERPRISE_API_BASE}/sign")
    print(f"Payload: {json.dumps(sign_payload, indent=2)}")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            sign_response = client.post(
                f"{ENTERPRISE_API_BASE}/sign",
                json=sign_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nStatus: {sign_response.status_code}")
            
            if sign_response.status_code != 200:
                print(f"Error: {sign_response.text}")
                return False
            
            sign_data = sign_response.json()
            print(f"Response: {json.dumps(sign_data, indent=2)[:500]}...")
            
            if not sign_data.get("success"):
                print(f"Sign failed: {sign_data}")
                return False
            
            signed_text = sign_data.get("data", {}).get("signed_text")
            if not signed_text:
                print("No signed_text in response!")
                return False
            
            print(f"\nSigned text length: {len(signed_text)} bytes")
            print(f"First 100 chars: {repr(signed_text[:100])}")
            
    except Exception as e:
        print(f"Sign request failed: {e}")
        return False
    
    # Step 2: Verify the signed content
    print("\n" + "=" * 60)
    print("STEP 2: Verifying signed content via verification-service")
    print("=" * 60)
    
    verify_payload = {
        "text": signed_text
    }
    
    print(f"\nPOST {API_BASE}/verify")
    print(f"Payload text length: {len(signed_text)} bytes")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            verify_response = client.post(
                f"{API_BASE}/verify",
                json=verify_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nStatus: {verify_response.status_code}")
            
            if verify_response.status_code != 200:
                print(f"Error: {verify_response.text}")
                return False
            
            verify_data = verify_response.json()
            print(f"\nResponse: {json.dumps(verify_data, indent=2)}")
            
            correlation_id = verify_data.get("correlation_id")
            print(f"\n{'='*60}")
            print(f"CORRELATION_ID: {correlation_id}")
            print(f"{'='*60}")
            
            verdict = verify_data.get("data", {})
            reason_code = verdict.get("reason_code")
            signer_id = verdict.get("signer_id")
            is_valid = verdict.get("valid")
            
            print(f"\nVerdict:")
            print(f"  - valid: {is_valid}")
            print(f"  - reason_code: {reason_code}")
            print(f"  - signer_id: {signer_id}")
            
            if reason_code == "SIGNER_UNKNOWN":
                print("\n❌ FAILED: Got SIGNER_UNKNOWN")
                print(f"\nTo see logs, run:")
                print(f"  docker logs encypher-verification-service | grep '{correlation_id}'")
                return False
            elif reason_code in ("OK", "UNTRUSTED_SIGNER"):
                print(f"\n✅ SUCCESS: Verification worked (reason: {reason_code})")
                return True
            else:
                print(f"\n⚠️  Unexpected reason_code: {reason_code}")
                return False
            
    except Exception as e:
        print(f"Verify request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sign_and_verify()
    sys.exit(0 if success else 1)
