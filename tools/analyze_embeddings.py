"""Comprehensive analysis of embeddings, segmentation, and Merkle tree."""
import asyncio
from pathlib import Path
import httpx

async def analyze():
    # Read the original article
    article_path = Path('../outputs/wikipedia_prepared/part_00000/article_0000000.txt')
    original_text = article_path.read_text(encoding='utf-8')
    
    print("=" * 80)
    print("ARTICLE ANALYSIS")
    print("=" * 80)
    print(f"Article: {article_path.name}")
    print(f"Original size: {len(original_text)} chars")
    print(f"Original lines: {len(original_text.splitlines())}")
    
    # Call the API to get embedding info
    api_url = 'http://127.0.0.1:9000/api/v1/enterprise/embeddings/encode-with-embeddings'
    headers = {'Authorization': 'Bearer demo-key-local'}
    data = {
        'document_id': article_path.stem,
        'text': original_text,
        'segmentation_level': 'sentence',
        'embedding_options': {'include_text': True}
    }
    
    print("\n" + "=" * 80)
    print("CALLING EMBEDDING API")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=120.0, headers=headers) as client:
        r = await client.post(api_url, json=data)
        r.raise_for_status()
        response = r.json()
    
    # Extract statistics
    stats = response.get('statistics', {})
    embedded_content = response.get('embedded_content', '')
    merkle_tree = response.get('merkle_tree', {})
    embeddings = response.get('embeddings', [])
    
    print("✓ API call successful")
    print("\nSegmentation:")
    print(f"  - Total sentences: {stats.get('total_sentences', 0)}")
    print(f"  - Embeddings created: {stats.get('embeddings_created', 0)}")
    print(f"  - Segmentation level: {stats.get('segmentation_level', 'N/A')}")
    print(f"  - Processing time: {stats.get('processing_time_ms', 0):.2f} ms")
    print("\nMerkle Tree:")
    print(f"  - Root ID: {merkle_tree.get('root_id', 'N/A')}")
    print(f"  - Root hash: {merkle_tree.get('root_hash', 'N/A')[:32]}...")
    print(f"  - Tree depth: {merkle_tree.get('depth', 0)}")
    print(f"  - Leaf count: {merkle_tree.get('leaf_count', 0)}")
    
    print("\nEmbedded Content:")
    print(f"  - Size: {len(embedded_content)} chars")
    print(f"  - Size increase: {((len(embedded_content) - len(original_text)) / len(original_text) * 100):.1f}%")
    
    # Count invisible characters
    invisible_count = sum(1 for c in embedded_content if ord(c) > 0xE0000 or (0xFE00 <= ord(c) <= 0xFE0F))
    print(f"  - Invisible chars: {invisible_count}")
    
    # Check for C2PA wrapper
    has_c2pa = any(ord(c) > 0xE0000 for c in embedded_content[-5000:])
    print(f"  - Has C2PA wrapper at end: {has_c2pa}")
    
    # Decode embeddings from the embedded content
    print("\n" + "=" * 80)
    print("DECODING EMBEDDINGS")
    print("=" * 80)
    
    # Try to extract metadata from embedded content using our library
    try:
        from shared_commercial_libs.unicode_metadata import UnicodeMetadata
        
        extracted = UnicodeMetadata.extract_metadata(embedded_content)
        if extracted:
            print("✓ Successfully extracted C2PA metadata")
            print("\nExtracted Metadata:")
            print(f"  - Instance ID: {extracted.get('instance_id', 'N/A')}")
            print(f"  - Signer ID: {extracted.get('signer_id', 'N/A')}")
            print(f"  - Timestamp: {extracted.get('timestamp', 'N/A')}")
            print(f"  - Document ID: {extracted.get('document_id', 'N/A')}")
            print(f"  - Merkle root: {extracted.get('merkle_root_id', 'N/A')}")
            print(f"  - Total segments: {extracted.get('total_segments', 'N/A')}")
        else:
            print("✗ No metadata extracted")
    except Exception as e:
        print(f"✗ Error extracting metadata: {e}")
    
    # Get Merkle tree structure
    print("\n" + "=" * 80)
    print("MERKLE TREE STRUCTURE")
    print("=" * 80)
    
    merkle_root_id = merkle_tree.get('root_id')
    if merkle_root_id:
        tree_url = f'http://127.0.0.1:9000/api/v1/enterprise/merkle/tree/{merkle_root_id}'
        
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            r = await client.get(tree_url)
            if r.status_code == 200:
                tree_data = r.json()
                print("✓ Merkle tree retrieved from database")
                print("\nTree Info:")
                print(f"  - Root ID: {merkle_root_id}")
                print(f"  - Root hash: {tree_data.get('root_hash', 'N/A')[:32]}...")
                print(f"  - Total nodes: {len(tree_data.get('nodes', []))}")
                print(f"  - Leaf nodes: {len([n for n in tree_data.get('nodes', []) if n.get('is_leaf')])}")
                print(f"  - Internal nodes: {len([n for n in tree_data.get('nodes', []) if not n.get('is_leaf')])}")
                
                # Show first few leaf nodes
                leaves = [n for n in tree_data.get('nodes', []) if n.get('is_leaf')][:5]
                if leaves:
                    print(f"\nFirst {len(leaves)} leaf nodes:")
                    for i, leaf in enumerate(leaves):
                        print(f"  [{i}] Hash: {leaf.get('hash', 'N/A')[:16]}... | Index: {leaf.get('leaf_index', 'N/A')}")
            else:
                print(f"✗ Could not retrieve Merkle tree (status {r.status_code})")
    else:
        print("✗ No merkle_root_id in response")
    
    # Show embedding details
    print("\n" + "=" * 80)
    print("EMBEDDING DETAILS")
    print("=" * 80)
    
    if embeddings:
        print(f"✓ {len(embeddings)} embeddings in response")
        print("\nFirst 5 embeddings:")
        for i, emb in enumerate(embeddings[:5]):
            print(f"  [{i}] Leaf index: {emb.get('leaf_index', 'N/A')} | Hash: {emb.get('leaf_hash', 'N/A')[:16]}...")
            print(f"      Text preview: {emb.get('text_content', '')[:50]}...")
    else:
        print("✗ No embeddings in response")
    
    # Show sample of embedded content
    print("\n" + "=" * 80)
    print("SAMPLE EMBEDDED CONTENT")
    print("=" * 80)
    
    lines = embedded_content.splitlines()
    print(f"Showing first 3 lines (of {len(lines)} total):\n")
    for i, line in enumerate(lines[:3], 1):
        # Show visible text and indicate invisible chars
        visible_chars = sum(1 for c in line if ord(c) < 0xE0000 and not (0xFE00 <= ord(c) <= 0xFE0F))
        invisible_chars = len(line) - visible_chars
        
        # Truncate long lines
        display_line = line[:100] + "..." if len(line) > 100 else line
        print(f"Line {i}: {display_line}")
        print(f"  → {visible_chars} visible chars, {invisible_chars} invisible chars\n")
    
    print("=" * 80)
    print("ANALYSIS COMPLETE ✓")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(analyze())
