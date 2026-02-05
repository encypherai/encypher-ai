"""Debug script to see what the API is actually returning."""

import asyncio
import httpx
import os

async def debug_zw_response():
    """Check what the API returns for zw_embedding."""
    
    # Get API key from env
    api_key = os.getenv("API_KEY", "test_key_professional")
    base_url = "http://localhost:8000"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Test with 3 sentences
    text = "First sentence for ZW test. Second sentence here. Third sentence completes it."
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        response = await client.post(
            "/api/v1/sign/advanced",
            headers=headers,
            json={
                "document_id": "debug_zw_001",
                "text": text,
                "manifest_mode": "zw_embedding",
                "segmentation_level": "sentence",
            },
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            embedded = data.get("embedded_content")
            
            if embedded:
                from app.utils.zw_crypto import find_all_minimal_signed_uuids
                
                # Use contiguous sequence detection (no magic numbers)
                found_sigs = find_all_minimal_signed_uuids(embedded)
                count = len(found_sigs)
                print(f"\nOriginal text: {len(text)} chars")
                print(f"Embedded text: {len(embedded)} chars")
                print(f"Overhead: {len(embedded) - len(text)} chars")
                print(f"ZW signatures found: {count}")
                print(f"Expected: 3 signatures")
                
                # Show positions of each signature
                print(f"\nSignature positions:")
                for i, (start, end, sig) in enumerate(found_sigs):
                    print(f"  Signature #{i+1}: pos {start}-{end} ({len(sig)} chars)")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_zw_response())
